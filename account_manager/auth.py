# -*- coding: utf-8 -*-
import asyncio
import csv
import os
import random
from pathlib import Path

from aiogram.types import Message
from loguru import logger
from telethon import TelegramClient
from telethon.errors import (
    AuthKeyDuplicatedError, TimedOutError, PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
    AuthKeyUnregisteredError
)
from telethon.sessions import StringSession

from core.config import API_ID, API_HASH, MT_PROXY_IP
from core.proxy import Proxy, setup_proxy
from database.database import delete_account_from_db, getting_account

mobile_device = {
    "device_model": "Pixel 5",
    "system_version": "11",
    "app_version": "8.4.1",
    "lang_code": "en",
    "system_lang_code": "en-US",
}


async def get_account_info(client: TelegramClient) -> dict:
    """
    Получает информацию о пользователе Telegram через client.get_me().

    :param client: Авторизованный клиент Telethon.
    :return: dict с полями: id, phone, first_name, last_name, username
    """
    me = await client.get_me()
    phone = me.phone or ""
    logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")

    return {
        "id": me.id,
        "phone": phone,
        "first_name": me.first_name,
        "last_name": me.last_name,
        "username": me.username
    }


class CheckingAccountsValidity:

    def __init__(self, message: Message, path: str | None = None):
        """
        :param message: Сообщение для отправки уведомлений (опционально)
        :param path: Путь к папке с .session файлами (опционально)
        """
        self.message = message
        self.path = Path(path) if path else None
        self.user_id = message.from_user.id
        self.proxy = Proxy()  # Инициализация класса Proxy для проверки прокси.
        # self.proxy_config = get_proxy_config("mtproxy")

    async def client_connect_string_session(self, session_name) -> TelegramClient | None:
        """
        Подключение к Telegram аккаунту через StringSession

        :param session_name: Имя аккаунта для подключения (файл .session)
        :return: Клиент Telegram или None, если подключение не удалось
        """
        logger.info(f"🔗 Подключение через MTProxy: {MT_PROXY_IP}:{443}")
        client = TelegramClient(
            StringSession(session_name),
            api_id=API_ID,
            api_hash=API_HASH,
            device_model=mobile_device["device_model"],
            system_version=mobile_device["system_version"],
            app_version=mobile_device["app_version"],
            lang_code=mobile_device["lang_code"],
            system_lang_code=mobile_device["system_lang_code"],
            # connection=connection.ConnectionTcpMTProxyAbridged,
            proxy=('socks5', "87.239.250.238", 39301, True, "C8MRdMvXh8", "FmUmOnx2JW")
        )

        try:
            await client.connect()

            if not await client.is_user_authorized():
                logger.error("❌ Сессия недействительна или аккаунт не авторизован!")
                await self.write_csv(data=session_name)
                try:
                    await client.disconnect()
                except ValueError:
                    logger.error("❌ Сессия недействительна или аккаунт не авторизован!")
                return None

            await get_account_info(client)
            return client

        except AuthKeyDuplicatedError:
            logger.error(
                "❌ AuthKeyDuplicatedError: Повторный ввод ключа авторизации "
                "(сессия используется в другом месте)")
            await client.disconnect()
            await self.write_csv(data=session_name)
            return None
        except Exception as e:
            logger.exception(f"Ошибка подключения: {e}")
            await client.disconnect()
            return None

    async def write_csv(self, data):
        """
        Запись данных в CSV файл.
        :param data: Список значений (например, список аккаунтов)
        """
        with open('file.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([data])

    async def read_invalid_sessions(self) -> list[str]:
        """Чтение всех невалидных сессий из CSV"""
        invalid_sessions = []
        if os.path.exists('file.csv'):
            with open('file.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        invalid_sessions.append(row[0])
        return invalid_sessions

    async def verify_account(self, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.
        :param session_name: Имя аккаунта для проверки
        """
        try:
            logger.info(f"Проверка аккаунта {session_name}")
            client: TelegramClient = await self.client_connect_string_session(session_name=session_name)

            if client is None:
                return

            try:
                if not await client.is_user_authorized():
                    await client.disconnect()
                    await asyncio.sleep(5)
                    await self.write_csv(data=session_name)
                else:
                    logger.info(f"Аккаунт {session_name} авторизован")
                    await client.disconnect()
            except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
                    AuthKeyUnregisteredError, AuthKeyDuplicatedError) as e:
                await delete_account_from_db(session_string=session_name)
            except TimedOutError as e:
                logger.exception(e)
                await asyncio.sleep(2)
            except AttributeError:
                pass

            invalid_sessions = await self.read_invalid_sessions()
            logger.info(f"❌ Невалидные сессии: {invalid_sessions}")
            for session in invalid_sessions:
                await delete_account_from_db(session_string=session)

            try:
                os.remove("file.csv")
            except FileNotFoundError:
                pass

        except Exception as error:
            logger.exception(error)

    async def connect_client(self) -> TelegramClient | None:
        """
        Подключение клиента Telethon и проверка сессии.
        :return: client или None, если сессия невалидна
        """
        client = TelegramClient(
            self.path,
            api_id=API_ID,
            api_hash=API_HASH,
            device_model=mobile_device["device_model"],
            system_version=mobile_device["system_version"],
            app_version=mobile_device["app_version"],
            lang_code=mobile_device["lang_code"],
            system_lang_code=mobile_device["system_lang_code"],
            # connection=connection.ConnectionTcpMTProxyAbridged,
            proxy=('socks5', "87.239.250.238", 39301, True, "C8MRdMvXh8", "FmUmOnx2JW")
        )
        try:
            await client.connect()

            if not await client.is_user_authorized():
                logger.warning(f"⚠️ Сессия {self.path} не авторизована")
                return None
            account_info = await get_account_info(client)
            logger.success(f"✅ Сессия активна: {account_info['phone'] or account_info['id']}")
            return client
        except Exception as e:
            logger.exception(f"Ошибка подключения к {self.path}: {e}")
            return None

    async def start_random_client(self):
        """
        Запускает Telegram-клиент со случайной сессией из указанной папки.
        :return: Авторизованный TelegramClient или None
        """
        try:
            records = getting_account()
            chosen_session_name = random.choice(records)

            if not chosen_session_name or not isinstance(chosen_session_name, str):
                logger.error(f"❌ Неверный формат сессии: {type(chosen_session_name)}")
                return None

            logger.info(f"Используется сессия: {chosen_session_name[:30]}...")

            client = TelegramClient(
                StringSession(chosen_session_name),
                api_id=API_ID,
                api_hash=API_HASH,
                device_model=mobile_device["device_model"],
                system_version=mobile_device["system_version"],
                app_version=mobile_device["app_version"],
                lang_code=mobile_device["lang_code"],
                system_lang_code=mobile_device["system_lang_code"],
                timeout=30,
            )
            await client.connect()

            if not await client.is_user_authorized():
                logger.error("Клиент не авторизован. Запустите сначала авторизацию.")
                await client.disconnect()
                return None

            logger.info("Телеграм-клиент запущен.")
            return client

        except Exception as e:
            logger.exception(f"❌ Ошибка запуска клиента: {e}")
            return None
