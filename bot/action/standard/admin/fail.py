from bot.action.core.action import Action
from bot.action.util.textformat import FormattedText


class FailAction(Action):
    def process(self, event):
        error = NotARealError("simulated error")
        response = FormattedText().bold("Simulating bot error...")
        if event.command_args == "fatal":
            error = NotARealFatalError("simulated fatal error")
            response.newline().normal(" - ").bold("FATAL")
        self.api.send_message(response.build_message().to_chat_replying(event.message))
        raise error


class NotARealError(Exception):
    pass


class NotARealFatalError(BaseException):
    pass
