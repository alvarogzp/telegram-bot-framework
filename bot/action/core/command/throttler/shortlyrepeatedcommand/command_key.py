class CommandKey:
    def __init__(self, event, *funcs_to_apply: callable):
        self.key = tuple((func(event) for func in funcs_to_apply))

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    # helper methods for subclasses

    @staticmethod
    def _chat_id(event):
        return event.chat.id

    @staticmethod
    def _user_id(event):
        return event.message.from_ and event.message.from_.id

    @staticmethod
    def _command(event):
        return event.command

    @staticmethod
    def _command_args(event):
        return event.command_args

    @staticmethod
    def _reply_to_message_id(event):
        return event.message.reply_to_message and event.message.reply_to_message.message_id


class NonPersonalCommandKey(CommandKey):
    def __init__(self, event):
        super().__init__(
            event,
            self._chat_id,
            self._command,
            self._command_args,
            self._reply_to_message_id
        )


class PersonalCommandKey(CommandKey):
    def __init__(self, event):
        super().__init__(
            event,
            self._chat_id,
            self._user_id,
            self._command,
            self._command_args,
            self._reply_to_message_id
        )


class CommandKeyFactory:
    def __init__(self):
        self.personal_commands = []

    def add_personal_command(self, command: str):
        self.personal_commands.append("/" + command.lower())

    def get_command_key(self, event):
        if self._is_personal(event.command):
            return PersonalCommandKey(event)
        return NonPersonalCommandKey(event)

    def _is_personal(self, command: str):
        return command.lower() in self.personal_commands
