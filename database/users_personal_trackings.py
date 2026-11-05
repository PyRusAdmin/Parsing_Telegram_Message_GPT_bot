from datetime import datetime

from loguru import logger  # https://github.com/Delgan/loguru
from peewee import (
    BigIntegerField, AutoField, DateTimeField, CharField, IntegerField
)

from database.database import database

"""
В таблице users_personal_trackings будут храниться данные о пользователе, бота.

Работа с таблицей users_personal_trackings должна находиться в файле users_personal_trackings.py, 
для быстрого ориентирования в проекте.

Структура users_personal_trackings: 
- id - ID записи в базе данных
- user_id - id пользователя Telegram 
- user_username - username пользователя Telegram
- user_firstname - firstname пользователя Telegram
- user_last_name - last_name пользователя Telegram
- created_group_link - Группа в которую будут отправляться сообщения
- created_group_id - Telegram-id группы которую сознал аккаунт для пересылки сообщений
- language - Язык интерфейса бота ('ru', 'en' или 'unset' при первом запуске).
- stars - количество приобретенных звезд, для дальнейших покупок в проекте
- last_free_download_at - дата последнего скачивания базы данных
- shared_account - Добавить аккаунт общий, который выдал администратор
- last_changed_at - Время последнего изменения в таблице
"""


class UsersPersonalTrackings(database.Model):
    """
    Модель для хранения данных о пользователе бота и настроек персонального отслеживания.
    Таблица users_personal_trackings (объединенная таблица User и users_personal_trackings).
    """

    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(unique=True, index=True)  # id пользователя Telegram
    user_username = CharField(max_length=255, null=True)  # username пользователя Telegram
    user_firstname = CharField(max_length=255, null=True)  # firstname пользователя Telegram
    user_last_name = CharField(max_length=255, null=True)  # last_name пользователя Telegram
    created_group_link = CharField(max_length=255, null=True)  # Группа в которую будут отправляться сообщения
    created_group_id = BigIntegerField(null=True)  # Telegram-id группы которую сознал аккаунт для пересылки сообщений
    language = CharField(max_length=10, default="ru")  # Язык интерфейса бота ('ru', 'en' или 'unset' при первом запуске)
    stars = IntegerField(default=0)  # количество приобретенных звезд, для дальнейших покупок в проекте
    last_free_download_at = DateTimeField(null=True)  # дата последнего скачивания базы данных
    shared_account = CharField(default="", null=True)  # Добавить аккаунт общий, который выдал администратор
    last_changed_at = DateTimeField(default=datetime.now)  # Время последнего изменения в таблице

    # Персональный аккаунт для отслеживания (для обратной совместимости)
    personal_account = CharField(default="", null=True)

    class Meta:
        """Метаданные таблицы пользователей и персонального отслеживания"""
        table_name = "users_personal_trackings"

    # Свойства для обратной совместимости с кодом, использовавшим поля модели User
    @property
    def username(self):
        """Алиас для username (обратная совместимость с User.username)."""
        return self.user_username

    @username.setter
    def username(self, value):
        self.user_username = value

    @property
    def first_name(self):
        """Алиас для first_name (обратная совместимость с User.first_name)."""
        return self.user_firstname

    @first_name.setter
    def first_name(self, value):
        self.user_firstname = value

    @property
    def last_name(self):
        """Алиас для last_name (обратная совместимость с User.last_name)."""
        return self.user_last_name

    @last_name.setter
    def last_name(self, value):
        self.user_last_name = value


# Алиас для обратной совместимости
PersonalTracking = UsersPersonalTrackings


def delete_account_from_user_table(user_id: int, personal_account: str) -> None:
    """
    Удаляет невалидную или отозванную сессию Telegram-аккаунта пользователя.
    :param user_id: (int) Уникальный Telegram ID пользователя — владельца сессии.
    :param personal_account: (str) Строка сессии Telethon (StringSession), подлежащая удалению.
    :return: None
    """
    query = UsersPersonalTrackings.delete().where(
        (UsersPersonalTrackings.user_id == user_id) & (UsersPersonalTrackings.personal_account == personal_account)
    )
    deleted_count = query.execute()
    logger.info(f"🗑️ Удалено {deleted_count} невалидных записей из UsersPersonalTrackings для user_id={user_id}")


def get_user_accounts(user_id: int):
    """
    Получает аккаунты пользователя из таблицы UsersPersonalTrackings.
    Возвращает список словарей для обратной совместимости.
    """
    rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    if rec and rec.personal_account:
        return [{
            'session_string': rec.personal_account,
        }]
    return []


def get_session_count(user_id: int) -> int:
    """
    Подсчитывает количество подключенных персональных аккаунтов пользователя в базе данных.

    :param user_id: (int) ID пользователя Telegram.
    :return int: Количество сессий (0, если аккаунты отсутствуют).
    """
    return UsersPersonalTrackings.select().where(
        (UsersPersonalTrackings.user_id == user_id) &
        (UsersPersonalTrackings.personal_account.is_null(False)) &
        (UsersPersonalTrackings.personal_account != '')
    ).count()


def get_group_id_with_personal_tracking(user_id: int):
    """
    Получает created_group_id (ID группы, в которую пересылаются найденные сообщения по ключевым словам)
    :param user_id: ID пользователя Telegram.
    :return Any: ID группы, в которую будут отправляться сообщения, которые были найдены по ключевым словам.
    """
    return UsersPersonalTrackings.select(UsersPersonalTrackings.created_group_id).where(
        UsersPersonalTrackings.user_id == user_id).scalar()


def write_account_to_db(session_string: str, user_id: int) -> None:
    """
    Запись аккаунта в базу данных в таблицу users_personal_trackings.
    :param session_string: Строка сессии
    :param user_id: ID пользователя Telegram
    """
    UsersPersonalTrackings.insert(
        user_id=user_id,
        personal_account=session_string,
    ).on_conflict(
        conflict_target=[UsersPersonalTrackings.user_id],
        update={
            UsersPersonalTrackings.personal_account: session_string,
            UsersPersonalTrackings.last_changed_at: datetime.now(),
        }
    ).execute()

    logger.info(f"Аккаунт успешно записан в базу данных")
