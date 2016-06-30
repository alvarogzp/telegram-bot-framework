from bot.actions.action import Action, IntermediateAction


class StopAction(Action):
    def process(self, event):
        raise KeyboardInterrupt()


class AdminAction(IntermediateAction):
    def process(self, event):
        from_ = event.message.from_
        if from_ is not None and str(from_.id) == self.config.get_admin_user_id():
            self._continue(event)
