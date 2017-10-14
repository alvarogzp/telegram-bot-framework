from bot.action.util.textformat import FormattedText
from bot.api.api import Api
from bot.logger.message_sender.reusable import ReusableMessageSender


class FormattedTextReusableMessageSender(ReusableMessageSender):
    def __init__(self, api: Api, chat_id, separator: FormattedText = FormattedText().newline().newline()):
        super().__init__(api, separator)
        self.chat_id = chat_id
        self.message_id = None
        self.formatted_text = FormattedText()

    def _is_new(self):
        return self.message_id is None

    def _send_new(self, formatted_text: FormattedText):
        message = self.formatted_text.concat(formatted_text).build_message().to_chat(chat_id=self.chat_id)
        sent_message = self.api.send_message(message)
        self.message_id = sent_message.message_id

    def _send_edit(self, formatted_text: FormattedText):
        message = self.formatted_text.concat(self.separator).concat(formatted_text)\
            .build_message().to_chat(chat_id=self.chat_id)
        message.set_message_id(self.message_id)
        self.api.editMessageText(**message.data)

    def new(self):
        self.formatted_text = FormattedText()
        self.message_id = None
