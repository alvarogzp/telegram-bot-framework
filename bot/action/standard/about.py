from typing import Sequence

import pkg_resources

from bot import project_info
from bot.action.core.action import Action
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message


class AboutAction(Action):
    def __init__(self, project_package_name: str, authors: Sequence[Sequence[str]] = (), is_open_source: bool = False,
                 url: str = None, license_name: str = None, license_url: str = None,
                 donation_addresses: Sequence[Sequence[str]] = ()):
        super().__init__()
        self.version = VersionAction.get_version(project_package_name)
        self.authors = self.__get_authors(authors)
        self.is_open_source = is_open_source
        self.url = url
        self.license = self.__get_license(license_name, license_url)
        self.donation_addresses = self.__get_donation_addresses(donation_addresses)
        self.message = Message()

    def post_setup(self):
        bot_name = self.cache.bot_info.first_name
        self.message = self.__build_message(
            bot_name, self.version, self.authors, self.__get_framework(), self.is_open_source, self.license, self.url,
            self.donation_addresses
        )

    @staticmethod
    def __build_message(bot_name: str, version: str, authors: FormattedText, framework: FormattedText,
                        is_open_source: bool, license: FormattedText, url: str, donation_addresses: FormattedText):
        text = FormattedText()\
            .normal("{bot_name}, version {version}.").newline()\
            .normal("Based on {framework}.")
        if authors:
            text.newline().newline()\
                .bold("Authors").normal(":").newline()\
                .normal("{authors}")
        if is_open_source:
            text.newline().newline()\
                .normal("{bot_name} is Open Source.").newline()\
                .normal("You can inspect its code, improve it and launch your own instance "
                        "(complying with the license).")
        if license:
            text.newline().newline()\
                .normal("{bot_name} is licensed under the {license} license.")
        if url:
            text.newline().newline()\
                .normal("Project home:").newline()\
                .normal("{url}")
        if donation_addresses:
            text.newline().newline()\
                .normal("If you find {bot_name} useful and want to support its development, "
                        "please consider donating to the following addresses:").newline()\
                .normal("{donation_addresses}")
        return text.start_format()\
            .bold(bot_name=bot_name, version=version)\
            .normal(url=url)\
            .concat(framework=framework, authors=authors, license=license, donation_addresses=donation_addresses)\
            .end_format()\
            .build_message()

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

    def process(self, event):
        self.api.send_message(self.message.copy().to_chat_replying(event.message))


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
