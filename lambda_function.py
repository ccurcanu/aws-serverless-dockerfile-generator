# -*- coding: utf-8 -*-

import copy
import datetime
import os
import logging
import sys
import hashlib
import json

import boto3
import botocore.exceptions
import github

GITHUB_ACCESS_TOKEN = os.environ.get("github_access_token", None)
DOCKERFILE_GITHUB_REPO = os.environ.get("dockerfile_github_repository", None)
INTERNAL_STORE_PATH = "internal/store.json"


class GitHubRepository():
    """ Code repository in GitHub is modeled by this class.

    The __init__ method accepts the following arguments:
        name (str): Full name of the repository in GitHub (i.e. hashicorp/terraform).
        access_token (str): GitHub account access token.

    """

    def __init__(self, name, access_token):
        self.github = github.Github(access_token)
        self.repo = self.github.get_repo(name)

    @property
    def latest_release_version(self):
        """ Return latest release version of the GitHub repository.

        Note:
            Some GitHub repositories code releases are not convergent with the release processes
            of the actual product they are offering. As an example, hashicorp/terraform have
            the GitHub repository in sync with the product releases as mentioned on the
            official web site, allowing us to use this method reliably, but ansible/ansible is not.

        Returns:
            Version of the latest relese (str, i.e.: 'v0.11.9'), or None

        """
        releases = [ rel for rel in self.repo.get_releases() if not rel.prerelease ]
        if len(releases):
            return releases[0].tag_name

    def get_file_content(self, file_path, ref="master"):
        """Return the content of the file.

        Args:
            file_path (str): Path of the file relative to root of the code repository.
            ref (str): Branch reference that you want to use (default: master)

        Return:
            Content of the file (str).

        """
        return self.repo.get_file_contents(file_path, ref).decoded_content.decode()

    def commit(self, commit_files, commit_msg, branch="heads/master", type="text", mode="100644"):
        """ Commit a list of files on specified branch.

        Note:
            At this moment it supports only text file. The full implementation should deal with blobs also.
            In case of blobs we should also encode the content before adding it to the tree.

        Args:
            commit_files (list): A list of tuples containing the file name, and file content as str objects.
            commit_msg (str): Commit message.
            branch (str): Branch reference where the commit will be added (default: heads/master).
            type (str): Type of the content (default: 'text'). May be blob, or others also.
            mode (str): File mode of the commited files (default: '100644').

        """
        index_files = []
        master_ref = self.repo.get_git_ref(branch)
        master_sha = master_ref.object.sha
        base_tree = self.repo.get_git_tree(master_ref.object.sha)
        for file_entry in commit_files:
            file_name,file_content = file_entry[0], file_entry[1]
            tree_el = github.InputGitTreeElement(file_name, mode, type, file_content)
            index_files.append(tree_el)
        tree = self.repo.create_git_tree(index_files, base_tree)
        parent = self.repo.get_git_commit(master_ref.object.sha)
        commit = self.repo.create_git_commit(commit_msg, tree, [parent])
        master_ref.edit(commit.sha)


class Store():
    """ Internal JSON file modeled as a store.

    The __init__ method accepts the following arguments:
        file_content (str): Content of the JSON obj that will be constructed.
        dockerfile_repo_name (str): Name of the dockerfile GitHub repository.

    Note:
        The Dockerfile repository (ccurcanu/docker-cloud-tools) has a JSON file located into internal/store.json
        where internal state is stored. Most important is the versions of each tracked cloud management tool.
        Other internal state is stored.

    """

    def __init__(self, file_content, dockerfile_repo_name=DOCKERFILE_GITHUB_REPO):
        self.json = json.loads(file_content)
        self.dockerfile_repo_name = os.path.basename(dockerfile_repo_name)

    @property
    def dump(self):
        """ Dump of the JSON object as str with visibile identation"""
        return json.dumps(self.json, indent=4)

    @property
    def sha(self):
        """ SHA256 hash of the internal JSON dump"""
        content = self.dump.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    @property
    def template_variables(self):
        """ Return dict used to populate README.md and Dockerfile templates with values.

            Note:
                keys (str): Are mentioned as template key for each tracked cloud tool in the internal tool.
                values (str): Values are the versions mentioned in the internal store.

            It will be fed to str().format() method in order to populate the template content with variable.

        """
        template = dict()
        for item in self.json:
            remove_prefix = self.remove_prefix(item)
            version = self.json[item]["version"]
            if remove_prefix and version.startswith(remove_prefix):
                version = self.json[item]["version"].replace(remove_prefix, "")
            template.update({self.json[item]["template_key"]: version})
        return template

    def equals(self, store):
        """ Compare two objects and return True if they are having same content."""
        return self.sha == store.sha

    def different(self, store):
        """ Compare two objects, complement of equals method above."""
        return not self.equals(store)

    def version(self, tool_name):
        """ Version (str) of the tool, as specified in the internal JSON content."""
        if tool_name in self.json:
            return self.json[tool_name]["version"]

    def set_version(self, tool_name, version):
        if tool_name in self.json:
            self.json[tool_name]["version"] = version
        else:
            raise Exception("Error: repo key %s not existing in store" % tool_name)

    def set_next_version_dockerfile(self):
        """ Increments the version of the dockerfile repository as specified in internal JSON content"""
        next_ver = int(self.json[self.dockerfile_repo_name]["version"].strip()) + 1
        self.json[self.dockerfile_repo_name]["version"] = str(next_ver)

    def github_repo_full_name(self, tool_name):
        """ Get the full name of the repository as it is mentioned in the internal JSON content."""
        if tool_name in self.json:
            return self.json[tool_name]["github_repo"]

    def remove_prefix(self, tool_name):
        """ Return version str prefix if JSON content entry has ``remove_prefix`` specified.

            Note:
                Some tools have versions like 'v0.11.9' (terraform), or "go1.11.1" (go).

            Return:
                prefix (str): Prefix of the version.
                None: if the ```remove_prefix``` is not present in the tool item. """
        if tool_name in self.json:
            if "remove_prefix" in self.json[tool_name]:
                return self.json[tool_name]["remove_prefix"]

    def force_version(self, tool_name):
        """ Detect if ``force_version`` tag is present in the JSON content entry
            for the tool_name. """
        if tool_name in self.json:
            return "force_version" in self.json[tool_name]
        return False

    def update_summary(self, other_store):
        """ Composes a version update summary (str) comparing current state with
            the state of another similar type object. """
        summary = str()
        headline = "Changes detected on:"
        has_changes = False
        for k, v in self.json.items():
            other_ver = other_store.version(k)
            curr_ver = self.version(k)
            if curr_ver == other_ver:
                continue
            headline += " %s" % k
            summary += "%s\t\t changed version %s -> %s \n" % (k, other_ver, curr_ver)
            has_changes = True
        if has_changes:
            return headline + '\n' + summary


class StorageManager():
    """ S3 object storage is modelled by this class.

        The __init__ method has the following arguments:
            bucket_name (str): Name of the bucket

    """
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3_resource = boto3.resource("s3")

    def read_object(self, file_name):
        try:
            file_obj = self.s3_resource.Object(self.bucket_name, file_name)
            return file_obj.get()["Body"].read().decode()
        except botocore.exceptions.ClientError as e:
            return

    def write_object(self, file_name, content):
        file_obj = self.s3_resource.Object(self.bucket_name, file_name)
        file_obj.put(Body=content.encode("utf-8"))


class LambdaException(Exception):
    """ Will used this to handle exceptions. """

    pass


def github_repository(name, access_token=GITHUB_ACCESS_TOKEN):
    try:
        return GitHubRepository(name, access_token)
    except Exception as e: # @TODO: Please remove Exception
        raise LambdaException("Error: GitHubRepository('%s'): %s" % \
                (name, str(e)))


def main(context, is_testing_env=False):

    bucket_name = os.environ.get("internal_s3_bucket", None)
    if bucket_name is None:
        raise LambdaException("Error: internal_s3_bucket env variable not set.")

    storage_mngr = StorageManager(bucket_name=bucket_name)
    lambda_store_content = storage_mngr.read_object(INTERNAL_STORE_PATH)

    dockerfile_github = github_repository(DOCKERFILE_GITHUB_REPO)
    store_content = dockerfile_github.get_file_content(INTERNAL_STORE_PATH)
    dockerfile_store = Store(store_content)
    dockerfile_store_orig = copy.deepcopy(dockerfile_store)
    terraform_github = github_repository(dockerfile_store.github_repo_full_name("terraform"))

    if lambda_store_content is None:
        content = dockerfile_store.dump
        storage_mngr.write_object(INTERNAL_STORE_PATH, content)
        lambda_store = Store(content)
    else:
        lambda_store = Store(lambda_store_content)

    curr_tf_ver = dockerfile_store.version("terraform")
    new_tf_ver = terraform_github.latest_release_version
    if is_testing_env:
        new_tf_ver = context.get("terraform_version", None)
    force_tf_ver = dockerfile_store.force_version("terraform")
    if curr_tf_ver != new_tf_ver and (not force_tf_ver):
        dockerfile_store.set_version("terraform", new_tf_ver)

    if dockerfile_store.different(lambda_store):
        dockerfile_store.set_next_version_dockerfile()
        template_readme = dockerfile_github.get_file_content("templates/README.md")
        template_dockerfile = dockerfile_github.get_file_content("templates/Dockerfile")
        commit_msg = dockerfile_store.update_summary(lambda_store)
        store_dump = dockerfile_store.dump
        commit_files_dockerfile = [
            ("internal/store.json", store_dump),
            ("Dockerfile", template_dockerfile.format(**dockerfile_store.template_variables)),
            ("README.md", template_readme.format(**dockerfile_store.template_variables))
        ]
        dockerfile_github.commit(commit_files_dockerfile, commit_msg)
        try:
            storage_mngr.write_object(INTERNAL_STORE_PATH, store_dump)
        except botocore.exceptions.ClientError as e:
            raise LambdaException("Error: Uploading object to s3 bucket: %s" % (str(e)))

    return 0


def lambda_handler(event, context, is_testing_env=False):
	return main(context, is_testing_env=is_testing_env)
