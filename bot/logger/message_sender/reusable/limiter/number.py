from bot.logger.message_sender.reusable.limiter import ReusableMessageLimiter


class NumberReusableMessageLimiter(ReusableMessageLimiter):
    def __init__(self, max_uses: int = 5):
        self.max_uses = max_uses
        self.current_uses = 0

    def should_issue_new_message_pre_add(self, new_text):
        return self.current_uses >= self.max_uses

    def notify_new_message_issued(self):
        self.current_uses = 0

    def notify_about_to_send_message(self):
        self.current_uses += 1
