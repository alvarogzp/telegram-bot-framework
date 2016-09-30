from bot.action.core.action import Action
from bot.action.core.command import CommandUsageMessage
from bot.action.util.textformat import FormattedText


class GroupSettingsAction(Action):
    def process(self, event):
        action, key, new_value = self.parse_args(event.command_args.split(" "))
        if key is not None and self.is_valid_key(key):
            state = event.state.get_for("settings")
            if action == "list":
                response = self.list_settings(state)
            elif action == "get":
                response = self.get_current_value(state, key)
            elif action == "set":
                response = self.set_new_value(state, key, new_value)
            elif action == "del":
                response = self.set_new_value(state, key, None)
            else:
                response = self.get_usage(event)
        else:
            response = self.get_usage(event)
        response.to_chat_replying(event.message)
        self.api.send_message(response)

    @staticmethod
    def parse_args(args):
        action = "get"
        key = None
        new_value = None
        if len(args) == 1 and args[0] != "":
            key = args[0]
            if key == "list":
                action = key
        elif len(args) > 1:
            action = args[0]
            key = args[1]
            new_value = " ".join(args[2:])
        return action, key, new_value

    @staticmethod
    def is_valid_key(key):
        return key.replace("_", "").isalpha()

    @staticmethod
    def list_settings(state):
        keys = state.list_keys()
        if len(keys) == 0:
            return FormattedText().normal("No setting has been modified on this chat.").build_message()
        formatted_keys = "\n".join(sorted(keys))
        return FormattedText().normal("List of modified settings on this chat:").newline()\
            .code_block(formatted_keys)\
            .build_message()

    def get_current_value(self, state, key):
        value = self.__get_current_value(state, key)
        return FormattedText().bold("Setting").normal(":").newline().code_block(key).newline().newline()\
            .bold("Value").normal(":").newline().concat(value)\
            .build_message()

    def set_new_value(self, state, key, new_value):
        previous_value = self.__get_current_value(state, key)
        state.set_value(key, new_value)
        current_value = self.__get_current_value(state, key)
        return FormattedText().bold("Setting updated!").newline().newline()\
            .bold("Name").normal(":").newline().code_block(key).newline().newline()\
            .bold("Previous value").normal(":").newline().concat(previous_value).newline().newline()\
            .bold("Current value").normal(":").newline().concat(current_value)\
            .build_message()

    @staticmethod
    def __get_current_value(state, key):
        text = FormattedText()
        current_value = state.get_value(key)
        if current_value is not None:
            text.code_block(current_value)
        else:
            text.italic("Not set (default value is used)")
        return text

    @staticmethod
    def get_usage(event):
        return CommandUsageMessage.get_usage_message(event.command, ["list", "[get] <key>", "set <key> <value>", "del <key>"])
