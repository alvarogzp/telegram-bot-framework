class MessageSender:
    def send(self, text):
        raise NotImplementedError()


class IntermediateMessageSender(MessageSender):
    def __init__(self, sender: MessageSender):
        self.sender = sender

    def send(self, text):
        raise NotImplementedError()
