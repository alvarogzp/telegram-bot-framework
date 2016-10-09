import gettext

from bot.action.core.action import IntermediateAction

LOCALE_DIR = "locales"

DEFAULT_DOMAIN = "telegram-bot"
DEFAULT_LANGUAGE = "en"

CACHED_TRANSLATIONS = {}


def get_translation(domain, language):
    key = (domain, language)
    translation = CACHED_TRANSLATIONS.get(key)
    if translation is None:
        translation = gettext.translation(domain, LOCALE_DIR, languages=[language], fallback=True)
        CACHED_TRANSLATIONS[key] = translation
    return translation


class InternationalizationAction(IntermediateAction):
    def __init__(self):
        super().__init__()
        self.default_translation = get_translation(DEFAULT_DOMAIN, DEFAULT_LANGUAGE)

    def process(self, event):
        event.i18n = InternationalizationHelper
        self._continue(event)
        if InternationalizationHelper.is_enabled(event):
            InternationalizationHelper.disable(event)
            self.default_translation.install()
        event.i18n = None


class InternationalizationHelper:
    @classmethod
    def enable(cls, event, domain):
        language = cls._get_language(event)
        translation = get_translation(domain, language)
        translation.install()
        _ = event._ = translation.gettext
        return _

    @staticmethod
    def _get_language(event):
        return event.state.get_for("settings").get_value("language", DEFAULT_LANGUAGE)

    @staticmethod
    def is_enabled(event):
        return event._ is not None

    @staticmethod
    def disable(event):
        event._ = None
