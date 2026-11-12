from loguru import logger  # https://github.com/Delgan/loguru

from database.account_free import AccountFree, ensure_account_free_columns
from database.database import database, TelegramGroups
from database.users_accounts import UsersAccounts, ensure_users_accounts_columns
from database.users_groups import UsersGroups
from database.users_keywords import UsersKeywords
from database.users_personal_trackings import UsersPersonalTrackings
from database.users_questions import UsersQuestions

"""Создает таблицы для базы данных, если ранее не были созданы"""


def init_database():
    """
    Инициализация базы данных и создание таблиц, если они не существуют.
    """
    database.connect(reuse_if_open=True)

    # Создание таблиц для базы данных
    database.create_tables(
        [
            UsersAccounts,  # Таблица аккаунтов пользователей
            AccountFree,  # Таблица бесплатных аккаунтов от админа (выдаются пользователям для парсинга ключевых слов)
            TelegramGroups,  # Таблица общей базы Telegram-групп и каналов по категориям
            UsersQuestions,  # Таблица вопросов и ответов пользователей для расширения базы знаний
            UsersPersonalTrackings,  # Данные о пользователях настройки персонального отслеживания
            UsersKeywords,  # Ключевые слова пользователей
            UsersGroups  # Целевые каналы и группы пользователей для мониторинга
        ],
        safe=True
    )

    # Проверяем и при необходимости добавляем недостающие колонки в таблицы
    ensure_account_free_columns()
    ensure_users_accounts_columns()

    logger.info(
        "✅ База данных инициализирована. Проверены/созданы таблицы:\n"
        "  • Account (users_accounts) — аккаунты пользователей для поиска ключевых слов\n"
        "  • AccountFree — пул бесплатных аккаунтов от администратора\n"
        "  • TelegramGroup — общая база каналов и групп по категориям\n"
        "  • Question (users_questions) — вопросы пользователей для базы знаний\n"
        "  • UsersPersonalTrackings (users_personal_trackings) — профили пользователей бота и персональный трекинг\n"
        "  • Keywords (users_keywords) — ключевые слова пользователей для отслеживания\n"
        "  • Group (users_groups) — отслеживаемые пользователями каналы и группы"
    )

    database.close()
