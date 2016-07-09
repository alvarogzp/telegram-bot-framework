from bot.action.core.action import Action

SECONDS_IN_A_DAY = 86400
OFFSET_FROM_UTC_IN_SECONDS = 2 * 3600


class PoleAction(Action):
    def process(self, event):
        state = event.state.get_for("pole")
        if event.global_gap_detected:  # reset everything
            state.last_message_timestamp = None
            state.current_day_message_count = None

        current_message_timestamp = event.message.date
        previous_message_timestamp = state.last_message_timestamp
        state.last_message_timestamp = str(current_message_timestamp)
        if previous_message_timestamp is not None:
            current_message_day = self.get_day_number(current_message_timestamp)
            previous_message_day = self.get_day_number(int(previous_message_timestamp))

            if current_message_day != previous_message_day:  # day change: pole
                self.build_pole_and_add_to(state, "poles", event.message)
                state.current_day_message_count = str(1)
            else:
                current_day_message_count = state.current_day_message_count
                if current_day_message_count is not None:
                    current_day_message_count = int(current_day_message_count)
                    if current_day_message_count < 3:
                        current_day_message_count += 1
                        if current_day_message_count == 2:
                            self.build_pole_and_add_to(state, "subpoles", event.message)
                            state.current_day_message_count = str(current_day_message_count)
                        elif current_day_message_count == 3:
                            self.build_pole_and_add_to(state, "subsubpoles", event.message)
                            state.current_day_message_count = None

    def build_pole_and_add_to(self, state, key, message):
        pole = self.build_pole_from_message(message)
        self.add_pole_to(state, key, pole)

    @staticmethod
    def add_pole_to(state, key, pole):
        state.set_value(key, pole.serialize(), append=True)

    @staticmethod
    def build_pole_from_message(message):
        user_id = message.from_.id if message.from_ is not None else "-"
        return Pole(user_id, message.date, message.message_id)

    @staticmethod
    def get_day_number(timestamp):
        return (timestamp + OFFSET_FROM_UTC_IN_SECONDS) // SECONDS_IN_A_DAY


class Pole:
    def __init__(self, user_id, date, message_id):
        self.user_id = user_id
        self.date = date
        self.message_id = message_id

    def serialize(self):
        return "%s %s %s\n" % (self.user_id, self.date, self.message_id)
