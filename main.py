# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import sys

from loguru import logger

# Путь к корню проекта
project_root = os.path.dirname(os.path.abspath(__file__))

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

processes = []
for cmd in commands:
    try:
        p = subprocess.Popen(cmd, env=env)
        processes.append(p)
    except Exception as e:
        logger.warning(f"⚠️ Не удалось запустить команду '{cmd[0]}': {e}")

try:
    # Ожидаем завершения всех процессов
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    logger.info("Interrupt received, terminating subprocesses...")
    for p in processes:
        p.terminate()

