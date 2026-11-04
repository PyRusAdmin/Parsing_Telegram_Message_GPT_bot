from datetime import datetime

from loguru import logger
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


def add_user_keywords(user_id: int, keywords: list[str], user_username: str = "", user_firstname: str = "", user_session_string: str = "") -> None:
    """
    Безопасно добавляет список ключевых слов в базу данных data/bot.db, пропуская дубликаты, если они есть.
    В базе данных могут быть одинаковые ключевые слова, но не у одного пользователя. Например, 1 пользователь ввел слово
    'Ищу' и у второго пользователя может быть 'Ищу', но не может быть у 1 пользователя 2 слова 'Ищу' в базе данных
    data/bot.db в таблице users_keywords.
    :param user_id: ID пользователя Telegram.
    :param keywords: Список ключевых слов, которые будут отслеживаться в Группе / канале Telegram.
    :param user_username: username пользователя Telegram.
    :param user_firstname: firstname пользователя Telegram.
    :param user_session_string: стринг сессия аккаунта для отслеживания ключевых слов в группе.
    :return None: Нечего не возвращаем, так как записываем в базу данных
    """
    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        Keywords.get_or_create(
            user_id=user_id,
            user_keyword=kw_clean,
            defaults={
                "user_username": user_username,
                "user_firstname": user_firstname,
                "user_session_string": user_session_string,
            }
        )


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
    Модель для хранения ключевых слов пользователя, для последующего поиска групп и каналов.
    В таблице users_keywords хранятся ключевые слова для последующего поиска групп и каналов.
    """

    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(index=True)  # id пользователя Telegram
    user_username = CharField(default="", null=True)  # username пользователя Telegram
    user_firstname = CharField(default="", null=True)  # firstname пользователя Telegram
    user_keyword = CharField()  # ключевые слова введенные пользователем Telegram
    user_session_string = CharField(default="", null=True)  # стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах. Данная сессия будет отслеживать ключевое слово в определенной группе, которую выберет пользователь бота.
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные персональной таблицы ключевых слов"""

        table_name = "users_keywords"  # Имя таблицы с ключевыми словами
        # Уникальная связка: один пользователь не может добавить одно слово дважды,
        # но разные пользователи могут использовать одинаковые слова.
        indexes = (
            (("user_id", "user_keyword"), True),
        )


def clear_all_user_keywords(user_id: int) -> int:
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
