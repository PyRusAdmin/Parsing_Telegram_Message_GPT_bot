from loguru import logger  # https://github.com/Delgan/loguru
from peewee import CharField

from database.database import database

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
    Запись сессии бесплатного аккаунта администратора в базу данных.

    :param session_string: (str) Строка сессии Telethon.
    :param phone_number: (str) Номер телефона подключаемого аккаунта Telegram.
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


def getting_free_account():
    """
    Получение списка свободных сессий аккаунтов из базы данных.

    :return: (list[str]) Список строк сессий свободных аккаунтов.
    """
    records = []
    for record in AccountFree.select(AccountFree.session_string):
        records.append(record.session_string)

    return records
