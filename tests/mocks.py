import dockerfilegenerator.lib.constants as libconstants

import botocore.exceptions

import constants


class FakeGitHubRepository:

    def __init__(self, name):
        self.name = name
        self.commit_called = False

    def get_file_contents(self, file_path, **kwargs):
        if file_path == libconstants.TEMPLATE_GITHUB_DOCKERFILE_PATH:
            return constants.TEMPLATE_DOCKERFILE_SAMPLE
        elif file_path == libconstants.TEMPLATE_GITHUB_README_PATH:
            return constants.TEMPLATE_README_SAMPLE
        else:
            return constants.JSON_CONTENT

    def commit(self, files, msg):
        self.commit_called = True


class FakeStorageManager:

    def __init__(self, bucket_name, **kwargs):
        self.file_name_written = None
        self.bucket_name = bucket_name
        self.read_return_none = False
        self.raise_exception = False

    def read_object(self, file_name):
        self.file_name_read = file_name
        if self.read_return_none:
            return None
        return constants.JSON_CONTENT

    def write_object(self, file_name, content):
        self.file_name_written = file_name
        if self.raise_exception:
            raise Exception(file_name)
        self.content_written = content
