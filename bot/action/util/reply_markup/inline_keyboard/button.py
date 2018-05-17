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

    @staticmethod
    def switch_inline_query(text: str, query: str = "", current_chat: bool = True):
        switch_inline_query_key = "switch_inline_query_current_chat" if current_chat else "switch_inline_query"
        return InlineKeyboardButton({
            "text": text,
            switch_inline_query_key: query
        })
