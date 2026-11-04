from loguru import logger  # https://github.com/Delgan/loguru

from database.database import (
    database, Account, AccountFree, TelegramGroup, Question, User, PersonalTrackingStats
)
from database.group_user_database import Group
from database.keywords_user_database import Keywords
from database.personal_tracking import PersonalTracking

"""Создает таблицы для базы данных, если ранее не были созданы"""


def migrate_old_table_names():
    """Переименовывает старые имена таблиц и колонок в новую структуру (users_keywords, users_accounts, users_groups)"""
    table_renames = [
        ("keywords", "users_keywords"),
        ("account", "users_accounts"),
        ("users_account", "users_accounts"),
        ("user_groups", "users_groups"),
        ("personal_tracking", "users_personal_tracking")
    ]
    cursor = database.execute_sql("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    for old_name, new_name in table_renames:
        if old_name in existing_tables and new_name not in existing_tables:
            logger.info(f"🔄 Миграция таблицы: {old_name} -> {new_name}")
            database.execute_sql(f"ALTER TABLE {old_name} RENAME TO {new_name};")
            logger.success(f"✅ Таблица '{old_name}' успешно переименована в '{new_name}'")
            existing_tables.remove(old_name)
            existing_tables.add(new_name)

    # Проверяем колонки в users_accounts
    if "users_accounts" in existing_tables:
        cursor_cols = database.execute_sql("PRAGMA table_info(users_accounts);")
        existing_cols = {row[1] for row in cursor_cols.fetchall()}

        if "session_string" in existing_cols and "user_session_string" not in existing_cols:
            logger.info("🔄 Миграция: переименование колонки 'session_string' -> 'user_session_string' в 'users_accounts'...")
            database.execute_sql("ALTER TABLE users_accounts RENAME COLUMN session_string TO user_session_string;")
            existing_cols.remove("session_string")
            existing_cols.add("user_session_string")

        if "phone_number" in existing_cols and "phone_number_session_string" not in existing_cols:
            logger.info("🔄 Миграция: переименование колонки 'phone_number' -> 'phone_number_session_string' в 'users_accounts'...")
            database.execute_sql("ALTER TABLE users_accounts RENAME COLUMN phone_number TO phone_number_session_string;")
            existing_cols.remove("phone_number")
            existing_cols.add("phone_number_session_string")

        columns_to_add_accounts = [
            ("user_id", "INTEGER"),
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("phone_number_session_string", "VARCHAR(255)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_accounts:
            if col_name not in existing_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_accounts'...")
                database.execute_sql(f"ALTER TABLE users_accounts ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_accounts'")
                existing_cols.add(col_name)

    # Проверяем колонки в users_keywords
    if "users_keywords" in existing_tables:
        cursor_kw_cols = database.execute_sql("PRAGMA table_info(users_keywords);")
        existing_kw_cols = {row[1] for row in cursor_kw_cols.fetchall()}

        columns_to_add_kw = [
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("user_session_string", "VARCHAR(500)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_kw:
            if col_name not in existing_kw_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_keywords'...")
                database.execute_sql(f"ALTER TABLE users_keywords ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_keywords'")
                existing_kw_cols.add(col_name)

    # Проверяем колонки в users_groups
    if "users_groups" in existing_tables:
        cursor_gr_cols = database.execute_sql("PRAGMA table_info(users_groups);")
        existing_gr_cols = {row[1] for row in cursor_gr_cols.fetchall()}

        columns_to_add_gr = [
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("id_group", "INTEGER"),
            ("name_group", "VARCHAR(255)"),
            ("user_session_string", "VARCHAR(500)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_gr:
            if col_name not in existing_gr_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_groups'...")
                database.execute_sql(f"ALTER TABLE users_groups ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_groups'")
                existing_gr_cols.add(col_name)


def init_database():
    """Инициализация БД и создание таблиц"""
    database.connect(reuse_if_open=True)

    migrate_old_table_names()

    database.create_tables(
        [
            Account,  # Таблица аккаунтов пользователей (users_accounts)
            AccountFree,  # Таблица бесплатных аккаунтов от админа (выдаются пользователям для парсинга ключевых слов)
            TelegramGroup,  # Таблица общей базы Telegram-групп и каналов по категориям
            Question,  # Таблица вопросов и ответов пользователей для расширения базы знаний
            User,  # Таблица профилей пользователей Telegram (язык, баланс Stars, регистрация)
            PersonalTracking,
            # Таблица настроек персонального отслеживания (целевые группы, привязанные сессии, ID техгруппы)
            PersonalTrackingStats,  # Таблица статистики персонального отслеживания (подключение групп, покупка слотов)
            Keywords,  # Таблица ключевых слов пользователей (users_keywords)
            Group  # Таблица целевых каналов и групп пользователей для мониторинга (users_groups)
        ],
        safe=True
    )

    logger.info(
        "✅ База данных инициализирована. Проверены/созданы таблицы:\n"
        "  • Account (users_accounts) — аккаунты пользователей для поиска ключевых слов\n"
        "  • AccountFree — пул бесплатных аккаунтов от администратора\n"
        "  • TelegramGroup — общая база каналов и групп по категориям\n"
        "  • Question — вопросы пользователей для базы знаний\n"
        "  • User — профили пользователей бота (язык, Stars)\n"
        "  • PersonalTracking (users_personal_tracking) — данные о пользователе бота, персональные настройки трекинга\n"
        "  • PersonalTrackingStats — статистика трекинга и покупок слотов\n"
        "  • Keywords (users_keywords) — ключевые слова пользователей для отслеживания\n"
        "  • Group (users_groups) — отслеживаемые пользователями каналы и группы"
    )

    database.close()
