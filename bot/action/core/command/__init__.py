from bot.action.core.action import IntermediateAction
from bot.action.core.command.parser import UnderscoredCommandParser, CommandParser
from bot.action.core.command.throttler import NoThrottler
from bot.action.core.command.throttler.shortlyrepeatedcommand import ShortlyRepeatedCommandThrottler
from bot.api.domain import MessageEntityParser


class CommandAction(IntermediateAction):
    def __init__(self, command, underscores_as_spaces=True):
        super().__init__()
        self.parser = (UnderscoredCommandParser if underscores_as_spaces else CommandParser)(command)
        self.throttler = NoThrottler()  # overridden on post_setup where we have access to api

    def post_setup(self):
        self.parser.build_command_matcher(self.cache.bot_info.username)
        self.throttler = ShortlyRepeatedCommandThrottler(self.api)

    def process(self, event):
        for entity in self.get_entities(event):
            if self.is_valid_command(entity):
                parser = MessageEntityParser(event.message)
                command_text = parser.get_entity_text(entity)
                if self.parser.matches_command(command_text):
                    event.command = self.parser.get_command_name(command_text)
                    additional_text = parser.get_text_after_entity(entity)
                    event.command_args = self.parser.get_command_args(command_text, additional_text).lstrip(" ")
                    if self.throttler.should_execute(event):
                        self._continue(event)

    @staticmethod
    def get_entities(event):
        entities = event.message.entities
        return entities if entities is not None else []

    @staticmethod
    def is_valid_command(entity):
        return entity.type == "bot_command" and entity.offset == 0


class UnderscoredCommandBuilder:
    @staticmethod
    def build_command(command, *args):
        underscored_args = "_" + "_".join(args)
        at_start = command.find("@")
        if at_start != -1:
            return command[:at_start] + underscored_args + command[at_start:]
        else:
            return command + underscored_args