# -*- coding: utf-8 -*-

import copy
import os
import subprocess
import unittest

from lambda_function import StorageManager, Store, GitHubRepository

import boto3

class StoreTestCase(unittest.TestCase):

    def setUp(self):
        content = """
{
    "terraform": {
        "github_repo": "hashicorp/terraform",
        "version": "v0.11.9",
        "template_key": "TERRAFORM_VERSION",
        "remove_prefix": "v",
        "force_version": "true"
    },
    "packer": {
        "github_repo": "hashicorp/packer",
        "version": "v1.3.1",
        "template_key": "PACKER_VERSION",
        "remove_prefix": "v"
    },
    "docker-cloud-tools": {
        "github_repo": "ccurcanu/docker-cloud-tools",
        "version": "1",
        "template_key": "DOCKERFILE_VERSION"
    }
}"""

        self.store1 = Store(content, dockerfile_repo_name="docker-cloud-tools")
        self.store2 = copy.deepcopy(self.store1)

        content_store3 = content.replace("v0.11.9", "v0.11.10")
        self.store3 = Store(content_store3, dockerfile_repo_name="docker-cloud-tools")

    def test_sha(self):
        self.assertEqual(self.store1.sha, self.store2.sha)
        self.assertEqual(self.store1.sha, self.store1.sha)

    def test_dump(self):
        correct_dump = '{\n    "terraform": {\n        "github_repo": "hashicorp/terraform",\n        "version": "v0.11.9",\n        "template_key": "TERRAFORM_VERSION",\n        "remove_prefix": "v",\n        "force_version": "true"\n    },\n    "packer": {\n        "github_repo": "hashicorp/packer",\n        "version": "v1.3.1",\n        "template_key": "PACKER_VERSION",\n        "remove_prefix": "v"\n    },\n    "docker-cloud-tools": {\n        "github_repo": "ccurcanu/docker-cloud-tools",\n        "version": "1",\n        "template_key": "DOCKERFILE_VERSION"\n    }\n}'
        self.assertIsInstance(correct_dump, str)
        self.assertEqual(correct_dump, self.store1.dump)

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
        self.assertEqual(self.store1.github_repo_full_name("terraform"), "hashicorp/terraform")
        self.assertEqual(self.store1.github_repo_full_name("packer"), "hashicorp/packer")
        self.assertEqual(self.store1.github_repo_full_name("docker-cloud-tools"), "ccurcanu/docker-cloud-tools")

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
        update_summary = 'Changes detected on: terraform packer docker-cloud-tools\nterraform\t\t changed version v0.11.9 -> v0.11.10 \npacker\t\t changed version v1.3.1 -> v1.3.2 \ndocker-cloud-tools\t\t changed version 1 -> 2 \n'
        self.assertEqual(self.store2.update_summary(self.store1), update_summary)
        self.assertIsNone(self.store2.update_summary(self.store2))


class GitHubRepositoryTestCase(unittest.TestCase):

    def setUp(self):
        pass

        def tearDown(self):
            pass


class StorageManagerTestCase(unittest.TestCase):

    def run_cmd(self, cmd):
        proc = subprocess.Popen(cmd.split())
        proc.wait()
        return proc.returncode

    def setUp(self):
        self.bucket_name = "ccurcanu-dockerfile-test"
        self.test_file_name = os.path.join(os.sep, "tmp", "test_s3.%d" % os.getpid())
        self.mngr = StorageManager(bucket_name=self.bucket_name)
        self.run_cmd("aws s3 mb s3://%s --region eu-west-2" % self.bucket_name)
        with open(self.test_file_name, "w") as fd:
            fd.write("test file content")
        self.run_cmd("aws s3 cp %s s3://%s --region eu-west-2" % (self.test_file_name, self.bucket_name))

    def tearDown(self):
        self.run_cmd("aws s3 rb s3://ccurcanu-dockerfile-test --force")

    @unittest.SkipTest
    def test_object_read(self):
        file_content = self.mngr.read_object(os.path.basename(self.test_file_name))
        self.assertIsNotNone(file_content)
        self.assertIsInstance(file_content, str)
        self.assertEqual(file_content, "test file content")
        file_content = self.mngr.read_object("non-existing")
        self.assertIsNone(file_content)

    @unittest.SkipTest
    def test_object_write(self):
        write_object_name = "write-object-test.%d" % (os.getpid())
        write_object_name_content = "test file content"
        self.mngr.write_object(write_object_name, "test file content")
        self.run_cmd("aws s3 cp s3://%s/%s /tmp" % (self.bucket_name, write_object_name))
        with open("/tmp/%s" % write_object_name, "r") as fd:
            content = fd.read()
            self.assertEquals(content, "test file content")


if __name__ == '__main__':
    unittest.main()
