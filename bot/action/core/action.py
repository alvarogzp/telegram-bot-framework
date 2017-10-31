from bot.api.api import Api
from bot.multithreading.scheduler import SchedulerApi
from bot.storage import Config, State, Cache


class Action:
    def __init__(self):
        pass

    def get_name(self):
        return self.__class__.__name__

    def setup(self, api: Api, config: Config, state: State, cache: Cache, scheduler: SchedulerApi):
        self.api = api
        self.config = config
        self.state = state
        self.cache = cache
        self.scheduler = scheduler
        self.post_setup()

    def post_setup(self):
        pass

    def process(self, event):
        pass

    def pre_shutdown(self):
        pass

    def shutdown(self):
        self.pre_shutdown()


class ActionGroup(Action):
    def __init__(self, *actions):
        super().__init__()
        self.actions = list(actions)

    def add(self, *actions):
        self.actions.extend(actions)

    def setup(self, *args):
        super().setup(*args)
        self.for_each(lambda action: action.setup(*args))

    def process(self, event):
        self.for_each(lambda action: action.process(event._copy()))

    def shutdown(self):
        self.for_each(lambda action: action.shutdown())
        super().shutdown()

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
