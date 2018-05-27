from bot.action.core.action import Action
from bot.action.standard.info.formatter.chat import ChatInfoFormatter
from bot.action.standard.info.formatter.user import UserInfoFormatter
from bot.action.util.textformat import FormattedText


class UserInfoAction(Action):
    def __init__(self, always_sender: bool = False, member_info: bool = True):
        super().__init__()
        self.always_sender = always_sender
        self.member_info = member_info

    def process(self, event):
        user = self._get_user(event)
        if user is None:
            response = self._error_response()
        else:
            formatter = UserInfoFormatter(self.api.no_async, user, event.chat)
            formatter.format(member_info=self.member_info)
            response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))

    def _get_user(self, event):
        message = event.message
        user = message.from_
        if not self.always_sender:
            replied_message = message.reply_to_message
            if replied_message is not None:
                user = replied_message.from_
            if self._should_use_reply_forward_user(event):
                # shorthand for: replied_message.forward_from if replied_message is not None else None
                # the check is needed because this is outside of the previous "if replied_message is not None" block
                # because we want to take "forward" arg into account even if no replied_message (to display the
                # error response)
                user = replied_message and replied_message.forward_from
        return user

    def _should_use_reply_forward_user(self, event):
        return self._args_equals_to(event, "forward") or self._replied_sender_matches_command_sender(event.message)

    @staticmethod
    def _args_equals_to(event, expected_args: str):
        command_args = event.command_args or ""
        return command_args.lower() == expected_args.lower()

    @staticmethod
    def _replied_sender_matches_command_sender(message):
        replied_message = message.reply_to_message
        if replied_message is not None:
            command_from = message.from_
            replied_from = replied_message.from_
            if command_from is not None and replied_from is not None and command_from.id == replied_from.id:
                return True
        return False

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
            formatter = ChatInfoFormatter(self.api.no_async, chat, self.cache.bot_info, event.message.from_)
            formatter.format(full_info=True)
            response = formatter.get_formatted()
        self.api.send_message(response.build_message().to_chat_replying(event.message))

    @staticmethod
    def _error_response():
        return FormattedText().bold("No chat").normal(" (try with /user)")
