import constants


class FakeGitHubRepository:

    def __init__(self, name):
        self.name = name

    def get_file_contents(self, *args, **kwargs):
        return constants.JSON_CONTENT
