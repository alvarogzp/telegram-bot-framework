import json

from bot.action.extra.messages.mapper import StoredMessageMapper
from bot.action.extra.messages.operations import MessageList, MessageIdOperations

MIN_MESSAGES_TO_KEEP = 5000
MAX_MESSAGES_TO_KEEP = 15000


class MessageStorageHandler:
    def __init__(self, event):
        self.state = event.state.get_for("messages")

    def get_stored_messages(self):
        return MessageList(self.state.list_keys(), self.state)

    def save_message(self, message):
        data = StoredMessageMapper.from_api(message).map().to_data()
        dump = json.dumps(data)
        self.state.set_value(str(message.message_id), dump + "\n", append=True)

    def delete_old_messages(self):
        stored_ids = self.state.list_keys()
        if len(stored_ids) > MAX_MESSAGES_TO_KEEP:
            number_of_messages_to_delete = len(stored_ids) - MIN_MESSAGES_TO_KEEP
            ids_to_delete = MessageIdOperations.sorted(stored_ids, keep_only_first=number_of_messages_to_delete)
            self.__delete_messages(ids_to_delete)

    def __delete_messages(self, message_ids_to_delete):
        for message_id in message_ids_to_delete:
            self.state.set_value(message_id, None)
