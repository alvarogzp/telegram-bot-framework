from bot.actions.action import Action
from bot.api.domain import Message


class LeaveAction(Action):
    def process_message(self, message):
        left_chat_member = message.left_chat_member
        if left_chat_member is not None:
            if left_chat_member.id != self.cache.bot_info.id:
                reply = Message.create_reply(message, "" + left_chat_member.first_name + " was kicked by " + message._from.first_name)
                self.api.send_message(reply)
