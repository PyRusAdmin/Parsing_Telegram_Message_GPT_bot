# -*- coding: utf-8 -*-
from functools import cache
from pathlib import Path

from fluent.runtime import FluentLocalization, FluentResourceLoader


@cache
def get_l10n(lang: str) -> FluentLocalization:
    """
    Получить объект локализации для указанного языка.
    Кэшируется для производительности.
    """
    locales_dir = Path(__file__).parent
    loader = FluentResourceLoader(str(locales_dir))
    return FluentLocalization([lang], [f"{lang}.ftl"], loader)


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """
    Получить перевод по ключу.

    :param key: Ключ сообщения (например, 'registered-message')
    :param lang: Язык локализации (например, 'ru', 'en')
    :param kwargs: Переменные для подстановки (например, name='Иван')
    :return: Переведённая строка
    """
    l10n = get_l10n(lang)
    return l10n.format_value(key, kwargs)


def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Получить перевод по ключу (обратная совместимость).

    :param lang: Язык локализации (например, 'ru', 'en')
    :param key: Ключ сообщения (например, 'registered-message')
    :param kwargs: Переменные для подстановки (например, name='Иван')
    :return: Переведённая строка
    """
    l10n = get_l10n(lang)
    return l10n.format_value(key, kwargs)
