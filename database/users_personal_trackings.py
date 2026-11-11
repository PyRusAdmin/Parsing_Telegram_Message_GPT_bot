from datetime import datetime

from loguru import logger  # https://github.com/Delgan/loguru
from peewee import BigIntegerField, AutoField, DateTimeField, CharField, IntegerField

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
    language = CharField(max_length=10,
                         default="ru")  # Язык интерфейса бота ('ru', 'en' или 'unset' при первом запуске)
    stars = IntegerField(default=0)  # количество приобретенных звезд, для дальнейших покупок в проекте
    last_free_download_at = DateTimeField(null=True)  # дата последнего скачивания базы данных
    shared_account = CharField(default="", null=True)  # Добавить аккаунт общий, который выдал администратор
    last_changed_at = DateTimeField(default=datetime.now)  # Время последнего изменения в таблице

    # Персональный аккаунт для отслеживания (для обратной совместимости)
    personal_account = CharField(default="", null=True)

    @property
    def username(self) -> str:
        return self.user_username or ""

    @property
    def first_name(self) -> str:
        return self.user_firstname or ""

    @property
    def last_name(self) -> str:
        return self.user_last_name or ""

    class Meta:
        """Метаданные таблицы пользователей и персонального отслеживания"""
        table_name = "users_personal_trackings"


def delete_account_from_user_table(user_id: int, personal_account: str) -> None:
    """
    Удаляет невалидную или отозванную сессию Telegram-аккаунта пользователя.

    :param user_id: (int) Уникальный Telegram ID пользователя — владельца сессии.
    :param personal_account: (str) Строка сессии Telethon (StringSession), подлежащая удалению.
    """
    query = UsersPersonalTrackings.delete().where(
        (UsersPersonalTrackings.user_id == user_id) & (UsersPersonalTrackings.personal_account == personal_account)
    )
    deleted_count = query.execute()
    logger.info(f"🗑️ Удалено {deleted_count} невалидных записей из UsersPersonalTrackings для user_id={user_id}")


def get_user_accounts(user_id: int):
    """
    Получает аккаунты пользователя из таблицы users_personal_trackings.

    :param user_id: (int) Telegram ID пользователя.
    :return: (list[dict]) Список словарей с данными сессий пользователя.
    """
    rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    if rec:
        if rec.personal_account:
            return [{
                'session_string': rec.personal_account,
                'is_shared': False
            }]
        elif rec.shared_account:
            return [{
                'session_string': rec.shared_account,
                'is_shared': True
            }]
    return []


def get_session_count(user_id: int) -> int:
    """
    Подсчитывает количество подключенных персональных или свободных аккаунтов пользователя.

    :param user_id: (int) Telegram ID пользователя.
    :return: (int) Количество сессий (0, если аккаунты отсутствуют).
    """
    return UsersPersonalTrackings.select().where(
        (UsersPersonalTrackings.user_id == user_id) &
        (
                ((UsersPersonalTrackings.personal_account.is_null(False)) & (
                        UsersPersonalTrackings.personal_account != '')) |
                ((UsersPersonalTrackings.shared_account.is_null(False)) & (UsersPersonalTrackings.shared_account != ''))
        )
    ).count()


def get_group_id_with_personal_tracking(user_id: int):
    """
    Получает ID группы, созданной пользователем для пересылки найденных сообщений.

    :param user_id: (int) Telegram ID пользователя.
    :return: (int | None) Telegram ID группы для уведомлений или None.
    """
    return UsersPersonalTrackings.select(UsersPersonalTrackings.created_group_id).where(
        UsersPersonalTrackings.user_id == user_id).scalar()


def write_account_to_db(session_string: str, user_id: int) -> None:
    """
    Запись персонального аккаунта в базу данных в таблицу users_personal_trackings.
    Свободный аккаунт при этом очищается.

    :param session_string: (str) Строка сессии Telethon.
    :param user_id: (int) Telegram ID пользователя.
    """
    UsersPersonalTrackings.insert(
        user_id=user_id,
        personal_account=session_string,
        shared_account="",
    ).on_conflict(
        conflict_target=[UsersPersonalTrackings.user_id],
        update={
            UsersPersonalTrackings.personal_account: session_string,
            UsersPersonalTrackings.shared_account: "",
            UsersPersonalTrackings.last_changed_at: datetime.now(),
        }
    ).execute()

    logger.info(f"Личный аккаунт успешно записан в базу данных для user_id={user_id}")


def set_user_shared_account(user_id: int, session_string: str) -> None:
    """
    Записывает свободный аккаунт от администратора в таблицу users_personal_trackings.
    Личный аккаунт при этом очищается.

    :param user_id: (int) Telegram ID пользователя.
    :param session_string: (str) Строка сессии Telethon свободного аккаунта.
    """
    UsersPersonalTrackings.insert(
        user_id=user_id,
        shared_account=session_string,
        personal_account="",
    ).on_conflict(
        conflict_target=[UsersPersonalTrackings.user_id],
        update={
            UsersPersonalTrackings.shared_account: session_string,
            UsersPersonalTrackings.personal_account: "",
            UsersPersonalTrackings.last_changed_at: datetime.now(),
        }
    ).execute()

    logger.info(f"Свободный аккаунт администратора успешно назначен пользователю {user_id}")


def clear_user_account(user_id: int) -> bool:
    """
    Очищает привязанный аккаунт пользователя (как личный, так и свободный).

    :param user_id: (int) Telegram ID пользователя.
    :return: (bool) True если запись обновлена.
    """
    updated = UsersPersonalTrackings.update(
        personal_account="",
        shared_account="",
        last_changed_at=datetime.now()
    ).where(UsersPersonalTrackings.user_id == user_id).execute()
    logger.info(f"Аккаунт пользователя {user_id} очищен (personal и shared).")
    return bool(updated)
