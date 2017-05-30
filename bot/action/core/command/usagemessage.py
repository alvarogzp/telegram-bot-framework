from bot.action.util.textformat import FormattedText


class CommandUsageMessage:
    @classmethod
    def get_formatted_usage_text(cls, command, args=None, description=""):
        text = FormattedText().bold("Usage").newline()
        if type(args) is list:
            text.concat(FormattedText().newline().join((cls.__get_command_with_args(command, arg) for arg in args)))
        else:
            text.concat(cls.__get_command_with_args(command, args))
        if description:
            if not isinstance(description, FormattedText):
                description = FormattedText().normal(description)
            text.newline().newline().concat(description)
        return text

    @classmethod
    def get_usage_message(cls, command, args=None, description=""):
        return cls.get_formatted_usage_text(command, args, description).build_message()

    @staticmethod
    def __get_command_with_args(command, args):
        text = command
        if args:
            text += " " + args
        return FormattedText().code_inline(text)
