from bot.action.core.action import Action
from bot.action.standard.info.formatter.chat import ChatInfoFormatter
from bot.action.standard.info.formatter.user import UserInfoFormatter
from bot.action.util.textformat import FormattedText


class MeInfoAction(Action):
    def process(self, event):
        formatter = UserInfoFormatter(self.api, event.message.from_, event.chat)
        formatter.format(member_info=True)
        response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))


class UserInfoAction(Action):
    def process(self, event):
        message = event.message
        user = message.from_
        replied_message = message.reply_to_message
        if replied_message is not None:
            user = replied_message.from_
            command_args = event.command_args or ""
            if command_args.lower() == "forward":
                user = replied_message.forward_from
        if user is None:
            response = self._error_response()
        else:
            formatter = UserInfoFormatter(self.api, user, event.chat)
            formatter.format(member_info=True)
            response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))

    @staticmethod
    def _error_response():
        return FormattedText().bold("No user").normal(" (try with /chat)")


class ChatInfoAction(Action):
    def process(self, event):
        chat = event.chat
        replied_message = event.message.reply_to_message
        if replied_message is not None:
            chat = replied_message.forward_from_chat
        if chat is None:
            response = self._error_response()
        else:
            formatter = ChatInfoFormatter(self.api, chat, self.cache.bot_info, event.message.from_)
            formatter.format(full_info=True)
            response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))

    @staticmethod
    def _error_response():
        return FormattedText().bold("No chat").normal(" (try with /user)")
