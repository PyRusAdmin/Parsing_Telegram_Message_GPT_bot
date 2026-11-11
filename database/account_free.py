from datetime import datetime

from loguru import logger  # https://github.com/Delgan/loguru
from peewee import CharField, BigIntegerField, DateTimeField

from database.database import database

"""
Таблица с аккаунтами, подключаемыми администратором бота, для общего использования
"""


class AccountFree(database.Model):
    """Свободные аккаунты для подключения, которые подключает администратор бота"""
    session_string = CharField(unique=True)  # Уникальность для защиты от дубликатов
    phone_number = CharField(default="", null=True)  # Номер телефона аккаунта
    first_name = CharField(default="", null=True)  # Имя аккаунта
    last_name = CharField(default="", null=True)  # Фамилия аккаунта
    account_id = BigIntegerField(default=0, null=True, index=True)  # Telegram ID аккаунта
    date_added = DateTimeField(default=datetime.now)  # Дата добавления аккаунта в базу данных

    class Meta:
        """Метаданные таблицы свободных аккаунтов"""
        table_name = 'account_free'


def ensure_account_free_columns() -> None:
    """
    Автоматически добавляет недостающие колонки в существующую таблицу account_free (миграция схемы SQLite).
    """
    try:
        cursor = database.execute_sql("PRAGMA table_info(account_free)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        cols_to_add = [
            ("phone_number", "TEXT DEFAULT ''"),
            ("first_name", "TEXT DEFAULT ''"),
            ("last_name", "TEXT DEFAULT ''"),
            ("account_id", "INTEGER DEFAULT 0"),
            ("date_added", "DATETIME NULL"),
        ]
        for col_name, col_type in cols_to_add:
            if col_name not in existing_cols:
                try:
                    database.execute_sql(f"ALTER TABLE account_free ADD COLUMN {col_name} {col_type}")
                    logger.info(f"➕ Колонка {col_name} добавлена в таблицу account_free")
                except Exception as alter_err:
                    logger.debug(f"Колонка {col_name} в account_free: {alter_err}")
    except Exception as e:
        logger.warning(f"Ошибка проверки колонок таблицы account_free: {e}")


def write_account_to_db_free(
    session_string: str,
    phone_number: str = "",
    first_name: str = "",
    last_name: str = "",
    account_id: int | None = None
) -> None:
    """
    Запись сессии бесплатного аккаунта администратора в базу данных.

    :param session_string: (str) Строка сессии Telethon.
    :param phone_number: (str) Номер телефона подключаемого аккаунта Telegram.
    :param first_name: (str) Имя аккаунта.
    :param last_name: (str) Фамилия аккаунта.
    :param account_id: (int | None) Telegram ID аккаунта.
    """
    clean_phone = (phone_number or "").lstrip("+")
    acc_id = int(account_id) if account_id else 0

    AccountFree.insert(
        session_string=session_string,
        phone_number=clean_phone,
        first_name=first_name or "",
        last_name=last_name or "",
        account_id=acc_id,
        date_added=datetime.now(),
    ).on_conflict(
        conflict_target=[AccountFree.session_string],
        update={
            AccountFree.phone_number: clean_phone,
            AccountFree.first_name: first_name or "",
            AccountFree.last_name: last_name or "",
            AccountFree.account_id: acc_id,
            AccountFree.date_added: datetime.now(),
        }
    ).execute()

    logger.info(
        f"✅ Бесплатный аккаунт +{clean_phone} ({first_name} {last_name}, ID: {acc_id}) успешно сохранен в account_free"
    )


def delete_account_from_free_db(session_string: str) -> bool:
    """
    Удаляет аккаунт из таблицы account_free по сессии.

    :param session_string: (str) Строка сессии Telethon.
    :return: (bool) True, если аккаунт удален, иначе False.
    """
    try:
        deleted = AccountFree.delete().where(AccountFree.session_string == session_string).execute()
        if deleted:
            logger.info("🗑️ Аккаунт удален из таблицы account_free")
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка при удалении аккаунта из account_free: {e}")
        return False


def getting_free_account() -> list[str]:
    """
    Получение списка свободных сессий аккаунтов из базы данных.

    :return: (list[str]) Список строк сессий свободных аккаунтов.
    """
    records = []
    for record in AccountFree.select(AccountFree.session_string):
        records.append(record.session_string)

    return records


def get_free_accounts_count() -> int:
    """
    Возвращает общее количество свободных аккаунтов в пуле.
    """
    return AccountFree.select().count()
