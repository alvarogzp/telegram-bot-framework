from bot.action.util.reply_markup.inline_keyboard.button import InlineKeyboardButton
from bot.action.util.reply_markup.inline_keyboard.layout import InlineKeyboardLayout, FixedColumnsInlineKeyboardLayout
from bot.api.domain import ApiObject


class InlineKeyboardMarkup(ApiObject):
    def __init__(self, layout: InlineKeyboardLayout):
        self.layout = layout
        self.keyboard = []
        super().__init__(inline_keyboard=self.keyboard)

    def add(self, button: InlineKeyboardButton):
        if self.layout.should_create_new_row():
            self.keyboard.append([])
        self.keyboard[-1].append(button.data)
        return self

    @staticmethod
    def with_fixed_columns(number_of_columns: int = 1):
        return InlineKeyboardMarkup(FixedColumnsInlineKeyboardLayout(number_of_columns))
