from datetime import datetime

from loguru import logger
from peewee import (
    BigIntegerField, AutoField, DateTimeField, CharField, DoesNotExist
)

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
- date_added - Дата добавления в базу данных
"""


class UsersAccounts(database.Model):
    """
    Модель для хранения аккаунтов пользователя.
    В таблице users_accounts хранятся аккаунты пользователя.
    """
    id = AutoField()  # ID записи в базе данных
    user_id = BigIntegerField(index=True, null=True)  # id пользователя Telegram
    user_username = CharField(default="", null=True)  # username пользователя Telegram
    user_firstname = CharField(default="", null=True)  # firstname пользователя Telegram
    user_session_string = CharField(
        unique=True)  # стринг сессия аккаунта, который подключил аккаунт для дальнейшего поиска ключевых слов в группах
    phone_number_session_string = CharField(default="", null=True)  # номер телефона аккаунта
    date_added = DateTimeField(default=datetime.now)  # Дата добавления в базу данных

    class Meta:
        """Метаданные таблицы аккаунтов пользователей"""
        table_name = 'users_accounts'


def write_account_to_user_table(user_id: int, session_string: str, phone_number: str = "", user_username: str = "",
                                user_firstname: str = ""):
    """
    Записывает или обновляет аккаунт пользователя в таблице users_accounts.

    :param user_id: (int) ID пользователя в Telegram.
    :param session_string: (str) Строка сессии Telegram.
    :param phone_number: (str) Номер телефона аккаунта (по умолчанию "").
    :param user_username: (str) Юзернейм пользователя в Telegram (по умолчанию "").
    :param user_firstname: (str) Имя пользователя в Telegram (по умолчанию "").
    :return: (UsersAccounts | None) Созданный или обновленный объект аккаунта или None при ошибке.
    """
    try:
        account, created = UsersAccounts.get_or_create(
            user_session_string=session_string,
            defaults={
                "phone_number_session_string": phone_number,
                "user_id": user_id,
                "user_username": user_username,
                "user_firstname": user_firstname
            }
        )
        if not created:
            account.phone_number_session_string = phone_number or account.phone_number_session_string
            account.user_id = user_id or account.user_id
            account.user_username = user_username or account.user_username
            account.user_firstname = user_firstname or account.user_firstname
            account.save()
        logger.info(f"Аккаунт {phone_number} записан в users_accounts для user_id={user_id}")
        return account
    except Exception as e:
        logger.exception(f"Ошибка при записи в users_accounts: {e}")
        return None


def getting_account():
    """
    Получение списка сессий всех аккаунтов пользователей из базы данных.

    :return: (list[str]) Список строк сессий пользователей.
    """
    records = []
    for record in UsersAccounts.select(UsersAccounts.user_session_string):
        records.append(record.user_session_string)

    return records


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
