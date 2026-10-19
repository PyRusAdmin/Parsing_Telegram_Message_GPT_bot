from loguru import logger  # https://github.com/Delgan/loguru

from database.database import database, Account, AccountFree, UserAccountsTable, TelegramGroup, Question, User, \
    PersonalTracking, PersonalTrackingStats
from database.group_user_database import Group
from database.keywords_user_database import Keywords

"""Создает таблицы для базы данных, если ранее небыли созданы"""


def init_database():
    """Инициализация БД и создание таблиц"""
    database.connect(reuse_if_open=True)

    try:
        database.execute_sql('PRAGMA journal_mode = WAL;')
    except Exception as e:
        logger.warning(f"Failed to set WAL journal mode: {e}")

    database.create_tables([Account], safe=True)  # Создание таблицы аккаунтов
    database.create_tables([AccountFree], safe=True)  # Создание таблицы аккаунтов для подключения (свободных)
    database.create_tables([UserAccountsTable], safe=True)  # Создание таблицы аккаунтов пользователя

    database.create_tables([TelegramGroup], safe=True)  # Создание таблицы Telegram-групп
    database.create_tables([Question], safe=True)  # Создание таблицы вопросов пользователей для расширения базы знаний
    database.create_tables([User], safe=True)  # Создание таблицы пользователей

    database.create_tables([PersonalTracking, PersonalTrackingStats], safe=True)
    logger.info("✅ Таблицы персонального отслеживания (personal_tracking) готовы.")

    # Создаем таблицу с ключевыми словами от пользователей, для парсинга сообщений в Telegram
    database.create_tables([Keywords], safe=True)
    logger.info("✅ Таблица (keywords) для Ключевых слов создана.")

    # Создаем таблицу с группами / каналами от пользователей, для последующего парсинга сообщений в Telegram
    database.create_tables([Group], safe=True)
    logger.info("✅ Таблица (group) для Групп / каналов слов создана.")

    # Проверка наличия колонок stars и last_free_download_at в таблице user (SQLite-миграция)
    cursor = database.cursor()  #
    cursor.execute("PRAGMA table_info(user)")
    columns = [row[1] for row in cursor.fetchall()]
    if "stars" not in columns:
        logger.info("Migrating database: adding 'stars' column to user table")
        database.execute_sql('ALTER TABLE "user" ADD COLUMN "stars" INTEGER DEFAULT 0;')
    if "last_free_download_at" not in columns:
        logger.info("Migrating database: adding 'last_free_download_at' column to user table")
        database.execute_sql('ALTER TABLE "user" ADD COLUMN "last_free_download_at" DATETIME;')

    database.close()
