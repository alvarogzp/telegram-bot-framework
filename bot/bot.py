import traceback

from bot.api.api import Api
from bot.api.telegram import TelegramBotApi
from bot.domain import Message, Chat
from bot.storage import Config
from bot.storage import State


CONFIG_DIR = "config"
STATE_DIR = "state"


class Bot:
    def __init__(self):
        self.config = Config(CONFIG_DIR)
        self.state = State(STATE_DIR)
        telegram_api = TelegramBotApi(self.config.get_auth_token(), self.config.is_debug_enabled())
        self.api = Api(telegram_api, self.state)
        self.admin_chat = Chat(self.config.get_admin_user_id())
        self.bot_info = self.api.get_me()

    def run(self):
        self.send_to_admin("Started")
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.send_to_admin("KeyboardInterrupt")
        except BaseException as e:
            self.send_to_admin("Fatal error: " + str(e))
            raise e
        finally:
            self.send_to_admin("Finished")

    def main_loop(self):
        for update in self.api.get_pending_updates():
            self.process_update(update, is_pending=True)
        while True:
            for update in self.api.get_updates():
                self.process_update(update)

    def process_update(self, update, is_pending=False):
        try:
            if update.message is not None:
                self.process_message(update.message)
        except BaseException as e:
            self.send_to_admin("Error while processing update: " + str(e))
            traceback.print_exc()

    def process_message(self, message):
        if message.text is not None:
            self.process_text_message(message)

    def process_text_message(self, message: Message):
        print(message.text)
        self.api.send_message(message.reply_message("test response"))

    def send_to_admin(self, message):
        message_to_admin = "[admin] " + message
        self.api.send_message(Message(self.admin_chat, message_to_admin))
