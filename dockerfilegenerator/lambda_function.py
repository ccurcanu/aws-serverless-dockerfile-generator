# -*- coding: utf-8 -*-

import botocore.exceptions

import lib.constants as constants
import lib.exceptions as exceptions
import lib.versions as versions
import lib.jsonstore as jsonstore
import lib.s3store as s3store
import lib.github as github


TRACKED_TOOLS_NEXT_VERSIONS = {
    "terraform": versions.get_latest_hashicorp_terraform_version(),
    "packer": versions.get_latest_hashicorp_packer_version(),
}


def save_state_to_s3(bucket, dockerfile_store_content):
    try:
        bucket.write_object(
            constants.INTERNAL_STATE_FILE, dockerfile_store_content)
    except botocore.exceptions.ClientError as e:
        raise exceptions.LambdaException(
            "Error: Uploading object to s3 bucket: %s" % (str(e)))


def get_internal_known_state(bucket, dockerfile_github):
    internal_state = bucket.read_object(constants.INTERNAL_STATE_FILE)
    if internal_state is None:
        internal_state = dockerfile_github.dump
        save_state_to_s3(bucket, internal_state)
    return jsonstore.Store(internal_state)


def get_tools_current_version(dockerfile):
    return {(tool_name, dockerfile.version(tool_name))
            for tool_name in dockerfile.dump}


def update_dockerfile_store_versions(dockerfile):
    current_versions = get_tools_current_version(dockerfile)
    next_versions = TRACKED_TOOLS_NEXT_VERSIONS
    dockerfile_changed = False
    for tool in current_versions:
        if next_versions.get(tool, None) is None:
            continue
        if current_versions[tool] != next_versions[tool]:
            if dockerfile.force_version(tool):
                continue
            dockerfile.set_version(tool, next_versions[tool])
            dockerfile_changed = True
    if dockerfile_changed:
        dockerfile.set_next_version_dockerfile()


def update_files_on_github(repo, dockerfile, prev_dockerfile):
    template_dockerfile = repo.get_file_contents(
        constants.TEMPLATE_GITHUB_DOCKERFILE_PATH)
    template_readme = repo.get_file_contents(
        constants.TEMPLATE_GITHUB_README_PATH)
    commit_msg = dockerfile.update_summary(prev_dockerfile)
    commit_files = [
        (constants.INTERNAL_STATE_FILE, dockerfile.dump),
        ("Dockerfile", template_dockerfile.format(
            **dockerfile.template_variables)),
        ("README.md", template_readme.format(
            **dockerfile.template_variables))]
    repo.commit(commit_files, commit_msg)


def main():
        bucket = s3store.get_bucket_manager()
        dockerfile_repo = github.get_github_repository(
            constants.DOCKERFILE_GITHUB_REPO)
        dockerfile = jsonstore.get_dockerfile(dockerfile_repo)
        lambda_known_dockerfile_state = get_internal_known_state(
            bucket, dockerfile)
        update_dockerfile_store_versions(dockerfile)
        if dockerfile.different(lambda_known_dockerfile_state):
            update_files_on_github(
                dockerfile_repo,
                dockerfile,
                lambda_known_dockerfile_state)
            save_state_to_s3(bucket, dockerfile.dump)
        return 0


def lambda_handler(event, context):
    return main()
