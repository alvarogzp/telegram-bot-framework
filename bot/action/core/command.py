import re

from bot.action.core.action import IntermediateAction
from bot.api.domain import Message, MessageEntityParser


class CommandAction(IntermediateAction):
    def __init__(self, command):
        super().__init__()
        self.command = command

    def post_setup(self):
        self.command_pattern = re.compile("^/" + self.command + "(@" + self.cache.bot_info.username + ")?$",
                                          re.IGNORECASE)

    def process(self, event):
        for entity in self.get_entities(event):
            if self.is_valid_command(entity):
                parser = MessageEntityParser(event.message)
                command_text = parser.get_entity_text(entity)
                if self.matches_expected_command(command_text):
                    event.command = command_text
                    event.command_args = self.get_command_args(parser, entity)
                    self._continue(event)

    @staticmethod
    def get_entities(event):
        entities = event.message.entities
        return entities if entities is not None else []

    @staticmethod
    def is_valid_command(entity):
        return entity.type == "bot_command" and entity.offset == 0

    def matches_expected_command(self, command_text):
        return self.command_pattern.match(command_text) is not None

    @staticmethod
    def get_command_args(parser, entity):
        return parser.get_text_after_entity(entity)[1:]


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
