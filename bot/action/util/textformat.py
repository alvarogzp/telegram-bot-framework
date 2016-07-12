from bot.api.domain import Message


class FormattedTextBuilder:
    def __init__(self, mode="HTML"):
        self.formatter = TextFormatterFactory.get_for_mode(mode)
        self.mode = mode
        self.text = ""

    def normal(self, text):
        self.text += self._escaped(text)
        return self

    def bold(self, text):
        self.text += self.formatter.bold(self._escaped(text))
        return self

    def italic(self, text):
        self.text += self.formatter.italic(self._escaped(text))
        return self

    def url(self, text, url):
        self.text += self.formatter.url(self._escaped(text), self._escaped(url))
        return self

    def code_inline(self, text):
        self.text += self.formatter.code_inline(self._escaped(text))
        return self

    def code_block(self, text):
        self.text += self.formatter.code_block(self._escaped(text))
        return self

    def build_message(self):
        return Message.create(self.text, parse_mode=self.mode)

    def _escaped(self, text):
        return self.formatter.escape(text)


class TextFormatter:
    def escape(self, text):
        return text

    def bold(self, text):
        return text

    def italic(self, text):
        return text

    def url(self, text, url):
        return text + " (" + url + ")"

    def code_inline(self, text):
        return text

    def code_block(self, text):
        return text


class HtmlTextFormatter(TextFormatter):
    def escape(self, text):
        return text.replace("<", "&lt;")\
                   .replace(">", "&gt;")\
                   .replace("&", "&amp;")\
                   .replace("\"", "&quot;")

    def bold(self, text):
        return self._surround_with_tag(text, "b")

    def italic(self, text):
        return self._surround_with_tag(text, "i")

    def url(self, text, url):
        return self._surround_with_tag(text, "a", href=url)

    def code_inline(self, text):
        return self._surround_with_tag(text, "code")

    def code_block(self, text):
        return self._surround_with_tag(text, "pre")

    @staticmethod
    def _surround_with_tag(text, tag, **attributes):
        attributes_string = ""
        for name, value in attributes.items():
            attributes_string += " " + name + "=\"" + value + "\""
        open_tag = "<" + tag + attributes_string + ">"
        close_tag = "</" + tag + ">"
        return open_tag + text + close_tag


class MarkdownTextFormatter(TextFormatter):
    def escape(self, text):
        return text.replace("[", "\\[")\
                   .replace("_", "\\_")\
                   .replace("*", "\\*")\
                   .replace("`", "\\`")

    def bold(self, text):
        return self._wrap(text, "*")

    def italic(self, text):
        return self._wrap(text, "_")

    def url(self, text, url):
        return self._wrap(text, "[", "]") + self._wrap(url, "(", ")")

    def code_inline(self, text):
        return self._wrap(text, "`")

    def code_block(self, text):
        return self._wrap(text, "```")

    @staticmethod
    def _wrap(text, wrapping_chars, close_wrapping_chars=None):
        if close_wrapping_chars is None:
            close_wrapping_chars = wrapping_chars
        return wrapping_chars + text + close_wrapping_chars


class TextFormatterFactory:
    markdown = MarkdownTextFormatter()
    html = HtmlTextFormatter()

    @classmethod
    def get_for_mode(cls, mode):
        if mode == "Markdown":
            return cls.get_markdown_formatter()
        elif mode == "HTML":
            return cls.get_html_formatter()
        else:
            raise Exception("Unknown TextFormatter requested (" + mode + ")")

    @classmethod
    def get_markdown_formatter(cls):
        return cls.markdown

    @classmethod
    def get_html_formatter(cls):
        return cls.html
