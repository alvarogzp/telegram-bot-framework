from bot.action.core.action import Action, IntermediateAction
from bot.action.core.command.usagemessage import CommandUsageMessage
from bot.api.domain import Message

ON_VALUE = "on"
OFF_VALUE = "off"

STATUS_VALUES = {
    ON_VALUE: True,
    OFF_VALUE: False
}


class GetSetFeatureAction(Action):
    def process(self, event):
        feature, new_status = self.parse_args(event.command_args.split())
        handler = FeatureStatusHandler(event, feature)
        if feature is not None and new_status is not None:
            self.set_status(handler, new_status.lower())
        elif feature is not None:
            self.send_current_status(handler)
        else:
            self.send_usage(event)

    @staticmethod
    def parse_args(args):
        feature = None
        new_status = None
        if 0 < len(args) <= 2:
            feature = args[0]
            if len(args) > 1:
                new_status = args[1]
        return feature, new_status

    def set_status(self, handler, new_status):
        if new_status in STATUS_VALUES:
            handler.set_status(new_status)
            self.send_current_status(handler, "Done!\n")
        else:
            self.send_usage(handler.event)

    def send_current_status(self, handler, prepend=""):
        status = handler.get_status_string()
        response = prepend + "Current status of *%s*: *%s*" % (handler.feature, status.upper())
        self.api.send_message(Message.create_reply(handler.event.message, response), parse_mode="Markdown")

    def send_usage(self, event):
        usage_message = CommandUsageMessage.get_usage_message(event.command, "<feature> [on|off]")
        self.api.send_message(usage_message.to_chat_replying(event.message))


class ToggleableFeatureAction(IntermediateAction):
    def __init__(self, feature):
        super().__init__()
        self.feature = feature

    def process(self, event):
        if FeatureStatusHandler(event, self.feature).enabled:
            self._continue(event)


class FeatureStatusHandler:
    def __init__(self, event, feature):
        self.event = event
        self.feature = feature
        self.state_handler = FeatureStateHandler(event, feature)

    @property
    def enabled(self):
        return STATUS_VALUES[self.get_status_string()]

    def get_status_string(self):
        return self.state_handler.state.get_value("status", OFF_VALUE)

    def set_status(self, new_status):
        if new_status == OFF_VALUE:
            self.state_handler.delete()
        else:
            self.state_handler.state.status = new_status


class FeatureStateHandler:
    def __init__(self, event, feature):
        self.event = event
        self.feature = feature

    @property
    def state(self):
        return self.event.state.get_for("features").get_for(self.feature)

    def delete(self):
        self.event.state.get_for("features").set_value(self.feature, None)
