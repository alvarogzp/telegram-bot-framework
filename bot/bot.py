import traceback

from bot.action.core.action import Update, Action
from bot.api.api import Api
from bot.api.domain import Chat, Message
from bot.api.telegram import TelegramBotApi
from bot.storage import Config, Cache
from bot.storage import State


CONFIG_DIR = "config"
STATE_DIR = "state"


class Bot:
    def __init__(self):
        self.config = Config(CONFIG_DIR)
        self.state = State(STATE_DIR)
        self.cache = Cache()
        telegram_api = TelegramBotApi(self.config.get_auth_token(), self.config.is_debug_enabled())
        self.api = Api(telegram_api, self.state)
        self.cache.admin_chat = Chat.create(id=self.config.get_admin_user_id())
        self.cache.bot_info = self.api.get_me()
        self.action = Action()

    def set_action(self, action: Action):
        action.setup(self.api, self.config, self.state, self.cache)
        self.action = action

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
            self.action.process(Update(update, is_pending))
        except KeyboardInterrupt:
            raise  # to stop main loop
        except BaseException as e:
            self.send_to_admin("Error while processing update. Action " + self.action.get_name() + " failed with error: " + str(e))
            traceback.print_exc()

    def process_message(self, message):
        if message.text is not None:
            self.process_text_message(message)

    def process_text_message(self, message):
        print(message.text)
        self.api.send_message(message.reply_message("test response"))

    def send_to_admin(self, message):
        message_to_admin = "[admin] " + message
        self.api.send_message(Message.create(chat=self.cache.admin_chat, text=message_to_admin))
