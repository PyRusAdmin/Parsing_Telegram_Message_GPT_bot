from datetime import datetime

from loguru import logger
from peewee import (
    IntegerField, AutoField, DateTimeField, CharField
)

from database.database import database

"""
Работа с группами пользователей, которые пользователи добавили в бота (в базу данных, для дальнейшего отслеживания ключевых слов)

Работа с группами пользователя для отслеживания ключевых слов. Все данные пользователей хранится в одной таблице, 
для удобства масштабирования
"""


def get_user_channel_usernames(user_id: int) -> tuple[list[str], int]:
    """
    Получает все username каналов/групп пользователя по user_id.

    :param user_id: Telegram ID пользователя
    :return: Кортеж (список username, общее количество)
    """
    try:
        records = (Group
                   .select(Group.username)
                   .where(Group.user_id == user_id)
                   .order_by(Group.date_added.desc()))

        usernames = [row.username for row in records]
        return usernames, len(usernames)

    except Exception as e:
        logger.exception(f"Ошибка при получении каналов пользователя {user_id}: {e}")
        return [], 0


class Group(database.Model):
    """Динамическая модель для хранения технической группы пользователя"""
    id = AutoField()  # <-- добавляем первичный ключ (иначе всё пишется в одну строку)
    user_id = IntegerField()  # Телеграм-ID пользователя
    username_group = CharField(unique=True)  # Поле для хранения технической группы
    date_added = DateTimeField(default=datetime.now)  # Дата добавления

    class Meta:
        """Метаданные персональной таблицы целевой группы"""
        table_name = "group"  # Имя таблицы с группами
        # Уникальная связка: один пользователь не может добавить одну группу дважды,
        # но разные пользователи могут использовать одинаковые группы.
        indexes = (
            (("user_id", "username_group"), True),  # один пользователь не добавит один канал дважды
        )


def get_tracked_channels_count(user_id: int) -> int:
    """
    Получает количество отслеживаемых каналов для указанного пользователя.

    :param user_id: Telegram ID пользователя
    :return: Количество отслеживаемых каналов
    """
    return Group.select().where(Group.user_id == user_id).count()


def get_group_count(user_id: int):
    """
    Получение количества групп для отслеживания
    :param user_id: Telegram ID пользователя
    :return int: Количество записей (обычно 0 или 1, так как группа одна).
    """
    return Group.select().where(Group.user_id == user_id).count()


def add_user_group(user_id: int, group: list[str]) -> None:
    """
    Безопасно добавляет список групп/каналов в базу данных data/bot.db, пропуская дубликаты, если они есть.
    В базе данных могут быть одинаковые username групп, но не у одного пользователя. Например, @python_jobs
    может быть добавлен несколькими пользователями, но не может быть дважды у одного пользователя в таблице Groups.
    :param user_id: ID пользователя Telegram.
    :param group: Список username групп/каналов, которые будут отслеживаться.
    :return None: Нечего не возвращаем, так как записываем в базу данных
    """
    for gr in group:
        Group.get_or_create(user_id=user_id, username_group=gr)


def dell_group(user_id: int, username: str):
    """
    Удаляет группу из отслеживания ключевых слов.

    :param user_id: Telegram ID пользователя
    :param username: Username группы
    :return: True, если группа удалена, иначе False
    """
    try:
        (
            Group.delete().where(Group.user_id == user_id, Group.username == username).execute()
        )
        return True
    except Exception as e:
        logger.exception(e)
