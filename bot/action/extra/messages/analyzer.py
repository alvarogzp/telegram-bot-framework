from bot.action.util.format import TextSummarizer, DateFormatter, UserFormatter, SizeFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message, Photo, ApiObjectList

BULLET_STRING = "➡️ "
START_CONTENT_STRING = "⬇ "


class MessageAnalyzer:
    def __init__(self, stored_message, user_storage_handler):
        self.message_id = stored_message.message_id
        self.message = stored_message.message
        self.edited_messages = stored_message.edited_messages
        self.user_storage_handler = user_storage_handler

    def get_short_info(self, show_command):
        return FormattedText()\
            .normal(show_command)\
            .normal(" at ").bold(self.date)\
            .normal(" by ").bold(self.user)\
            .normal(self.__get_edits_info())\
            .normal(" ").concat(self._get_summary())

    def __get_edits_info(self):
        return (" (%s edits)" % len(self.edited_messages)) if self.has_been_edited else ""

    def _get_summary(self):
        """:rtype: FormattedText"""
        raise NotImplementedError()

    def get_full_content(self):
        """:rtype: list[Message]|Message"""
        raise NotImplementedError()

    @property
    def has_been_edited(self):
        return len(self.edited_messages) > 0

    @property
    def last_message(self):
        """Returns either the message or, if edited, the last edition message."""
        if self.has_been_edited:
            return self.edited_messages[-1]
        return self.message

    @property
    def date(self):
        return DateFormatter.format(self.message.date)

    @property
    def full_date(self):
        return DateFormatter.format_full(self.message.date)

    @property
    def user(self):
        return self._user_formatter(self.message.from_).default_format

    @property
    def full_user(self):
        return self._user_formatter(self.message.from_).full_format

    def _user_formatter(self, user_id):
        return UserFormatter.retrieve(user_id, self.user_storage_handler)

    @property
    def bullet(self):
        return BULLET_STRING

    @property
    def start_content(self):
        return START_CONTENT_STRING

    def _full_content_header(self):
        text = FormattedText()\
            .normal(self.bullet)\
            .normal("Message ").bold(self.message_id)\
            .normal(" sent on ").bold(self.full_date)\
            .normal(" by ").bold(self.full_user)\
            .normal(".").newline()
        self.__add_forwarded_info_if_needed(text)
        self.__add_edit_info_if_needed(text)
        return text.newline()

    def __add_forwarded_info_if_needed(self, text):
        if self.message.forward_date:
            # all forwarded messages have forward_date field
            # but forwards from channels do not have forward_from (instead they have forward_from_chat)
            # but forwards from channels where sender is not hidden have both (forward_from and forward_from_chat)
            text.normal(self.bullet).normal("This message was forwarded from ")
            if self.message.forward_from_chat:
                text.bold(self.message.forward_from_chat.title).normal(" channel")
                if self.message.forward_from:
                    formatted_user = self._user_formatter(self.message.forward_from).full_format
                    text.normal(" (written by ").bold(formatted_user).normal(")")
            elif self.message.forward_from:
                formatted_user = self._user_formatter(self.message.forward_from).full_format
                text.bold(formatted_user)
            else:
                text.italic("no owner info available")
            formatted_date = DateFormatter.format_full(self.message.forward_date)
            text.normal(" originally sent on ").bold(formatted_date).normal(".").newline()

    def __add_edit_info_if_needed(self, text):
        if self.has_been_edited:
            text.normal(self.bullet).normal("This message has been edited ")\
                .bold(len(self.edited_messages)).bold(" time(s)").normal(".").newline()

    def _full_edits_content(self, edited_field="text"):
        text = FormattedText()
        total_number_of_edits = len(self.edited_messages)
        for index, edited_message in enumerate(self.edited_messages):
            formatted_date = DateFormatter.format_full(edited_message.edit_date)
            edited_content = getattr(edited_message, edited_field)
            text.newline().newline()
            text.normal(self.bullet).normal("Edit ").bold(index + 1).bold("/").bold(total_number_of_edits)\
                .normal(", done at ").bold(formatted_date).normal(".").newline()
            if edited_content is None:
                text.normal(self.bullet).bold(edited_field.capitalize()).bold(" deleted")
            else:
                text.normal(self.start_content).bold("New ").bold(edited_field).bold(":").newline()
                text.normal(edited_content)
        return text


class UnknownMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        return FormattedText().bold("❓ Unknown")

    def get_full_content(self):
        text = self._full_content_header()
        text.normal(self.bullet).bold("This message type is not supported yet :(")
        return text.build_message()


class TextMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        summarized_text = TextSummarizer.summarize(self.last_message.text, max_number_of_characters=15)
        return FormattedText().normal("✍️ [ ").italic(summarized_text).normal(" ]")

    def get_full_content(self):
        text = self._full_content_header()
        text.normal(self.start_content).bold("Text:").newline()
        text.normal(self.message.text)
        text.concat(self._full_edits_content("text"))
        return text.build_message()


class PhotoMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        summary = FormattedText().bold("🌅 Photo")
        caption = self.last_message.caption
        if caption:
            summarized_caption = TextSummarizer.summarize(caption, max_number_of_characters=9)
            summary.normal(" [ ").italic(summarized_caption).normal(" ]")
        return summary

    def get_full_content(self):
        text = self._full_content_header()
        photo = self.__get_photo()
        description = FormattedText()\
            .normal("{bullet}Message is a {dimensions}{size} {photo}")\
            .start_format()\
            .normal(bullet=self.bullet)\
            .concat(dimensions=self.__get_formatted_photo_dimensions(photo),
                    size=self.__get_formatted_photo_size(photo))\
            .bold(photo="🌅 Photo")\
            .end_format()
        text.concat(description)
        if self.message.caption:
            text.newline().newline()
            text.normal(self.start_content).bold("Caption:").newline()
            text.normal(self.message.caption)
        text.concat(self._full_edits_content("caption"))
        text.newline().newline()
        text.normal(self.start_content).bold("Following is the photo:")
        photo_message = Photo.create_photo(photo.file_id)
        if self.message.caption:
            photo_message.with_caption(self.message.caption)
        return [text.build_message(), photo_message]

    @staticmethod
    def __get_formatted_photo_dimensions(photo):
        height = photo.height
        width = photo.width
        return FormattedText().bold("{width}↔️ x {height}↕️")\
            .start_format().normal(width=width, height=height).end_format()

    @staticmethod
    def __get_formatted_photo_size(photo):
        size = photo.file_size
        if size is not None:
            size = SizeFormatter.format(size)
            return FormattedText().normal(" ({size})")\
                .start_format().bold(size=size).end_format()
        return FormattedText()

    def __get_photo(self):
        photo = self.message.photo
        if type(photo) is ApiObjectList:
            # backward compatibility for previous messages stored with an array of photo info
            photo = list(photo)[-1]
        return photo


class StickerMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        summary = FormattedText()
        emoji = self.message.sticker.emoji
        if emoji:
            summary.normal(emoji)
        else:
            summary.normal("📃")
        summary.bold(" Sticker")
        return summary

    def get_full_content(self):
        pass


class DocumentMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        # todo add caption if present?
        return FormattedText().bold("📄 Document")

    def get_full_content(self):
        pass


class VoiceMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        # todo add caption if present?
        return FormattedText().bold("🎤 Voice")

    def get_full_content(self):
        pass


class MessageAnalyzerResolver:
    def __init__(self, user_storage_handler):
        self.user_storage_handler = user_storage_handler

    def get_analyzer(self, stored_message):
        message_data = stored_message.message
        message_type = UnknownMessageAnalyzer
        if message_data.text is not None:
            message_type = TextMessageAnalyzer
        elif message_data.photo:
            message_type = PhotoMessageAnalyzer
        elif message_data.sticker:
            message_type = StickerMessageAnalyzer
        elif message_data.document:
            # todo differentiate gifs
            message_type = DocumentMessageAnalyzer
        elif message_data.voice:
            message_type = VoiceMessageAnalyzer
        return message_type(stored_message, self.user_storage_handler)


# Following is the public API that is supposed to be used

def get_short_info(user_storage_handler, stored_message, show_command):
    return MessageAnalyzerResolver(user_storage_handler).get_analyzer(stored_message).get_short_info(show_command)


def get_full_content(user_storage_handler, stored_message):
    return MessageAnalyzerResolver(user_storage_handler).get_analyzer(stored_message).get_full_content()
