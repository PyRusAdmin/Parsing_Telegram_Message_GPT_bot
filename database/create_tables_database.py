from loguru import logger  # https://github.com/Delgan/loguru

from database.database import (
    database, Account, AccountFree, TelegramGroup, Question, User, PersonalTrackingStats
)
from database.group_user_database import Group
from database.keywords_user_database import Keywords
from database.personal_tracking import PersonalTracking

"""Создает таблицы для базы данных, если ранее не были созданы"""


def migrate_old_table_names():
    """Переименовывает старые имена таблиц (keywords -> users_keywords, account -> users_account, user_groups -> users_groups)"""
    table_renames = [
        ("keywords", "users_keywords"),
        ("account", "users_account"),
        ("user_groups", "users_groups")
    ]
    cursor = database.execute_sql("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    for old_name, new_name in table_renames:
        if old_name in existing_tables and new_name not in existing_tables:
            logger.info(f"🔄 Миграция таблицы: {old_name} -> {new_name}")
            database.execute_sql(f"ALTER TABLE {old_name} RENAME TO {new_name};")
            logger.success(f"✅ Таблица '{old_name}' успешно переименована в '{new_name}'")


def init_database():
    """Инициализация БД и создание таблиц"""
    database.connect(reuse_if_open=True)

    migrate_old_table_names()

    database.create_tables(
        [
            Account,  # Таблица общих аккаунтов (users_account)
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
        "  • Account (users_account) — общие аккаунты для массового AI-поиска\n"
        "  • AccountFree — пул бесплатных аккаунтов от администратора\n"
        "  • TelegramGroup — общая база каналов и групп по категориям\n"
        "  • Question — вопросы пользователей для базы знаний\n"
        "  • User — профили пользователей бота (язык, Stars)\n"
        "  • PersonalTracking — персональные настройки трекинга и сессий\n"
        "  • PersonalTrackingStats — статистика трекинга и покупок слотов\n"
        "  • Keywords (users_keywords) — ключевые слова пользователей для отслеживания\n"
        "  • Group (users_groups) — отслеживаемые пользователями каналы и группы"
    )

    database.close()
