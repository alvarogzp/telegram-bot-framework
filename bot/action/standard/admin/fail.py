from bot.action.core.action import Action
from bot.action.util.textformat import FormattedText


class FailAction(Action):
    def process(self, event):
        api = self.api.no_async
        error = NotARealError("simulated error")
        response = FormattedText().bold("Simulating bot error...")
        args = event.command_args.split()
        if "fatal" in args:
            error = NotARealFatalError("simulated fatal error")
            response.newline().normal(" - ").bold("FATAL")
        if "async" in args:
            api = self.api.async
            response.newline().normal(" - ").bold("async")
        api.send_message(response.build_message().to_chat_replying(event.message))
        raise error


class NotARealError(Exception):
    pass


class NotARealFatalError(BaseException):
    pass
