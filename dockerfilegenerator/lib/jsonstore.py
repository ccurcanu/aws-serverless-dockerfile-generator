# -*- coding: utf-8 -*-

import collections
import os
import hashlib
import json

import constants


class Store():
    """ Internal JSON file modeled as a store.

    The __init__ method accepts the following parameters:

    content (str): Content of the JSON obj that will be constructed.
    repo_name (str): Name of the dockerfile GitHub repository.

    Notes:

        The Dockerfile repository (ccurcanu/docker-cloud-tools) has a JSON file
    located as 'internal/store.json' where internal state is stored.

    Most important is the versions of each tracked tool.

    Other internal state is stored.

    """

    def __init__(self, content, repo_name):
        self.json = json.loads(content)
        self.dockerfile_repo_name = os.path.basename(repo_name)

    @property
    def dump(self):
        """ Dump of the JSON object as str with visibile identation"""
        return json.dumps(self.json, indent=4)

    @property
    def sha(self):
        """ SHA256 hash of the internal JSON dump"""
        content = self.dump.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    @property
    def template_variables(self):
        """ Return a dict used to populate README.md and Dockerfile templates
        with values.

        Notes:

        keys (str): Are mentioned as template key for each tracked tool in the
            internal tool.

        values (str): Values are the versions mentioned in the internal store.
        """
        template = dict()
        for item in self.json:
            remove_prefix = self.remove_prefix(item)
            version = self.json[item]["version"]
            if remove_prefix and version.startswith(remove_prefix):
                version = self.json[item]["version"].replace(remove_prefix, "")
            template.update({self.json[item]["template_key"]: version})
        return template

    def equals(self, store):
        return self.sha == store.sha

    def different(self, store):
        return not self.equals(store)

    def version(self, tool_name):
        """ Return version (str) of the tool from json store"""
        if tool_name in self.json:
            return self.json[tool_name]["version"]

    def set_version(self, tool_name, version):
        if tool_name in self.json:
            self.json[tool_name]["version"] = version
        else:
            raise Exception(
                "Error: repo key '%s' not existing in store" % tool_name)

    def set_next_version_dockerfile(self):
        """ Increments the version of the dockerfile repo from internal json"""
        self.json[self.dockerfile_repo_name]["version"] = str(
            self._get_dockerfile_current_version() + 1)

    def _get_dockerfile_current_version(self):
        return int(self.json[self.dockerfile_repo_name]["version"].strip())

    def github_repo_name(self, tool_name):
        if tool_name in self.json:
            return self.json[tool_name]["github_repo"]

    def remove_prefix(self, tool_name):
        """ Return version str prefix if JSON content entry has
        'remove_prefix' specified.

        Notes:

        Example of version with prefix is 'v0.11.9' (for terraform), where
        prefix is 'v'.

        Return:

        prefix (str): Prefix of the version. None: if the 'remove_prefix' is
            not present in the tool item. """
        if tool_name in self.json:
            if "remove_prefix" in self.json[tool_name]:
                return self.json[tool_name]["remove_prefix"]

    def force_version(self, tool_name):
        """ Detect if 'force_version' tag is present in the JSON content entry
        for the tool_name. """
        if tool_name in self.json:
            return "force_version" in self.json[tool_name]
        return False

    def update_summary(self, other_store):
        """ Composes a version update summary (str) comparing current state
        with the state of another similar type object. """

        changes = self._get_changed_versions(other_store)
        headline = "\nChanges detected on: " + ', '.join(changes.keys()) + "\n"
        summary = "Versions:\n"
        for tool_name in changes:
            summary += 4 * " " + "* %s (% s -> % s)\n" % (
                tool_name, changes[tool_name][0], changes[tool_name][1])
        return headline + "\n" + summary

    def _get_changed_versions(self, other_store):
        changes = collections.OrderedDict()
        for tool_name in self.json:
            old_ver = other_store.version(tool_name)
            new_ver = self.version(tool_name)
            if old_ver == new_ver:
                continue
            changes[tool_name] = (old_ver, new_ver)
        return changes


def get_dockerfile(repo):
    return Store(
        repo.get_dockerfile_content(),
        constants.DOCKERFILE_GITHUB_REPO)
