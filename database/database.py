# -*- coding: utf-8 -*-
import os
from datetime import datetime

from asgiref.sync import sync_to_async
from loguru import logger
from peewee import (
    SqliteDatabase, IntegerField, AutoField, TextField, DateTimeField, Model, CharField, DoesNotExist, fn
)

db = SqliteDatabase(
    'data/bot.db', timeout=30,
    pragmas={'journal_mode': 'wal', 'cache_size': 4096, 'synchronous': 'NORMAL'},
    autocommit=True  # ✅ Важно!
)


class BaseModel(Model):
    class Meta:
        database = db


def init_database():
    """Инициализация БД и создание таблиц"""
    db.connect(reuse_if_open=True)
    db.create_tables([Account], safe=True)  # Создание таблицы аккаунтов
    db.create_tables([UserAccountsTable], safe=True)  # Создание таблицы аккаунтов пользователя
    db.create_tables([Groups], safe=True)  # Создание таблицы с группами пользователей
    db.create_tables([TelegramGroup], safe=True)  # Создание таблицы Telegram-групп
    db.close()


def migrate_add_availability_column():
    """
    Миграция: добавляет колонку availability в таблицу telegram_groups.
    
    Запускается один раз при обновлении базы данных.
    Если колонка уже существует — миграция пропускается.
    """
    try:
        db.connect(reuse_if_open=True)

        # Проверяем, существует ли уже колонка
        cursor = db.execute_sql("PRAGMA table_info(telegram_groups)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'availability' not in columns:
            # Добавляем колонку availability со значением по умолчанию 'unknown'
            db.execute_sql("""
                ALTER TABLE telegram_groups 
                ADD COLUMN availability TEXT DEFAULT 'unknown'
            """)
            logger.info("✅ Миграция: добавлена колонка 'availability' в таблицу 'telegram_groups'")
        else:
            logger.info("ℹ️ Колонка 'availability' уже существует в таблице 'telegram_groups'")

    except Exception as e:
        logger.exception(f"❌ Ошибка при выполнении миграции availability: {e}")
    finally:
        db.close()


"""
Работа с группами пользователя для отслеживания ключевых слов. Все данные пользователей хранится в одной таблице, 
для удобства масштабирования
"""


class Groups(BaseModel):
    id = AutoField()  # автоинкремент
    user_id = IntegerField()  # ID пользователя Telegram
    username = CharField(null=True)  # Username пользователя Telegram
    date_added = DateTimeField(default=datetime.now)  # Дата добавления группы

    class Meta:
        table_name = f"users_groups"  # Имя таблицы
        indexes = (
            (("user_id", "username"), True),  # один пользователь не добавит один канал дважды
        )


def dell_group(user_id: int, username: str):
    """
    Удаляет группу из отслеживания ключевых слов.

    :param user_id: Telegram ID пользователя
    :param username: Username группы
    :return: True, если группа удалена, иначе False
    """
    try:
        (Groups
         .delete()
         .where(Groups.user_id == user_id, Groups.username == username)
         .execute())
        return True
    except Exception as e:
        logger.exception(e)


def get_tracked_channels_count(user_id: int) -> int:
    """
    Получает количество отслеживаемых каналов для указанного пользователя.

    :param user_id: Telegram ID пользователя
    :return: Количество отслеживаемых каналов
    """
    try:
        count = (Groups
                 .select()
                 .where(Groups.user_id == user_id)
                 .count())
        return count
    except Exception as e:
        logger.error(f"Ошибка при получении количества отслеживаемых каналов для пользователя {user_id}: {e}")
        return 0


def get_user_channel_usernames(user_id: int) -> tuple[list[str], int]:
    """
    Получает все username каналов/групп пользователя по user_id.

    :param user_id: Telegram ID пользователя
    :return: Кортеж (список username, общее количество)
    """
    try:
        records = (Groups
                   .select(Groups.username)
                   .where(Groups.user_id == user_id)
                   .order_by(Groups.date_added.desc()))

        usernames = [row.username for row in records]
        return usernames, len(usernames)

    except Exception as e:
        logger.error(f"Ошибка при получении каналов пользователя {user_id}: {e}")
        return [], 0


"""
Таблица с аккаунтами пользователя пользователей телеграмм бота
"""


class UserAccountsTable(BaseModel):
    id = AutoField()  # ✅ Первичный ключ (обязательно!)
    user_id = IntegerField(index=True)  # ID пользователя Telegram
    session_string = CharField(unique=True, max_length=500, index=True)
    phone_number = CharField(max_length=20, index=True)
    created_at = DateTimeField(default=datetime.now)  # ✅ Полезно для отладки

    class Meta:
        database = db
        table_name = f"user_accounts_table"  # Динамическое имя таблицы


def write_account_to_user_table(user_id: int, session_string: str, phone_number: str):
    """
    Записывает аккаунт в персональную таблицу пользователя: {user_id}_accounts
    """
    try:
        user_accounts = UserAccountsTable.create(
            user_id=user_id,  # ID пользователя Telegram
            session_string=session_string,  # Строка сессии Telegram аккаунта
            phone_number=phone_number  # Номер телефона аккаунта
        )
        user_accounts.save()
    except Exception as e:
        logger.exception(e)


def get_user_accounts(user_id: int):
    """
    Получает все аккаунты пользователя из его персональной таблицы

    :param user_id: ID пользователя Telegram
    :return: Список словарей с данными аккаунтов
    """
    try:
        accounts = (UserAccountsTable
                    .select()
                    .where(UserAccountsTable.user_id == user_id))

        # Преобразуем объекты модели в словари
        result = [
            {
                'user_id': account.user_id,
                'session_string': account.session_string,
                'phone_number': account.phone_number,
                'created_at': account.created_at
            }
            for account in accounts
        ]
        return result
    except Exception as e:
        logger.exception(f"❌ Ошибка получения аккаунтов пользователя {user_id}: {e}")
        return []


"""Работа с аккаунтами"""


class Account(Model):
    """Модель аккаунта"""
    session_string = CharField(unique=True)  # уникальность для защиты от дубликатов
    phone_number = CharField()  # номер телефона аккаунта

    class Meta:
        database = db
        table_name = 'account'


def write_account_to_db(session_string, phone_number):
    """
    Запись аккаунта в базу данных
    :param phone_number: Номер телефона аккаунта
    :param session_string: Строка сессии
    """
    try:
        Account.insert(session_string=session_string, phone_number=phone_number).on_conflict(action='IGNORE').execute()
    except Exception as e:
        logger.exception(e)


def getting_account():
    """
    Получение аккаунтов из базы данных
    :return: Список аккаунтов из базы данных
    """
    records = []
    for record in Account.select(Account.session_string):
        records.append(record.session_string)

    return records


async def delete_account_from_db(session_string: str) -> None:
    """
    Удаляет аккаунт из таблицы 'account' по session_string.
    Перед удалением извлекает и логирует номер телефона.

    :param session_string: Строка сессии аккаунта
    :return: None
    """
    try:
        # Ищем аккаунт по session_string
        account = Account.get(Account.session_string == session_string)
        phone_number = account.phone_number
        logger.info(f"Найден аккаунт для удаления: {phone_number}")
        # Удаляем запись
        account.delete_instance()
        logger.info(f"Аккаунт {phone_number} успешно удалён из базы данных.")
    except DoesNotExist:
        logger.info(f"Аккаунт с session_string='{session_string}' не найден в базе.")
    except Exception as e:
        logger.exception("Ошибка при удалении аккаунта")
        logger.info(f"Ошибка при удалении аккаунта: {e}")


class User(BaseModel):
    """
    Модель для хранения основных данных пользователя Telegram.

    Используется для регистрации пользователей при первом запуске бота (/start)
    и хранения их профиля и языка интерфейса. Таблица общая для всех пользователей.

    Attributes:
        user_id (IntegerField): Уникальный идентификатор пользователя Telegram (первичный ключ).
        username (CharField, optional): Telegram-ник пользователя (может быть None).
        first_name (CharField, optional): Имя пользователя.
        last_name (CharField, optional): Фамилия пользователя.
        language (CharField): Язык интерфейса бота ('ru', 'en' или 'unset' при первом запуске).

    Meta:
        table_name (str): Имя таблицы в базе данных — 'user' (по умолчанию от имени класса).
    """
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    language = CharField(default="ru")  # "ru" или "en"


def create_keywords_model(user_id):
    """
    Динамически создаёт модель Peewee для хранения ключевых слов конкретного пользователя.

    Модель используется для отслеживания слов или фраз, по которым пользователь хочет фильтровать сообщения в группах.
    Создаётся отдельная таблица для каждого пользователя по шаблону 'keywords_<user_id>'.

    :param user_id: (int) Уникальный идентификатор пользователя Telegram.
    :return peewee.Model: Класс модели Peewee с полями `id` и `user_keyword`.

    Model Fields:
        id (AutoField):
            Автоинкрементный первичный ключ.
        user_keyword (CharField):
            Уникальное ключевое слово для поиска в сообщениях.
    """

    class Keywords(BaseModel):
        id = AutoField()  # <-- добавляем первичный ключ (иначе всё пишется в одну строку)
        user_keyword = CharField(unique=True)  # Поле для хранения ключевого слова

        class Meta:
            table_name = f"{user_id}_keywords"  # Имя таблицы

    return Keywords  # Возвращаем класс модели


def create_group_model(user_id):
    """
    Динамически создаёт модель Peewee для хранения технической группы пользователя.

    Модель используется для сохранения одного Telegram-чата (группы или канала),
    куда бот будет пересылать найденные сообщения, содержащие ключевые слова.
    Создаётся отдельная таблица для каждого пользователя по шаблону 'group_<user_id>'.

    :param user_id: (int) Уникальный идентификатор пользователя Telegram.
    :return peewee.Model: Класс модели Peewee с полями `id` и `user_group`.

    Model Fields:
        id (AutoField):
            Автоинкрементный первичный ключ.
        user_group (CharField):
            Уникальное имя технической группы (например, @my_alerts_channel).
    """

    class Group(BaseModel):
        id = AutoField()  # <-- добавляем первичный ключ (иначе всё пишется в одну строку)
        user_group = CharField(unique=True)  # Поле для хранения технической группы

        class Meta:
            table_name = f"{user_id}_group"  # Имя таблицы

    return Group  # Возвращаем класс модели


"""
Работа с моделью TelegramGroup. База групп и каналов в Telegram.
"""


class TelegramGroup(BaseModel):
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
    link = CharField()  # Ссылка на группу
    availability = CharField(null=True)  # Статус активности
    date_added = DateTimeField(default=datetime.now)  # Дата добавления

    class Meta:
        table_name = 'telegram_groups'


def clean_telegram_id_duplicates():
    """Удаляет все дубликаты по telegram_id, оставляя самую свежую запись"""
    deleted_count = 0

    # Находим все telegram_id с дублями
    duplicates = (
        TelegramGroup
        .select(
            TelegramGroup.telegram_id,
            fn.COUNT(TelegramGroup.id).alias("cnt")
        )
        .where(TelegramGroup.telegram_id.is_null(False))
        .group_by(TelegramGroup.telegram_id)
        .having(fn.COUNT(TelegramGroup.id) > 1)
    )

    for dup in duplicates:
        tid = dup.telegram_id

        # Оставляем самую новую запись
        keep = (
            TelegramGroup
            .select(TelegramGroup.id)
            .where(TelegramGroup.telegram_id == tid)
            .order_by(TelegramGroup.date_added.desc())
            .limit(1)
            .get()
        )

        # Удаляем все остальные
        deleted = (
            TelegramGroup
            .delete()
            .where(
                (TelegramGroup.telegram_id == tid) &
                (TelegramGroup.id != keep.id)
            )
            .execute()
        )
        deleted_count += deleted

    print(f"✅ Очищено дубликатов по telegram_id: {deleted_count}")
    return deleted_count


async def get_groups_without_category() -> list[dict]:
    """Получает группы без категории (в отдельном потоке для БД)"""

    def _fetch():
        if db.is_closed():
            db.connect(reuse_if_open=True)

        groups = TelegramGroup.select().where(
            (TelegramGroup.username.is_null(False)) &
            (TelegramGroup.category == '')
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


def getting_number_records_database():
    """Получает количество записей в базе данных о найденных группах пользователями"""
    return TelegramGroup.select().count()


def get_target_group_count(user_id: int) -> int:
    """
    Получает количество технических групп (куда пересылаются уведомления),
    подключённых конкретным пользователем.

    Ищет записи в таблице `group_{user_id}`.

    :param user_id: (int) ID пользователя Telegram.
    :return int: Количество записей (обычно 0 или 1, так как группа одна).
    """
    GroupModel = create_group_model(user_id)

    # Убедимся, что таблица существует, иначе count() вызовет ошибку
    if not GroupModel.table_exists():
        return 0

    return GroupModel.select().count()


def get_session_count(user_id: int) -> int:
    """
    Подсчитывает количество .session файлов в папке accounts/{user_id}/.

    :param user_id: (int) ID пользователя Telegram.
    :return int: Количество .session файлов (0, если папка не существует или файлов нет).
    """
    session_dir = os.path.join("accounts", str(user_id))
    if not os.path.exists(session_dir):
        return 0

    session_files = [
        f for f in os.listdir(session_dir)
        if f.endswith(".session")
    ]
    return len(session_files)


def get_keywords_count(user_id: int):
    """
    Получение количества ключевых слов для отслеживания
    :param user_id:
    :return int: Количество записей (обычно 0 или 1, так как группа одна).
    """

    Keywords = create_keywords_model(user_id)

    # Убедимся, что таблица существует, иначе count() вызовет ошибку
    if not Keywords.table_exists():
        return 0

    return Keywords.select().count()
