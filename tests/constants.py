
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


JSON_CONTENT_WITH_FORCE_TEMPLATE = """
{{
  "terraform": {{
    "github_repo": "hashicorp/terraform",
    "version": "{TF_VERSION}",
    "template_key": "TERRAFORM_VERSION",
    "remove_prefix": "v",
    "force_version": "true"
  }},

  "packer": {{
    "github_repo": "hashicorp/packer",
    "version": "vxx.yy.zz",
    "template_key": "PACKER_VERSION",
    "remove_prefix": "v"
  }},

  "ansible": {{
    "github_repo": "ansible/ansible",
    "version": "v2.7.0",
    "template_key": "ANSIBLE_VERSION"
  }},

  "go": {{
    "github_repo": "golang/go",
    "version": "goxxx.yyy.zzz",
    "template_key": "GO_VERSION"
  }},

  "dockerfile-generator-testing": {{
    "github_repo": "ccurcanu/dockerfile-generator-testing",
    "version": "{DOCKERFILE_VERSION}",
    "template_key": "DOCKERFILE_VERSION"
  }}

}}"""


TEST_STORE_DUMP_EXPECTED = '{\n    "terraform": {\n        "github_repo": "hashicorp/terraform",\n        "version": "v0.11.9",\n        "template_key": "TERRAFORM_VERSION",\n        "remove_prefix": "v",\n        "force_version": "true"\n    },\n    "packer": {\n        "github_repo": "hashicorp/packer",\n        "version": "v1.3.1",\n        "template_key": "PACKER_VERSION",\n        "remove_prefix": "v"\n    },\n    "docker-cloud-tools": {\n        "github_repo": "ccurcanu/docker-cloud-tools",\n        "version": "1",\n        "template_key": "DOCKERFILE_VERSION"\n    }\n}'


TEST_STORE_UPDATE_SUMMARY = """
Changes detected on: terraform, packer, docker-cloud-tools

Versions:
    * terraform (v0.11.9 -> v0.11.10)
    * packer (v1.3.1 -> v1.3.2)
    * docker-cloud-tools (1 -> 2)
"""

TEST_OBJECT_READ_S3_CONTENT = "Content from S3"
