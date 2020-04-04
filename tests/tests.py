# -*- coding: utf-8 -*-

import copy
import unittest

import constants

from .src.jsonstore import Store


class StoreTestCase(unittest.TestCase):

    def setUp(self):
        self.store1 = jsonstore.Store(
            constants.JSON_CONTENT, dockerfile_repo_name="docker-cloud-tools")
        self.store2 = copy.deepcopy(self.store1)
        content_store3 = constants.JSON_CONTENT.replace("v0.11.9", "v0.11.10")
        self.store3 = jsonstore.Store(
            content_store3, dockerfile_repo_name="docker-cloud-tools")

    def test_sha(self):
        self.assertEqual(self.store1.sha, self.store2.sha)
        self.assertEqual(self.store1.sha, self.store1.sha)

    def test_dump(self):
        self.assertIsInstance(constants.TEST_STORE_DUMP_EXPECTED, str)
        self.assertEquals(constants.TEST_STORE_DUMP_EXPECTED, self.store1.dump)

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
        self.assertEqual(self.store1.github_repo_full_name(
            "terraform"), "hashicorp/terraform")
        self.assertEqual(self.store1.github_repo_full_name(
            "packer"), "hashicorp/packer")
        self.assertEqual(self.store1.github_repo_full_name(
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
        self.assertIsNone(self.store2.update_summary(self.store2))


# class TestsMixin():
#
#     def run_cmd(self, cmd, cwd=None, environ=os.environ):
#         proc = subprocess.Popen(cmd.split(), cwd=cwd)
#         proc.wait()
#         return proc.returncode
#
#     def setup_dockerfile_test_repo(self, clone_dir, source_branch, default=True):
#         self.run_cmd("git push origin --delete master", cwd=clone_dir)  # Ouuuh
#         if not default:
#             self.run_cmd("git fetch -u origin %s:%s -f" %
#                          (source_branch, source_branch), cwd=clone_dir)
#         self.run_cmd("git branch master %s -f" % source_branch, cwd=clone_dir)
#         self.run_cmd("git checkout master", cwd=clone_dir)
#         self.run_cmd("git push origin master -q", cwd=clone_dir)
#
#
# class StorageManagerTestCase(unittest.TestCase, TestsMixin):
#
#     def setUp(self):
#         self.bucket_name = "ccurcanu-dockerfile-test"
#         self.test_file_name = os.path.join(
#             os.sep, "tmp", "test_s3.%d" % os.getpid())
#         self.mngr = StorageManager(bucket_name=self.bucket_name)
#         self.run_cmd("aws s3 mb s3://%s --region eu-west-2" % self.bucket_name)
#         with open(self.test_file_name, "w") as fd:
#             fd.write("test file content")
#         self.run_cmd("aws s3 cp %s s3://%s --region eu-west-2" %
#                      (self.test_file_name, self.bucket_name))
#
#     def tearDown(self):
#         self.run_cmd("aws s3 rb s3://ccurcanu-dockerfile-test --force")
#
#     def test_object_read(self):
#         file_content = self.mngr.read_object(
#             os.path.basename(self.test_file_name))
#         self.assertIsNotNone(file_content)
#         self.assertIsInstance(file_content, str)
#         self.assertEqual(file_content, "test file content")
#         file_content = self.mngr.read_object("non-existing")
#         self.assertIsNone(file_content)
#
#     def test_object_write(self):
#         write_object_name = "write-object-test.%d" % (os.getpid())
#         write_object_name_content = "test file content"
#         self.mngr.write_object(write_object_name, "test file content")
#         self.run_cmd("aws s3 cp s3://%s/%s /tmp" %
#                      (self.bucket_name, write_object_name))
#         with open("/tmp/%s" % write_object_name, "r") as fd:
#             content = fd.read()
#             self.assertEquals(content, "test file content")
#
#
# JSON_CONTENT_WITHOUT_FORCE_TEMPLATE = """
# {{
#   "terraform": {{
#     "github_repo": "hashicorp/terraform",
#     "version": "{TF_VERSION}",
#     "template_key": "TERRAFORM_VERSION",
#     "remove_prefix": "v"
#   }},
#
#   "packer": {{
#     "github_repo": "hashicorp/packer",
#     "version": "{PK_VERSION}",
#     "template_key": "PACKER_VERSION",
#     "remove_prefix": "v"
#   }},
#
#   "ansible": {{
#     "github_repo": "ansible/ansible",
#     "version": "v2.7.0",
#     "template_key": "ANSIBLE_VERSION"
#   }},
#
#   "go": {{
#     "github_repo": "golang/go",
#     "version": "go1.11.1",
#     "template_key": "GO_VERSION"
#   }},
#
#   "dockerfile-generator-testing": {{
#     "github_repo": "ccurcanu/dockerfile-generator-testing",
#     "version": "{DOCKERFILE_VERSION}",
#     "template_key": "DOCKERFILE_VERSION"
#   }}
#
# }}
# """
#
#
# class LambdaFunctionTestCase(unittest.TestCase, TestsMixin):
#
#     """ This TestCase is not not generic.
#
#         Its purpose at this moment is only to test the lambda function locally
#         before deploying into production.
#
#     """
#
#     def setUp(self):
#         # Setup the internal store S3 bucket and content
#         self.bucket_name = "ccurcanu-dockerfile-test%s" % os.getpid()
#         self.test_file_name = "internal/store.json"
#         self.mngr = StorageManager(bucket_name=self.bucket_name)
#         self.run_cmd("aws s3 mb s3://%s --region eu-west-2" % self.bucket_name)
#         self.internal_store_path = "internal/store.json"
#         # Setup the master branch on github repository
#         self.dockerfile_repo = "ccurcanu/dockerfile-generator-testing"
#         self.dockerfile_repo_url = "git@github.com:%s.git" % self.dockerfile_repo
#         self.clone_dir = os.path.join(
#             os.sep, "tmp", os.path.basename(self.dockerfile_repo))
#         if os.path.exists(self.clone_dir):
#             print("Removing %s ..." % self.clone_dir)
#             shutil.rmtree(self.clone_dir)
#         self.run_cmd("git clone %s %s" %
#                      (self.dockerfile_repo_url, self.clone_dir))
#         self.environ = dict()
#         self.environ.update({"internal_s3_bucket": self.bucket_name})
#         self.environ.update(
#             {"github_access_token": os.environ.get("github_access_token")})
#         self.environ.update({"dockerfile_github_repository": os.environ.get(
#             "dockerfile_github_repository")})
#
#     def test_terraform_upgrade_by_hashicorp_release(self):
#         self.setup_dockerfile_test_repo(
#             self.clone_dir, "test-terraform-upgrade")
#         initial_values = {"TF_VERSION": "v0.11.8",
#                           "DOCKERFILE_VERSION": "1", "PK_VERSION": "v1.3.2"}
#         self.mngr.write_object(
#             self.internal_store_path, JSON_CONTENT_WITHOUT_FORCE_TEMPLATE.format(**initial_values))
#         try:
#             with mock.patch.dict("os.environ", self.environ):
#                 expected_new_tfpk_ver = "vXX.YY.ZZ"
#                 expected_dockerfile_ver = "2"
#                 dockerfile_repo_name = os.environ.get(
#                     "dockerfile_github_repository")
#                 github_access_token = os.environ.get("github_access_token")
#                 dockerfile_repo = GitHubRepository(
#                     dockerfile_repo_name, github_access_token)
#                 with mock.patch("lambda_function.get_latest_hashicorp_terraform_version", return_value=expected_new_tfpk_ver):
#                     with mock.patch("lambda_function.get_latest_hashicorp_packer_version", return_value=expected_new_tfpk_ver):
#                         retcode = lambda_function.lambda_handler(None, None)
#                         self.assertEqual(retcode, 0)
#                         expected_values = {"TF_VERSION": expected_new_tfpk_ver,
#                                            "DOCKERFILE_VERSION": expected_dockerfile_ver, "PK_VERSION": expected_new_tfpk_ver}
#                         expected_store_content = JSON_CONTENT_WITHOUT_FORCE_TEMPLATE.format(
#                             **expected_values)
#                         store_s3 = Store(self.mngr.read_object(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_github = Store(dockerfile_repo.get_file_content(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_expected = Store(
#                             expected_store_content, dockerfile_repo_name=dockerfile_repo_name)
#                         self.assertTrue(store_github.equals(store_s3))
#                         self.assertTrue(store_github.equals(store_expected))
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#                         # run the lambda function again with the same version of tf
#                         retcode = lambda_function.lambda_handler(None, None)
#                         store_s3 = Store(self.mngr.read_object(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_github = Store(dockerfile_repo.get_file_content(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         # version and Dockerfile has not been changed ...
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#                         self.assertTrue(store_github.equals(store_expected))
#                 expected_new_tfpk_ver = "vAA.BB.CC"
#                 expected_dockerfile_ver = "3"
#                 with mock.patch("lambda_function.get_latest_hashicorp_terraform_version", return_value=expected_new_tfpk_ver):
#                     with mock.patch("lambda_function.get_latest_hashicorp_packer_version", return_value=expected_new_tfpk_ver):
#                         retcode = lambda_function.lambda_handler(None, None)
#                         self.assertEqual(retcode, 0)
#                         expected_values = {"TF_VERSION": expected_new_tfpk_ver,
#                                            "DOCKERFILE_VERSION": expected_dockerfile_ver, "PK_VERSION": expected_new_tfpk_ver}
#                         expected_store_content = JSON_CONTENT_WITHOUT_FORCE_TEMPLATE.format(
#                             **expected_values)
#                         store_s3 = Store(self.mngr.read_object(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_github = Store(dockerfile_repo.get_file_content(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_expected = Store(
#                             expected_store_content, dockerfile_repo_name=dockerfile_repo_name)
#                         self.assertTrue(store_github.equals(store_s3))
#                         self.assertTrue(store_github.equals(store_expected))
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#                         # run the lambda function again with the same version of tf
#                         retcode = lambda_function.lambda_handler(None, None)
#                         store_s3 = Store(self.mngr.read_object(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_github = Store(dockerfile_repo.get_file_content(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         # version and Dockerfile has not been changed ...
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#                         self.assertTrue(store_github.equals(store_expected))
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#         except lambda_function.LambdaException as e:
#             self.fail(str(e))
#
#     def test_terraform_upgrade_by_force_version(self):
#         expected_new_tf_ver = "vx.y.z"  # the one from github...
#         expected_dockerfile_ver = "1"
#         initial_values = {
#             "TF_VERSION": expected_new_tf_ver,
#             "DOCKERFILE_VERSION": expected_dockerfile_ver,
#             "PK_VERSION": expected_new_tf_ver}  # Same like TF in this case
#         expected_store_content = JSON_CONTENT_WITH_FORCE_TEMPLATE.format(
#             **initial_values)
#         self.mngr.write_object(self.internal_store_path,
#                                expected_store_content)
#         self.setup_dockerfile_test_repo(
#             self.clone_dir, "test-terraform-upgrade-force", default=False)
#         try:
#             with mock.patch.dict("os.environ", self.environ):
#                 dockerfile_repo_name = os.environ.get(
#                     "dockerfile_github_repository")
#                 github_access_token = os.environ.get("github_access_token")
#                 dockerfile_repo = GitHubRepository(
#                     dockerfile_repo_name, github_access_token)
#                 with mock.patch("lambda_function.get_latest_hashicorp_terraform_version", return_value="whatever"):
#                     with mock.patch("lambda_function.get_latest_hashicorp_packer_version", return_value="vxx.yy.zz"):
#                         retcode = lambda_function.lambda_handler(None, None)
#                         self.assertEqual(retcode, 0)
#                         store_s3 = Store(self.mngr.read_object(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_github = Store(dockerfile_repo.get_file_content(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_expected = Store(
#                             expected_store_content, dockerfile_repo_name=dockerfile_repo_name)
#                         self.assertTrue(store_github.equals(store_s3))
#                         self.assertTrue(store_github.equals(store_expected))
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#                         # run the lambda function again with the same version of tf
#                         retcode = lambda_function.lambda_handler(None, None)
#                         self.assertEqual(retcode, 0)
#                         store_s3 = Store(self.mngr.read_object(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         store_github = Store(dockerfile_repo.get_file_content(
#                             self.internal_store_path), dockerfile_repo_name=dockerfile_repo_name)
#                         # version and Dockerfile has not been changed ...
#                         self.assertTrue(store_github.version(os.path.basename(
#                             dockerfile_repo_name)), expected_dockerfile_ver)
#                         self.assertTrue(store_github.equals(store_expected))
#         except lambda_function.LambdaException as e:
#             self.fail(str(e))
#         self.assertEqual(retcode, 0)
#
#     def tearDown(self):
#         self.run_cmd("aws s3 rb s3://%s --force" % self.bucket_name)


if __name__ == '__main__':
    unittest.main()
