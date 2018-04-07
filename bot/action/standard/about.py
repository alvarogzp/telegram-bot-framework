from typing import Sequence

import pkg_resources

from bot import project_info
from bot.action.core.action import Action
from bot.action.core.command import UnderscoredCommandBuilder
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message


ABOUT_FRAMEWORK_ARG = "framework"


class ProjectInfo:
    def __init__(self, project_package_name: str, authors: Sequence[Sequence[str]], is_open_source: bool,
                 url: str, license_name: str, license_url: str, donation_addresses: Sequence[Sequence[str]]):
        self.name = project_package_name
        self.framework = None  # type: FormattedText
        self.project_package_name = project_package_name
        self.authors = authors
        self.is_open_source = is_open_source
        self.url = url
        self.license_name = license_name
        self.license_url = license_url
        self.donation_addresses = donation_addresses


class AboutAction(Action):
    def __init__(self, project_package_name: str, authors: Sequence[Sequence[str]] = (), is_open_source: bool = False,
                 url: str = None, license_name: str = None, license_url: str = None,
                 donation_addresses: Sequence[Sequence[str]] = ()):
        super().__init__()
        self.info = ProjectInfo(
            project_package_name, authors, is_open_source, url, license_name, license_url, donation_addresses
        )
        self.message = Message()
        self.about_framework_message = self._about_framework()

    def post_setup(self):
        self.info.name = self.cache.bot_info.first_name
        self.message = self._about()

    def _about(self):
        return self.__about_message(self.info)

    def _about_framework(self):
        return self.__about_message(
            ProjectInfo(
                project_info.name,
                project_info.authors_credits,
                project_info.is_open_source,
                project_info.url,
                project_info.license_name,
                project_info.license_url,
                project_info.donation_addresses
            )
        )

    def __about_message(self, info: ProjectInfo):
        name = info.name
        version = VersionAction.get_version(info.project_package_name)
        authors = self.__get_authors(info.authors)
        framework = info.framework or FormattedText()
        is_open_source = info.is_open_source
        license = self.__get_license(info.license_name, info.license_url)
        url = info.url
        donation_addresses = self.__get_donation_addresses(info.donation_addresses)
        return self.__build_message(name, version, authors, framework, is_open_source, license, url, donation_addresses)

    @staticmethod
    def __get_framework(event):
        framework_name = project_info.name
        framework_url = project_info.url
        framework_version = VersionAction.get_version(framework_name)
        about_framework_command = UnderscoredCommandBuilder.build_command(event.command, ABOUT_FRAMEWORK_ARG)
        return FormattedText()\
            .normal("{url} {version} (see {about_framework_command})")\
            .start_format()\
            .url(framework_name, framework_url, name="url")\
            .normal(version=framework_version, about_framework_command=about_framework_command)\
            .end_format()

    @staticmethod
    def __get_license(name: str, url: str):
        if url:
            return FormattedText().url(name or url, url)
        if name:
            return FormattedText().bold(name)
        return FormattedText()

    @staticmethod
    def __get_authors(authors: Sequence[Sequence[str]]):
        texts = []
        for name, credit in authors:
            texts.append(
                FormattedText()
                .normal(" - {name} ({credit})")
                .start_format()
                .normal(name=name, credit=credit)
                .end_format()
            )
        return FormattedText().newline().join(texts)

    @staticmethod
    def __get_donation_addresses(donation_addresses: Sequence[Sequence[str]]):
        texts = []
        for name, address in donation_addresses:
            texts.append(
                FormattedText()
                .normal(" - {name}:️ {address}")
                .start_format()
                .normal(name=name)
                .bold(address=address)
                .end_format()
            )
        return FormattedText().newline().join(texts)

    @staticmethod
    def __build_message(name: str, version: str, authors: FormattedText, framework: FormattedText,
                        is_open_source: bool, license: FormattedText, url: str, donation_addresses: FormattedText):
        text = FormattedText()\
            .normal("{name}, version {version}.")
        if framework:
            text.newline()\
                .normal("Based on {framework}.")
        if authors:
            text.newline().newline()\
                .bold("Authors").normal(":").newline()\
                .normal("{authors}")
        if is_open_source:
            text.newline().newline()\
                .normal("{name} is Open Source.").newline()\
                .normal("You can inspect its code, improve it and launch your own instance "
                        "(complying with the license).")
        if license:
            text.newline().newline()\
                .normal("{name} is licensed under the {license} license.")
        if url:
            text.newline().newline()\
                .normal("Project home:").newline()\
                .normal("{url}")
        if donation_addresses:
            text.newline().newline()\
                .normal("If you find {name} useful and want to support its development, "
                        "please consider donating to the following addresses:").newline()\
                .normal("{donation_addresses}")
        return text.start_format()\
            .bold(name=name, version=version)\
            .normal(url=url)\
            .concat(framework=framework, authors=authors, license=license, donation_addresses=donation_addresses)\
            .end_format()\
            .build_message()

    def process(self, event):
        if event.command_args.lower() == ABOUT_FRAMEWORK_ARG:
            message = self.about_framework_message
        else:
            message = self.message
        self.api.send_message(message.copy().to_chat_replying(event.message))


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
