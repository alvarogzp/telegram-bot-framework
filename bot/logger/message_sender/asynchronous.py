from bot.logger.message_sender import IntermediateMessageSender, MessageSender
from bot.multithreading.work import Work
from bot.multithreading.worker import Worker


class AsynchronousMessageSender(IntermediateMessageSender):
    def __init__(self, sender: MessageSender, worker: Worker):
        super().__init__(sender)
        self.worker = worker

    def send(self, text):
        self.worker.post(Work(lambda: self.sender.send(text), "asynchronous_message_sender:send"))
