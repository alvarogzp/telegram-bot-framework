class InlineKeyboardButton:
    def __init__(self, data: dict):
        self.data = data

    @staticmethod
    def create(text: str,
               url: str = None,
               callback_data: str = None,
               switch_inline_query: str = None,
               switch_inline_query_current_chat: str = None):
        data = {
            "text": text
        }
        if url is not None:
            data["url"] = url
        if callback_data is not None:
            data["callback_data"] = callback_data
        if switch_inline_query is not None:
            data["switch_inline_query"] = switch_inline_query
        if switch_inline_query_current_chat is not None:
            data["switch_inline_query_current_chat"] = switch_inline_query_current_chat
        return InlineKeyboardButton(data)

    @classmethod
    def switch_inline_query(cls, text: str, query: str = "", current_chat: bool = True):
        switch_inline_query = query if not current_chat else None
        switch_inline_query_current_chat = query if current_chat else None
        return cls.create(
            text,
            switch_inline_query=switch_inline_query,
            switch_inline_query_current_chat=switch_inline_query_current_chat
        )

    @classmethod
    def callback(cls, text: str, data: str):
        return cls.create(text, callback_data=data)
