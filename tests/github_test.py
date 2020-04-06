import unittest
import unittest.mock

import dockerfilegenerator.lib.exceptions as exceptions
import dockerfilegenerator.lib.github as github

import constants


class GitHubRepositoryTestCase(unittest.TestCase):

    def setUp(self):
        with unittest.mock.patch("github.Github") as github_mock:
            github_mock.return_value = GitHubMock("access_key")
            self.repo = github.get_github_repository("repo_name", "access_key")

    def test_get_latest_release(self):
        self.repo.repo.set_releases(["1.0", "0.99", "0.98", "0.97"])
        self.assertEqual(self.repo.latest_release_version(), "1.0")

    def test_get_latest_release_none(self):
        self.repo.repo.set_releases(["1.0", "0.99", "0.98", "0.97"])
        self.repo.repo.set_releases_prerelease()
        self.assertIsNone(self.repo.latest_release_version())

    def test_get_file_contents(self):
        self.assertEqual(self.repo.get_file_contents(
            "some-path", "some-ref"), constants.TEST_GITHUB_GET_FILE_CONTENTS)

    def test_commit(self):
        self.repo.commit([("file1", "file1 content")], "Commiting file1")


class GitHubRepositoryUtilsTestCase(unittest.TestCase):

    def test_get_github_repository_successfull(self):
        with unittest.mock.patch("github.Github") as github_mock:
            github_mock.return_value = GitHubMock("access_key")
            obj = github.get_github_repository("repo_name", "access_key")
            self.assertIsInstance(obj, github.GitHubRepository)
            self.assertIsNotNone(obj)
            self.assertEqual(obj.name, "repo_name")

    def test_get_github_repository_failure(self):
        with unittest.mock.patch("github.Github") as github_mock:
            github_mock.return_value = GitHubMock(
                "access_key", raise_exception=True)
            with self.assertRaises(exceptions.LambdaException):
                github.get_github_repository("repo_name", "access_key")


class GitHubMock:

    def __init__(self, access_key, raise_exception=False):
        self.access_key = access_key
        self.raise_exception = raise_exception
        self.releases = []

    def get_repo(self, name):
        if self.raise_exception:
            raise Exception("All right..")
        repo = GithubRepositoryMock(name, self.access_key)
        repo.set_releases(self.releases)
        return repo


class GithubRepositoryMock:

    def __init__(self, *args, **kwargs):
        self.releases = []

    def get_git_ref(self, branch):
        return GitRefMock()

    def get_git_tree(self, ref):
        return None

    def create_git_tree(self, index, tree):
        return "<tree>"

    def get_git_commit(self, sha):
        return "<parent>"

    def create_git_commit(self, commit, tree, parent):
        return GitRefMock()

    def set_releases(self, rel_names):
        self.releases = [RepoReleaseMock(name) for name in rel_names]

    def set_releases_prerelease(self):
        for rel in self.releases:
            rel.prerelease = True

    def get_releases(self):
        return self.releases

    def get_file_contents(self, file_path, ref):
        return FileContentsMock(constants.TEST_GITHUB_GET_FILE_CONTENTS)


class RepoReleaseMock:

    def __init__(self, name):
        self.tag_name = name
        self.prerelease = False


class FileContentsMock:

    def __init__(self, content):
        self.decoded_content = bytes(content, "utf-8")


class GitRefMock:

    def __init__(self):
        self.object = self
        self.sha = "<sha>"

    def edit(self, param):
        pass
