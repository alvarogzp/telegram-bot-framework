from bot.actions.action import Action, IntermediateAction


class StopAction(Action):
    def process_message(self, message):
        raise KeyboardInterrupt()


class AdminAction(IntermediateAction):
    def process_message(self, message):
        if message.from_ is not None and str(message.from_.id) == self.config.get_admin_user_id():
            self._continue(lambda action: action.process_message(message))
