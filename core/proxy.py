# -*- coding: utf-8 -*-
import os

import python_socks.async_.asyncio
import requests
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


class Proxy:
    """
    Класс для проверки работоспособности прокси-серверов и работы с прокси из базы данных.
    """

    async def reading_proxy_data_from_the_database(self):
        """
        Считывает данные прокси из базы данных.

        :return: Словарь с данными прокси или None при ошибке
        """
        await self.checking_the_proxy_for_work()
        try:
            # proxy_random_list = random.choice(get_proxy_database())
            proxy = {
                'proxy_type': python_socks.ProxyType.SOCKS5,
                'addr': PROXY_IP,
                'port': int(PROXY_PORT),
                'username': PROXY_USER,
                'password': PROXY_PASSWORD,
                'rdns': True
            }
            return proxy
        except IndexError:
            proxy = None
            return proxy
        except Exception as error:
            logger.exception(error)
            return None

    async def checking_the_proxy_for_work(self) -> None:
        """
        Проверяет работоспособность всех прокси из базы данных.

        :return: None
        """
        try:
            # Подключение к proxy с проверкой на работоспособность
            await self.connecting_to_proxy_with_verification(
                # Тип proxy (например: SOCKS5)
                addr=PROXY_IP,  # Адрес (например: 194.67.248.9)
                port=PROXY_PORT,  # Порт (например: 9795)
                username=PROXY_USER,  # Логин (например: username)
                password=PROXY_PASSWORD,  # Пароль (например: password)
            )
        except Exception as error:
            logger.exception(error)

    @staticmethod
    async def connecting_to_proxy_with_verification(addr, port, username, password) -> None:
        """
        Подключается к прокси-серверу с проверкой его работоспособности.

        :param addr: Адрес прокси (например: 194.67.248.9)
        :param port: Порт прокси (например: 9795)
        :param username: Логин для аутентификации
        :param password: Пароль для аутентификации
        :return: None
        """
        # Пробуем подключиться по прокси
        try:
            proxy_url = f'socks5://{username}:{password}@{addr}:{port}'
            proxy = {
                'http': proxy_url,
                'https': proxy_url,
            }
            logger.warning(f"Проверяемый прокси: {proxy_url}")
            requests.get('https://httpbin.org/ip', proxies=proxy, timeout=10)
            logger.warning(f"⚠️ Proxy: {proxy_url} рабочий!")
        except requests.exceptions.RequestException:
            logger.warning(f"❌ Proxy не рабочий!")
        except Exception as error:
            logger.exception(error)


if __name__ == '__main__':
    setup_proxy()
