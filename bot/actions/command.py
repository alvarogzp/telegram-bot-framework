import re

from bot.actions.action import IntermediateAction


class CommandAction(IntermediateAction):
    def __init__(self, command):
        super().__init__()
        self.command = command

    def post_setup(self):
        self.command_pattern = re.compile("^/" + self.command + "(@" + self.cache.bot_info.username + "| |$)", re.IGNORECASE)

    def process_message(self, message):
        if self.command_pattern.match(message.text) is not None:
            self._continue(lambda action: action.process_message(message))
