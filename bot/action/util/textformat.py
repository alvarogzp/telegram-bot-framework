from bot.api.domain import Message


class FormattedText:
    def __init__(self, mode="HTML"):
        self.formatter = TextFormatterFactory.get_for_mode(mode)
        self.mode = mode
        self.text = ""

    def raw(self, text: str):
        self.text += text
        return self

    def normal(self, text: str):
        self.text += self._escaped(text)
        return self

    def bold(self, text: str):
        self.text += self.formatter.bold(self._escaped(text))
        return self

    def italic(self, text: str):
        self.text += self.formatter.italic(self._escaped(text))
        return self

    def url(self, text: str, url: str):
        self.text += self.formatter.url(self._escaped(text), self._escaped(url))
        return self

    def code_inline(self, text: str):
        self.text += self.formatter.code_inline(self._escaped_code(text))
        return self

    def code_block(self, text: str):
        self.text += self.formatter.code_block(self._escaped_code(text))
        return self

    def newline(self):
        self.text += "\n"
        return self

    def concat(self, formatted_text):
        """:type formatted_text: FormattedText"""
        assert self._is_compatible(formatted_text), "Cannot concat text with different modes"
        self.text += formatted_text.text
        return self

    def join(self, formatted_texts):
        """:type formatted_texts: list[FormattedText]"""
        formatted_texts = list(formatted_texts)  # so that after the first iteration elements are not lost if generator
        for formatted_text in formatted_texts:
            assert self._is_compatible(formatted_text), "Cannot join text with different modes"
        self.text = self.text.join((formatted_text.text for formatted_text in formatted_texts))
        return self

    def _is_compatible(self, formatted_text):
        """:type formatted_text: FormattedText"""
        return self.mode == formatted_text.mode

    def build_message(self):
        return Message.create(self.text, parse_mode=self.mode)

    def _escaped(self, text):
        return self.__escaped(text, self.formatter.escape)

    def _escaped_code(self, text):
        return self.__escaped(text, self.formatter.escape_code)

    @staticmethod
    def __escaped(text, escape_func):
        if type(text) is not str:
            text = str(text)
        return escape_func(text)

    def start_format(self):
        return FormattedTextStringFormat(self)

    def length(self):
        return len(self.text)

    def clear(self):
        self.text = ""


class FormattedTextFactory:
    @staticmethod
    def get_new_markdown():
        return FormattedText(mode="Markdown")

    @staticmethod
    def get_new_html():
        return FormattedText(mode="HTML")


class TextFormatter:
    def escape(self, text):
        return text

    def escape_code(self, text):
        """Override if code uses different escape rules"""
        return self.escape(text)

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
        return text.replace("&", "&amp;")\
                   .replace("<", "&lt;")\
                   .replace(">", "&gt;")\
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

    def escape_code(self, text):
        return text

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


class FormattedTextStringFormat:
    def __init__(self, formatted_text: FormattedText):
        self.formatted_text = formatted_text
        self.formatter = formatted_text.formatter
        self.format_args = []
        self.format_kwargs = {}

    def normal(self, *args, **kwargs):
        self._add(lambda x: x, args, kwargs)
        return self

    def bold(self, *args, **kwargs):
        self._add(self.formatter.bold, args, kwargs)
        return self

    def italic(self, *args, **kwargs):
        self._add(self.formatter.italic, args, kwargs)
        return self

    def url(self, text: str, url: str, name=None):
        text = self.formatter.url(self._escaped(text), self._escaped(url))
        if name is None:
            self.format_args.append(text)
        else:
            self.format_kwargs[name] = text
        return self

    def code_inline(self, *args, **kwargs):
        self._add(self.formatter.code_inline, args, kwargs)
        return self

    def code_block(self, *args, **kwargs):
        self._add(self.formatter.code_block, args, kwargs)
        return self

    def _add(self, func_to_apply, args, kwargs):
        self.format_args.extend((func_to_apply(self._escaped(arg)) for arg in args))
        for kwarg in kwargs:
            self.format_kwargs[kwarg] = func_to_apply(self._escaped(kwargs[kwarg]))

    def _escaped(self, text):
        return self.formatted_text._escaped(text)

    def concat(self, *args, **kwargs):
        """
        :type args: FormattedText
        :type kwargs: FormattedText
        """
        for arg in args:
            assert self.formatted_text._is_compatible(arg), "Cannot concat text with different modes"
            self.format_args.append(arg.text)
        for kwarg in kwargs:
            value = kwargs[kwarg]
            assert self.formatted_text._is_compatible(value), "Cannot concat text with different modes"
            self.format_kwargs[kwarg] = value.text
        return self

    def end_format(self):
        self.formatted_text.text = self.formatted_text.text.format(*self.format_args, **self.format_kwargs)
        return self.formatted_text
