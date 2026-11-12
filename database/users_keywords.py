from datetime import datetime

from peewee import BigIntegerField, AutoField, DateTimeField, CharField

from database.database import database

"""
В таблице users_keywords будут хранится ключевые слова для последующего поиска групп и каналов.

Работа с таблицей users_keywords должна находится в файле users_keywords.py, для быстрого ориентирования в проекте.

Структура users_keywords:
- id - ID записи в базе данных
- user_id - id пользователя Telegram
- user_username - username пользователя Telegram
- user_firstname - firstname пользователя Telegram
- user_keyword - ключевые слова введенные пользователем Telegram
- user_session_string - стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах.
  Данная сессия будет отслеживать ключевое слово в определенной группе, которую выберет пользователь бота.
- date_added - Дата добавления в базу данных
"""


class UsersKeywords(database.Model):
    """
    Модель для хранения ключевых слов пользователя, для последующего поиска групп и каналов.
    В таблице users_keywords хранятся ключевые слова для последующего поиска групп и каналов.
    """

    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(index=True)  # id пользователя Telegram
    user_username = CharField(default="", null=True)  # username пользователя Telegram
    user_firstname = CharField(default="", null=True)  # firstname пользователя Telegram
    user_keyword = CharField()  # ключевые слова введенные пользователем Telegram
    user_session_string = CharField(
        default="", null=True
    )  # стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные таблицы ключевых слов"""
        table_name = "users_keywords"  # Имя таблицы с ключевыми словами
        # Уникальная связка: один пользователь не может добавить одно слово дважды,
        # но разные пользователи могут использовать одинаковые слова.
        indexes = (
            (("user_id", "user_keyword"), True),
        )


def get_user_keywords_with_id(user_id: int, user_session_string: str = None) -> list:
    """
    Возвращает список словарей ключевых слов пользователя с их идентификаторами.

    :param user_id: (int) Telegram ID пользователя.
    :param user_session_string: (str | None) Фильтр по конкретной сессии аккаунта.
    :return: (list[dict]) Список словарей вида [{'id': 1, 'keyword': 'слово'}, ...].
    """
    query = UsersKeywords.select(UsersKeywords.id, UsersKeywords.user_keyword.alias("keyword")).where(
        UsersKeywords.user_id == user_id
    )
    if user_session_string:
        acc_specific = list(query.where(UsersKeywords.user_session_string == user_session_string).dicts())
        if acc_specific:
            return acc_specific
        # Fallback на общие ключевые слова
        general = list(query.where(
            (UsersKeywords.user_session_string == '') | (UsersKeywords.user_session_string.is_null())
        ).dicts())
        if general:
            return general

    return list(query.dicts())


def add_user_keywords(user_id: int, keywords: list[str], user_username: str = "", user_firstname: str = "",
                      user_session_string: str = "") -> None:
    """
    Безопасно добавляет список ключевых слов пользователя в базу данных.

    :param user_id: (int) ID пользователя в Telegram.
    :param keywords: (list[str]) Список ключевых слов для отслеживания.
    :param user_username: (str) Username пользователя в Telegram.
    :param user_firstname: (str) Имя пользователя в Telegram.
    :param user_session_string: (str) Строка сессии для отслеживания.
    """
    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        UsersKeywords.get_or_create(
            user_id=user_id,
            user_keyword=kw_clean,
            defaults={
                "user_username": user_username,
                "user_firstname": user_firstname,
                "user_session_string": user_session_string,
            }
        )


def get_user_keywords(user_id: int, user_session_string: str = None) -> list[str]:
    """
    Возвращает список ключевых слов пользователя в виде строк (с поддержкой фильтрации по аккаунту).

    :param user_id: (int) Telegram ID пользователя.
    :param user_session_string: (str | None) Фильтр по строке сессии конкретного аккаунта.
    :return: (list[str]) Список ключевых слов.
    """
    query = UsersKeywords.select(UsersKeywords.user_keyword).where(UsersKeywords.user_id == user_id)
    if user_session_string:
        acc_specific = [row.user_keyword for row in query.where(UsersKeywords.user_session_string == user_session_string)]
        if acc_specific:
            return acc_specific
        general = [row.user_keyword for row in query.where(
            (UsersKeywords.user_session_string == '') | (UsersKeywords.user_session_string.is_null())
        )]
        if general:
            return general

    return [row.user_keyword for row in query]


def get_keywords_count(user_id: int, user_session_string: str = None) -> int:
    """
    Получение количества ключевых слов пользователя для отслеживания.

    :param user_id: (int) Telegram ID пользователя.
    :param user_session_string: (str | None) Фильтр по строке сессии.
    :return: (int) Количество ключевых слов.
    """
    return len(get_user_keywords(user_id=user_id, user_session_string=user_session_string))


# def clear_all_user_keywords(user_id: int) -> int:
#     """
#     Удаляет все ключевые слова пользователя из базы данных.
#
#     :param user_id: (int) Telegram ID пользователя.
#     :return: (int) Количество удалённых записей.
#     """
#     try:
#         deleted = UsersKeywords.delete().where(UsersKeywords.user_id == user_id).execute()
#         logger.info(f'Deleted {deleted} keywords for user {user_id}')
#         return deleted
#     except Exception as e:
#         logger.exception(e)
#         return 0


def get_user_keywords_paginated(user_id: int, page: int = 0, page_size: int = 5) -> tuple:
    """
    Возвращает страницу ключевых слов пользователя с пагинацией.

    :param user_id: (int) Telegram ID пользователя.
    :param page: (int) Номер страницы (начиная с 0).
    :param page_size: (int) Количество записей на странице.
    :return: (tuple[list, int]) Кортеж из списка записей ключевых слов и общего количества.
    """
    total = UsersKeywords.select().where(UsersKeywords.user_id == user_id).count()
    records = (
        UsersKeywords.select()
        .where(UsersKeywords.user_id == user_id)
        .order_by(UsersKeywords.date_added.desc())
        .offset(page * page_size)
        .limit(page_size)
    )
    return list(records), total
