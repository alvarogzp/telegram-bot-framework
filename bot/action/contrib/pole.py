from bot.action.core.action import Action
from bot.api.domain import Message

SECONDS_IN_A_DAY = 86400
OFFSET_FROM_UTC_IN_SECONDS = 2 * 3600


class PoleAction(Action):
    def process(self, event):
        current_message_timestamp = event.message.date
        previous_message_timestamp = event.cache.last_message_timestamp
        event.cache.last_message_timestamp = current_message_timestamp
        if previous_message_timestamp is not None:
            current_message_seconds = self.get_seconds_within_day(current_message_timestamp)
            previous_message_seconds = self.get_seconds_within_day(previous_message_timestamp)

            if current_message_seconds < previous_message_seconds:  # day change: pole
                event.cache.current_day_message_count = 1
                event.cache.pole_messages = [event.message]
            else:
                current_day_message_count = event.cache.current_day_message_count
                if current_day_message_count is not None and current_day_message_count < 3:
                    current_day_message_count += 1
                    event.cache.pole_messages.append(event.message)
                    event.cache.current_day_message_count = current_day_message_count
                    if current_day_message_count == 3:
                        pole_message = event.cache.pole_messages[0]
                        subpole_message = event.cache.pole_messages[1]
                        subsubpole_message = event.cache.pole_messages[2]
                        self.api.send_message(Message.create_reply(pole_message, "pole"))
                        self.api.send_message(Message.create_reply(subpole_message, "subpole"))
                        self.api.send_message(Message.create_reply(subsubpole_message, "subsubpole"))

    @staticmethod
    def get_seconds_within_day(timestamp):
        return (timestamp + OFFSET_FROM_UTC_IN_SECONDS) % SECONDS_IN_A_DAY
