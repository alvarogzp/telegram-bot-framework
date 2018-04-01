from bot.action.util.format import DateFormatter
from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.api.domain import ApiObject


class ApiObjectInfoFormatter:
    def __init__(self, api: Api, api_object: ApiObject):
        self.api = api
        self.api_object = api_object
        self.info_items = []

    def format(self):
        raise NotImplementedError()

    def get_formatted(self):
        return FormattedText().newline().join(self.info_items)

    def _add_title(self, title: str):
        self._add(
            FormattedText().bold(title)
        )

    def _add_info(self, label: str, value, separator: str = ":", additional_text: str = ""):
        info = FormattedText()\
            .normal("{label}{separator} {value}")\
            .start_format()\
            .normal(label=label)\
            .normal(separator=separator)
        if isinstance(value, FormattedText):
            info.concat(value=value)
        else:
            info.bold(value=value)
        info = info.end_format()
        if additional_text:
            info.normal(" ").normal(additional_text)
        self._add(info)

    def _add_empty(self):
        self._add(FormattedText())

    def _add(self, text: FormattedText):
        self.info_items.append(text)

    @staticmethod
    def _text(text: str, default_text: str = "None"):
        if text is None:
            return FormattedText().italic(default_text)
        return text

    @staticmethod
    def _yes_no(data, yes_emoji: str = "✅", no_emoji: str = "❌", unknown_emoji: str = "❓"):
        if data:
            return "Yes " + yes_emoji
        elif data is not None:
            return "No " + no_emoji
        else:
            return FormattedText().italic("Unknown " + unknown_emoji)

    @staticmethod
    def _username(username: str):
        if username is None:
            return FormattedText().italic("None")
        return "@" + username

    @staticmethod
    def _invite_link(invite_link: str):
        if invite_link is None:
            return FormattedText().italic("Inaccessible or non existent")
        return invite_link

    @staticmethod
    def _pinned_message(message: ApiObject):
        if message is None:
            return FormattedText().italic("None")
        return "<{id}>".format(id=message.message_id)

    @staticmethod
    def _group_sticker_set(sticker_set_name: str):
        if sticker_set_name is None:
            return FormattedText().italic("None")
        return sticker_set_name

    @staticmethod
    def _date(date: int, default_text: str = "None"):
        if not date:
            return FormattedText().bold(default_text)
        return DateFormatter.format_full(date)
