# -*- coding: utf-8 -*-

import certifi
import urllib3
import json

from dockerfilegenerator.lib.constants import TF_LATEST_URL, PK_LATEST_URL
from dockerfilegenerator.lib.constants import GO_LATEST_URL


def get_latest_hashicorp_terraform_version():
    return "v" + get_hashicorp_api_item(TF_LATEST_URL, "current_version")


def get_latest_hashicorp_packer_version():
    return "v" + get_hashicorp_api_item(PK_LATEST_URL, "current_version")


def get_latest_golango_go_version():
    return http_get(GO_LATEST_URL).decode("utf-8")


def get_hashicorp_api_item(url, item):
    json_data = json.loads(http_get(url))
    if item in json_data:
        return json_data[item]
    raise Exception("Error: item '%s' not in %s" %
                    (item, json.dumps(json_data)))


def http_get(url):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request("GET", url)
    if response.status != 200:
        raise Exception("Error: GET %d, %s" % (response.status, url))
    response.close()
    return response.data
