# -*- coding: utf-8 -*-
import os

from loguru import logger  # https://github.com/Delgan/loguru

from core.config import PROXY_USER, PROXY_PASSWORD, PROXY_IP, PROXY_PORT


def setup_proxy():
    """
    Настраивает системные переменные окружения для использования HTTP/HTTPS прокси.

    Функция устанавливает переменные окружения `http_proxy` и `https_proxy` на основе
    данных, загруженных из конфигурационного файла (логин, пароль, IP и порт прокси-сервера).
    Это необходимо для обхода сетевых ограничений при работе с внешними API (например, Groq)
    или подключении к Telegram.

    Использует прокси-данные из модуля `core.config`:
        - PROXY_USER: логин для аутентификации на прокси
        - PROXY_PASSWORD: пароль
        - PROXY_IP: IP-адрес прокси-сервера
        - PROXY_PORT: порт прокси

    Raises:
        Exception: В случае ошибки устанавливается логирование с помощью `logger.exception`.

    Note:
        Прокси настраивается только на время выполнения скрипта.
        Используется схема 'http' для обоих протоколов (так как многие прокси поддерживают HTTPS через HTTP-туннель).
    """
    try:
        # Указываем прокси для HTTP и HTTPS
        os.environ['http_proxy'] = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}"
        os.environ['https_proxy'] = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_IP}:{PROXY_PORT}"
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    setup_proxy()
