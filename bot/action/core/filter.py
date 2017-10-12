from bot.action.core.action import IntermediateAction


class TextMessageAction(IntermediateAction):
    def process(self, event):
        text = event.message.text
        if text is not None:
            event.text = text
            self._continue(event)


class VoiceMessageAction(IntermediateAction):
    def process(self, event):
        voice = event.message.voice
        if voice is not None:
            event.voice = voice
            self._continue(event)


class NoForwardedMessage(IntermediateAction):
    def process(self, event):
        forwarded = event.message.forward_date
        if forwarded is None:
            self._continue(event)


class EditedMessageAction(IntermediateAction):
    def process(self, event):
        edited_message = event.update.edited_message
        if edited_message is not None:
            event.message = edited_message
            event.edited_message = edited_message
            event.chat = edited_message.chat
            self._continue(event)


class MessageAction(IntermediateAction):
    def process(self, event):
        message = event.update.message
        if message is not None:
            event.message = message
            event.chat = message.chat
            self._continue(event)


class ChosenInlineResultAction(IntermediateAction):
    def process(self, event):
        chosen_inline_result = event.update.chosen_inline_result
        if chosen_inline_result is not None:
            event.chosen_result = chosen_inline_result
            self._continue(event)


class InlineQueryAction(IntermediateAction):
    def process(self, event):
        inline_query = event.update.inline_query
        if inline_query is not None:
            event.query = inline_query
            self._continue(event)


class NoPendingAction(IntermediateAction):
    def process(self, event):
        if not event.is_pending:
            self._continue(event)


class PendingAction(IntermediateAction):
    def process(self, event):
        if event.is_pending:
            self._continue(event)
