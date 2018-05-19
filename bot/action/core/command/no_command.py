from bot.action.core.action import IntermediateAction
from bot.action.core.command import CommandAction


class NoCommandAction(IntermediateAction):
    def process(self, event):
        for entity in self.get_entities(event):
            if self.is_valid_command(entity):
                break
        else:
            self._continue(event)

    @staticmethod
    def get_entities(event):
        return CommandAction.get_entities(event)

    @staticmethod
    def is_valid_command(entity):
        return CommandAction.is_valid_command(entity)
