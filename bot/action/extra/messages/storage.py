import json

from bot.action.extra.messages.mapper import StoredMessageMapper
from bot.action.extra.messages.operations import MessageList, MessageIdOperations

DEFAULT_MESSAGES_KEEP_MIN = 1000
DEFAULT_MESSAGES_KEEP_MAX = 5000


class MessageStorageHandler:
    def __init__(self, config, event):
        self.config = config.get_for("messages")
        self.state = event.state.get_for("messages")

    def get_stored_messages(self):
        return MessageList(self.state.list_keys(), self.state)

    def save_message(self, message):
        data = StoredMessageMapper.from_api(message).map().to_data()
        dump = json.dumps(data)
        self.state.set_value(str(message.message_id), dump + "\n", append=True)

    def delete_old_messages(self):
        stored_ids = self.state.list_keys()
        max_messages_to_keep = self.config.get_value("keep_max", DEFAULT_MESSAGES_KEEP_MAX)
        if len(stored_ids) > max_messages_to_keep:
            min_messages_to_keep = self.config.get_value("keep_min", DEFAULT_MESSAGES_KEEP_MIN)
            number_of_messages_to_delete = len(stored_ids) - min_messages_to_keep
            ids_to_delete = MessageIdOperations.sorted(stored_ids, keep_only_first=number_of_messages_to_delete)
            self.__delete_messages(ids_to_delete)

    def __delete_messages(self, message_ids_to_delete):
        for message_id in message_ids_to_delete:
            self.state.set_value(message_id, None)
