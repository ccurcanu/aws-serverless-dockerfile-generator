# -*- coding: utf-8 -*-

import os


LAMBDA_GITHUB_ACCESS_TOKEN_PARAMETER_ = "github_access_token"
LAMBDA_REPO_URL_PARAMETER = "dockerfile_gihub_repository"
LAMBDA_S3_NAME_PARAMETER = "internal_s3_bucket"


GITHUB_ACCESS_TOKEN = os.environ.get(
    LAMBDA_GITHUB_ACCESS_TOKEN_PARAMETER_, None)

DOCKERFILE_GITHUB_REPO = os.environ.get(
    LAMBDA_REPO_URL_PARAMETER, None)

S3_BUCKET_NAME = os.environ.get(
    LAMBDA_S3_NAME_PARAMETER, None)

# Path in both S3 bucket and Github repository
INTERNAL_STATE_FILE = "internal/store.json"

TEMPLATE_GITHUB_DOCKERFILE_PATH = "templates/Dockerfile"
TEMPLATE_GITHUB_README_PATH = "templates/README.md"

TF_LATEST_URL = "https://checkpoint-api.hashicorp.com/v1/check/terraform"
PK_LATEST_URL = "https://checkpoint-api.hashicorp.com/v1/check/packer"
