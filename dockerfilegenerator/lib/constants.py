# -*- coding: utf-8 -*-

import os

import versions

LAMBDA_GITHUB_ACCESS_TOKEN_PARAMETER_ = "github_access_token"
LAMBDA_REPO_URL_PARAMETER = "dockerfile_repo_repository"
LAMBDA_S3_NAME_PARAMETER = "internal_s3_bucket"


GITHUB_ACCESS_TOKEN = os.environ.get(
    LAMBDA_GITHUB_ACCESS_TOKEN_PARAMETER_, None)

DOCKERFILE_GITHUB_REPO = os.environ.get(
    LAMBDA_GITHUB_ACCESS_TOKEN_PARAMETER_, None)

S3_BUCKET_NAME = os.environ.get(
    LAMBDA_S3_NAME_PARAMETER, None)

# Path in both S3 bucket and Github repository
INTERNAL_STATE_FILE = "internal/store.json"

TRACKED_TOOLS_NEXT_VERSIONS = {
    "terraform": versions.get_latest_hashicorp_terraform_version(),
    "packer": versions.get_latest_hashicorp_packer_version(),
    "go": versions.get_latest_golang_go_version()
}


TEMPLATE_GITHUB_DOCKERFILE_PATH = "templates/Dockerfile"
TEMPLATE_GITHUB_README_PATH = "templates/README.md"
