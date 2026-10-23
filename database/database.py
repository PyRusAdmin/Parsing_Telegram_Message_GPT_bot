from datetime import datetime

from asgiref.sync import sync_to_async
from loguru import logger  # https://github.com/Delgan/loguru
from peewee import (
    SqliteDatabase, IntegerField, BigIntegerField, AutoField, TextField, DateTimeField, CharField, DoesNotExist, fn
)

database = SqliteDatabase(
    'data/bot.db', timeout=30,
    pragmas={'cache_size': 4096, 'synchronous': 'NORMAL'},
    autocommit=True  # ✅ Важно!
)

"""
Работа с таблицей personal_tracking, для дальнейшего получения аккаунта, ID группы (created_group_id) в которую будут пересылаться 
найденные сообщения (целевая группа). 
"""


def get_group_id_with_personal_tracking(user_id):
    """
    Получает created_group_id (ID группы, в которую пересылаются найденные сообщения по ключевым словам)
    :param user_id: ID пользователя Telegram.
    :return Any: ID группы, в которую будут отправляться сообщения, которые были найдены по ключевым словам.
    """
    return PersonalTracking.select(PersonalTracking.created_group_id).where(
        PersonalTracking.user_id == user_id).scalar()


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


class PersonalTrackingStats(database.Model):
    """Модель базы данных для хранения статистики персонального отслеживания"""

    id = AutoField()
    user_id = BigIntegerField(index=True)
    event_type = CharField()  # 'group_connected', 'slot_purchased', 'changed_target'
    stars_amount = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """Метаданные таблицы статистики персонального отслеживания"""
        table_name = "personal_tracking_stats"


"""
Запись в базу данных вопросов пользователей, что бы расширить базу знаний
"""


class Question(database.Model):
    """Модель для хранения вопросов пользователей и ответов базы знаний"""
    id = AutoField()  # автоинкремент
    user_id = IntegerField()  # ID пользователя Telegram
    question = TextField()  # Вопрос пользователя
    answer = TextField(null=True)  # Ответ на вопрос


def add_question(user_id: int, question: str, answer: str):
    """
    Добавляет вопрос в базу данных.

    :param user_id: Telegram ID пользователя
    :param question: Вопрос пользователя
    :param answer: Ответ на вопрос
    :return: True, если вопрос добавлен, иначе False
    """
    Question.create(user_id=user_id, question=question, answer=answer)
    return True


def get_all_questions():
    """
    Получает все вопросы и ответы из базы данных.

    :return: Список словарей с вопросами и ответами
    """
    try:
        questions = Question.select()
        result = [
            {
                'user_id': q.user_id,
                'question': q.question,
                'answer': q.answer
            }
            for q in questions
        ]
        return result
    except Exception as e:
        logger.exception(f"❌ Ошибка получения всех вопросов: {e}")
        return []


"""
Таблица с аккаунтами подключаемых администратором бота, для общего использования
"""


class AccountFree(database.Model):
    """Свободные аккаунты для подключения, которые подключает администратор бота"""
    session_string = CharField(unique=True)  # Уникальность для защиты от дубликатов
    phone_number = CharField()  # Номер телефона аккаунта

    class Meta:
        """Метаданные таблицы свободных аккаунтов"""

        table_name = 'account_free'


def write_account_to_db_free(session_string: str, phone_number: str):
    """
    Запись аккаунта в базу данных. Если аккаунт подключает обычный пользователь, то пишет в свою таблицу с аккаунтами,
    если это администратор, то записывается в общую таблицу с общими бесплатными аккаунтами. Админа определяем по ID Telegram
    :param session_string: Строка сессии
    :param phone_number: номер телефона Telegram
    """

    AccountFree.insert(
        session_string=session_string,
        phone_number=phone_number,
    ).on_conflict(
        conflict_target=[AccountFree.session_string],
        update={
            AccountFree.phone_number: phone_number,
        }
    ).execute()

    logger.info(
        f"Аккаунт {phone_number} успешно записан в базу данных"
    )


# class UserAccountsTable(database.Model):
#     """Модель для хранения сессий подключенных Telegram-аккаунтов пользователей"""
#     id = AutoField()  # ✅ Первичный ключ (обязательно!)
#     user_id = IntegerField(index=True)  # ID пользователя Telegram
#     session_string = CharField(unique=True, max_length=500, index=True)
#     phone_number = CharField(max_length=20, index=True)
#     created_at = DateTimeField(default=datetime.now)  # ✅ Полезно для отладки
#
#     class Meta:
#         """Метаданные таблицы аккаунтов пользователей"""
#
#         table_name = f"user_accounts_table"  # Динамическое имя таблицы


# def write_account_to_user_table(user_id: int, session_string: str, phone_number: str):
#     """
#     Записывает аккаунт в персональную таблицу пользователя: {user_id}_accounts
#     """
#     try:
#         user_accounts = UserAccountsTable.create(
#             user_id=user_id,  # ID пользователя Telegram
#             session_string=session_string,  # Строка сессии Telegram аккаунта
#             phone_number=phone_number  # Номер телефона аккаунта
#         )
#         user_accounts.save()
#     except Exception as e:
#         logger.exception(e)


# def get_user_accounts(user_id: int):
#     """
#     Получает все аккаунты пользователя из его персональной таблицы
#
#     :param user_id: ID пользователя Telegram
#     :return: Список словарей с данными аккаунтов
#     """
#     try:
#         accounts = (UserAccountsTable
#                     .select()
#                     .where(UserAccountsTable.user_id == user_id)
#                     )
#
#         # Преобразуем объекты модели в словари
#         result = [
#             {
#                 'user_id': account.user_id,
#                 'session_string': account.session_string,
#                 'phone_number': account.phone_number,
#                 'created_at': account.created_at
#             }
#             for account in accounts
#         ]
#         return result
#     except Exception as e:
#         logger.exception(f"❌ Ошибка получения аккаунтов пользователя {user_id}: {e}")
#         return []


# def delete_account_from_user_table(user_id: int, session_string: str) -> None:
#     """
#     Удаляет аккаунт из таблицы 'user_accounts_table' по user_id и session_string.
#     """
#     try:
#         query = UserAccountsTable.delete().where(
#             (UserAccountsTable.user_id == user_id) & (UserAccountsTable.session_string == session_string)
#         )
#         deleted_count = query.execute()
#         logger.info(f"🗑️ Удалено {deleted_count} невалидных записей из UserAccountsTable для user_id={user_id}")
#     except Exception as e:
#         logger.exception(f"❌ Ошибка при удалении аккаунта из UserAccountsTable: {e}")


"""Работа с аккаунтами"""


class Account(database.Model):
    """Модель аккаунта"""
    session_string = CharField(unique=True)  # уникальность для защиты от дубликатов
    phone_number = CharField()  # номер телефона аккаунта

    class Meta:
        """Метаданные таблицы рабочих аккаунтов"""

        table_name = 'account'


def getting_free_account():
    """
    Получение свободных аккаунтов для подключения
    :return: Список аккаунтов
    """
    records = []
    for record in AccountFree.select(AccountFree.session_string):
        records.append(record.session_string)

    return records


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


class User(database.Model):
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
    stars = IntegerField(default=0)
    last_free_download_at = DateTimeField(null=True)


"""
Работа с моделью TelegramGroup. База групп и каналов в Telegram.
"""


class TelegramGroup(database.Model):
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
    """Возвращает все записи из таблицы telegram_groups в виде списка словарей."""
    return list(TelegramGroup.select().dicts())


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

    logger.info(f"Очищено дубликатов по telegram_id: {deleted_count}")
    return deleted_count


async def get_groups_without_category() -> list[dict]:
    """Получает группы без категории (в отдельном потоке для БД)"""

    def _fetch():
        """Извлекает из базы данных список групп без присвоенной категории"""
        if database.is_closed():
            database.connect(reuse_if_open=True)

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


def migrate_categories_to_lowercase():
    """
    Миграция: приводит все существующие категории к нижнему регистру.
    Запускать один раз после обновления логики.
    """
    if database.is_closed():
        database.connect(reuse_if_open=True)

    try:
        groups = TelegramGroup.select().where(
            TelegramGroup.category.is_null(False) &
            (TelegramGroup.category != '')
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
    """Получает количество записей в базе данных о найденных группах пользователями"""
    return TelegramGroup.select().count()
