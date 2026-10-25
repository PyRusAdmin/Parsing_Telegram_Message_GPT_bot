from datetime import datetime

from loguru import logger  # https://github.com/Delgan/loguru
from peewee import (
    BigIntegerField, AutoField, DateTimeField, CharField
)

from database.database import database

"""
Работа с таблицей personal_tracking, для дальнейшего получения аккаунта, ID группы (created_group_id) в которую будут пересылаться 
найденные сообщения (целевая группа). 
"""


class PersonalTracking(database.Model):
    """Модель базы данных для хранения настроек персонального отслеживания для пользователя"""

    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(unique=True, index=True)  # Телеграм-ID пользователя
    created_group_link = CharField(null=True)  # Группа в которую будут отправляться сообщения
    created_group_id = BigIntegerField(null=True)  # Telegram-id группы которую сознал аккаунт для пересылки сообщений
    last_changed_at = DateTimeField(default=datetime.now)  # Время последнего изменения
    created_at = DateTimeField(default=datetime.now)  # Дата создания
    personal_account = CharField(default="", null=True)  # Добавить персональный аккаунт для отслеживания
    shared_account = CharField(default="", null=True)  # Добавить аккаунт общий, который выдал администратор

    class Meta:
        """Метаданные таблицы персонального отслеживания"""
        table_name = "personal_tracking"  # Название таблицы


def delete_account_from_user_table(user_id: int, personal_account: str) -> None:
    """
    Удаляет невалидную или отозванную сессию Telegram-аккаунта пользователя.

    Функция выполняет удаление записи персонального отслеживания из таблицы
    'personal_tracking' по связке идентификатора пользователя Telegram и сохранённой строки сессии (StringSession).
    Используется фоновыми проверками валидности аккаунтов для своевременной очистки базы данных
    от устаревших, заблокированных или деавторизованных сессий.

    :param user_id: (int) Уникальный Telegram ID пользователя — владельца сессии.
    :param personal_account: (str) Строка сессии Telethon (StringSession), подлежащая удалению.
    :return: None
    """
    query = PersonalTracking.delete().where(
        (PersonalTracking.user_id == user_id) & (PersonalTracking.personal_account == personal_account)
    )
    deleted_count = query.execute()
    logger.info(f"🗑️ Удалено {deleted_count} невалидных записей из PersonalTracking для user_id={user_id}")


def get_user_accounts(user_id: int):
    """
    Получает аккаунты пользователя из таблицы PersonalTracking.
    Возвращает список словарей для обратной совместимости.
    """
    rec = PersonalTracking.get_or_none(PersonalTracking.user_id == user_id)
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
    return PersonalTracking.select().where(
        (PersonalTracking.user_id == user_id) &
        (PersonalTracking.personal_account.is_null(False)) &
        (PersonalTracking.personal_account != '')
    ).count()


def get_group_id_with_personal_tracking(user_id):
    """
    Получает created_group_id (ID группы, в которую пересылаются найденные сообщения по ключевым словам)
    :param user_id: ID пользователя Telegram.
    :return Any: ID группы, в которую будут отправляться сообщения, которые были найдены по ключевым словам.
    """
    return PersonalTracking.select(PersonalTracking.created_group_id).where(
        PersonalTracking.user_id == user_id).scalar()


def write_account_to_db(session_string: str, user_id: int):
    """
    Запись аккаунта в базу данных. Если аккаунт подключает обычный пользователь, то пишет в свою таблицу с аккаунтами,
    если это администратор, то записывается в общую таблицу с общими бесплатными аккаунтами. Админа определяем по ID Telegram
    :param session_string: Строка сессии
    :param user_id: ID пользователя Telegram
    """

    PersonalTracking.insert(
        user_id=user_id,
        personal_account=session_string,
    ).on_conflict(
        conflict_target=[PersonalTracking.user_id],
        update={
            PersonalTracking.personal_account: session_string,
            PersonalTracking.last_changed_at: datetime.now(),
        }
    ).execute()

    logger.info(f"Аккаунт успешно записан в базу данных")
