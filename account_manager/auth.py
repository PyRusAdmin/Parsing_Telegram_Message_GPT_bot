# -*- coding: utf-8 -*-
import asyncio
import csv
import os
import os.path
import random
from pathlib import Path

from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.errors import (
    AuthKeyDuplicatedError, TimedOutError, PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
    AuthKeyUnregisteredError
)
from telethon.sessions import StringSession

from core.config import API_ID, API_HASH
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
    
    :param client: (TelegramClient) Авторизованный клиент Telethon.
    :return: dict с полями:
        - id: ID пользователя
        - phone: номер телефона (или пустая строка)
        - first_name: имя
        - last_name: фамилия (может быть None)
        - username: юзернейм (может быть None)
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
        :param path: Путь к папке с .session файлами (опционально, нужен только для проверки файловых сессий)
        """
        self.message = message
        self.path = Path(path) if path else None  # ✅ path теперь опционален
        self.user_id = message.from_user.id

    async def client_connect_string_session(self, session_name) -> TelegramClient | None:
        """
        Подключение к Telegram аккаунту через StringSession

        :param session_name: Имя аккаунта для подключения (файл .session)
        :return: Клиент Telegram или None, если подключение не удалось
        """
        # Создаем клиент, используя StringSession и вашу строку
        client = TelegramClient(  # Создаем клиента Telegram
            StringSession(session_name),  # Строка сессии
            api_id=API_ID,  # ID приложения
            api_hash=API_HASH,  # Хэш приложения
            device_model=mobile_device["device_model"],
            system_version=mobile_device["system_version"],
            app_version=mobile_device["app_version"],
            lang_code=mobile_device["lang_code"],
            system_lang_code=mobile_device["system_lang_code"],
        )
        try:
            await client.connect()

            if not await client.is_user_authorized():
                logger.error("❌ Сессия недействительна или аккаунт не авторизован!")
                await self.write_csv(data=session_name)
                try:
                    await client.disconnect()  # Отключаемся от аккаунта, для освобождения процесса session файла.
                except ValueError:
                    logger.error("❌ Сессия недействительна или аккаунт не авторизован!")
                return None  # Не возвращаем клиента

            await get_account_info(client)  # Получаем и логируем информацию о пользователе
            return client  # Возвращаем клиента

        except AuthKeyDuplicatedError:
            logger.error(
                "❌ AuthKeyDuplicatedError: Повторный ввод ключа авторизации (на данный момент сеесия используется в другом месте)")
            await client.disconnect()
            await self.write_csv(data=session_name)
            return None  # Не возвращаем клиента

    async def write_csv(self, data):
        """
        Запись данных в CSV файл. (Аккаунты Telegram)
        Все данные будут записаны в одну строку.
        :param data: Список значений (например, список аккаунтов)
        :return:
        """
        with open('file.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Записываем данные как одну строку с одним элементом
            writer.writerow([data])  # Оборачиваем в список, чтобы строка не разбилась по символам

    async def read_invalid_sessions(self) -> list[str]:
        """Чтение всех невалидных сессий из CSV"""
        invalid_sessions = []
        if os.path.exists('file.csv'):
            with open('file.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Проверяем, не пустая ли строка
                        invalid_sessions.append(row[0])
        return invalid_sessions

    async def verify_account(self, session_name) -> None:
        """
        Проверяет и сортирует аккаунты.

        :param session_name: Имя аккаунта для проверки
        :return: None
        """
        try:
            logger.info(f"Проверка аккаунта {session_name}")
            client: TelegramClient = await self.client_connect_string_session(session_name=session_name)
            try:
                if not await client.is_user_authorized():  # Если аккаунт не авторизирован
                    await client.disconnect()
                    await asyncio.sleep(5)

                    # await delete_account_from_db(session_string=session_name, app_logger=self.app_logger)
                    await self.write_csv(data=session_name)

                else:
                    logger.info(f"Аккаунт {session_name} авторизован")
                    client.disconnect()  # Отключаемся после проверки
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

            # Удаляем файл file.csv, если он существует, чтобы очистить данные о невалидных сессиях перед новой проверкой
            try:
                os.remove("file.csv")
            except FileNotFoundError:  # Игнорируем ошибку, если файл не найден, так как это ожидаемо при первом запуске
                pass

        except Exception as error:
            logger.exception(error)

    # === Подключение клиента Telethon ===
    async def connect_client(self) -> TelegramClient | None:
        """
        Подключение клиента Telethon и проверка сессии.
        Использует self.path (путь к файлу БЕЗ расширения .session)
        :return: client или None, если сессия невалидна
        """
        if not self.path:
            logger.error("❌ self.path не установлен для connect_client()")
            return None

        client = TelegramClient(
            self.path,  # Telethon сам добавит .session
            api_id=API_ID,
            api_hash=API_HASH,
            device_model=mobile_device["device_model"],
            system_version=mobile_device["system_version"],
            app_version=mobile_device["app_version"],
            lang_code=mobile_device["lang_code"],
            system_lang_code=mobile_device["system_lang_code"],
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
        finally:
            # Не отключаем здесь — это делает вызывающий код после использования
            pass

    async def start_random_client(self):
        """
        Запускает Telegram-клиент со случайной сессией из указанной папки.

        :return: Авторизованный TelegramClient или None, если не удалось
        """

        records = getting_account()
        # Случайно выбираем сессию
        chosen_session_name = random.choice(records)
        logger.info(f"Используется сессия: {chosen_session_name}")

        client = TelegramClient(
            StringSession(chosen_session_name),
            api_id=API_ID,
            api_hash=API_HASH,
            device_model=mobile_device["device_model"],
            system_version=mobile_device["system_version"],
            app_version=mobile_device["app_version"],
            lang_code=mobile_device["lang_code"],
            system_lang_code=mobile_device["system_lang_code"],
        )

        await client.connect()

        if not await client.is_user_authorized():
            logger.error("Клиент не авторизован. Запустите сначала авторизацию.")
            await client.disconnect()
            return None

        logger.info("Телеграм-клиент запущен.")
        return client
