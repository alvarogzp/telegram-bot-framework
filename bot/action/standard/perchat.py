from bot.action.core.action import IntermediateAction
from bot.action.standard import chatsettings


class PerChatAction(IntermediateAction):
    def process(self, event):
        chat_id = event.chat.id
        event.config = self.config.get_for_chat_id(chat_id)
        event.state = self.state.get_for_chat_id(chat_id)
        event.cache = self.cache.get_for_chat_id(chat_id)
        event.settings = chatsettings.repository.get_for_event(event)
        self._continue(event)
