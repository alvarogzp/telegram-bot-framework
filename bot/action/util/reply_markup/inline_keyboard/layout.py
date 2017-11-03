class InlineKeyboardLayout:
    def should_create_new_row(self):
        raise NotImplementedError()


class FixedColumnsInlineKeyboardLayout(InlineKeyboardLayout):
    def __init__(self, number_of_columns: int = 1):
        self.number_of_columns = number_of_columns
        self.current_column_index = 0

    def should_create_new_row(self):
        current_column_index = self.current_column_index
        self.current_column_index += 1
        if self.current_column_index >= self.number_of_columns:
            self.current_column_index = 0
        return current_column_index == 0
