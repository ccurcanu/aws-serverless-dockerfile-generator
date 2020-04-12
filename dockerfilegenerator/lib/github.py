# -*- coding: utf-8 -*-

import github

import dockerfilegenerator.lib.constants as constants
import dockerfilegenerator.lib.exceptions as exceptions


class GitHubRepository:
    """ Code repository in GitHub is modeled by this class.

    The __init__ method accepts the following arguments:
        name (str): Full name of the repository in GitHub
            (i.e. hashicorp/terraform).
        access_token (str): GitHub account access token.

    """

    def __init__(self, name, access_token):
        self.github = github.Github(access_token)
        self.repo = self.github.get_repo(name)
        self.name = name

    def latest_release_version(self):
        """ Return latest release version of the GitHub repository.

        Note:
               Some GitHub repositories code releases are not convergent
            with the release processes of the product they are offering.

                As an example, hashicorp/terraform have the GitHub repository
            in sync with the product releases as mentioned on the official web
            site, allowing us to use this method, but ansible/ansible is not.

        Returns:
            Version of the latest relese (str, i.e.: 'v0.11.9'), or None"""

        releases = [
            rel for rel in self.repo.get_releases()
            if not rel.prerelease]
        if len(releases):
            return releases[0].tag_name

    def get_file_contents(self, file_rel_path, ref="master"):
        """Return the content of the file in a GitHub repository.

        Parameters:
            file_path (str): Relative file path to code repo.
            ref (str): Branch name (default: master)

        Return:
            Content of the file (str)."""
        content = self.repo.get_contents(file_rel_path, ref)
        return content.decoded_content.decode()

    def commit(self,
               commit_files,
               commit_msg,
               branch="heads/master",
               type="text",
               mode="100644"):
        """
            Commit a list of files on specified branch.

        Notes:
            At this moment it supports only text file.

        Parameters:
            commit_files (list):Tuples like (file name, content as str).
            commit_msg (str): Commit message.
            branch (str): Branch name (default: heads/master).
            type (str): Default is 'text'), may be 'blob', or others also.
            mode (str): File mode (default: '100644')."""

        index_files = []
        master_ref = self.repo.get_git_ref(branch)
        base_tree = self.repo.get_git_tree(master_ref.object.sha)
        for file_entry in commit_files:
            file_name, file_content = file_entry[0], file_entry[1]
            tree_el = github.InputGitTreeElement(
                file_name, mode, type, file_content)
            index_files.append(tree_el)
        tree = self.repo.create_git_tree(index_files, base_tree)
        parent = self.repo.get_git_commit(master_ref.object.sha)
        commit = self.repo.create_git_commit(commit_msg, tree, [parent])
        master_ref.edit(commit.sha)


def get_github_repository(name, access_token=constants.GITHUB_ACCESS_TOKEN):
    try:
        return GitHubRepository(name, access_token)
    except Exception as e:
        raise exceptions.LambdaException(
            "Error: GitHubRepository('%s'): %s" % (name, str(e)))
