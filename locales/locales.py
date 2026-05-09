from functools import cache
from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader


@cache
def get_l10n(lang: str) -> FluentLocalization:
    """
    Получить объект локализации для указанного языка.
    Кэшируется для производительности.
    """
    return FluentLocalization(
        [lang], [f"{lang}.ftl"], FluentResourceLoader(str(Path(__file__).parent))
    )


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Получить перевод по ключу.

    :param key: Ключ сообщения (например, 'registered-message')
    :param lang: Язык локализации (например, 'ru', 'en')
    :param kwargs: Переменные для подстановки (например, name='Иван')
    :return: Переведённая строка
    """
    return get_l10n(lang).format_value(key, kwargs)
