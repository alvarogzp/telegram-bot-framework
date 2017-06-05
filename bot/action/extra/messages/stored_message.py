import json

from bot.action.core.command import UnderscoredCommandBuilder
from bot.action.extra.messages import analyzer
from bot.action.extra.messages.mapper import StoredMessageMapper
from bot.api.domain import ApiObject


class StoredMessage:
    def __init__(self, message_id, message, *edited_messages, incomplete=False):
        self.message_id = message_id
        self.message = message
        self.edited_messages = edited_messages
        self.incomplete = incomplete

    @property
    def user_id(self):
        return self.message.from_

    def printable_info(self, event, user_storage_handler):
        show_command = UnderscoredCommandBuilder.build_command(event.command, self.message_id)
        return analyzer.get_short_info(user_storage_handler, self, show_command)

    def printable_full_message(self, user_storage_handler):
        return analyzer.get_full_content(user_storage_handler, self)

    @staticmethod
    def deserialize(message_id, data):
        messages = []
        for line in data.splitlines():
            message_data = json.loads(line)
            message = ApiObject.wrap_api_object(message_data)
            messages.append(message)
        return StoredMessage(message_id, *messages)

    @staticmethod
    def from_message(message):
        message_id = message.message_id
        data = StoredMessageMapper.from_api(message).map().to_data()
        mapped_message = ApiObject.wrap_api_object(data)
        return StoredMessage(message_id, mapped_message, incomplete=True)
