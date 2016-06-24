

class BotInfo:
    def __init__(self, username, name):
        self.username = username
        self.name = name


class Update:
    def __init__(self, message):
        self.message = message


class Message:
    def __init__(self, chat, text):
        self.chat = chat
        self.text = text

    def reply_message(self, text):
        return Message(self.chat, text)


class Chat:
    def __init__(self, chat_id):
        self.id = chat_id
