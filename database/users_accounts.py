from datetime import datetime

from loguru import logger
from peewee import BigIntegerField, AutoField, DateTimeField, CharField, BooleanField, DoesNotExist

from database.database import database

"""
В таблице users_accounts будут храниться аккаунты пользователя.

Структура users_accounts:
- id - ID записи в базе данных
- user_id - id пользователя Telegram 
- user_username - username пользователя Telegram
- user_firstname - firstname пользователя Telegram
- user_session_string - стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах 
- phone_number_session_string - номер телефона аккаунта
- account_title - пользовательское название кампании/темы (например, "Диваны", "Холодильники")
- target_group_id - Telegram ID персональной технической группы результатов для этого аккаунта
- target_group_link - инвайт-ссылка на техническую группу результатов
- track_all_chats - флаг отслеживания ВСЕХ чатов/групп (открытых и закрытых), где состоит аккаунт
- is_active - флаг активности фонового отслеживания для данного аккаунта
- date_added - Дата добавления в базу данных
"""


class UsersAccounts(database.Model):
    """
    Модель для хранения аккаунтов пользователя и их настроек мониторинга.
    В таблице users_accounts хранятся аккаунты пользователя.
    """
    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(index=True, null=True)  # id пользователя Telegram
    user_username = CharField(default="", null=True)  # username пользователя Telegram
    user_firstname = CharField(default="", null=True)  # firstname пользователя Telegram
    user_session_string = CharField(
        unique=True)  # стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах
    phone_number_session_string = CharField(default="", null=True)  # номер телефона аккаунта
    account_title = CharField(default="", null=True)  # название темы/кампании ("Диваны", "Холодильники")
    target_group_id = BigIntegerField(null=True)  # ID технической группы для пересылки
    target_group_link = CharField(default="", null=True)  # Ссылка на техническую группу
    track_all_chats = BooleanField(default=False)  # Отслеживать ли все группы, где состоит аккаунт
    is_active = BooleanField(default=False)  # Запущен ли мониторинг по этому аккаунту
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные таблицы аккаунтов пользователей"""
        table_name = 'users_accounts'


def ensure_users_accounts_columns() -> None:
    """
    Автоматически добавляет недостающие колонки в существующую таблицу users_accounts (миграция схемы SQLite).
    """
    try:
        cursor = database.execute_sql("PRAGMA table_info(users_accounts)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        cols_to_add = [
            ("account_title", "TEXT DEFAULT ''"),
            ("target_group_id", "INTEGER NULL"),
            ("target_group_link", "TEXT DEFAULT ''"),
            ("track_all_chats", "INTEGER DEFAULT 0"),
            ("is_active", "INTEGER DEFAULT 0"),
        ]
        for col_name, col_type in cols_to_add:
            if col_name not in existing_cols:
                try:
                    database.execute_sql(f"ALTER TABLE users_accounts ADD COLUMN {col_name} {col_type}")
                    logger.info(f"➕ Колонка {col_name} добавлена в таблицу users_accounts")
                except Exception as alter_err:
                    logger.debug(f"Колонка {col_name} в users_accounts: {alter_err}")
    except Exception as e:
        logger.warning(f"Ошибка проверки колонок таблицы users_accounts: {e}")


def write_account_to_user_table(user_id: int, session_string: str, phone_number: str = "", user_username: str = "",
                                user_firstname: str = "", account_title: str = ""):
    """
    Записывает или обновляет аккаунт пользователя в таблице users_accounts.

    :param user_id: (int) ID пользователя в Telegram.
    :param session_string: (str) Строка сессии Telegram.
    :param phone_number: (str) Номер телефона аккаунта (по умолчанию "").
    :param user_username: (str) Юзернейм пользователя в Telegram (по умолчанию "").
    :param user_firstname: (str) Имя пользователя в Telegram (по умолчанию "").
    :param account_title: (str) Тема/название кампании (например, "Диваны").
    :return: (UsersAccounts | None) Созданный или обновленный объект аккаунта или None при ошибке.
    """
    try:
        account, created = UsersAccounts.get_or_create(
            user_session_string=session_string,
            defaults={
                "phone_number_session_string": phone_number,
                "user_id": user_id,
                "user_username": user_username,
                "user_firstname": user_firstname,
                "account_title": account_title or (f"Аккаунт {phone_number}" if phone_number else "Мой аккаунт")
            }
        )
        if not created:
            account.phone_number_session_string = phone_number or account.phone_number_session_string
            account.user_id = user_id or account.user_id
            account.user_username = user_username or account.user_username
            account.user_firstname = user_firstname or account.user_firstname
            if account_title:
                account.account_title = account_title
            account.save()
        logger.info(f"Аккаунт {phone_number} записан в users_accounts для user_id={user_id}")
        return account
    except Exception as e:
        logger.exception(f"Ошибка при записи в users_accounts: {e}")
        return None


def get_user_accounts_list(user_id: int) -> list[UsersAccounts]:
    """
    Получает список всех аккаунтов пользователя из users_accounts.
    """
    return list(
        UsersAccounts.select()
        .where(UsersAccounts.user_id == user_id)
        .order_by(UsersAccounts.date_added.desc())
    )


def get_account_by_id(account_id: int) -> UsersAccounts | None:
    """
    Получает аккаунт по ID.
    """
    return UsersAccounts.get_or_none(UsersAccounts.id == account_id)


def get_account_by_session(session_string: str) -> UsersAccounts | None:
    """
    Получает аккаунт по строке сессии.
    """
    return UsersAccounts.get_or_none(UsersAccounts.user_session_string == session_string)


def update_account_settings(account_id: int, **kwargs) -> bool:
    """
    Обновляет поля аккаунта (account_title, target_group_id, target_group_link, track_all_chats, is_active).
    """
    try:
        acc = UsersAccounts.get_or_none(UsersAccounts.id == account_id)
        if not acc:
            return False
        for k, v in kwargs.items():
            if hasattr(acc, k):
                setattr(acc, k, v)
        acc.save()
        return True
    except Exception as e:
        logger.error(f"Ошибка обновления настроек аккаунта {account_id}: {e}")
        return False


def delete_account_by_id(account_id: int) -> bool:
    """
    Удаляет аккаунт по его ID.
    """
    try:
        acc = UsersAccounts.get_or_none(UsersAccounts.id == account_id)
        if acc:
            acc.delete_instance()
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка удаления аккаунта {account_id}: {e}")
        return False


# def getting_account():
#     """
#     Получение списка сессий всех аккаунтов пользователей из базы данных.
#
#     :return: (list[str]) Список строк сессий пользователей.
#     """
#     records = []
#     for record in UsersAccounts.select(UsersAccounts.user_session_string):
#         records.append(record.user_session_string)
#
#     return records


async def delete_account_from_db(session_string: str) -> None:
    """
    Удаляет аккаунт из таблицы users_accounts по session_string.

    :param session_string: (str) Строка сессии удаляемого аккаунта.
    """
    try:
        # Ищем аккаунт по user_session_string
        account = UsersAccounts.get(UsersAccounts.user_session_string == session_string)
        phone_number = account.phone_number_session_string
        logger.info(f"Найден аккаунт для удаления: {phone_number}")
        # Удаляем запись
        account.delete_instance()
        logger.info(f"Аккаунт {phone_number} успешно удалён из базы данных.")
    except DoesNotExist:
        logger.info(f"Аккаунт с session_string='{session_string}' не найден в базе.")
    except Exception as e:
        logger.exception("Ошибка при удалении аккаунта")
        logger.info(f"Ошибка при удалении аккаунта: {e}")
