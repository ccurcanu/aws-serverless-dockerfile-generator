import unittest
import unittest.mock as mock

import dockerfilegenerator.lib.versions as versions

import constants


class VersionsTestCase(unittest.TestCase):

    @mock.patch("dockerfilegenerator.lib.versions.get_hashicorp_api_item")
    def test_get_latest_hashicorp_terraform_version(self, item):
        item.return_value = constants.TEST_HASHICORP_TF_VERSION
        self.assertEqual(
            versions.get_latest_hashicorp_terraform_version(),
            constants.TEST_HASHICORP_TF_VERSION_EXPECTED)

    @mock.patch("dockerfilegenerator.lib.versions.get_hashicorp_api_item")
    def test_get_latest_hashicorp_packer_version(self, item):
        item.return_value = constants.TEST_HASHICORP_PK_VERSION
        self.assertEqual(
            versions.get_latest_hashicorp_packer_version(),
            constants.TEST_HASHICORP_PK_VERSION_EXPECTED)

    @mock.patch("urllib3.PoolManager")
    def test_get_hashicorp_api_item(self, manager):
        manager.return_value = RequestPoolManager(HttpResponseMock(
            constants.TEST_VERSIONS_GET_API_ITEM_RESPONSE_JSON))
        self.assertEqual(versions.get_latest_hashicorp_terraform_version(),
                         constants.TEST_HASHICORP_TF_VERSION_EXPECTED)

    @mock.patch("urllib3.PoolManager")
    def test_get_hashicorp_api_item_http_status_failure(self, manager):
        manager.return_value = RequestPoolManager(HttpResponseMock(
            constants.TEST_VERSIONS_GET_API_ITEM_RESPONSE_JSON, 404))
        with self.assertRaises(Exception):
            versions.get_latest_hashicorp_terraform_version()

    @mock.patch("urllib3.PoolManager")
    def test_get_hashicorp_api_item_item_not_found(self, manager):
        manager.return_value = RequestPoolManager(HttpResponseMock(
            constants.TEST_VERSIONS_GET_API_ITEM_RESPONSE_JSON))
        with self.assertRaises(Exception):
            versions.get_hashicorp_api_item("someurl", "someitem")

    @mock.patch("urllib3.PoolManager")
    def test_get_latest_golang_go_version(self, manager):
        manager.return_value = RequestPoolManager(HttpResponseMock(
            bytes(constants.EXPECTED_GOLANG_VERSION, encoding="utf-8")))
        version = versions.get_latest_golango_go_version()
        self.assertEqual(version, constants.EXPECTED_GOLANG_VERSION)


class RequestPoolManager:

    def __init__(self, response_mock):
        self.response_mock = response_mock

    def request(self, *args, **kwargs):
        return self.response_mock


class HttpResponseMock:

    def __init__(self, data, status=200):
        self.status = status
        self.data = data

    def close(self):
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
