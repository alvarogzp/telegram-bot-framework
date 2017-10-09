from bot.action.core.action import Action
from bot.api.domain import Message


class GreetAction(Action):
    def process(self, event):
        message = event.message
        chat = message.chat
        new_chat_member = message.new_chat_member
        if new_chat_member is not None:
            if new_chat_member.id == self.cache.bot_info.id:
                reply = Message.create_reply(message, "Hi! I'm " + self.cache.bot_info.first_name + " and have just entered " + chat.title)
            else:
                reply = Message.create_reply(message, "Hello " + new_chat_member.first_name + ". Welcome to " + chat.title)
            self.api.send_message(reply)


class LeaveAction(Action):
    def process(self, event):
        message = event.message
        left_chat_member = message.left_chat_member
        if left_chat_member is not None:
            if left_chat_member.id != self.cache.bot_info.id:
                reply = Message.create_reply(message, "" + left_chat_member.first_name + " was kicked by " + message.from_.first_name)
                self.api.send_message(reply)
