from datetime import datetime

from asgiref.sync import sync_to_async
from loguru import logger  # https://github.com/Delgan/loguru
from peewee import SqliteDatabase, IntegerField, TextField, DateTimeField, CharField, fn

database = SqliteDatabase(
    'data/bot.db', timeout=30,
    pragmas={'cache_size': 4096, 'synchronous': 'NORMAL'},
    autocommit=True  # ✅ Важно!
)

"""
Работа с моделью TelegramGroup. База групп и каналов в Telegram.
"""


class TelegramGroups(database.Model):
    """
    Модель для хранения данных о найденных Telegram-группах и каналах.

    Используется для централизованного хранения информации о группах,
    обнаруженных с помощью AI-поиска (через Groq). Позволяет избежать
    повторного поиска и дублирования. Таблица общая для всех пользователей.

    Attributes:
        telegram_id (IntegerField): Уникальный ID группы в Telegram (первичный ключ).
        group_hash (CharField): Уникальный хеш или ID группы, используется как ключ.
        name (CharField): Отображаемое название группы или канала.
        username (CharField, optional): Юзернейм (@username), может отсутствовать.
        description (TextField, optional): Описание группы из Telegram.
        participants (IntegerField): Количество участников, по умолчанию 0.
        category (CharField, optional): Категория, определённая ИИ (например, 'технологии').
        group_type (CharField): Тип чата — 'group', 'channel' или 'link'.
        language (CharField): Язык группы/канала — 'ru', 'en' или ''.
        link (CharField): Прямая ссылка на чат (https://t.me/...).
        availability (CharField): Статус активности группы
        date_added (DateTimeField): Дата и время добавления записи, по умолчанию — текущее время.

    Meta:
        table_name (str): Имя таблицы в базе данных — 'telegram_groups'.
    """
    telegram_id = IntegerField(null=True, unique=True)  # Новое поле: Telegram entity ID
    group_hash = CharField(null=True)  # ID группы или хеш username
    name = CharField()  # Название группы
    username = CharField(null=True)  # @username если есть
    description = TextField(null=True)  # Описание
    participants = IntegerField(default=0)  # Количество участников
    category = CharField(null=True)  # Категория (определяется AI)
    group_type = CharField()  # 'group', 'channel', 'link'
    language = CharField(null=True, default='')  # ru/en язык группы / канала
    link = CharField(null=True, default='')  # Ссылка на группу (может отсутствовать)
    availability = CharField(null=True)  # Статус активности
    date_added = DateTimeField(default=datetime.now)  # Дата добавления

    class Meta:
        """Метаданные таблицы Telegram-групп и каналов"""
        table_name = 'telegram_groups'


def get_all_data_telegram_groups():
    """
    Возвращает все записи из таблицы telegram_groups в виде списка словарей.

    :return: (list[dict]) Список словарей с данными всех групп и каналов.
    """
    return list(TelegramGroups.select().dicts())


def clean_telegram_id_duplicates():
    """
    Удаляет все дубликаты по telegram_id, оставляя самую свежую запись.

    :return: (int) Количество удалённых записей-дубликатов.
    """
    deleted_count = 0

    # Находим все telegram_id с дублями
    duplicates = (
        TelegramGroups
        .select(
            TelegramGroups.telegram_id,
            fn.COUNT(TelegramGroups.id).alias("cnt")
        )
        .where(TelegramGroups.telegram_id.is_null(False))
        .group_by(TelegramGroups.telegram_id)
        .having(fn.COUNT(TelegramGroups.id) > 1)
    )

    for dup in duplicates:
        tid = dup.telegram_id

        # Оставляем самую новую запись
        keep = (
            TelegramGroups
            .select(TelegramGroups.id)
            .where(TelegramGroups.telegram_id == tid)
            .order_by(TelegramGroups.date_added.desc())
            .limit(1)
            .get()
        )

        # Удаляем все остальные
        deleted = (
            TelegramGroups
            .delete()
            .where(
                (TelegramGroups.telegram_id == tid) &
                (TelegramGroups.id != keep.id)
            )
            .execute()
        )
        deleted_count += deleted

    logger.info(f"Очищено дубликатов по telegram_id: {deleted_count}")
    return deleted_count


async def get_groups_without_category() -> list[dict]:
    """
    Асинхронно получает список групп без категории из базы данных.

    :return: (list[dict]) Список групп без присвоенной категории.
    """

    def _fetch():
        """
        Извлекает из базы данных список групп без присвоенной категории.

        :return: (list[dict]) Список словарей с данными групп.
        """
        if database.is_closed():
            database.connect(reuse_if_open=True)

        groups = TelegramGroups.select().where(
            (TelegramGroups.username.is_null(False)) &
            (TelegramGroups.category == '')
        )

        return [
            {
                "telegram_id": group.telegram_id,
                "name": group.name,
                "username": group.username,
                "description": group.description,
                "group_type": group.group_type,
            }
            for group in groups
        ]

    try:
        return await sync_to_async(_fetch, thread_sensitive=True)()
    except Exception as e:
        logger.exception(f"❌ Ошибка получения групп: {e}")
        return []


def migrate_categories_to_lowercase():
    """
    Приводит все существующие категории в базе данных к нижнему регистру.

    :return: (int) Количество обновлённых записей.
    """
    if database.is_closed():
        database.connect(reuse_if_open=True)

    try:
        groups = TelegramGroups.select().where(
            TelegramGroups.category.is_null(False) &
            (TelegramGroups.category != '')
        )

        updated_count = 0
        for group in groups:
            if group.category != group.category.lower():
                group.category = group.category.lower()
                group.save()
                updated_count += 1

        logger.info(f"✅ Миграция категорий завершена: обновлено {updated_count} записей")
        return updated_count
    except Exception as e:
        logger.exception(f"❌ Ошибка миграции категорий: {e}")
        return 0


def getting_number_records_database():
    """
    Получает общее количество записей о группах и каналах в базе данных.

    :return: (int) Количество записей в таблице telegram_groups.
    """
    return TelegramGroups.select().count()
