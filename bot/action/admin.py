from bot.action.core.action import Action, IntermediateAction
from bot.api.domain import Message


class StopAction(Action):
    def process(self, event):
        raise KeyboardInterrupt()


class EvalAction(Action):
    def process(self, event):
        code = event.command_args
        result = eval(code)
        response_message = "Evaluated. Result: %s" % result
        self.api.send_message(Message.create_reply(event.message, response_message))


class AdminAction(IntermediateAction):
    def process(self, event):
        from_ = event.message.from_
        if from_ is not None and str(from_.id) == self.config.admin_user_id:
            self._continue(event)
