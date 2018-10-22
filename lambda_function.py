#!/usr/bin/env python

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
INTERNAL_S3_BUCKET_NAME = os.environ.get("internal_s3_bucket", None)
INTERNAL_STORE_PATH = "internal/store.json"


class GitHubRepository():

    def __init__(self, name, access_token):
        self.github = github.Github(access_token)
        self.repo = self.github.get_repo(name)

    @property
    def name(self):
        return self.repo.name

    @property
    def latest_version(self):
        releases = [ rel for rel in self.repo.get_releases() if not rel.prerelease ]
        if len(releases):
            return releases[0].tag_name

    def get_file_content(self, file_path, ref="master"):
        return self.repo.get_file_contents(file_path, ref).decoded_content.decode()

    def commit(self, commit_files, commit_msg, branch="heads/master", type="text", mode="100644"):
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

    def __init__(self, file_content, dockerfile_repo_name=DOCKERFILE_GITHUB_REPO):
        self.json = json.loads(file_content)
        self.dockerfile_repo_name = os.path.basename(dockerfile_repo_name)

    def dumps(self):
        return json.dumps(self.json, indent=4)

    def dump_template_variables(self):
        template = dict()
        for item in self.json:
            remove_prefix = self.remove_prefix(item)
            version = self.json[item]["version"]
            if remove_prefix and version.startswith(remove_prefix):
                version = self.json[item]["version"].replace(remove_prefix, "")
            template.update({self.json[item]["template_key"]: version})
        return template

    @property
    def sha(self):
        content = self.dumps().encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def equals(self, store):
        return self.sha == store.sha

    def different(self, store):
        return not self.equals(store)

    def version(self, repo_name):
        if repo_name in self.json:
            return self.json[repo_name]["version"]

    def set_version(self, repo_name, version):
        if repo_name in self.json:
            self.json[repo_name]["version"] = version
        else:
            raise Exception("Error: repo key %s not existing in store" % repo_name)

    def set_next_version_dockerfile(self):
        next_ver = int(self.json[self.dockerfile_repo_name]["version"].strip()) + 1
        self.json[self.dockerfile_repo_name]["version"] = str(next_ver)

    def get_dockerfile_version(self):
        return self.json[dockerfile_repo_name]["version"]

    def github_repo_full_name(self, repo_name):
        if repo_name in self.json:
            return self.json[repo_name]["github_repo"]

    def remove_prefix(self, repo_name):
        if repo_name in self.json:
            if "remove_prefix" in self.json[repo_name]:
                return self.json[repo_name]["remove_prefix"]

    def force_version(self, repo_name):
        if repo_name in self.json:
            return "force_version" in self.json[repo_name]

    def update_summary(self, other_store):
        summary = str()
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        headline = "%s changes on:" % now
        for k, v in self.json.items():
            other_ver = other_store.version(k)
            curr_ver = self.version(k)
            if curr_ver == other_ver:
                continue
            headline += " %s" % k
            summary += "%s\t\t changed version %s -> %s \n" % (k, other_ver, curr_ver)
        return headline + '\n' + summary


def github_repository(name, access_token=GITHUB_ACCESS_TOKEN):
    if access_token:
        return GitHubRepository(name, access_token)
    else:
        raise Exception("Error: Could not create '%s' repo obj as the github access token is empty" % name)



class StorageManager():

    def __init__(self, bucket_name=INTERNAL_S3_BUCKET_NAME):
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


def main():

    internal_store = StorageManager()

    dockerfile_github = github_repository(DOCKERFILE_GITHUB_REPO)
    dockerfile_store = Store(dockerfile_github.get_file_content(INTERNAL_STORE_PATH))
    dockerfile_store_orig = copy.deepcopy(dockerfile_store)

    lambda_internal_store = internal_store.read_object(INTERNAL_STORE_PATH)
    if lambda_internal_store is None:
        content = dockerfile_store.dumps()
        internal_store.write_object(INTERNAL_STORE_PATH, content)
        lambda_store = Store(content)
    else:
        lambda_store = Store(lambda_internal_store)

    template_readme = dockerfile_github.get_file_content("templates/README.md")
    template_dockerfile = dockerfile_github.get_file_content("templates/Dockerfile")

    terraform_github = github_repository(dockerfile_store.github_repo_full_name("terraform"))
    current_terraform_version = dockerfile_store.version("terraform")
    latest_terraform_version = terraform_github.latest_version
    if current_terraform_version != latest_terraform_version:
        dockerfile_store.set_version("terraform", latest_terraform_version)

    if dockerfile_store.different(dockerfile_store_orig):
        dockerfile_store.set_next_version_dockerfile()
        commit_msg = dockerfile_store.update_summary(dockerfile_store_orig)
        template_variables = dockerfile_store.dump_template_variables()
        store_dump = dockerfile_store.dumps()
        commit_files_dockerfile = [
            ("internal/store.json", store_dump),
            ("Dockerfile", template_dockerfile.format(**template_variables)),
            ("README.md", template_readme.format(**template_variables))
        ]
        dockerfile_github.commit(commit_files_dockerfile, commit_msg)
        internal_store.write_object(INTERNAL_STORE_PATH, store_dump)
    return 0


def lambda_handler(event, context):
	return main()
