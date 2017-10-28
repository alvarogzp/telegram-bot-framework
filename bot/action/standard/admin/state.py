from bot.action.core.action import Action
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.util.textformat import FormattedText


class StateAction(Action):
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

    def get_current_value(self, state, key, key_to_display):
        value = self.__get_current_value(state, key)
        return FormattedText().bold("Key").normal(":").newline().code_block(key_to_display).newline().newline()\
            .bold("Value").normal(":").newline().concat(value).build_message()

    def set_new_value(self, state, key, new_value, key_to_display):
        previous_value = self.__get_current_value(state, key)
        state.set_value(key, new_value)
        current_value = self.__get_current_value(state, key)
        return FormattedText().bold("State updated!").newline().newline()\
            .bold("Key").normal(":").newline().code_block(key_to_display).newline().newline()\
            .bold("Previous value").normal(":").newline().concat(previous_value).newline().newline()\
            .bold("Current value").normal(":").newline().concat(current_value).build_message()

    @staticmethod
    def __get_current_value(state, key):
        text = FormattedText()
        current_value = state.get_value(key)
        if current_value is not None:
            text.code_block(str(current_value))
        elif state.exists_value(key):
            keys = state.get_for(key).list_keys()
            formatted_keys = "\n".join(sorted(keys))
            text.italic("Key is a node.").newline().italic("Child keys:").newline().code_block(formatted_keys)
        else:
            text.italic("Key does not exists")
        return text

    @staticmethod
    def get_usage(event):
        return CommandUsageMessage.get_usage_message(event.command, ["[get] <key>", "set <key> <value>", "del <key>"])
