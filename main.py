# -*- coding: utf-8 -*-
import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.admin.admin import register_handlers_admin_panel
from handlers.admin.checking_accounts import register_checking_accounts
from handlers.admin.checking_group_for_ai import register_handlers_checking_group_for_ai
from handlers.admin.language_detection import register_handlers_languages
from handlers.admin.post_log import register_handlers_log
from handlers.user.checking_group_for_keywords import register_handlers_checking_group_for_keywords
from handlers.user.connect_account import register_connect_account_handler
from handlers.user.connect_group import register_entering_group_handler
from handlers.user.delete_group_from_database import register_handlers_delete
from handlers.user.entering_keyword import register_entering_keyword_handler
from handlers.user.get_dada import register_data_export_handlers
from handlers.user.handlers import register_greeting_handlers
from handlers.user.pars_ai import register_handlers_pars_ai
from handlers.user.post_doc import register_handlers_post_doc
from handlers.user.stop_tracking import register_stop_tracking_handler
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
        Панель пользователя
        """
        register_greeting_handlers()  # Регистрация приветственного меню и основных команд
        register_entering_keyword_handler()  # Регистрация обработчика для ввода и записи в БД ключевых слов
        register_entering_group_handler()  # Регистрация обработчика для ввода и записи в БД групп (техническая группа)
        register_data_export_handlers()  # Выдача пользователю введенных им данных
        register_stop_tracking_handler()  # Остановка отслеживания ключевых слов
        register_handlers_pars_ai()  # Ищет группы и каналы с помощью ИИ
        register_handlers_post_doc()  # Выдает пользователю документацию к проекту
        register_connect_account_handler()  # Подключение аккаунта
        register_handlers_checking_group_for_keywords()  # 🔍 Проверка группы на наличие ключевых слов
        register_handlers_delete()  # Удаление групп из базы данных пользователя

        """
        Панель администратора
        """
        register_handlers_admin_panel()  # Панель администратора
        register_handlers_log()  # Логирование
        register_handlers_checking_group_for_ai()  # Присвоение категории группам / каналам
        register_checking_accounts()  # ✅ Проверка аккаунтов
        register_handlers_languages()  # Присвоение языка группам / каналам

        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
