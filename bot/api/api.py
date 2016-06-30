from bot.api.telegram import TelegramBotApi
from bot.storage import State


class Api:
    def __init__(self, telegram_api: TelegramBotApi, state: State):
        self.telegram_api = telegram_api
        self.state = state

    def get_me(self):
        return self.telegram_api.get_me()

    def send_message(self, message):
        return self.telegram_api.send_message(chat_id=message.chat.id, text=message.text,
                                              reply_to_message_id=message.reply_to_message_id)

    def get_pending_updates(self):
        yield from self.get_updates(timeout=0)

    def get_updates(self, timeout=45):
        updates = self.telegram_api.get_updates(offset=self.__get_updates_offset(), timeout=timeout)
        for update in updates:
            self.__set_updates_offset(update.update_id)
            yield update

    def __get_updates_offset(self):
        return self.state.get_next_update_id()

    def __set_updates_offset(self, last_update_id):
        self.state.set_next_update_id(str(last_update_id + 1))
