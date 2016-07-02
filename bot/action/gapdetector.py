from bot.action.core.action import IntermediateAction
from bot.action.toggle import FeatureStateHandler


class BaseGapDetectorAction(IntermediateAction):
    @staticmethod
    def there_is_gap(current_update_id, expected_update_id):
        return expected_update_id is None or current_update_id != expected_update_id


class GlobalGapDetectorAction(BaseGapDetectorAction):
    def post_setup(self):
        self.gap_state = self.state.get_for("gap")

    def process(self, event):
        expected_update_id = self.get_expected_update_id()
        current_update_id = event.update.update_id
        self.gap_state.last_update_id = str(current_update_id)
        if self.there_is_gap(current_update_id, expected_update_id):
            print("Global Gap detected!")
            event.global_gap_detected = True
        self._continue(event)

    def get_expected_update_id(self):
        last_update_id = self.gap_state.last_update_id
        if last_update_id is not None:
            return int(last_update_id) + 1


class FeatureGapDetectorAction(BaseGapDetectorAction):
    def __init__(self, feature):
        super().__init__()
        self.feature = feature

    def process(self, event):
        state = FeatureStateHandler(event, self.feature).state
        current_update_id = event.update.update_id
        expected_update_id = self.get_expected_update_id(state)
        self.save_current_update_id(state, current_update_id)
        if self.there_is_gap(current_update_id, expected_update_id):
            event.feature_gap_detected = True
        self._continue(event)

    @staticmethod
    def get_expected_update_id(state):
        last_update_id = state.last_update_id
        if last_update_id is not None:
            return int(last_update_id) + 1

    @staticmethod
    def save_current_update_id(state, update_id):
        state.last_update_id = str(update_id)
