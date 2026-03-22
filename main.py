# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from database.database import clean_telegram_id_duplicates, init_database, migrate_add_availability_column
# from handlers.admin.admin import register_handlers_admin_panel
from handlers.admin.admin import router as admin
# from handlers.admin.checking_accounts import register_checking_accounts
from handlers.admin.checking_accounts import router as checking_accounts
# from handlers.admin.checking_group_for_ai import register_handlers_checking_group_for_ai
from handlers.admin.checking_group_for_ai import router as checking_group_for_ai
from handlers.admin.connecting_account import register_handlers_admin_connect_account
# from handlers.admin.language_detection import register_handlers_languages
from handlers.admin.language_detection import router as language_detection
# from handlers.admin.post_log import register_handlers_log
from handlers.admin.post_log import router as post_log
# from handlers.user.checking_group_for_keywords import register_handlers_checking_group_for_keywords
from handlers.user.checking_group_for_keywords import router as checking_group_for_keywords
# from handlers.user.connect_account import register_connect_account_handler
from handlers.user.connect_account import router as connect_account
from handlers.user.connect_group import router as connect_group
# from handlers.user.delete_group_from_database import register_handlers_delete
from handlers.user.delete_group_from_database import router as delete_group_from_database
# from handlers.user.connect_group import register_entering_group_handler
from handlers.user.entering_keyword import router as entering_keyword
from handlers.user.get_dada import router as get_dada
from handlers.user.handlers import router as handlers
# from handlers.user.handlers import register_greeting_handlers
# from handlers.user.pars_ai import register_handlers_pars_ai
from handlers.user.pars_ai import router as pars_ai
# from handlers.user.post_doc import register_handlers_post_doc
from handlers.user.post_doc import router as post_doc
# from handlers.user.stop_tracking import register_stop_tracking_handler
from handlers.user.stop_tracking import router as stop_tracking
from system.dispatcher import dp, bot

# from handlers.user.entering_keyword import register_entering_keyword_handler
# from handlers.user.get_dada import register_data_export_handlers

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
        init_database()  # Создание таблиц
        migrate_add_availability_column()  # Миграция: добавление колонки availability
        clean_telegram_id_duplicates()  # Чистка дублей в базе данных

        """
        Панель пользователя Telegram бота
        """
        # register_greeting_handlers()
        dp.include_router(handlers)  # Регистрация приветственного меню и основных команд
        # register_entering_keyword_handler()
        dp.include_router(entering_keyword)  # Регистрация обработчика для ввода и записи в БД ключевых слов
        # register_entering_group_handler()
        dp.include_router(connect_group)  # Регистрация обработчика для ввода и записи в БД групп (техническая группа)
        # register_data_export_handlers()
        dp.include_router(get_dada)  # Выдача пользователю введенных им данных
        # register_stop_tracking_handler()
        dp.include_router(stop_tracking)  # Остановка отслеживания ключевых слов
        # register_handlers_pars_ai()
        dp.include_router(pars_ai)  # Ищет группы и каналы с помощью ИИ
        # register_handlers_post_doc()
        dp.include_router(post_doc)  # Выдает пользователю документацию к проекту
        # register_connect_account_handler()
        dp.include_router(connect_account)  # Подключение аккаунта
        # register_handlers_checking_group_for_keywords()
        dp.include_router(checking_group_for_keywords)  # Проверка группы на наличие ключевых слов
        # register_handlers_delete()
        dp.include_router(delete_group_from_database)  # Удаление групп из базы данных пользователя

        """
        Панель администратора Telegram бота
        """
        # register_handlers_admin_panel()
        dp.include_router(admin)  # Панель администратора
        # register_handlers_log()
        dp.include_router(post_log)  # Логирование
        # register_handlers_checking_group_for_ai()
        dp.include_router(checking_group_for_ai)  # Присвоение категории группам / каналам
        # register_checking_accounts()
        dp.include_router(checking_accounts)  # ✅ Проверка аккаунтов
        # register_handlers_languages()
        dp.include_router(language_detection)  # Присвоение языка группам / каналам
        register_handlers_admin_connect_account()
        dp.include_router(delete_group_from_database)  # Подключение аккаунтов админом бота

        await dp.start_polling(bot)  # Запуск поллинг обновлений от Telegram

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
