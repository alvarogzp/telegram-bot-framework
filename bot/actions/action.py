from bot.api.api import Api
from bot.storage import Config, State, Cache


class Action:
    def __init__(self):
        pass

    def get_name(self):
        return self.__class__.__name__

    def setup(self, api: Api, config: Config, state: State, cache: Cache):
        self.api = api
        self.config = config
        self.state = state
        self.cache = cache

    def process_update(self, update, is_pending_update):
        pass


class IntermediateAction(Action):
    def __init__(self):
        super().__init__()
        self.next_actions = []

    def then(self, *next_actions):
        self.next_actions = next_actions
        return self

    def setup(self, *args):
        super().setup(*args)
        self._continue(lambda action: action.setup(*args))

    def _continue(self, func):
        for action in self.next_actions:
            func(action)
