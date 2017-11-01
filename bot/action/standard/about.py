import pkg_resources

from bot import project_info
from bot.action.core.action import Action
from bot.action.util.textformat import FormattedText


class AboutAction(Action):
    def __init__(self, project_package_name: str, author_handle: str = None, is_open_source: bool = False,
                 source_url: str = None, license_name: str = None):
        super().__init__()
        self.version = VersionAction.get_version(project_package_name)
        self.author_handle = author_handle
        self.is_open_source = is_open_source
        self.source_url = source_url
        self.license_name = license_name
        self.text = FormattedText()

    def post_setup(self):
        bot_name = self.cache.bot_info.first_name
        self.text = self.__build_message_text(bot_name, self.version, self.author_handle, self.__get_framework(),
                                              self.is_open_source, self.license_name, self.source_url)

    @staticmethod
    def __build_message_text(bot_name: str, version: str, author: str, framework: FormattedText,
                             is_open_source: bool, license_name: str, source_url: str):
        text = FormattedText()\
            .normal("{bot_name}, version {version}.").newline()\
            .newline()\
            .normal("Created by {author} using {framework}.")
        if is_open_source:
            text.newline().newline()\
                .normal("This bot is Open Source.").newline()\
                .normal("You can view the code, improve it and launch your own instance (complying with the license).")
        if license_name:
            text.newline().newline()\
                .normal("It is licensed under the {license} license.")
        if source_url:
            text.newline().newline()\
                .normal("You can find the source code on: {source_url}")
        return text.start_format()\
            .bold(bot_name=bot_name, version=version, license=license_name)\
            .normal(author=author, source_url=source_url)\
            .concat(framework=framework)\
            .end_format()

    @staticmethod
    def __get_framework():
        framework_name = project_info.name
        framework_url = project_info.source_url
        framework_version = VersionAction.get_version(framework_name)
        return FormattedText()\
            .normal("{url} ({version})").start_format()\
            .url(framework_name, framework_url, name="url")\
            .normal(version=framework_version)\
            .end_format()

    def process(self, event):
        self.api.send_message(self.text.build_message().to_chat_replying(event.message))


class VersionAction(Action):
    def __init__(self, project_package_name: str, releases_url: str = None):
        super().__init__()
        version = self.get_version(project_package_name)
        self.text = FormattedText().normal("Version {version}")
        if releases_url:
            self.text.newline().newline().normal("Releases: {releases_url}")
        self.text.start_format().bold(version=version).normal(releases_url=releases_url).end_format()

    @staticmethod
    def get_version(project_package_name: str):
        try:
            return pkg_resources.get_distribution(project_package_name).version
        except:
            return "<unknown>"

    def process(self, event):
        self.api.send_message(self.text.build_message().to_chat_replying(event.message))
