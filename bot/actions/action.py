from bot.api.api import Api
from bot.storage import Config, State, Cache


class Action:
    def __init__(self):
        self.discard_pending_updates = True

    def get_name(self):
        return self.__class__.__name__

    def setup(self, api: Api, config: Config, state: State, cache: Cache):
        self.api = api
        self.config = config
        self.state = state
        self.cache = cache

    def process_update(self, update, is_pending_update):
        if is_pending_update and self.discard_pending_updates:
            return
        if update.message is not None:
            self.process_message(update.message)

    def process_message(self, message):
        pass
