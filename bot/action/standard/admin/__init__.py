import sys

from bot.action.core.action import Action, IntermediateAction
from bot.action.util.textformat import FormattedText
from bot.api.domain import Message
from bot.logger.formatter.exception import ExceptionFormatter

EXIT_STATUS_TO_HALT_BOT = 55


class RestartAction(Action):
    def process(self, event):
        response_text = "Restarting bot...\nCommands might not work while restarting."
        self.api.send_message(Message.create_reply(event.message, response_text))
        raise KeyboardInterrupt()


class EvalAction(Action):
    def process(self, event):
        code = event.command_args
        response = FormattedText()
        try:
            result = eval(code)
        except Exception as e:
            response.normal("Error: {error}").start_format().bold(error=ExceptionFormatter.format(e)).end_format()
        else:
            response.normal("Result: {result}").start_format().bold(result=result).end_format()
        self.api.send_message(response.build_message().to_chat_replying(event.message))


class HaltAction(Action):
    def process(self, event):
        response_text = "Bot stopped.\nYou need to launch it manually for it to work again."
        self.api.send_message(Message.create_reply(event.message, response_text))
        sys.exit(EXIT_STATUS_TO_HALT_BOT)


class AdminAction(IntermediateAction):
    def process(self, event):
        from_ = event.message.from_
        if from_ is not None and str(from_.id) == self.config.admin_user_id:
            self._continue(event)


class AdminActionWithErrorMessage(IntermediateAction):
    def process(self, event):
        from_ = event.message.from_
        if from_ is not None and str(from_.id) == self.config.admin_user_id:
            self._continue(event)
        else:
            error_response = "You are not allowed to perform this action (admins only)."
            self.api.send_message(Message.create_reply(event.message, error_response))
