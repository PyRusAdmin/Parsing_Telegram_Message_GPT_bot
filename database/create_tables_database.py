from loguru import logger  # https://github.com/Delgan/loguru

from database.database import (
    database, Account, AccountFree, TelegramGroup, Question, User, PersonalTracking, PersonalTrackingStats
)
from database.group_user_database import Group
from database.keywords_user_database import Keywords

"""Создает таблицы для базы данных, если ранее небыли созданы"""


def init_database():
    """Инициализация БД и создание таблиц"""
    database.connect(reuse_if_open=True)

    database.create_tables(
        [
            Account,  # Создание таблицы аккаунтов (Аккаунты используются для массового поиска групп / каналов)
            AccountFree,  # Создание таблицы аккаунтов для подключения(Аккаунты используемые для парсинга ключевых слов)
            TelegramGroup,  # Создание таблицы Telegram-групп
            Question,  # Создание таблицы вопросов пользователей для расширения базы знаний
            User,  # Создание таблицы пользователей
            PersonalTracking,
            PersonalTrackingStats,
            Keywords,
            Group

        ],
        safe=True
    )

    logger.info("✅ Таблицы: Account, AccountFree, TelegramGroup, Question, User, PersonalTracking, PersonalTrackingStats, Keywords, Group")

    database.close()
