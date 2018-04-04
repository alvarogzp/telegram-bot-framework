from bot.action.core.action import Action


class FailAction(Action):
    def process(self, event):
        raise NotARealError("simulated error")


class NotARealError(Exception):
    pass
