from bot.action.standard.chatsettings import ChatSettings


class OptOutManager:
    def __init__(self, global_state):
        self.state = global_state

    def should_display_message(self, event, user_id):
        return self.is_override_enabled_on_chat(event) or \
               not self.has_user_opted_out(user_id) or \
               user_id == event.message.from_.id

    @staticmethod
    def is_override_enabled_on_chat(event):
        return event.settings.get(ChatSettings.OVERRIDE_MESSAGES_OPT_OUT) == "on"

    def has_user_opted_out(self, user_id):
        return str(user_id) in self.state.opted_out_from_messages_feature.splitlines()

    def add_user(self, user_id):
        self.state.set_value("opted_out_from_messages_feature", str(user_id) + "\n", append=True)

    def remove_user(self, user_id):
        users = self.state.opted_out_from_messages_feature.splitlines()
        users.remove(str(user_id))
        self.state.opted_out_from_messages_feature = "".join((user + "\n" for user in users))
