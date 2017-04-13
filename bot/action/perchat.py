from bot.action.chatsettings import ChatSettings
from bot.action.core.action import IntermediateAction


class PerChatAction(IntermediateAction):
    def process(self, event):
        chat_id = event.chat.id
        event.config = self.config.get_for_chat_id(chat_id)
        event.state = self.state.get_for_chat_id(chat_id)
        event.cache = self.cache.get_for_chat_id(chat_id)
        event.settings = ChatSettings(event)
        self._continue(event)
