# -*- coding: utf-8 -*-

import certifi
import urllib3
import json

TF_LATEST_URL = "https://checkpoint-api.hashicorp.com/v1/check/terraform"
PK_LATEST_URL = "https://checkpoint-api.hashicorp.com/v1/check/packer"


def get_latest_hashicorp_terraform_version():
    return 'v' + get_hashicorp_api_item(TF_LATEST_URL, "current_version")


def get_latest_hashicorp_packer_version():
    return 'v' + get_hashicorp_api_item(PK_LATEST_URL, "current_version")


def get_hashicorp_api_item(url, item):
    http = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request("GET", url)
    if response.status != 200:
        raise Exception("Error: GET %d, %s" % (response.status, url))
    json_data = json.loads(response.data)
    del http
    if item in json_data:
        return json_data[item]
    raise Exception("Error: item '%s' not in %s" %
                    (item, json.dumps(json_data)))
