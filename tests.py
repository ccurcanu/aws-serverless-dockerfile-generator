import os
import subprocess
import unittest
from lambda_function import StorageManager

import boto3


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

    def test_object_read(self):
        file_content = self.mngr.read_object(os.path.basename(self.test_file_name))
        self.assertIsNotNone(file_content)
        self.assertIsInstance(file_content, str)
        self.assertEqual(file_content, "test file content")
        file_content = self.mngr.read_object("non-existing")
        self.assertIsNone(file_content)

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
