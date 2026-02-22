# -*- coding: utf-8 -*-
import os
from datetime import datetime

from loguru import logger
from peewee import Model, CharField
from peewee import SqliteDatabase, IntegerField, AutoField, TextField, DateTimeField
from peewee import fn

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
    db.create_tables([Account], safe=True)
    db.create_tables([UserAccountsTable], safe=True)
    db.close()


# def create_accounts_table(user_id: int):
#     """
#     Создаёт и возвращает модель Peewee для таблицы аккаунтов пользователя.
#     Таблица создаётся автоматически при первом вызове.
#     """
# 🔹 Вложенный класс модели — создаётся заново для каждого user_id

class UserAccountsTable(BaseModel):
    id = AutoField()  # ✅ Первичный ключ (обязательно!)
    user_id = IntegerField(index=True)  # ID пользователя Telegram
    session_string = CharField(unique=True, max_length=500, index=True)
    phone_number = CharField(max_length=20, index=True)
    created_at = DateTimeField(default=datetime.now)  # ✅ Полезно для отладки

    class Meta:
        database = db
        table_name = f"user_accounts_table"  # Динамическое имя таблицы


# 🔹 Создаём таблицу, если не существует
# db.connect(reuse_if_open=True)
# db.create_tables([UserAccountsTable], safe=True)
#
# return UserAccountsTable  # ✅ Возвращаем класс модели для использования


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
    except Account.DoesNotExist:
        logger.info(f"Аккаунт с session_string='{session_string}' не найден в базе.")
    except Exception as e:
        logger.exception("Ошибка при удалении аккаунта")
        logger.info(f"Ошибка при удалении аккаунта: {e}")


def get_account_list():
    """
    Получаем подключенные аккаунты: возвращаем список кортежей (phone, session_string)
    :return: Список кортежей (phone, session_string)
    """
    accounts = []
    for account in Account.select(Account.phone_number, Account.session_string):
        accounts.append((account.phone_number, account.session_string))

    return accounts  # Список аккаунтов


async def update_phone_by_session(session_string: str, new_phone: str, app_logger) -> bool:
    """
    Обновляет номер телефона аккаунта в базе по session_string.

    :param session_string: Строка сессии
    :param new_phone: Новый номер телефона
    :param app_logger: Логгер
    :return: True при успехе, False при ошибке
    """
    try:
        rows_updated = (Account
                        .update(phone_number=new_phone)
                        .where(Account.session_string == session_string)
                        .execute())
        if rows_updated > 0:
            await app_logger.log_and_display(f"✅ Номер аккаунта обновлён: {new_phone}")
            return True
        else:
            await app_logger.log_and_display(f"⚠️ Аккаунт с session_string='{session_string}' не найден для обновления")
            return False
    except Exception as e:
        logger.exception("Ошибка при обновлении номера")
        await app_logger.log_and_display(f"❌ Ошибка обновления номера: {e}")
        return False


def get_user_channel_usernames(user_id: int):
    """
    Возвращает множество username каналов/групп пользователя из БД (в нижнем регистре).

    :param user_id: Telegram user_id
    :return: db_channels, total_count
    """
    Groups = create_groups_model(user_id=user_id)
    total_count = Groups.select().count()
    db_channels = {
        group.username.lower()
        for group in (
            Groups
            .select(Groups.username)
            .where(Groups.username.is_null(False))
        )
    }
    return db_channels, total_count


def delete_group_by_username(user_id: int, channel: str):
    """
    Удаляет группу или канал пользователя из БД по username.

    Используется для очистки базы данных от невалидных или недоступных
    Telegram-групп/каналов (например, если канал удалён или бот потерял доступ).

    :param user_id: (int) Telegram user_id, для которого создана таблица групп
    :param channel: (str) Username группы/канала без '@'
    :return: (int) Количество удалённых записей
    """
    Groups = create_groups_model(user_id)
    Groups.delete().where(Groups.username == channel).execute()


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


def write_account_to_dbs(user_id: int, session_string: str, phone_number: str):
    AccountsTable = create_accounts_table(user_id)
    account, created = AccountsTable.get_or_create(
        session_string=session_string,
        defaults={"phone_number": phone_number}
    )
    if created:
        logger.info(f"✅ Аккаунт {phone_number} записан в БД.")
    else:
        logger.info(f"⚠️ Аккаунт {phone_number} уже существует в БД.")


# database/database.py

def write_account_to_user_table(user_id: int, session_string: str, phone_number: str) -> bool:
    """
    Записывает аккаунт в персональную таблицу пользователя: {user_id}_accounts

    :param user_id: ID пользователя Telegram
    :param session_string: Строка сессии Telethon (StringSession)
    :param phone_number: Номер телефона аккаунта
    :return: True если успешно, False при ошибке
    """
    try:
        # 🔹 Создаём модель и таблицу для пользователя (если нет)
        UserAccountsTable = create_accounts_table(user_id)

        # 🔹 Вставляем или обновляем запись (защита от дубликатов)
        query = (UserAccountsTable
        .insert(session_string=session_string, phone_number=phone_number)
        .on_conflict(
            conflict_target=[UserAccountsTable.session_string],
            preserve=[UserAccountsTable.phone_number],
            action="UPDATE"
        ))
        query.execute()

        logger.info(f"💾 Аккаунт {phone_number} сохранён в таблицу {user_id}_accounts")
        return True

    except Exception as e:
        logger.exception(f"❌ Ошибка записи в таблицу {user_id}_accounts: {e}")
        return False


def get_user_accounts(user_id: int) -> list[dict]:
    """
    Получает все аккаунты пользователя из его персональной таблицы

    :param user_id: ID пользователя Telegram
    :return: Список словарей с данными аккаунтов
    """
    try:
        UserAccountsTable = create_accounts_table(user_id)

        accounts = []
        for account in UserAccountsTable.select():
            accounts.append({
                "session_string": account.session_string,
                "phone_number": account.phone_number
            })
        return accounts

    except Exception as e:
        logger.exception(f"❌ Ошибка получения аккаунтов пользователя {user_id}: {e}")
        return []


def delete_user_account(user_id: int, session_string: str) -> bool:
    """
    Удаляет аккаунт из персональной таблицы пользователя

    :param user_id: ID пользователя Telegram
    :param session_string: Строка сессии для удаления
    :return: True если удалено, False если не найдено или ошибка
    """
    try:
        UserAccountsTable = create_accounts_table(user_id)

        deleted = (UserAccountsTable
                   .delete()
                   .where(UserAccountsTable.session_string == session_string)
                   .execute())

        if deleted > 0:
            logger.info(f"🗑️ Аккаунт удалён из таблицы {user_id}_accounts")
            return True
        else:
            logger.warning(f"⚠️ Аккаунт не найден в таблице {user_id}_accounts")
            return False

    except Exception as e:
        logger.exception(f"❌ Ошибка удаления аккаунта пользователя {user_id}: {e}")
        return False


def create_groups_model(user_id):
    """
    Динамически создаёт модель Peewee для хранения чатов конкретного пользователя.

    Модель используется для отслеживания списка Telegram-групп и каналов, добавленных пользователем для мониторинга.
    Создаётся отдельная таблица для каждого пользователя по шаблону 'groups_<user_id>'.

    :param user_id: (int) Уникальный идентификатор пользователя Telegram.
    :return peewee.Model: Класс модели Peewee с полем `username_chat_channel`.

    Model Fields:
        username_chat_channel (CharField):
            Уникальное имя чата (канала) в формате @username или название.
    """

    class Groups(BaseModel):
        id = IntegerField(null=True)
        group_id = CharField(unique=True)
        group_hash = CharField(unique=True, index=True)
        name = CharField()
        username = CharField(null=True, unique=True)  # ← ДОБАВЛЕНО unique=True
        description = TextField(null=True)
        participants = IntegerField(default=0)
        category = CharField(null=True)
        group_type = CharField()
        link = CharField()
        date_added = DateTimeField(default=datetime.now)

        class Meta:
            table_name = f"{user_id}_groups"  # Имя таблицы

    return Groups  # Возвращаем класс модели


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


class TelegramGroup(BaseModel):
    """
    Модель для хранения данных о найденных Telegram-группах и каналах.

    Используется для централизованного хранения информации о группах,
    обнаруженных с помощью AI-поиска (через Groq). Позволяет избежать
    повторного поиска и дублирования. Таблица общая для всех пользователей.

    Attributes:
        group_hash (CharField): Уникальный хеш или ID группы, используется как ключ.
        name (CharField): Отображаемое название группы или канала.
        username (CharField, optional): Юзернейм (@username), может отсутствовать.
        description (TextField, optional): Описание группы из Telegram.
        participants (IntegerField): Количество участников, по умолчанию 0.
        category (CharField, optional): Категория, определённая ИИ (например, 'технологии').
        group_type (CharField): Тип чата — 'group', 'channel' или 'link'.
        link (CharField): Прямая ссылка на чат (https://t.me/...).
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


def get_tracked_channels_count(user_id: int):
    """
    Получение количества подключенных групп для отслеживания ключевых слов

    :param user_id: (int) ID пользователя Telegram.
    :return int: Количество записей (обычно 0 или 1, так как группа одна).
    """
    GroupModel = create_groups_model(user_id)

    # Убедимся, что таблица существует, иначе count() вызовет ошибку
    if not GroupModel.table_exists():
        return 0

    return GroupModel.select().count()


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
