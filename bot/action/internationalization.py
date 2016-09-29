import gettext

from bot.action.core.action import IntermediateAction

LOCALE_DIR = "locales"
TRANSLATION_DOMAIN = "telegram-bot"

DEFAULT_LANGUAGE = "en"


class InternationalizationAction(IntermediateAction):
    def __init__(self):
        super().__init__()
        self.cached_translations = {}
        self.default_translation = self.__get_translation(DEFAULT_LANGUAGE)

    def process(self, event):
        lang = event.state.get_for("settings").get("language", DEFAULT_LANGUAGE)
        translation = self.__get_translation(lang)
        translation.install()
        event._ = translation.gettext
        self._continue(event)
        self.default_translation.install()

    def __get_translation(self, language):
        if language in self.cached_translations:
            return self.cached_translations[language]
        translation = gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR, languages=[language], fallback=True)
        self.cached_translations[language] = translation
        return translation
