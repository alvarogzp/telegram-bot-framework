import traceback

from bot.action.core.action import Update, Action
from bot.api.api import Api
from bot.api.domain import Message
from bot.api.telegram import TelegramBotApi
from bot.logger.error_handler import ErrorHandler
from bot.multithreading.scheduler import SchedulerApi
from bot.storage import Config, Cache
from bot.storage import State


CONFIG_DIR = "config"
STATE_DIR = "state"


class Bot:
    def __init__(self):
        self.config = Config(CONFIG_DIR)
        self.state = State(STATE_DIR)
        self.cache = Cache()
        debug = self.config.is_debug_enabled()
        telegram_api = TelegramBotApi(self.config.auth_token, debug)
        self.api = Api(telegram_api, self.state)
        self.error_handler = ErrorHandler(self.api, self.config.admin_chat_id, debug)
        self.scheduler = SchedulerApi(self.error_handler.handle_work_error)
        self.scheduler.setup()
        self.cache.bot_info = self.api.getMe()
        self.action = Action()

    def set_action(self, action: Action):
        action.setup(self.api, self.config, self.state, self.cache, self.scheduler)
        self.action = action

    def run(self):
        self.send_to_admin("Started")
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.send_to_admin("KeyboardInterrupt")
        except SystemExit as e:
            self.send_to_admin("SystemExit: " + str(e))
            raise e
        except BaseException as e:
            self.send_to_admin("Fatal error: " + str(e))
            raise e
        finally:
            self.shutdown()

    def main_loop(self):
        for update in self.api.get_pending_updates():
            self.process_update(update, is_pending=True)
        while True:
            for update in self.api.get_updates():
                self.process_update(update)

    def process_update(self, update, is_pending=False):
        try:
            self.action.process(Update(update, is_pending))
        except Exception as e:
            self.send_to_admin("Error while processing update. Action " + self.action.get_name() + " failed with error: " + str(e))
            traceback.print_exc()

    def shutdown(self):
        self.scheduler.shutdown()
        self.send_to_admin("Finished")

    def send_to_admin(self, message):
        message_to_admin = "[admin] " + message
        self.api.send_message(Message.create(text=message_to_admin, chat_id=self.config.admin_user_id))
