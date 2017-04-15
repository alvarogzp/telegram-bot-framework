from bot.api.domain import Message
from bot.api.telegram import TelegramBotApi
from bot.storage import State


class Api:
    def __init__(self, telegram_api: TelegramBotApi, state: State):
        self.telegram_api = telegram_api
        self.state = state

    def send_message(self, message: Message, **params):
        message_params = message.data.copy()
        message_params.update(params)
        if self.__should_send_message(message_params):
            return self.telegram_api.sendMessage(**message_params)

    def __should_send_message(self, message_params):
        chat_id = message_params.get("chat_id")
        if chat_id:
            chat_state = self.state.get_for_chat_id(chat_id)
            is_silenced = chat_state.silenced
            if is_silenced:
                return False
        return True

    def get_pending_updates(self):
        there_are_pending_updates = True
        while there_are_pending_updates:
            there_are_pending_updates = False
            for update in self.get_updates(timeout=0):
                there_are_pending_updates = True
                yield update

    def get_updates(self, timeout=45):
        updates = self.telegram_api.getUpdates(offset=self.__get_updates_offset(), timeout=timeout)
        for update in updates:
            self.__set_updates_offset(update.update_id)
            yield update

    def __get_updates_offset(self):
        return self.state.next_update_id

    def __set_updates_offset(self, last_update_id):
        self.state.next_update_id = str(last_update_id + 1)

    def __getattr__(self, item):
        return self.telegram_api.__getattr__(item)
