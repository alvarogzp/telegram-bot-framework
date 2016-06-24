from bot.api.telegram import TelegramBotApi
from bot.domain import BotInfo, Chat, Message, Update
from bot.storage import State


class Api:
    def __init__(self, telegram_api: TelegramBotApi, state: State):
        self.telegram_api = telegram_api
        self.state = state

    def get_me(self):
        response = self.telegram_api.get_me()
        username = response.get_or_fail("username")
        first_name = response.get_or_fail("first_name")
        return BotInfo(username, first_name)

    def send_message(self, message: Message):
        self.telegram_api.send_message(chat_id=message.chat.id, text=message.text)

    def get_pending_updates(self):
        yield from self.get_updates(timeout=0)

    def get_updates(self, timeout=45):
        response = self.telegram_api.get_updates(offset=self.__get_updates_offset(), timeout=timeout)
        for response_update in response:
            update_id = response_update.get_or_fail("update_id")
            self.__set_updates_offset(update_id)
            response_message = response_update.get_or_fail("message")
            response_chat = response_message.get_or_fail("chat")
            chat = Chat(response_chat.get_or_fail("id"))
            message = Message(chat, response_message.get_or_default("text"))
            yield Update(message)

    def __get_updates_offset(self):
        return self.state.get_next_update_id()

    def __set_updates_offset(self, last_update_id):
        self.state.set_next_update_id(str(last_update_id + 1))
