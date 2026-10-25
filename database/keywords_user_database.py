from datetime import datetime

from peewee import BigIntegerField, AutoField, DateTimeField, CharField

from database.database import database

"""Таблица с ключевыми словами пользователей для поиска ключевых слов в группах и каналах"""


def get_user_keywords_with_id(user_id: int) -> list[Keywords]:
    """Возвращает список словарей [{'id': 1, 'keyword': 'слово'}, ...] для API. (Для ВЕБ АПП)"""
    query = (
        Keywords.select(Keywords.id, Keywords.user_keyword.alias("keyword"))
        .where(Keywords.user_id == user_id)
        .dicts()
    )
    return list(query)


def add_user_keywords(user_id: int, keywords: list[str]) -> None:
    """
    Безопасно добавляет список ключевых слов в базу данных data/bot.db, пропуская дубликаты, если они есть.
    В базе данных могут быть одинаковые ключевые слова, но не у одного пользователя. Например, 1 пользователь ввел слово
    'Ищу' и у второго пользователя может быть 'Ищу', но не может быть у 1 пользователя 2 слова 'Ищу' в базе данных
    data/bot.db в таблице keywords.
    :param user_id: ID пользователя Telegram.
    :param keywords: Список ключевых слов, которые будут отслеживаться в Группе / канале Telegram.
    :return None: Нечего не возвращаем, так как записываем в базу данных
    """
    for kw in keywords:
        Keywords.get_or_create(user_id=user_id, user_keyword=kw)


def get_user_keywords(user_id: int) -> list[str]:
    """Возвращает список ключевых слов (строк) для пользователя."""
    query = Keywords.select(Keywords.user_keyword).where(Keywords.user_id == user_id)
    return [row.user_keyword for row in query]


def get_keywords_count(user_id: int):
    """
    Получение количества ключевых слов для отслеживания
    :param user_id: Telegram ID пользователя
    :return int: Количество записей (обычно 0 или 1, так как группа одна).
    """
    return Keywords.select().where(Keywords.user_id == user_id).count()


class Keywords(database.Model):
    """
    Модель для хранения ключевых слов пользователя, для последующего поиска ключевых слов в группах и каналах Telegram
    """

    id = AutoField()  # <-- добавляем первичный ключ (иначе всё пишется в одну строку)
    user_id = BigIntegerField(index=True)  # Телеграм-ID пользователя
    user_keyword = CharField()  # Поле для хранения ключевого слова для пользователя
    date_added = DateTimeField(default=datetime.now)  # Дата добавления

    class Meta:
        """Метаданные персональной таблицы ключевых слов"""

        table_name = "keywords"  # Имя таблицы с ключевыми словами
        # Уникальная связка: один пользователь не может добавить одно слово дважды,
        # но разные пользователи могут использовать одинаковые слова.
        indexes = (
            (("user_id", "user_keyword"), True),
        )


def clear_all_user_keywords(user_id: int) -> int:
    from loguru import logger
    try:
        deleted = Keywords.delete().where(Keywords.user_id == user_id).execute()
        logger.info(f'Deleted {deleted} keywords for user {user_id}')
        return deleted
    except Exception as e:
        logger.exception(e)
        return 0


def get_user_keywords_paginated(user_id: int, page: int = 0, page_size: int = 5) -> tuple:
    total = Keywords.select().where(Keywords.user_id == user_id).count()
    records = (
        Keywords.select()
        .where(Keywords.user_id == user_id)
        .order_by(Keywords.date_added.desc())
        .offset(page * page_size)
        .limit(page_size)
    )
    return list(records), total
