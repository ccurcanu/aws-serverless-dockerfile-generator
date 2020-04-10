# -*- coding: utf-8 -*-

import copy
import unittest
import unittest.mock as mock

import dockerfilegenerator.lib.jsonstore as jsonstore
import dockerfilegenerator.generator as generator

import constants
import mocks


class GeneratorUtilsTestCase(unittest.TestCase):

    def setUp(self):
        with mock.patch(constants.S3STORE_MNGR_NAME) as s3_bucket_mngr:
            s3_bucket_mngr.return_value = None
            with mock.patch(constants.GITHUB_REPO_NAME) as github_repo:
                github_repo.return_value = mocks.FakeGitHubRepository(
                    "docker-cloud-tools")
                self.generator = generator.DockerfileGeneratorLambda()
        self.generator.dockerfile = jsonstore.Store(
            constants.JSON_CONTENT, "docker-cloud-tools")
        self.mockTrackedTools = {
            "terraform": self._get_version,
            "packer": self._get_version}
        generator.TRACKED_TOOLS = self.mockTrackedTools

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
        generator.TRACKED_TOOLS = self.mockTrackedTools
        self.generator.update_dockerfile_versions()
        self.assertTrue(
            self.generator.dockerfile.different(original_dockerfile))
        self.assertEqual(self.generator.dockerfile.dump,
                         constants.EXPECTED_TEST_UPDATE_DOCKERFILE)

    def test_update_dockerfile_versions_no_tracked_tool(self):
        self.generator.dockerfile = jsonstore.Store(
            constants.JSON_CONTENT_TESTING_UTILS_NO_TRACKED_TOOL,
            "docker-cloud-tools")
        original_dockerfile = copy.deepcopy(self.generator.dockerfile)
        self.generator.update_dockerfile_versions()
        self.assertFalse(
            self.generator.dockerfile.different(original_dockerfile))

    def test_update_dockerfile_versions_force_version(self):
        self.generator.dockerfile = jsonstore.Store(
            constants.JSON_CONTENT_TESTING_UTILS_NO_UPDATES,
            "docker-cloud-tools")
        original_dockerfile = copy.deepcopy(self.generator.dockerfile)
        self.generator.update_dockerfile_versions()
        self.assertFalse(
            self.generator.dockerfile.different(original_dockerfile))

    def _get_version(self, version="v1.0.0"):
        return version


# class DockerfileGeneratorLambdaTestCase(unittest.TestCase):
#
#     def setUp(self):
#         pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
