from bot.actions.core.action import IntermediateAction


class TextMessageAction(IntermediateAction):
    def process(self, event):
        text = event.message.text
        if text is not None:
            event.text = text
            self._continue(event)


class MessageAction(IntermediateAction):
    def process(self, event):
        message = event.update.message
        if message is not None:
            event.message = message
            self._continue(event)


class NoPendingAction(IntermediateAction):
    def process(self, event):
        if not event.is_pending:
            self._continue(event)
