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
        return self.telegram_api.sendMessage(**message_params)

    def get_pending_updates(self):
        return self.get_updates(timeout=0)

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
