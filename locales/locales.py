from functools import cache
from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader


@cache
def get_l10n(lang: str) -> FluentLocalization:
    """
    Получить объект локализации FluentLocalization для указанного языка.

    :param lang: (str) Код языка ('ru', 'en').
    :return: (FluentLocalization) Экземпляр объекта локализации.
    """
    return FluentLocalization(
        [lang], [f"{lang}.ftl"], FluentResourceLoader(str(Path(__file__).parent))
    )


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Получить локализованную строку по ключу.

    :param key: (str) Ключ локализации (например, 'welcome_message_template').
    :param lang: (str) Код языка ('ru', 'en').
    :param kwargs: Дополнительные именованные параметры для подстановки в шаблон.
    :return: (str) Локализованная строка с подставленными значениями.
    """
    if not lang or lang not in ("ru", "en"):
        lang = "ru"
    val = get_l10n(lang).format_value(key, kwargs)
    if val == key and lang != "ru":
        val = get_l10n("ru").format_value(key, kwargs)
    return val
