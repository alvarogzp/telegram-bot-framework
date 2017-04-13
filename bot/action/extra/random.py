import random

from bot.action.core.action import Action
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.action.util.textformat import FormattedText


class RandomChoiceAction(Action):
    def process(self, event):
        choices = event.command_args.splitlines()
        if len(choices) == 0:
            response = self.get_random_float_between_0_and_1()
        elif len(choices) == 1:
            start, end = self.try_get_range(choices[0])
            if start is not None:
                response = self.get_random_in_range(start, end)
            else:
                response = self.get_help(event)
        else:  # len(choices) > 1
            response = self.get_random_choice(choices)
        if response.chat_id is None:
            response.to_chat(message=event.message)
        if response.reply_to_message_id is None:
            response = response.reply_to_message(message=event.message)
        self.api.send_message(response)

    @staticmethod
    def try_get_range(arg):
        split = arg.split(" ")
        if len(split) == 2 and all((e.isnumeric() or (len(e) > 1 and e[0] == "-" and e[1:].isnumeric()) for e in split)):
            return int(split[0]), int(split[1])
        return None, None

    @staticmethod
    def get_help(event):
        args = [
            "",
            "start end",
            "option1 {line-break} option2 [{line-break} option 3 ...]"
        ]
        description = (
            "Without arguments, display a random float number in the range \[0, 1).\n\n"
            "Add two integers separated by a space to get a random number in that range,"
            " including both endpoints: \[start, end].\n\n"
            "Put various options, each one in a different line to get one chosen randomly."
        )
        return CommandUsageMessage.get_usage_message(event.command, args, description)

    @staticmethod
    def get_random_float_between_0_and_1():
        chosen = random.random()
        return FormattedText().normal("Choosing a random float number between 0 and 1 (1 is not included).").newline().newline()\
            .normal("Chosen number: ").bold(chosen)\
            .build_message()

    @staticmethod
    def get_random_in_range(start, end):
        if start > end:
            return FormattedText().bold("Sorry").normal(", for this to work the first number must be ").bold("lower")\
                .normal(" than the second number.").build_message()
        chosen = random.randint(start, end)
        return FormattedText().normal("Choosing a random number between ").bold(start).normal(" and ").bold(end).normal(" (both included).").newline().newline()\
            .normal("Chosen number: ").bold(chosen)\
            .build_message()

    @staticmethod
    def get_random_choice(choices):
        number_of_elements = len(choices)
        chosen = random.choice(choices)
        return FormattedText().normal("Choosing a random element from the ones you provided.").newline().newline()\
            .normal("Number of elements: ").normal(number_of_elements).newline().newline()\
            .normal("Chosen option: ").bold(chosen)\
            .build_message()
