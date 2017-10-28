from bot.action.core.action import IntermediateAction
from bot.api.domain import Message


class GroupAdminAction(IntermediateAction):
    def process(self, event):
        chat = event.message.chat
        if chat.type == "private":
            # lets consider private chat members are admins :)
            self._continue(event)
        else:
            user = event.message.from_
            if user is not None:
                chat_member = self.api.getChatMember(chat_id=chat.id, user_id=user.id)
                if chat_member.status in ("creator", "administrator"):
                    self._continue(event)
                else:
                    error_response = "Sorry, this command is only available to group admins."
                    self.api.send_message(Message.create_reply(event.message, error_response))
