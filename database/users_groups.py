from datetime import datetime

from loguru import logger  # https://github.com/Delgan/loguru
from peewee import AutoField, DateTimeField, CharField, BigIntegerField

from database.database import database
from keyboards.keyboards import menu_launch_tracking_keyboard
from locales.locales import t

"""
Работа с группами пользователей, которые пользователи добавили в бота (в базу данных, для дальнейшего отслеживания ключевых слов)

Работа с группами пользователя для отслеживания ключевых слов. Все данные пользователей хранится в одной таблице, 
для удобства масштабирования
"""


class UsersGroups(database.Model):
    """
    Модель для хранения групп для отслеживания ключевых слов.
    В таблице users_groups хранятся группы для отслеживания ключевых слов.
    """

    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(index=True)  # id пользователя Telegram
    user_username = CharField(default="", null=True)  # username пользователя Telegram
    user_firstname = CharField(default="", null=True)  # firstname пользователя Telegram
    username_group = CharField(default="", null=True)  # username группы в которой будет отслеживание ключевых слов
    id_group = BigIntegerField(null=True,
                               index=True)  # id группы в которой будет отслеживаться ключевые слова (для отслеживания закрытых групп. аккаунт будет на них подписан)
    name_group = CharField(default="", null=True)  # название группы в которой будет отслеживаться ключевые слова
    user_session_string = CharField(default="",
                                    null=True)  # стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах. Данная сессия будет отслеживать ключевое слово в определенной группе, которую выберет пользователь бота.
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные персональной таблицы целевой группы"""
        table_name = "users_groups"  # Имя таблицы с группами
        # Уникальная связка: один пользователь не может добавить одну группу дважды,
        # но разные пользователи могут использовать одинаковые группы.
        indexes = (
            (("user_id", "username_group"), True),  # один пользователь не добавит один канал дважды
        )


# Алиас для обратной совместимости
Group = UsersGroups


def get_user_channel_usernames(user_id: int) -> tuple[list[str], int]:
    """
    Получает все username каналов/групп пользователя по user_id.

    :param user_id: Telegram ID пользователя
    :return: Кортеж (список username, общее количество)
    """
    records = (UsersGroups
               .select(UsersGroups.username_group)
               .where(UsersGroups.user_id == user_id)
               .order_by(UsersGroups.date_added.desc()))

    usernames = [row.username_group for row in records]
    return usernames, len(usernames)


def get_group_count(user_id: int):
    """
    Получение количества групп для отслеживания
    :param user_id: Telegram ID пользователя
    :return int: Количество записей (обычно 0 или 1, так как группа одна).
    """
    return UsersGroups.select().where(UsersGroups.user_id == user_id).count()


def add_user_group(user_id: int, group: list[str], user_username: str = "", user_firstname: str = "",
                   id_group: int | None = None, name_group: str = "", user_session_string: str = "") -> None:
    """
    Безопасно добавляет список групп/каналов в базу данных data/bot.db, пропуская дубликаты, если они есть.
    В базе данных могут быть одинаковые username групп, но не у одного пользователя. Например, @python_jobs
    может быть добавлен несколькими пользователями, но не может быть дважды у одного пользователя в таблице Groups.
    :param user_id: ID пользователя Telegram.
    :param group: Список username групп/каналов, которые будут отслеживаться.
    :param user_username: username пользователя Telegram.
    :param user_firstname: firstname пользователя Telegram.
    :param id_group: ID группы Telegram (для закрытых групп).
    :param name_group: Название группы Telegram.
    :param user_session_string: Стринг сессия аккаунта для отслеживания.
    :return None: Нечего не возвращаем, так как записываем в базу данных
    """
    for gr in group:
        gr_clean = gr.strip()
        if not gr_clean:
            continue
        UsersGroups.get_or_create(
            user_id=user_id,
            username_group=gr_clean,
            defaults={
                "user_username": user_username,
                "user_firstname": user_firstname,
                "id_group": id_group,
                "name_group": name_group,
                "user_session_string": user_session_string,
            }
        )


def dell_group(user_id: int, username_group: str):
    """
    Удаляет группу из отслеживания ключевых слов.

    :param user_id: Telegram ID пользователя
    :param username_group: Username группы
    :return: True, если группа удалена, иначе False
    """
    try:
        (
            UsersGroups.delete().where(UsersGroups.user_id == user_id,
                                       UsersGroups.username_group == username_group).execute()
        )
        return True
    except Exception as e:
        logger.exception(e)


def clear_all_user_groups(user_id: int) -> int:
    """
    Удаляет все группы/каналы пользователя из отслеживания.

    :param user_id: Telegram ID пользователя
    :return: Количество удалённых записей
    """
    try:
        deleted = UsersGroups.delete().where(UsersGroups.user_id == user_id).execute()
        logger.info(f"Удалено {deleted} каналов для пользователя {user_id}")
        return deleted
    except Exception as e:
        logger.exception(e)
        return 0


def get_user_groups_paginated(user_id: int, page: int = 0, page_size: int = 5) -> tuple[list, int]:
    """
    Возвращает страницу каналов пользователя с пагинацией.

    :param user_id: Telegram ID пользователя
    :param page: Номер страницы (0-based)
    :param page_size: Количество записей на странице
    :return: Кортеж (список объектов Group, общее количество)
    """
    total = UsersGroups.select().where(UsersGroups.user_id == user_id).count()
    records = (
        UsersGroups.select()
        .where(UsersGroups.user_id == user_id)
        .order_by(UsersGroups.date_added.desc())
        .offset(page * page_size)
        .limit(page_size)
    )
    return list(records), total


async def get_user_channels_or_notify(user_id: int, user_lang, message, client):
    """
    Получает список каналов пользователя из БД или отправляет уведомление об их отсутствии
    :param user_id:
    :param user_lang:
    :param message:
    :param client:
    """
    channels = [group.username_group for group in UsersGroups.select().where(UsersGroups.user_id == user_id)]

    if not channels:
        logger.warning(f"⚠️ Список каналов пуст для пользователя {user_id}.")
        await client.disconnect()
        await message.answer(
            t("tracking_launch_error", lang=user_lang),
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None

    return channels
