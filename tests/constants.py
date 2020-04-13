
JSON_CONTENT = """
{
    "terraform": {
        "github_repo": "hashicorp/terraform",
        "version": "v0.11.9",
        "template_key": "TERRAFORM_VERSION",
        "remove_prefix": "v",
        "force_version": "true"
    },
    "packer": {
        "github_repo": "hashicorp/packer",
        "version": "v1.3.1",
        "template_key": "PACKER_VERSION",
        "remove_prefix": "v"
    },
    "docker-cloud-tools": {
        "github_repo": "ccurcanu/docker-cloud-tools",
        "version": "1",
        "template_key": "DOCKERFILE_VERSION"
    }
}"""


TEST_STORE_DUMP_EXPECTED = """{
    "terraform": {
        "github_repo": "hashicorp/terraform",
        "version": "v0.11.9",
        "template_key": "TERRAFORM_VERSION",
        "remove_prefix": "v",
        "force_version": "true"
    },
    "packer": {
        "github_repo": "hashicorp/packer",
        "version": "v1.3.1",
        "template_key": "PACKER_VERSION",
        "remove_prefix": "v"
    },
    "docker-cloud-tools": {
        "github_repo": "ccurcanu/docker-cloud-tools",
        "version": "1",
        "template_key": "DOCKERFILE_VERSION"
    }
}"""


TEST_STORE_UPDATE_SUMMARY = """
Changes detected on: terraform, packer, docker-cloud-tools

Versions:
    * terraform (v0.11.9 -> v0.11.10)
    * packer (v1.3.1 -> v1.3.2)
    * docker-cloud-tools (1 -> 2)
"""

TEST_OBJECT_READ_S3_CONTENT = "Content from S3"

TEST_GITHUB_GET_FILE_CONTENTS = "Some fake content from GitHub"

TEST_HASHICORP_TF_VERSION = "1.0.0"
TEST_HASHICORP_TF_VERSION_EXPECTED = "v" + TEST_HASHICORP_TF_VERSION

TEST_HASHICORP_PK_VERSION = TEST_HASHICORP_TF_VERSION
TEST_HASHICORP_PK_VERSION_EXPECTED = TEST_HASHICORP_TF_VERSION_EXPECTED

TEST_VERSIONS_GET_API_ITEM_RESPONSE_JSON = """
{
    "product": "<product>",
    "current_version": "%s",
    "current_release": "<some release>",
    "alerts": []
}
""" % TEST_HASHICORP_TF_VERSION


S3STORE_MNGR_NAME = "dockerfilegenerator.lib.s3store.get_s3_bucket_manager"
GITHUB_REPO_NAME = "dockerfilegenerator.lib.github.GitHubRepository"
TRACKED_TOOLS_NAME = "dockerfilegenerator.generator.TRACKED_TOOLS"


EXPECTED_TOOLS_CURRENT_VERSION = {
    'terraform': 'v0.11.9',
    'packer': 'v1.3.1',
    'docker-cloud-tools': '1'}


EXPECTED_TOOLS_NEXT_VERSION = {
    'terraform': 'v1.0.0',
    'packer': 'v1.0.0'}


EXPECTED_TEST_UPDATE_DOCKERFILE = """{
    "terraform": {
        "github_repo": "hashicorp/terraform",
        "version": "v0.11.9",
        "template_key": "TERRAFORM_VERSION",
        "remove_prefix": "v",
        "force_version": "true"
    },
    "packer": {
        "github_repo": "hashicorp/packer",
        "version": "v1.0.0",
        "template_key": "PACKER_VERSION",
        "remove_prefix": "v"
    },
    "docker-cloud-tools": {
        "github_repo": "ccurcanu/docker-cloud-tools",
        "version": "2",
        "template_key": "DOCKERFILE_VERSION"
    }
}"""

JSON_CONTENT_TESTING_UTILS_NO_TRACKED_TOOL = """
{
    "sometool": {
        "github_repo": "sometool",
        "version": "v0.0.1",
        "template_key": "SOMEKEY",
        "remove_prefix": "v"
    }
}"""


JSON_CONTENT_TESTING_UTILS_NO_UPDATES = """
{
    "terraform": {
        "github_repo": "hashicorp/terraform",
        "version": "v1.0.0",
        "template_key": "TERRAFORM_VERSION",
        "remove_prefix": "v"
    },
    "packer": {
        "github_repo": "hashicorp/packer",
        "version": "v1.0.0",
        "template_key": "PACKER_VERSION",
        "remove_prefix": "v"

    },
    "docker-cloud-tools": {
        "github_repo": "ccurcanu/docker-cloud-tools",
        "version": "1",
        "template_key": "DOCKERFILE_VERSION"
    }
}"""

TEMPLATE_DOCKERFILE_SAMPLE = "Nothing else yet"
TEMPLATE_README_SAMPLE = "Nothong else yet"

INTERNAL_STATE_WITH_NO_FURTHER_CHANGES = """
{
    "terraform": {
        "github_repo": "hashicorp/terraform",
        "version": "v0.11.9",
        "template_key": "TERRAFORM_VERSION",
        "remove_prefix": "v",
        "force_version": "true"
    },
    "packer": {
        "github_repo": "hashicorp/packer",
        "version": "v1.0.0",
        "template_key": "PACKER_VERSION",
        "remove_prefix": "v"
    },
    "docker-cloud-tools": {
        "github_repo": "ccurcanu/docker-cloud-tools",
        "version": "1",
        "template_key": "DOCKERFILE_VERSION"
    }
}"""

EXPECTED_GOLANG_VERSION = "go1.0.0"
