from bot.logger.message_sender.message_builder import MessageBuilder


class ReusableMessageLimiter:
    def should_issue_new_message_pre_add(self, new_text):
        return False

    def should_issue_new_message_post_add(self, builder: MessageBuilder):
        return False

    def notify_new_message_issued(self):
        pass

    def notify_about_to_send_message(self):
        pass
