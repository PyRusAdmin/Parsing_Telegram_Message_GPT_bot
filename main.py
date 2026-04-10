# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from loguru import logger

from database.database import (
    clean_telegram_id_duplicates, init_database, migrate_add_availability_column, migrate_link_column_to_nullable
)
from handlers.admin.admin import router as admin
from handlers.admin.checking_accounts import router as checking_accounts
from handlers.admin.checking_group_for_ai import router as checking_group_for_ai
from handlers.admin.connecting_account import router as connecting_account
from handlers.admin.language_detection import router as language_detection
from handlers.admin.post_log import router as post_log
from handlers.user.checking_group_for_keywords import router as checking_group_for_keywords
from handlers.user.connect_account import router as connect_account
from handlers.user.connect_group import router as connect_group
from handlers.user.delete_group_from_database import router as delete_group_from_database
from handlers.user.entering_keyword import router as entering_keyword
from handlers.user.get_dada import router as get_dada
from handlers.user.handlers import router as handlers
from handlers.user.pars_ai import router as pars_ai
from handlers.user.post_doc import router as post_doc
from handlers.user.stop_tracking import router as stop_tracking
from system.dispatcher import dp, bot

logger.add("logs/log.log", rotation="1 MB", compression="zip", enqueue=True)  # Логирование бота


async def main() -> None:
    """
    Основная асинхронная функция для запуска Telegram-бота.

    Выполняет следующие действия:
    1. Инициализирует базу данных с помощью `init_db()`.
    2. Регистрирует все обработчики команд и сообщений через соответствующие функции регистрации.
    3. Запускает поллинг обновлений от Telegram через `dp.start_polling(bot)`.

    Обработчики включают:
    - Приветственное меню и основные команды.
    - Ввод и хранение ключевых слов для отслеживания.
    - Подключение пользовательских аккаунтов Telegram (.session файлы).
    - Управление отслеживанием и остановкой парсинга.
    - Экспорт данных, логирование, поиск групп через ИИ, выдачу документации и т.д.

    :return: None
    """

    try:
        """
        Рабата с базой данных
        """
        init_database()
        migrate_add_availability_column()
        migrate_link_column_to_nullable()
        clean_telegram_id_duplicates()

        """
        Панель пользователя Telegram бота
        """
        dp.include_router(handlers)
        dp.include_router(entering_keyword)
        dp.include_router(connect_group)
        dp.include_router(get_dada)
        dp.include_router(stop_tracking)
        dp.include_router(pars_ai)
        dp.include_router(post_doc)
        dp.include_router(connect_account)
        dp.include_router(checking_group_for_keywords)
        dp.include_router(delete_group_from_database)

        """
        Панель администратора Telegram бота
        """
        dp.include_router(admin)
        dp.include_router(post_log)
        dp.include_router(checking_group_for_ai)
        dp.include_router(checking_accounts)
        dp.include_router(language_detection)
        dp.include_router(connecting_account)

        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
