# -*- coding: utf-8 -*-
import asyncio
import os
from pathlib import Path

from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient

from core.config import api_id, api_hash
from keyboards.user.keyboards import menu_launch_tracking_keyboard


class CheckingAccountsValidity:

    def __init__(self, message: Message, path: str):
        self.message = message
        self.path = path

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

    # === Подключение клиента Telethon ===
    async def connect_client(self, session_name, user):
        """
        Подключение клиента Telethon и проверка сессий. Возвращается client.connect()
        :param user: Пользователь из базы данных, для определения языка пользователя
        :param session_name: имя сессии Telethon
        :return: client - клиент Telethon
        """

        client = TelegramClient(session_name, api_id, api_hash, system_version="4.16.30-vxCUSTOM")
        await client.connect()

        # === Проверка авторизации ===
        if not await client.is_user_authorized():
            logger.error(f"⚠️ Сессия {session_name} недействительна — требуется повторный вход.")
            await self.message.answer(
                "⚠️ Сессия аккаунта недействительна (session файл не валидный) — требуется повторный вход. Отправьте валидный файл сессии",
                reply_markup=menu_launch_tracking_keyboard()
            )
            return

        me = await client.get_me()
        phone = me.phone or ""
        logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")
        logger.success("✅ Сессия активна, подключение успешно!")

        return client

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

    async def checking_accounts(self):
        """
        ✅ Проверка аккаунтов на валидность
        :return: (list) Список доступных сессий.
        """
        await self.checking_accounts_for_validity()
        available_sessions = await self.get_available_sessions()
        return available_sessions
