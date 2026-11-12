from functools import cache
from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader

SUPPORTED_LANGUAGES = ("ru", "en", "zh", "hi", "es", "fr", "ar", "bn", "pt")

LANGUAGE_NAMES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "zh": "🇨🇳 中文",
    "hi": "🇮🇳 हिन्दी",
    "es": "🇪🇸 Español",
    "fr": "🇫🇷 Français",
    "ar": "🇸🇦 العربية",
    "bn": "🇧🇩 বাংলা",
    "pt": "🇵🇹 Português",
}


@cache
def get_l10n(lang: str) -> FluentLocalization:
    """
    Получить объект локализации FluentLocalization для указанного языка.

    :param lang: (str) Код языка ('ru', 'en', 'zh', 'hi', 'es', 'fr', 'ar', 'bn', 'pt').
    :return: (FluentLocalization) Экземпляр объекта локализации.
    """
    if lang not in SUPPORTED_LANGUAGES:
        lang = "ru"
    return FluentLocalization(
        [lang, "ru"], [f"{lang}.ftl", "ru.ftl"], FluentResourceLoader(str(Path(__file__).parent))
    )


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Получить локализованную строку по ключу с автоматическим fallback на русский язык.

    :param key: (str) Ключ локализации (например, 'welcome_message_template').
    :param lang: (str) Код языка из SUPPORTED_LANGUAGES.
    :param kwargs: Дополнительные именованные параметры для подстановки в шаблон.
    :return: (str) Локализованная строка с подставленными значениями.
    """
    if not lang or lang not in SUPPORTED_LANGUAGES:
        lang = "ru"
    val = get_l10n(lang).format_value(key, kwargs)
    if val == key and lang != "ru":
        val = get_l10n("ru").format_value(key, kwargs)
    return val
