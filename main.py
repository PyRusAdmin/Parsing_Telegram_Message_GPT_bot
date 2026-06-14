# -*- coding: utf-8 -*-
import os
import subprocess
import sys

from loguru import logger


# logger.add("logs/log.log", rotation="1 MB", compression="zip", enqueue=True)  # Логирование бота


# async def main() -> None:
#     """
#     Основная асинхронная функция для запуска Telegram-бота.

#     Выполняет следующие действия:
#     1. Инициализирует базу данных с помощью `init_db()`.
#     2. Регистрирует все обработчики команд и сообщений через соответствующие функции регистрации.
#     3. Запускает поллинг обновлений от Telegram через `dp.start_polling(bot)`.

#     Обработчики включают:
#     - Приветственное меню и основные команды.
#     - Ввод и хранение ключевых слов для отслеживания.
#     - Подключение пользовательских аккаунтов Telegram (.session файлы).
#     - Управление отслеживанием и остановкой парсинга.
#     - Экспорт данных, логирование, поиск групп через ИИ, выдачу документации и т.д.

#     :return: None
#     """

#     try:
#         """
#         Рабата с базой данных
#         """
#         init_database()
#         clean_telegram_id_duplicates()

#         """
#         Панель пользователя Telegram бота
#         """
#         dp.include_router(handlers)
#         dp.include_router(entering_keyword)
#         dp.include_router(connect_group)
#         dp.include_router(get_dada)
#         dp.include_router(stop_tracking)
#         dp.include_router(pars_ai)
#         dp.include_router(post_doc)
#         dp.include_router(connect_account)
#         dp.include_router(checking_group_for_keywords)
#         dp.include_router(delete_group_from_database)
#         dp.include_router(transfer_settings)

#         """
#         Панель администратора Telegram бота
#         """
#         dp.include_router(admin)
#         dp.include_router(post_log)
#         dp.include_router(checking_group_for_ai)
#         dp.include_router(checking_accounts)
#         dp.include_router(language_detection)
#         dp.include_router(connecting_account)

#         # Миграция: приводим все категории к нижнему регистру

#         logger.info("🔄 Запуск миграции категорий в нижнем регистре...")
#         updated = migrate_categories_to_lowercase()
#         if updated:
#             logger.info(f"✅ Обновлено {updated} категорий на нижний регистр")

#         # Determine port
#         port_env = os.getenv("PORT")
#         if not port_env or port_env == "_____" or not port_env.isdigit():
#             port = 8000
#         else:
#             port = int(port_env)

#         logger.info(f"🌐 Starting FastAPI Web Server on http://0.0.0.0:{port}")
#         config = uvicorn.Config(app, host="0.0.0.0", port=port, loop="asyncio")
#         server = uvicorn.Server(config)

#         await asyncio.gather(
#             dp.start_polling(bot),
#             server.serve()
#         )

#     except Exception as e:
#         logger.exception(e)


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#     asyncio.run(main())




# Настройка логирования: указываем файл, размер ротации и сжатие
logger.add("logs/log.log", rotation="1 MB", compression="zip")

# Путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))

import shutil

tuna_cmd = "tuna"
if not shutil.which(tuna_cmd):
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        possible_path = os.path.join(local_appdata, "Microsoft", "WindowsApps", "tuna.exe")
        if os.path.exists(possible_path):
            tuna_cmd = possible_path

# Команды с указанием PYTHONPATH
commands = [
    [sys.executable, "bot.py"],  # запускает бота и веб-сервер
    [
        tuna_cmd,
        "http",
        "3000",
        "--subdomain=parsingbot",
    ],  # запускает туннель tuna на порту 3000 с поддоменом parsingbot
]

# Установить PYTHONPATH на корень проекта и настроить PORT
env = os.environ.copy()
env["PYTHONPATH"] = project_root
env["PORT"] = "3000"

processes = [subprocess.Popen(cmd, env=env) for cmd in commands]

try:
    # Ожидаем завершения всех процессов
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    logger.info("Interrupt received, terminating subprocesses...")
    for p in processes:
        p.terminate()