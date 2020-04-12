# -*- coding: utf-8 -*-

import boto3
import botocore.exceptions

import dockerfilegenerator.lib.constants as constants
import dockerfilegenerator.lib.exceptions as exceptions


class StorageManager():

    """ S3 object storage bucket is modelled by this class.

    The __init__ method has the following parameters:

    bucket_name (str): Name of the bucket. """

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3_resource = boto3.resource("s3")

    def read_object(self, file_name):
        try:
            file_obj = self.s3_resource.Object(self.bucket_name, file_name)
            return file_obj.get()["Body"].read().decode()
        except (botocore.exceptions.ClientError, Exception):
            return

    def write_object(self, file_name, content):
        file_obj = self.s3_resource.Object(self.bucket_name, file_name)
        file_obj.put(Body=content.encode("utf-8"))


def get_s3_bucket_manager(bucket_name=constants.S3_BUCKET_NAME):
    if not bucket_name:
        raise exceptions.LambdaException(
            "Error: '%s' lambda env variable not set." %
            constants.LAMBDA_S3_NAME_PARAMETER)
    return StorageManager(bucket_name=bucket_name)
