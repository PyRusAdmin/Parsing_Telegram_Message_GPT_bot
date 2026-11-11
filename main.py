import os
import shutil
import subprocess
import sys

from loguru import logger  # https://github.com/Delgan/loguru


def run_main():
    """
    Запуск связки туннеля Tuna, Telegram-бота и FastAPI веб-сервера.
    """
    # Путь к корню проекта
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Папка для логов
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Инициализируем команду tuna значением по умолчанию (защита от UnboundLocalError)
    tuna_cmd = "tuna"

    # Проверяем наличие исполняемого файла tuna
    local_root_tuna = os.path.join(project_root, "tuna.exe")
    if os.path.exists(local_root_tuna):
        tuna_cmd = local_root_tuna
    elif not shutil.which(tuna_cmd):
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            possible_path = os.path.join(local_appdata, "Microsoft", "WindowsApps", "tuna.exe")
            if os.path.exists(possible_path):
                tuna_cmd = possible_path

    has_tuna = os.path.exists(tuna_cmd) or shutil.which(tuna_cmd) is not None

    # Установить PYTHONPATH на корень проекта и настроить PORT
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root
    env["PORT"] = "3000"

    processes = []

    # 1. Запуск туннеля Tuna (в фоне без перехвата консоли)
    if has_tuna:
        tuna_log_path = os.path.join(logs_dir, "tuna.log")
        tuna_command = [
            tuna_cmd,
            "http",
            "3000",
            "--subdomain=support-manager-bot",
            "--log",
            tuna_log_path,
        ]
        try:
            # Перенаправляем вывод туннеля, чтобы интерактивный интерфейс Tuna не перехватывал консоль
            # и не затирал логи Telegram-бота и веб-сервера
            p_tuna = subprocess.Popen(
                tuna_command,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            processes.append(p_tuna)
            logger.info("🌐 Туннель Tuna запущен в фоне (логи: logs/tuna.log, поддомен: support-manager-bot)")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось запустить туннель Tuna: {e}")
    else:
        logger.warning("⚠️ Утилита tuna не найдена. Приложение будет работать локально на порту 3000.")

    # 2. Запуск основного процесса бота и веб-сервера (с выводом логов прямо в консоль)
    bot_command = [sys.executable, os.path.join(project_root, "bot.py")]
    try:
        p_bot = subprocess.Popen(bot_command, env=env)
        processes.append(p_bot)
        logger.info("🤖 Запуск Telegram-бота и веб-сервера...")
    except Exception as e:
        logger.exception(f"❌ Не удалось запустить bot.py: {e}")

    try:
        # Ожидаем завершения процессов
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения (Ctrl+C), останавливаем процессы...")
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass
        for p in processes:
            try:
                p.wait(timeout=3)
            except Exception:
                p.kill()
        logger.info("Все процессы успешно остановлены.")


if __name__ == "__main__":
    run_main()
