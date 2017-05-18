from bot.action.util.format import TextSummarizer, DateFormatter, UserFormatter, SizeFormatter, TimeFormatter
from bot.action.util.textformat import FormattedText
from bot.api.domain import ApiObjectList, Message, CaptionableMessage, Photo, Sticker, Document, Voice

BULLET_STRING = "➡️ "
START_CONTENT_STRING = "⬇ "

GIF_MIME_TYPE = "video/mp4"


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

    def _summarized(self, field="text", max_characters=15):
        text = FormattedText()
        content = getattr(self.last_message, field)
        if content:
            summarized_content = TextSummarizer.summarize(content, max_number_of_characters=max_characters)
            text.normal(" [ ").italic(summarized_content).normal(" ]")
        return text

    def _summarized_caption(self, max_characters):
        return self._summarized("caption", max_characters)

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

    def _full_content(self, content_field="text", prepend_newlines_if_content=False):
        text = FormattedText()
        content = getattr(self.message, content_field)
        if content is not None:
            if prepend_newlines_if_content:
                text.newline().newline()
            text.normal(self.start_content).bold(content_field.capitalize()).bold(":").newline()
            text.normal(content)
        text.concat(self._full_edits_content(content_field))
        return text

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

    @staticmethod
    def _printable_dimensions(width, height):
        return "{width}↔️ x {height}↕️".format(width=width, height=height)

    @staticmethod
    def _formatted_size(size_in_bytes):
        if size_in_bytes is not None:
            size = SizeFormatter.format(size_in_bytes)
            return FormattedText().normal(" ({size})").start_format().bold(size=size).end_format()
        else:
            return FormattedText()

    def _formatted_mime_type(self, mime_type):
        if mime_type is not None:
            return FormattedText().newline().normal(self.bullet).normal("Type: ").bold(mime_type)
        else:
            return FormattedText()

    def _add_caption_if_present(self, captionable_message: CaptionableMessage):
        caption = self.message.caption
        if caption:
            captionable_message.with_caption(caption)


class UnknownMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        return FormattedText().bold("❓ Unknown")

    def get_full_content(self):
        text = self._full_content_header()
        text.normal(self.bullet).bold("This message type is not supported yet :(")
        return text.build_message()


class TextMessageAnalyzer(MessageAnalyzer):
    def _get_summary(self):
        return FormattedText().normal("✍️").concat(self._summarized("text", max_characters=15))

    def get_full_content(self):
        text = self._full_content_header()
        text.concat(self._full_content("text"))
        return text.build_message()


class PhotoMessageAnalyzer(MessageAnalyzer):
    @property
    def printable_type(self):
        return "🌅 Photo"

    def _get_summary(self):
        return FormattedText().bold(self.printable_type).concat(self._summarized_caption(max_characters=9))

    def get_full_content(self):
        text = self._full_content_header()
        photo = self.__get_photo()
        description = FormattedText()\
            .normal("{bullet}Message is a {dimensions}{size} {photo}")\
            .start_format()\
            .normal(bullet=self.bullet)\
            .bold(dimensions=self._printable_dimensions(photo.width, photo.height))\
            .concat(size=self._formatted_size(photo.file_size))\
            .bold(photo=self.printable_type)\
            .end_format()
        text.concat(description)
        text.concat(self._full_content("caption", prepend_newlines_if_content=True))
        text.newline().newline()
        text.normal(self.start_content).bold("Following is the photo:")
        photo_message = Photo.create_photo(photo.file_id)
        self._add_caption_if_present(photo_message)
        return [text.build_message(), photo_message]

    def __get_photo(self):
        photo = self.message.photo
        if type(photo) is ApiObjectList:
            # backward compatibility for previous messages stored with an array of photo info
            photo = list(photo)[-1]
        return photo


class StickerMessageAnalyzer(MessageAnalyzer):
    @property
    def printable_type(self):
        return self.__get_emoji() + " Sticker"

    def _get_summary(self):
        return FormattedText().bold(self.printable_type)

    def get_full_content(self):
        text = self._full_content_header()
        sticker = self.message.sticker
        description = FormattedText()\
            .normal("{bullet}Message is a {dimensions}{size} {sticker}")\
            .start_format()\
            .normal(bullet=self.bullet)\
            .bold(dimensions=self._printable_dimensions(sticker.width, sticker.height))\
            .concat(size=self._formatted_size(sticker.file_size))\
            .bold(sticker=self.printable_type)\
            .end_format()
        text.concat(description)
        text.newline().newline()
        text.normal(self.start_content).bold("Following is the sticker:")
        sticker_message = Sticker.create_sticker(sticker.file_id)
        return [text.build_message(), sticker_message]

    def __get_emoji(self, default="📃"):
        emoji = self.message.sticker.emoji
        return emoji if emoji else default


class DocumentMessageAnalyzer(MessageAnalyzer):
    @property
    def printable_type(self):
        return "📄 Document"

    def _get_summary(self):
        return FormattedText().bold(self.printable_type).concat(self._summarized_caption(max_characters=6))

    def get_full_content(self):
        text = self._full_content_header()
        document = self.message.document
        description = FormattedText()\
            .normal("{bullet}Message is a{size} {document}")\
            .start_format()\
            .normal(bullet=self.bullet)\
            .concat(size=self._formatted_size(document.file_size))\
            .bold(document=self.printable_type)\
            .end_format()
        text.concat(description)
        text.concat(self.__formatted_file_name(document.file_name))
        text.concat(self._formatted_mime_type(document.mime_type))
        text.concat(self._full_content("caption", prepend_newlines_if_content=True))
        text.newline().newline()
        text.normal(self.start_content).bold("Following is the document:")
        document_message = Document.create_document(document.file_id)
        self._add_caption_if_present(document_message)
        return [text.build_message(), document_message]

    def __formatted_file_name(self, file_name):
        if file_name is not None:
            return FormattedText().newline().normal(self.bullet).normal("Name: ").bold(file_name)
        else:
            return FormattedText()


class GifMessageAnalyzer(DocumentMessageAnalyzer):
    @property
    def printable_type(self):
        return "🎥 GIF"

    def _get_summary(self):
        return FormattedText().bold(self.printable_type).concat(self._summarized_caption(max_characters=11))

    def get_full_content(self):
        text = self._full_content_header()
        gif = self.message.document
        description = FormattedText()\
            .normal("{bullet}Message is a{size} {gif}")\
            .start_format()\
            .normal(bullet=self.bullet)\
            .concat(size=self._formatted_size(gif.file_size))\
            .bold(gif=self.printable_type)\
            .end_format()
        text.concat(description)
        text.concat(self._full_content("caption", prepend_newlines_if_content=True))
        text.newline().newline()
        text.normal(self.start_content).bold("Following is the GIF:")
        gif_message = Document.create_document(gif.file_id)
        self._add_caption_if_present(gif_message)
        return [text.build_message(), gif_message]


class VoiceMessageAnalyzer(MessageAnalyzer):
    @property
    def printable_type(self):
        return "🎤 Voice"

    def _get_summary(self):
        return FormattedText().bold(self.printable_type).concat(self._summarized_caption(max_characters=9))

    def get_full_content(self):
        text = self._full_content_header()
        voice = self.message.voice
        description = FormattedText()\
            .normal("{bullet}Message is a {duration}{size} {voice}")\
            .start_format()\
            .normal(bullet=self.bullet)\
            .bold(duration=TimeFormatter.format(voice.duration))\
            .concat(size=self._formatted_size(voice.file_size))\
            .bold(voice=self.printable_type)\
            .end_format()
        text.concat(description)
        text.concat(self._formatted_mime_type(voice.mime_type))
        text.concat(self._full_content("caption", prepend_newlines_if_content=True))
        text.newline().newline()
        text.normal(self.start_content).bold("Following is the voice:")
        voice_message = Voice.create_voice(voice.file_id)
        self._add_caption_if_present(voice_message)
        return [text.build_message(), voice_message]


class MessageAnalyzerResolver:
    def __init__(self, user_storage_handler):
        self.user_storage_handler = user_storage_handler

    def get_analyzer(self, stored_message):
        message_data = stored_message.message
        analyzer = UnknownMessageAnalyzer
        if message_data.text is not None:
            analyzer = TextMessageAnalyzer
        elif message_data.photo:
            analyzer = PhotoMessageAnalyzer
        elif message_data.sticker:
            analyzer = StickerMessageAnalyzer
        elif message_data.document:
            if message_data.document.mime_type == GIF_MIME_TYPE:
                # treating all files of that mime type as gifs, until better way of identifying gifs is known
                analyzer = GifMessageAnalyzer
            else:
                analyzer = DocumentMessageAnalyzer
        elif message_data.voice:
            analyzer = VoiceMessageAnalyzer
        return analyzer(stored_message, self.user_storage_handler)


# Following is the public API that is supposed to be used

def get_short_info(user_storage_handler, stored_message, show_command):
    return MessageAnalyzerResolver(user_storage_handler).get_analyzer(stored_message).get_short_info(show_command)


def get_full_content(user_storage_handler, stored_message):
    return MessageAnalyzerResolver(user_storage_handler).get_analyzer(stored_message).get_full_content()
