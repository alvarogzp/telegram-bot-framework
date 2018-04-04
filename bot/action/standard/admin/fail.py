from bot.action.core.action import Action


class FailAction(Action):
    def process(self, event):
        if event.command_args == "fatal":
            raise NotARealFatalError("simulated fatal error")
        raise NotARealError("simulated error")


class NotARealError(Exception):
    pass


class NotARealFatalError(BaseException):
    pass
