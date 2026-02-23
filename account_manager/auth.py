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

from core.config import api_id, api_hash
from database.database import delete_account_from_db, getting_account, write_account_to_user_table

mobile_device = {
    "device_model": "Pixel 5",
    "system_version": "11",
    "app_version": "8.4.1",
    "lang_code": "en",
    "system_lang_code": "en-US",
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

    async def scanning_folder_for_session_files(self):
        """
        Сканируем папку на наличие session-файлов
        :return: Список Path объектов с .session файлами или пустой список, если не найдены.
        """
        sessions_dir = Path(self.path)
        session_files = list(sessions_dir.glob('*.session'))

        if not session_files:
            await self.message.answer("❌ Не найдено ни одного session-файла в папке accounts/parsing")
            # logger.error("Session-файлы не найдены")
            logger.warning(f"В папке {sessions_dir} не найдено ни одного .session файла.")
            return []

        logger.info(f"Найдено {len(session_files)} session-файлов.")
        return session_files

    async def get_available_sessions(self):
        """
        Сканирует указанную папку и возвращает список имён session-файлов без расширения.

        :return: Список имён сессий (без расширения .session)
        """
        session_files = await self.scanning_folder_for_session_files()
        available_sessions = [str(f.stem) for f in session_files]
        logger.info(f"Найдено {len(available_sessions)} аккаунтов: {available_sessions}")
        return available_sessions

    async def checking_accounts_for_validity(self):
        """
        ✅ Проверка аккаунтов на валидность

        :return:
        """
        available_sessions = await self.get_available_sessions()
        # ✅ Проверка аккаунтов на валидность из папки parsing
        await self.connect_client_test(available_sessions=available_sessions, path=self.path)

    async def client_connect_string_session(self, session_name: str) -> TelegramClient | None:
        """
        Подключение к Telegram аккаунту через StringSession

        :param session_name: Имя аккаунта для подключения (файл .session)
        :return: Клиент Telegram или None, если подключение не удалось
        """
        # Создаем клиент, используя StringSession и вашу строку
        client = TelegramClient(  # Создаем клиента Telegram
            StringSession(session_name),  # Строка сессии
            api_id=api_id,  # ID приложения
            api_hash=api_hash,  # Хэш приложения
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

            me = await client.get_me()  # Получаем информацию о пользователе
            phone = me.phone or ""
            logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")
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

    async def handle_banned_account(self, telegram_client, session_name, exception):
        """
        Обработка banned аккаунтов.
        telegram_client.disconnect() - Отключение от Telegram.
        working_with_accounts() - Перемещение файла. Исходный путь к файлу - account_folder. Путь к новой папке,
        куда нужно переместить файл - new_account_folder

        :param telegram_client: Экземпляр клиента Telegram
        :param session_name: Имя аккаунта (session string)
        :param exception: Исключение, вызвавшее бан
        :return: None
        """
        logger.info(f"⛔ Аккаунт banned: {session_name}. {str(exception)}")
        await telegram_client.disconnect()
        await delete_account_from_db(session_string=session_name)

    async def handle_get_directory_path(self):
        """
        Обработчик события выбора session файлов

        Открывает диалоговое окно для выбора session файлов и подключает их к базе данных.
        """
        try:
            # Создаем клиент с обычной сессией
            client = TelegramClient(
                session=self.path,
                api_id=api_id,
                api_hash=api_hash,
                device_model=mobile_device["device_model"],
                system_version=mobile_device["system_version"],
                app_version=mobile_device["app_version"],
                lang_code=mobile_device["lang_code"],
                system_lang_code=mobile_device["system_lang_code"],
            )

            try:
                await client.connect()

                # Преобразуем в StringSession
                session_string = StringSession.save(client.session)
                await client.disconnect()

                # Переподключаемся через StringSession
                client = TelegramClient(
                    StringSession(session_string),
                    api_id=api_id,
                    api_hash=api_hash,
                    device_model=mobile_device["device_model"],
                    system_version=mobile_device["system_version"],
                    app_version=mobile_device["app_version"],
                    lang_code=mobile_device["lang_code"],
                    system_lang_code=mobile_device["system_lang_code"],
                )

                await client.connect()
                me = await client.get_me()

                phone = me.phone or ""
                logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")

                # Записываем в базу данных
                write_account_to_user_table(
                    user_id=self.user_id,
                    session_string=session_string,
                    phone_number=phone
                )
                await client.disconnect()

            except Exception as error:
                logger.exception(error)
                await client.disconnect()

        except Exception as e:
            logger.exception(e)

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
            api_id=api_id,
            api_hash=api_hash,
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

            me = await client.get_me()
            logger.success(f"✅ Сессия активна: {me.phone or me.id}")
            return client

        except Exception as e:
            logger.exception(f"Ошибка подключения к {self.path}: {e}")
            return None
        finally:
            # Не отключаем здесь — это делает вызывающий код после использования
            pass

    # === Подключение клиента Telethon ===
    async def connect_client_test(self, path, available_sessions):
        """
        Подключение клиента Telethon и проверка сессий. Возвращается client.connect()
        :param available_sessions: список доступных сессий Telethon
        :param path: путь к папке с сессиями
        :return: client - клиент Telethon
        """
        logger.info(f"🧾 Проверка сессий... {available_sessions}")

        for session_name in available_sessions:

            client = TelegramClient(f"{path}/{session_name}", api_id, api_hash, system_version="4.16.30-vxCUSTOM")

            await client.connect()

            # === Проверка авторизации ===
            if not await client.is_user_authorized():
                logger.error(f"⚠️ Сессия {session_name} недействительна — требуется повторный вход.")
                await client.disconnect()
                await asyncio.sleep(1)  # дать время ОС освободить файл
                try:
                    os.remove(f"{path}/{session_name}.session")
                except FileNotFoundError:
                    pass  # файл уже удалён

                continue  # переходим к следующей сессии

            me = await client.get_me()
            phone = me.phone or ""
            logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")
            logger.info("✅ Сессия активна, подключение успешно!")

            await asyncio.sleep(1)  # дать время ОС освободить файл
            await client.disconnect()
            try:
                os.rename(f"{path}/{session_name}.session", f"{path}/{phone}.session")
            except FileExistsError:
                await client.disconnect()
                os.remove(f"{path}/{session_name}.session")

            if client.is_connected():
                await client.disconnect()  # отключаемся, если подключены

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
            api_id=api_id,
            api_hash=api_hash,
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

    async def checking_accounts(self):
        """
        ✅ Проверка аккаунтов на валидность
        :return: (list) Список доступных сессий.
        """
        await self.checking_accounts_for_validity()
        available_sessions = await self.get_available_sessions()
        return available_sessions
