from bot.action.core.action import Action
from bot.action.core.command import CommandUsageMessage
from bot.action.util.textformat import FormattedText


class ConfigAction(Action):
    def process(self, event):
        action, key, new_value = self.parse_args(event.command_args.split(" "))
        if key is not None:
            parsed_key, state = self.get_parsed_key_and_state(key, event)
            if action == "get":
                response = self.get_current_value(state, parsed_key, key)
            elif action == "set":
                response = self.set_new_value(state, parsed_key, new_value, key)
            elif action == "del":
                response = self.set_new_value(state, parsed_key, None, key)
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
        elif len(args) > 1:
            action = args[0]
            key = args[1]
            new_value = " ".join(args[2:])
        return action, key, new_value

    def get_parsed_key_and_state(self, key, event):
        if key.startswith("/"):
            state = self.state
            key = key[1:]
        else:
            state = event.state
        return key, state

    @staticmethod
    def get_current_value(state, key, key_to_display):
        current_value = state.get_value(key)
        return FormattedText().bold("Key").normal(":").newline().code_block(key_to_display).newline().newline()\
            .bold("Value").normal(":").newline().code_block(str(current_value)).build_message()

    @staticmethod
    def set_new_value(state, key, new_value, key_to_display):
        previous_value = state.get_value(key)
        state.set_value(key, new_value)
        current_value = state.get_value(key)
        return FormattedText().bold("Config updated!").newline().newline()\
            .bold("Key").normal(":").newline().code_block(key_to_display).newline().newline()\
            .bold("Previous value").normal(":").newline().code_block(str(previous_value)).newline().newline()\
            .bold("Current value").normal(":").newline().code_block(str(current_value)).build_message()

    @staticmethod
    def get_usage(event):
        return CommandUsageMessage.get_usage_message(event.command, ["[get] <key>", "set <key> <value>", "del <key>"])
