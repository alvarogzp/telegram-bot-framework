import gettext

from bot.action.core.action import IntermediateAction

LOCALE_DIR = "locales"
TRANSLATION_DOMAIN = "telegram-bot"

DEFAULT_LANGUAGE = "en"

CACHED_TRANSLATIONS = {}


class InternationalizationAction(IntermediateAction):
    def __init__(self):
        super().__init__()
        self.default_translation = self.__get_translation(DEFAULT_LANGUAGE)

    def process(self, event):
        lang = event.state.get_for("settings").get_value("language", DEFAULT_LANGUAGE)
        translation = self.__get_translation(lang)
        translation.install()
        event._ = translation.gettext
        self._continue(event)
        self.default_translation.install()

    @staticmethod
    def __get_translation(language):
        if language in CACHED_TRANSLATIONS:
            translation = CACHED_TRANSLATIONS[language]
        else:
            translation = gettext.translation(TRANSLATION_DOMAIN, LOCALE_DIR, languages=[language], fallback=True)
            CACHED_TRANSLATIONS[language] = translation
        return translation
