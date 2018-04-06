import pkg_resources

from bot import project_info
from bot.action.core.action import Action
from bot.action.util.textformat import FormattedText


class AboutAction(Action):
    def __init__(self, project_package_name: str, author_handle: str = None, is_open_source: bool = False,
                 url: str = None, license_name: str = None, license_url: str = None):
        super().__init__()
        self.version = VersionAction.get_version(project_package_name)
        self.author_handle = author_handle
        self.is_open_source = is_open_source
        self.url = url
        self.license = self.__get_license(license_name, license_url)
        self.text = FormattedText()

    def post_setup(self):
        bot_name = self.cache.bot_info.first_name
        self.text = self.__build_message_text(bot_name, self.version, self.author_handle, self.__get_framework(),
                                              self.is_open_source, self.license, self.url)

    @staticmethod
    def __build_message_text(bot_name: str, version: str, author: str, framework: FormattedText,
                             is_open_source: bool, license: FormattedText, url: str):
        text = FormattedText()\
            .normal("{bot_name}, version {version}.").newline()\
            .newline()\
            .normal("Created by {author} using {framework}.")
        if is_open_source:
            text.newline().newline()\
                .normal("This bot is Open Source.").newline()\
                .normal("You can view the code, improve it and launch your own instance (complying with the license).")
        if license:
            text.newline().newline()\
                .normal("It is licensed under the {license} license.")
        if url:
            text.newline().newline()\
                .normal("Project home:").newline()\
                .normal("{url}")
        return text.start_format()\
            .bold(bot_name=bot_name, version=version)\
            .normal(author=author, url=url)\
            .concat(framework=framework, license=license)\
            .end_format()

    @staticmethod
    def __get_framework():
        framework_name = project_info.name
        framework_url = project_info.url
        framework_version = VersionAction.get_version(framework_name)
        return FormattedText()\
            .normal("{url} ({version})").start_format()\
            .url(framework_name, framework_url, name="url")\
            .normal(version=framework_version)\
            .end_format()

    @staticmethod
    def __get_license(name: str, url: str):
        if url:
            return FormattedText().url(name or url, url)
        if name:
            return FormattedText().bold(name)

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
