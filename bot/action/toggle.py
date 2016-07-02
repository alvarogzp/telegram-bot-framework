from bot.action.core.action import Action
from bot.api.domain import Message

CHANGE_STATUS_VALUES = {
    "on": True,
    "off": False
}


class GetSetFeatureAction(Action):
    def process(self, event):
        feature, new_status = self.parse_args(event.command_args.split())
        if feature is not None and new_status is not None:
            self.set_status(event, feature, new_status.lower())
        elif feature is not None:
            self.send_current_status(event, feature)
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

    def set_status(self, event, feature, new_status):
        if new_status in CHANGE_STATUS_VALUES:
            self.save_status(event, feature, new_status)
            self.send_current_status(event, feature, "Done!\n")
        else:
            self.send_usage(event)

    def send_current_status(self, event, feature, prepend=""):
        status = self.get_status(event, feature)
        response = prepend + "Current status of %s: %s" % (feature, status)
        self.api.send_message(Message.create_reply(event.message, response))

    def send_usage(self, event):
        self.api.send_message(Message.create_reply(event.message, "Usage: " + event.command + " <feature> [on|off]"))

    @staticmethod
    def get_status(event, feature):
        return event.state.get_for("features").get_value(feature, "off")

    @staticmethod
    def save_status(event, feature, new_status):
        event.state.get_for("features").set_value(feature, new_status)
