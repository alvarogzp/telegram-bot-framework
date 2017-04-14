import re


class CommandParser:
    def __init__(self, command):
        self.command = command

    def build_command_matcher(self, bot_username):
        self.command_pattern = re.compile("^/" + self.command + "(@" + bot_username + ")?$", re.IGNORECASE)

    def matches_command(self, command):
        return self.command_pattern.match(command) is not None

    def get_command_name(self, command):
        return command

    def get_command_args(self, command, additional_text):
        return additional_text


class UnderscoredCommandParser(CommandParser):
    def __init__(self, command):
        super().__init__(command + "(_[^@]*)?")
        self.original_command = command

    def get_command_name(self, command):
        name = command[:self.__get_command_end_position()]
        at_start = command.find("@")
        if at_start != -1:
            name += command[at_start:]
        return name

    def get_command_args(self, command, additional_text):
        in_command_args = command[self.__get_command_end_position():]
        at_start = in_command_args.find("@")
        if at_start != -1:
            in_command_args = in_command_args[:at_start]
        return in_command_args.replace("_", " ") + additional_text

    def __get_command_end_position(self):
        return len(self.original_command) + 1
