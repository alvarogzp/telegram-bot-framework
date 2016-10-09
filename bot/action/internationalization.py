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
        i18n = InternationalizationHelper(event)
        event.i18n = i18n
        self._continue(event)
        if i18n.is_enabled():
            self.default_translation.install()


class InternationalizationHelper:
    def __init__(self, event):
        self.event = event
        self.enabled = False

    def enable(self, domain):
        language = self._get_language()
        translation = get_translation(domain, language)
        translation.install()
        _ = self.event._ = translation.gettext
        self.enabled = True
        return _

    def _get_language(self):
        return self.event.state.get_for("settings").get_value("language", DEFAULT_LANGUAGE)

    def is_enabled(self):
        return self.enabled
