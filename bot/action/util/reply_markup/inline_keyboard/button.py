class InlineKeyboardButton:
    def __init__(self, data: dict):
        self.data = data

    @staticmethod
    def switch_inline_query(text: str, query: str = "", current_chat: bool = True):
        switch_inline_query_key = "switch_inline_query_current_chat" if current_chat else "switch_inline_query"
        return InlineKeyboardButton({
            "text": text,
            switch_inline_query_key: query
        })
