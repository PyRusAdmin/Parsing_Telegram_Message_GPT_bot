import csv
import os
import random
from pathlib import Path
from typing import Optional

from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.errors import (
    AuthKeyDuplicatedError, PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
    AuthKeyUnregisteredError
)
from telethon.sessions import StringSession

from core.config import API_ID, API_HASH, mobile_device
from database.users_personal_trackings import delete_account_from_user_table
from keyboards.keyboards import menu_launch_tracking_keyboard
from locales.locales import t


async def get_account_info(client: TelegramClient) -> dict:
    """
    Получает информацию о пользователе Telegram через client.get_me().

    :param client: (TelegramClient) Авторизованный клиент Telethon.
    :return: (dict) Словарь с данными аккаунта: id, phone, first_name, last_name, username.
    """
    me = await client.get_me()
    phone = me.phone or ""
    first_name = me.first_name or ""
    last_name = me.last_name or ""
    username = me.username or ""
    logger.info(f"🧾 Аккаунт: | ID: {me.id} | Phone: {phone}")

    return {
        "id": me.id,  # Идентификатор пользователя Telegram
        "phone": phone,  # Номер телефона пользователя Telegram
        "first_name": first_name,  # Имя пользователя Telegram
        "last_name": last_name,  # Фамилия пользователя Telegram
        "username": username  # Никнейм пользователя Telegram
    }


async def check_and_cleanup_session(session_string: str, user_id: int = 0, user_lang: str = "ru") -> tuple[
    bool, Optional[str]]:
    """
    Универсальная потокобезопасная проверка сессии Telethon.
    При обнаружении невалидности автоматически удаляет запись из базы данных
    и безопасно уведомляет пользователя через Telegram-бота.

    :param session_string: (str) Строка сессии Telethon (StringSession).
    :param user_id: (int) Telegram ID пользователя (0, если неизвестен).
    :param user_lang: (str) Языковой код интерфейса пользователя ('ru' или 'en').
    :return: (tuple[bool, Optional[str]]) (True, None) если сессия валидна, иначе (False, описание ошибки).
    """
    if not session_string:
        return False, "Empty session string"

    checker = CheckingAccountsValidity()
    try:
        from database.account_free import delete_account_from_free_db
        client = await checker.client_connect_string_session(session_name=session_string)
        if client is None:
            if user_id:
                delete_account_from_user_table(user_id=user_id, personal_account=session_string)
            delete_account_from_free_db(session_string)
            return False, "Failed to connect client"

        try:
            if not await client.is_user_authorized():
                logger.warning(f"⚠️ Сессия не авторизована: {session_string[:25]}...")
                await client.disconnect()
                if user_id:
                    delete_account_from_user_table(user_id=user_id, personal_account=session_string)
                delete_account_from_free_db(session_string)
                return False, "Session not authorized"
            else:
                logger.info(f"✅ Сессия авторизована: {session_string[:25]}...")
                await client.disconnect()
                return True, None
        except (PhoneNumberBannedError, UserDeactivatedBanError, AuthKeyNotFound,
                AuthKeyUnregisteredError, AuthKeyDuplicatedError) as e:
            logger.warning(f"❌ Невалидная/заблокированная сессия: {e}")
            delete_account_from_free_db(session_string)
            if user_id:
                delete_account_from_user_table(user_id=user_id, personal_account=session_string)
                try:
                    from system.dispatcher import bot
                    await bot.send_message(
                        chat_id=user_id,
                        text=t("session_invalid", lang=user_lang or "ru"),
                        reply_markup=menu_launch_tracking_keyboard(lang=user_lang or "ru")
                    )
                except Exception as notify_err:
                    logger.warning(
                        f"Не удалось отправить уведомление о невалидной сессии пользователю {user_id}: {notify_err}")
            return False, str(e)
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при проверке авторизации: {e}")
            try:
                await client.disconnect()
            except Exception:
                pass
            return False, str(e)
    except Exception as e:
        logger.exception(f"❌ Ошибка в check_and_cleanup_session: {e}")
        return False, str(e)


class CheckingAccountsValidity:
    """Класс для проверки валидности и подключения аккаунтов Telegram"""

    def __init__(self, path: str | None = None):
        """
        Инициализирует валидатор аккаунтов.

        :param path: (str | None) Путь к файлу сессии или папке с сессиями (опционально).
        """
        self.path = Path(path) if path else None

    async def client_connect_string_session(self, session_name) -> TelegramClient | None:
        """
        Подключение к Telegram аккаунту через StringSession.

        :param session_name: (str) Строка сессии (StringSession) для подключения.
        :return: (TelegramClient | None) Клиент Telegram или None, если подключение не удалось.
        """
        client = TelegramClient(
            StringSession(session_name),
            api_id=API_ID,
            api_hash=API_HASH,
            connection_retries=2,
            retry_delay=1,
            timeout=10,
            device_model=mobile_device["device_model"],
            system_version=mobile_device["system_version"],
            app_version=mobile_device["app_version"],
            lang_code=mobile_device["lang_code"],
            system_lang_code=mobile_device["system_lang_code"],
        )

        try:
            await client.connect()

            if not await client.is_user_authorized():
                logger.warning("⚠️ Сессия недействительна или аккаунт не авторизован")
                await self.write_csv(data=session_name)
                try:
                    await client.disconnect()
                except Exception:
                    pass
                return None

            account_info = await get_account_info(client)
            return client

        except AuthKeyDuplicatedError:
            logger.warning(
                "⚠️ AuthKeyDuplicatedError: Повторный ввод ключа авторизации (сессия используется в другом месте)"
            )
            try:
                await client.disconnect()
            except Exception:
                pass
            await self.write_csv(data=session_name)
            return None
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning(f"⚠️ Ошибка подключения к Telegram для StringSession: {e}")
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
            return None
        except Exception as e:
            logger.warning(f"⚠️ Ошибка подключения сессии: {e}")
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
            return None

    async def write_csv(self, data):
        """
        Запись данных в CSV файл.

        :param data: (Any) Данные для записи в файл (например, строка сессии).
        """
        with open('file.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([data])

    async def read_invalid_sessions(self) -> list[str]:
        """
        Чтение всех невалидных сессий из CSV файла.

        :return: (list[str]) Список строк невалидных сессий.
        """
        invalid_sessions = []
        if os.path.exists('file.csv'):
            with open('file.csv', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        invalid_sessions.append(row[0])
        return invalid_sessions

    async def verify_account(self, session_name: str, user_id: int = 0, user_lang: str = "ru") -> bool:
        """
        Проверяет валидность аккаунта и удаляет невалидные сессии из базы данных пользователя.

        :param session_name: (str) Строка сессии для проверки.
        :param user_id: (int) Telegram ID пользователя.
        :param user_lang: (str) Языковой код интерфейса пользователя.
        :return: (bool) True, если аккаунт валиден, иначе False.
        """
        is_valid, _ = await check_and_cleanup_session(session_string=session_name, user_id=user_id, user_lang=user_lang)
        return is_valid

    async def connect_client(self) -> TelegramClient | None:
        """
        Подключение клиента Telethon по пути файла сессии и проверка авторизации.

        :return: (TelegramClient | None) Авторизованный клиент Telegram или None, если сессия невалидна.
        """
        client = TelegramClient(
            str(self.path),
            api_id=API_ID,
            api_hash=API_HASH,
            connection_retries=2,
            retry_delay=1,
            timeout=10,
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
                try:
                    await client.disconnect()
                except Exception:
                    pass
                return None
            account_info = await get_account_info(client)
            logger.success(f"✅ Сессия активна: {account_info.get('phone') or account_info.get('id')}")
            return client
        except (ConnectionError, TimeoutError, OSError) as ce:
            logger.warning(f"⚠️ Ошибка подключения к Telegram для сессии {self.path}: {ce}")
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
            return None
        except Exception as e:
            logger.warning(f"⚠️ Не удалось валидировать сессию {self.path}: {e}")
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
            return None

    async def verify_free_account(self, session_name: str, user_lang: str = "ru") -> bool:
        """
        Проверяет валидность аккаунта из пула свободных (AccountFree) и при невалидности/бане
        автоматически удаляет его из таблицы account_free.

        :param session_name: (str) Строка сессии.
        :param user_lang: (str) Язык для сообщений.
        :return: (bool) True, если аккаунт валиден, иначе False.
        """
        from database.account_free import delete_account_from_free_db
        is_valid, _ = await check_and_cleanup_session(session_string=session_name, user_id=0, user_lang=user_lang)
        if not is_valid:
            delete_account_from_free_db(session_name)
        return is_valid

    async def start_random_client(self):
        """
        Запускает клиент Telethon, выбирая случайную сессию из свободных аккаунтов администратора (account_free).

        :return: (TelegramClient | None) Авторизованный TelegramClient или None при ошибке.
        """
        try:
            from database.account_free import getting_free_account
            records = getting_free_account()
            if not records:
                logger.error("❌ В таблице account_free нет доступных аккаунтов для поиска!")
                return None

            chosen_session_name = random.choice(records)
            logger.info(f"Используется сессия из account_free: {chosen_session_name[:30]}...")

            return await self.client_connect_string_session(chosen_session_name)

        except Exception as e:
            logger.exception(f"❌ Ошибка запуска клиента из account_free: {e}")
            return None
