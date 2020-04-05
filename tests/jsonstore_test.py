# -*- coding: utf-8 -*-

import copy
import unittest

import constants

from dockerfilegenerator.lib import jsonstore


class FakeGitHubRepository:

    def __init__(self, name):
        self.name = name

    def get_dockerfile_content(self):
        return constants.JSON_CONTENT


class StoreUtilsTestCase(unittest.TestCase):

    def test_get_dockerfile(self):
        dockerfile = jsonstore.get_dockerfile(FakeGitHubRepository("reponame"))
        self.assertIsInstance(dockerfile, jsonstore.Store)


class StoreTestCase(unittest.TestCase):

    def setUp(self):
        self.store1 = jsonstore.Store(
            constants.JSON_CONTENT, "docker-cloud-tools")
        self.store2 = copy.deepcopy(self.store1)
        content_store3 = constants.JSON_CONTENT.replace("v0.11.9", "v0.11.10")
        self.store3 = jsonstore.Store(
            content_store3, "docker-cloud-tools")

    def test_sha(self):
        self.assertEqual(self.store1.sha, self.store2.sha)
        self.assertEqual(self.store1.sha, self.store1.sha)

    def test_dump(self):
        self.assertIsInstance(constants.TEST_STORE_DUMP_EXPECTED, str)
        self.assertEqual(constants.TEST_STORE_DUMP_EXPECTED, self.store1.dump)

    def test_template_variables(self):
        t_var = self.store1.template_variables
        self.assertIsInstance(t_var, dict)
        self.assertEqual(t_var["TERRAFORM_VERSION"], "0.11.9")
        self.assertEqual(t_var["PACKER_VERSION"], "1.3.1")
        self.assertEqual(t_var["DOCKERFILE_VERSION"], "1")

    def test_equals(self):
        self.assertTrue(self.store1.equals(self.store1))
        self.assertTrue(self.store1.equals(self.store2))
        self.assertFalse(self.store1.equals(self.store3))

    def test_different(self):
        self.assertTrue(self.store1.different(self.store3))
        self.assertTrue(self.store3.different(self.store1))
        self.assertFalse(self.store3.different(self.store3))

    def test_version(self):
        self.assertEqual(self.store1.version("terraform"), "v0.11.9")
        self.assertEqual(self.store1.version("packer"), "v1.3.1")
        self.assertEqual(self.store1.version("docker-cloud-tools"), "1")

    def test_set_version(self):
        self.assertEqual(self.store3.version("terraform"), "v0.11.10")
        self.store3.set_version("terraform", "v0.11.11")
        self.assertEqual(self.store3.version("terraform"), "v0.11.11")
        self.assertEqual(self.store3.version("packer"), "v1.3.1")
        self.store3.set_version("packer", "v1.3.2")
        self.assertEqual(self.store3.version("packer"), "v1.3.2")
        self.assertEqual(self.store3.version("docker-cloud-tools"), "1")
        self.store3.set_version("docker-cloud-tools", "2")
        self.assertEqual(self.store3.version("docker-cloud-tools"), "2")

    def test_set_next_version_dockerfile(self):
        self.assertEqual(self.store1.version("docker-cloud-tools"), "1")
        self.store1.set_next_version_dockerfile()
        self.assertEqual(self.store1.version("docker-cloud-tools"), "2")
        self.store1.set_next_version_dockerfile()
        self.store1.set_next_version_dockerfile()
        self.assertEqual(self.store1.version("docker-cloud-tools"), "4")

    def test_get_github_repo_full_name(self):
        self.assertEqual(self.store1.github_repo_name(
            "terraform"), "hashicorp/terraform")
        self.assertEqual(self.store1.github_repo_name(
            "packer"), "hashicorp/packer")
        self.assertEqual(self.store1.github_repo_name(
            "docker-cloud-tools"), "ccurcanu/docker-cloud-tools")

    def test_remove_prefix(self):
        self.assertEqual(self.store1.remove_prefix("terraform"), "v")
        self.assertIsNone(self.store1.remove_prefix("docker-cloud-tools"))
        self.assertEqual(self.store1.remove_prefix("packer"), "v")

    def test_force_version(self):
        self.assertTrue(self.store1.force_version("terraform"))
        self.assertFalse(self.store1.force_version("ansible"))
        self.assertFalse(self.store1.force_version("docker-cloud-tools"))

    def test_update_summary(self):
        self.store2.set_version("terraform", "v0.11.10")
        self.store2.set_version("packer", "v1.3.2")
        self.store2.set_version("docker-cloud-tools", "2")
        self.assertEqual(self.store2.update_summary(
            self.store1), constants.TEST_STORE_UPDATE_SUMMARY)
