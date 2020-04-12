import unittest
import unittest.mock

import dockerfilegenerator.lib.exceptions as exceptions
import dockerfilegenerator.lib.s3store as s3store

import constants


class StorageManagerTestCase(unittest.TestCase):

    def setUp(self):
        self.mngr_clean = self._get_manager()
        self.mngr_that_will_raise_exception = self._get_manager(
            with_raising_exception=True)

    def _get_manager(self, with_raising_exception=False):
        with unittest.mock.patch("boto3.resource") as resource:
            resource.return_value = BotoS3ManagerMock(
                raise_exception=with_raising_exception)
            return s3store.StorageManager("bucket_name")

    def test_manager_init(self):
        self.assertIsInstance(self.mngr_clean, s3store.StorageManager)
        self.assertIsInstance(
            self.mngr_that_will_raise_exception, s3store.StorageManager)

    def test_object_read_succcess(self):
        self.assertEqual(self.mngr_clean.read_object(
            "file_object_name_in_s3"), constants.TEST_OBJECT_READ_S3_CONTENT)

    def test_object_read_fail(self):
        self.assertEqual(self.mngr_that_will_raise_exception.read_object(
            "file_object_name_in_s3"), None)

    def test_object_write(self):
        self.mngr_clean.write_object(
            "file/object/path", constants.TEST_OBJECT_READ_S3_CONTENT)
        written_content = self.mngr_clean.s3_resource.Object.written_content
        self.assertEqual(written_content.decode("utf-8"),
                         constants.TEST_OBJECT_READ_S3_CONTENT)


class S3StoreUtilsTestCase(unittest.TestCase):

    def test_get_s3_bucket_manager_raise_exception(self):
        with self.assertRaises(exceptions.LambdaException):
            s3store.get_s3_bucket_manager(bucket_name=None)

    def test_get_s3_bucket_manager(self):
        self.assertIsInstance(
            s3store.get_s3_bucket_manager(bucket_name="somename"),
            s3store.StorageManager)


class BotoS3ManagerMock:

    def __init__(self, *args, **kwargs):
        self.raise_exception = kwargs.get("raise_exception", False)
        self.Object = BotoS3ObjectMock(raise_exception=self.raise_exception)


class BotoS3ObjectMock:

    def __init__(self, *args, **kwargs):
        self.raise_exception = kwargs.get("raise_exception", False)
        self.written_content = None

    def __call__(self, *args, **kwargs):
        return self

    def get(self, *args, **kwargs):
        if self.raise_exception:
            raise Exception("Error reading stuff")
        return {
            "Body": S3ObjectStreamMock(constants.TEST_OBJECT_READ_S3_CONTENT)}

    def put(self, *args, **kwargs):
        body = kwargs.get("Body")
        self.written_content = body


class S3ObjectStreamMock:

    def __init__(self, content):
        self.content = content

    def read(self):
        return self

    def decode(self):
        return self.content
