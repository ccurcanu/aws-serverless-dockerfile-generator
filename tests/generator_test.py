# -*- coding: utf-8 -*-

import copy
import os
import unittest
import unittest.mock as mock

import dockerfilegenerator.lib.exceptions as exceptions

import constants


ENVIRON_PATCH = {
    "dockerfile_github_repository": "something/docker-cloud-tools",
    "github_access_token": "<sometoken>",
    "internal_s3_bucket":  "<bucketname>"
}

with mock.patch.dict(os.environ, ENVIRON_PATCH):
    import mocks
    from dockerfilegenerator.lib import jsonstore
    from dockerfilegenerator import generator


class TestsMixin:

    @mock.patch.dict(os.environ, ENVIRON_PATCH)
    def _init_generator(self,
                        storage_manager_return_read_none=False,
                        storage_manager_raise_exception_when_write=False):
        with mock.patch(constants.S3STORE_MNGR_NAME) as s3_bucket_mngr:
            storage_manager = mocks.FakeStorageManager("bucketname")
            storage_manager.read_return_none = storage_manager_return_read_none
            storage_manager.raise_exception = \
                storage_manager_raise_exception_when_write
            s3_bucket_mngr.return_value = storage_manager
            with mock.patch(constants.GITHUB_REPO_NAME) as github_repo:
                github_repo.return_value = mocks.FakeGitHubRepository(
                    "docker-cloud-tools")
                self.generator = generator.DockerfileGeneratorLambda()
        self.mockTrackedTools = {
            "terraform": self._get_version,
            "packer": self._get_version}
        generator.TRACKED_TOOLS = self.mockTrackedTools

    def _update_dockerfile_versions(self, dockerfile_content):
        self.generator.dockerfile = jsonstore.Store(
            dockerfile_content, "docker-cloud-tools")
        original_dockerfile = copy.deepcopy(self.generator.dockerfile)
        self.generator.update_dockerfile_versions()
        return original_dockerfile

    def _get_version(self, version="v1.0.0"):
        return version


class GeneratorUtilsTestCase(unittest.TestCase, TestsMixin):

    def setUp(self):
        self._init_generator()

    def test_tools_current_versions(self):
        self.assertFalse(hasattr(self.generator, "_tools_current_versions"))
        self.assertDictEqual(
            self.generator.tools_current_versions,
            constants.EXPECTED_TOOLS_CURRENT_VERSION)
        self.assertDictEqual(
            self.generator.tools_current_versions,
            constants.EXPECTED_TOOLS_CURRENT_VERSION)

    def test_tools_next_versions(self):
        self.assertFalse(
            hasattr(self.generator, "_tools_next_versions"))
        self.assertDictEqual(
            self.generator.tools_next_versions,
            constants.EXPECTED_TOOLS_NEXT_VERSION)
        self.assertDictEqual(
            self.generator.tools_next_versions,
            constants.EXPECTED_TOOLS_NEXT_VERSION)

    def test_update_dockerfile_versions(self):
        original_dockerfile = copy.deepcopy(self.generator.dockerfile)
        self.generator.update_dockerfile_versions()
        self.assertTrue(
            self.generator.dockerfile.different(original_dockerfile))
        self.assertEqual(self.generator.dockerfile.dump,
                         constants.EXPECTED_TEST_UPDATE_DOCKERFILE)

    def test_update_dockerfile_versions_no_tracked_tool(self):
        original_dockerfile = self._update_dockerfile_versions(
            constants.JSON_CONTENT_TESTING_UTILS_NO_TRACKED_TOOL)
        self.assertFalse(
            self.generator.dockerfile.different(original_dockerfile))

    def test_update_dockerfile_versions_force_version(self):
        original_dockerfile = self._update_dockerfile_versions(
            constants.JSON_CONTENT_TESTING_UTILS_NO_UPDATES)
        self.assertFalse(
            self.generator.dockerfile.different(original_dockerfile))


class DockerfileGeneratorLambdaTestCase(unittest.TestCase, TestsMixin):

    def setUp(self):
        self._init_generator()

    def test_internal_state(self):
        self.assertIsNone(self.generator._internal_state)
        state = self.generator.internal_state
        self.assertIsInstance(state, jsonstore.Store)
        self.assertEqual(state.dump, constants.TEST_STORE_DUMP_EXPECTED)
        self.assertEqual(self.generator._internal_state, state)
        new_state_obj = self.generator.internal_state
        self.assertEqual(state, new_state_obj)

    def test_internal_state_with_s3_failure(self):
        self._init_generator(storage_manager_return_read_none=True)
        self.assertIsNone(self.generator.s3bucket.file_name_written)
        state = self.generator.internal_state
        self.assertIsInstance(state, jsonstore.Store)
        self.assertIsNotNone(self.generator.s3bucket.file_name_written)

    def test_commit(self):
        self.assertFalse(self.generator.dockerfile_repo.commit_called)
        self.generator.update_files_on_github()
        self.assertTrue(self.generator.dockerfile_repo.commit_called)

    def test_save_state_to_s3(self):
        self._init_generator(storage_manager_raise_exception_when_write=True)
        with self.assertRaises(exceptions.LambdaException):
            self.generator.save_state_to_s3("something")

    def test_main_with_changes(self):
        self.assertFalse(self.generator.dockerfile_repo.commit_called)
        self.assertIsNone(self.generator.s3bucket.file_name_written)
        self.assertEqual(self.generator.main(), 0)
        self.assertTrue(self.generator.dockerfile_repo.commit_called)
        self.assertIsNotNone(self.generator.s3bucket.file_name_written)

    @mock.patch(constants.S3STORE_MNGR_NAME)
    @mock.patch(constants.GITHUB_REPO_NAME)
    def test_main_without_changes(self, github_repo, s3_bucket_mngr):
        self._test_lambda_handler(
            s3_bucket_mngr,
            github_repo,
            constants.INTERNAL_STATE_WITH_NO_FURTHER_CHANGES)

    @mock.patch(constants.S3STORE_MNGR_NAME)
    @mock.patch(constants.GITHUB_REPO_NAME)
    def test_lambda_handler(self, github_repo, s3_bucket_mngr):
        self._test_lambda_handler(s3_bucket_mngr, github_repo)

    def _test_lambda_handler(self, mock1, mock2, dockerfile_content=None):
        mock1.return_value = mocks.FakeStorageManager("bucketname")
        mock2.return_value = mocks.FakeGitHubRepository(
            "docker-cloud-tools", content=dockerfile_content)
        self.assertEqual(generator.lambda_handler(), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
