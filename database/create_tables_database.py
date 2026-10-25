from loguru import logger  # https://github.com/Delgan/loguru

from database.database import (
    database, Account, AccountFree, TelegramGroup, Question, User, PersonalTracking, PersonalTrackingStats
)
from database.group_user_database import Group
from database.keywords_user_database import Keywords

"""Создает таблицы для базы данных, если ранее не были созданы"""


def init_database():
    """Инициализация БД и создание таблиц"""
    database.connect(reuse_if_open=True)

    database.create_tables(
        [
            Account,  # Таблица общих аккаунтов (используются для массового поиска групп/каналов через AI)
            AccountFree,  # Таблица бесплатных аккаунтов от админа (выдаются пользователям для парсинга ключевых слов)
            TelegramGroup,  # Таблица общей базы Telegram-групп и каналов по категориям
            Question,  # Таблица вопросов и ответов пользователей для расширения базы знаний
            User,  # Таблица профилей пользователей Telegram (язык, баланс Stars, регистрация)
            PersonalTracking,  # Таблица настроек персонального отслеживания (целевые группы, привязанные сессии, ID техгруппы)
            PersonalTrackingStats,  # Таблица статистики персонального отслеживания (подключение групп, покупка слотов)
            Keywords,  # Таблица ключевых слов пользователей для фильтрации сообщений
            Group  # Таблица целевых каналов и групп пользователей для мониторинга (user_groups)
        ],
        safe=True
    )

    logger.info(
        "✅ База данных инициализирована. Проверены/созданы таблицы:\n"
        "  • Account — общие аккаунты для массового AI-поиска\n"
        "  • AccountFree — пул бесплатных аккаунтов от администратора\n"
        "  • TelegramGroup — общая база каналов и групп по категориям\n"
        "  • Question — вопросы пользователей для базы знаний\n"
        "  • User — профили пользователей бота (язык, Stars)\n"
        "  • PersonalTracking — персональные настройки трекинга и сессий\n"
        "  • PersonalTrackingStats — статистика трекинга и покупок слотов\n"
        "  • Keywords — ключевые слова пользователей для отслеживания\n"
        "  • Group (user_groups) — отслеживаемые пользователями каналы и группы"
    )

    database.close()
