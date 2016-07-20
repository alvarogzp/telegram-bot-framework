import re

from bot.action.core.action import IntermediateAction
from bot.api.domain import Message, MessageEntityParser


class CommandAction(IntermediateAction):
    def __init__(self, command, underscores_as_spaces=True):
        super().__init__()
        self.parser = (UnderscoredCommandParser if underscores_as_spaces else CommandParser)(command)

    def post_setup(self):
        self.parser.build_command_matcher(self.cache.bot_info.username)

    def process(self, event):
        for entity in self.get_entities(event):
            if self.is_valid_command(entity):
                parser = MessageEntityParser(event.message)
                command_text = parser.get_entity_text(entity)
                if self.parser.matches_command(command_text):
                    event.command = self.parser.get_command_name(command_text)
                    additional_text = parser.get_text_after_entity(entity)
                    event.command_args = self.parser.get_command_args(command_text, additional_text).lstrip()
                    self._continue(event)

    @staticmethod
    def get_entities(event):
        entities = event.message.entities
        return entities if entities is not None else []

    @staticmethod
    def is_valid_command(entity):
        return entity.type == "bot_command" and entity.offset == 0

    def get_command_args(self, parser, entity, command_text):
        return parser.get_text_after_entity(entity)


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
        in_command_args = command[self.__get_command_end_position()+1:]
        at_start = in_command_args.find("@")
        if at_start != -1:
            in_command_args = in_command_args[:at_start]
        return in_command_args.replace("_", " ") + additional_text

    def __get_command_end_position(self):
        return len(self.original_command) + 1


class CommandUsageMessage:
    @classmethod
    def get_usage_message(cls, command, args=None, description=""):
        message = "*Usage*\n"
        if type(args) is list:
            message += "\n".join((cls.__get_command_with_args(command, arg) for arg in args))
        else:
            message += cls.__get_command_with_args(command, args)
        if description:
            message += "\n\n" + description
        return Message.create(message, parse_mode="Markdown")

    @staticmethod
    def __get_command_with_args(command, args):
        text = "`" + command
        if args:
            text += " " + args
        text += "`"
        return text


class UnderscoredCommandBuilder:
    @staticmethod
    def build_command(command, *args):
        underscored_args = "_" + "_".join(args)
        at_start = command.find("@")
        if at_start != -1:
            return command[:at_start] + underscored_args + command[at_start:]
        else:
            return command + underscored_args
