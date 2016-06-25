from bot.actions.action import IntermediateAction


class TextMessageAction(IntermediateAction):
    def process_message(self, message):
        if message.text is not None:
            self._continue(lambda action: action.process_message(message))


class MessageAction(IntermediateAction):
    def process_update(self, update, is_pending_update):
        if update.message is not None:
            self._continue(lambda action: action.process_message(update.message))


class NoPendingAction(IntermediateAction):
    def process_update(self, update, is_pending_update):
        if not is_pending_update:
            self._continue(lambda action: action.process_update(update, is_pending_update))
