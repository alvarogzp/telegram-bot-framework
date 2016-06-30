from bot.api.api import Api
from bot.storage import Config, State, Cache
from bot.utils.dictionaryobject import DictionaryObject


class Event(DictionaryObject):
    pass


class Update(Event):
    def __init__(self, update, is_pending):
        super().__init__()
        self.update = update
        self.is_pending = is_pending


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
        self.post_setup()

    def post_setup(self):
        pass

    def process(self, event):
        pass


class ActionGroup(Action):
    def __init__(self, *actions):
        super().__init__()
        self.actions = list(actions)

    def add(self, *actions):
        self.actions.extend(actions)

    def setup(self, *args):
        self.for_each(lambda action: action.setup(*args))
        super().setup(*args)

    def process(self, event):
        self.for_each(lambda action: action.process(event._copy()))

    def for_each(self, func):
        for action in self.actions:
            func(action)


class IntermediateAction(ActionGroup):
    def __init__(self):
        super().__init__()

    def then(self, *next_actions):
        self.add(*next_actions)
        return self

    def _continue(self, event):
        super().process(event)
