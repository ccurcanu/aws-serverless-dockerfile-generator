# -*- coding: utf-8 -*-

import botocore.exceptions
import logging

import dockerfilegenerator.lib.constants as constants
import dockerfilegenerator.lib.exceptions as exceptions
import dockerfilegenerator.lib.versions as versions
import dockerfilegenerator.lib.jsonstore as jsonstore
import dockerfilegenerator.lib.s3store as s3store
import dockerfilegenerator.lib.github as github

logger = logging.getLogger()

TRACKED_TOOLS = {
    "terraform": versions.get_latest_hashicorp_terraform_version,
    "packer": versions.get_latest_hashicorp_packer_version,
}


class UtilsMixin:

    @property
    def tools_current_versions(self):
        if not hasattr(self, "_tools_current_versions"):
            self._tools_current_versions = None
        if self._tools_current_versions is None:
            self._tools_current_versions = dict(
                (tool_name, self.dockerfile.version(tool_name))
                for tool_name in self.dockerfile.json)
        return self._tools_current_versions

    @property
    def tools_next_versions(self):
        if not hasattr(self, "_tools_next_versions"):
            self._tools_next_versions = None
        if self._tools_next_versions is None:
            self._tools_next_versions = dict(
                (tool_name, TRACKED_TOOLS[tool_name]())
                for tool_name in TRACKED_TOOLS)
        return self._tools_next_versions

    def update_dockerfile_versions(self):
        dockerfile_changed = False
        for tool in self.tools_current_versions:
            # TODO: Refactor this method...
            if self.dockerfile.force_version(tool):
                logger.info("Update versions: %s has force_version" % tool)
                continue
            if tool == self.dockerfile.dockerfile_repo_name:
                continue
            current_version = self.tools_current_versions[tool]
            next_version = self.tools_next_versions.get(tool, None)
            if next_version is None:
                logger.info("Update versions: %s has no next version" % tool)
                continue
            if current_version == next_version:
                logger.info(
                    "Update versions: %s has no changed version" % tool)
                continue
            self.dockerfile.set_version(tool, next_version)
            logger.info("Update versions: %s has next version %s" %
                        (tool, next_version))
            dockerfile_changed = True
        if dockerfile_changed:
            self.dockerfile.set_next_version_dockerfile()
        return dockerfile_changed


class DockerfileGeneratorLambda(UtilsMixin):

    def __init__(self):
        self.s3bucket = s3store.get_s3_bucket_manager()
        self.dockerfile_repo = github.get_github_repository(
            constants.DOCKERFILE_GITHUB_REPO)
        self.dockerfile = jsonstore.get_dockerfile(self.dockerfile_repo)
        self._internal_state = None
        self.exit_code = 0

    @property
    def internal_state(self):
        """ Get the state from AWS S3 json file, or use the one from Github,
        if there is none."""
        if self._internal_state is None:
            internal_state = self.s3bucket.read_object(
                constants.INTERNAL_STATE_FILE)
            if internal_state is None:
                logger.info("Internal state: No state from S3")
                internal_state = self.dockerfile.dump
                self.save_state_to_s3(internal_state)
            self._internal_state = jsonstore.Store(internal_state)
        return self._internal_state

    def update_files_on_github(self):
        template_dockerfile = self.dockerfile_repo.get_file_contents(
            constants.TEMPLATE_GITHUB_DOCKERFILE_PATH)
        template_readme = self.dockerfile_repo.get_file_contents(
            constants.TEMPLATE_GITHUB_README_PATH)
        commit_msg = self.dockerfile.update_summary(self.internal_state)
        commit_files = [
            (constants.INTERNAL_STATE_FILE, self.dockerfile.dump),
            ("Dockerfile", template_dockerfile.format(
                **self.dockerfile.template_variables)),
            ("README.md", template_readme.format(
                **self.dockerfile.template_variables))]
        logger.info("Updating files on Github with message:\n\t%s" %
                    commit_msg)
        self.dockerfile_repo.commit(commit_files, commit_msg)

    def save_state_to_s3(self, content):
        try:
            logger.info("Saving state to S3")
            self.s3bucket.write_object(constants.INTERNAL_STATE_FILE, content)
        except (botocore.exceptions.ClientError, Exception) as e:
            raise exceptions.LambdaException(
                "Error: Uploading object to s3 bucket: %s" % (str(e)))

    def main(self):
        if self.update_dockerfile_versions():
            self.update_files_on_github()
            self.save_state_to_s3(self.dockerfile.dump)
        return self.exit_code  # Making Lambda Service happy


def lambda_handler():
    return DockerfileGeneratorLambda().main()
