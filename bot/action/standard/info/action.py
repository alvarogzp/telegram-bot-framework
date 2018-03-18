from bot.action.core.action import Action
from bot.action.standard.info.formatter.chat import ChatInfoFormatter
from bot.action.standard.info.formatter.user import UserInfoFormatter


class MeInfoAction(Action):
    def process(self, event):
        formatter = UserInfoFormatter(self.api, event.message.from_, event.chat)
        formatter.format(member_info=True)
        response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))


class ChatInfoAction(Action):
    def process(self, event):
        formatter = ChatInfoFormatter(self.api, event.chat, self.cache.bot_info, event.message.from_)
        formatter.format(full_info=True)
        response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))
