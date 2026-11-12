import asyncio
import csv
import hashlib
import hmac
import io
import json
import os
import random
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

from aiogram.types import BufferedInputFile, LabeledPrice
from asgiref.sync import sync_to_async
from fastapi import (
    APIRouter, BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from g4f.client import Client
from groq import AsyncGroq
from loguru import logger  # https://github.com/Delgan/loguru
from openai import AsyncOpenAI
from telethon.errors import (
    AuthKeyUnregisteredError, FloodWaitError, UsernameInvalidError
)
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity, get_account_info
from account_manager.parser import (
    active_clients, filter_messages, get_full_info_group, stop_flags, stop_tracking, update_group_channels_data_base
)
from account_manager.utilit import detect_language
from ai.ai import category_assignment, get_groq_response, search_groups_in_telegram
from core.config import ADMIN_USER_ID, BOT_TOKEN, GROQ_API_KEY, OPENROUTER_API_KEY, OPENROUTER_BASE_URL
from database.database import (
    TelegramGroups, get_all_data_telegram_groups, get_groups_without_category, getting_number_records_database,
    database
)
from database.account_free import getting_free_account
from database.users_accounts import write_account_to_user_table, UsersAccounts
from database.users_groups import UsersGroups, get_group_count
from database.users_keywords import get_keywords_count, get_user_keywords_with_id, UsersKeywords
from database.users_personal_trackings import get_session_count, UsersPersonalTrackings
from database.users_questions import get_all_questions
from handlers.admin.checking_group_for_ai import get_best_g4f_model
from handlers.admin.language_detection import ai_llama_fri
from handlers.user.pars_ai import (
    can_user_download_free, create_excel_file, parse_ai_group_names, save_group_to_db, parse_search_input
)
from handlers.user_language import determines_user_language
from locales.locales import t
from system.dispatcher import bot

# Инициализировать FastAPI

app = FastAPI(title="AutoParseAlertBot Web API", version="0.1.0")

# Добавьте промежуточное ПО CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# TODO: После рефактинга удалить закоментированный код 29.08.2026


class MockMessage:
    """Имитация объекта сообщения aiogram для обработки запросов из веб-интерфейса"""

    # Mock Message для совместимости с обработчиками ботов

    def __init__(self, user_id: int, username: Optional[str] = "web_user"):
        """
        Инициализирует объект MockMessage для имитации Telegram-сообщения.

        :param user_id: (int) Идентификатор пользователя в Telegram.
        :param username: (Optional[str]) Имя пользователя в Telegram.
        """
        self.from_user = type('User', (), {
            'id': user_id,
            'username': username or 'web_user',
            'first_name': 'Web',
            'last_name': 'User'
        })()
        self.chat = type('Chat', (), {'id': user_id})()
        # Лениво обращайтесь к боту для предотвращения круговых зависимостей или неинициализированных переменных
        from system.dispatcher import bot
        self.bot = bot

    async def answer(self, text: str, parse_mode=None, reply_markup=None, **kwargs):
        """
        Имитирует отправку текстового ответа пользователю через Telegram-бота.

        :param text: (str) Текст отправляемого сообщения.
        :param parse_mode: Режим форматирования текста (HTML, Markdown и др.).
        :param reply_markup: Клавиатура или разметка сообщения.
        :param kwargs: Дополнительные параметры отправки сообщения.
        :return: Объект отправленного сообщения Telegram или None при ошибке.
        """
        from system.dispatcher import bot
        try:
            return await bot.send_message(
                chat_id=self.from_user.id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            logger.exception(f"Failed to send mock answer to {self.from_user.id}: {e}")

    async def reply(self, text: str, parse_mode=None, reply_markup=None, **kwargs):
        """
        Имитирует ответ на сообщение пользователю через Telegram-бота.

        :param text: (str) Текст отправляемого ответа.
        :param parse_mode: Режим форматирования текста.
        :param reply_markup: Клавиатура или разметка сообщения.
        :param kwargs: Дополнительные параметры отправки сообщения.
        :return: Объект отправленного сообщения Telegram или None при ошибке.
        """
        return await self.answer(text, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)

    async def answer_document(self, document, caption=None, parse_mode=None, reply_markup=None, **kwargs):
        """
        Имитирует отправку документа пользователю через Telegram-бота.

        :param document: Отправляемый документ (файл или BufferedInputFile).
        :param caption: Подпись к документу.
        :param parse_mode: Режим форматирования подписи.
        :param reply_markup: Клавиатура или разметка сообщения.
        :param kwargs: Дополнительные параметры отправки сообщения.
        :return: Объект отправленного сообщения Telegram или None при ошибке.
        """
        from system.dispatcher import bot
        try:
            return await bot.send_document(
                chat_id=self.from_user.id,
                document=document,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            logger.exception(f"Failed to send mock document to {self.from_user.id}: {e}")

    async def answer_photo(self, photo, caption=None, parse_mode=None, reply_markup=None, **kwargs):
        """
        Имитирует отправку фотографии пользователю через Telegram-бота.

        :param photo: Отправляемая фотография.
        :param caption: Подпись к фотографии.
        :param parse_mode: Режим форматирования подписи.
        :param reply_markup: Клавиатура или разметка сообщения.
        :param kwargs: Дополнительные параметры отправки сообщения.
        :return: Объект отправленного сообщения Telegram или None при ошибке.
        """
        from system.dispatcher import bot
        try:
            return await bot.send_photo(
                chat_id=self.from_user.id,
                photo=photo,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                **kwargs
            )
        except Exception as e:
            logger.exception(f"Failed to send mock photo to {self.from_user.id}: {e}")

    async def edit_text(self, text: str, parse_mode=None, reply_markup=None, **kwargs):
        """
        Имитирует редактирование текста сообщения через Telegram-бота.

        :param text: (str) Новый текст сообщения.
        :param parse_mode: Режим форматирования текста.
        :param reply_markup: Клавиатура или разметка сообщения.
        :param kwargs: Дополнительные параметры отправки сообщения.
        :return: Результат вызова метода answer.
        """
        return await self.answer(text, parse_mode=parse_mode, reply_markup=reply_markup, **kwargs)


@app.middleware("http")
async def db_session_middleware(request, call_next):
    """
    Обеспечивает активное подключение к базе данных для каждого HTTP-запроса.

    :param request: Входящий HTTP-запрос.
    :param call_next: Функция для передачи запроса следующему обработчику.
    :return: HTTP-ответ сервера.
    """
    # Промежуточное программное обеспечение для подключения к базе данных
    if database.is_closed():
        database.connect(reuse_if_open=True)
    response = await call_next(request)
    return response


def get_client_ip(request: Request) -> str:
    """
    Извлекает реальный IP пользователя с учетом прокси (X-Forwarded-For, X-Real-IP, CF-Connecting-IP).

    :param request: (Request) Объект HTTP-запроса FastAPI.
    :return: (str) IP-адрес клиента.
    """
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


async def get_country_by_ip(ip: str) -> Optional[str]:
    """
    Определяет двухбуквенный код страны (RU, US и т.д.) по IP через ip-api.com.

    :param ip: (str) IP-адрес пользователя.
    :return: (Optional[str]) Двухбуквенный код страны или None.
    """
    if ip.startswith(("127.", "192.168.", "10.", "172.16.", "localhost")):
        return None
    try:
        def _fetch():
            """
            Выполняет запрос к внешнему сервису гео-IP для определения кода страны.

            :return: (Optional[str]) Двухбуквенный код страны или None.
            """
            url = f"http://ip-api.com/json/{ip}?fields=countryCode,status"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    return data.get("countryCode")
            return None

        return await asyncio.to_thread(_fetch)
    except Exception as e:
        logger.warning(f"⚠️ Ошибка определения страны по IP {ip}: {e}")
        return None


async def detect_language_by_ip(ip: str, accept_language_header: Optional[str] = None) -> str:
    """
    Определяет предпочтительный язык ('ru' или 'en') на основе IP пользователя и заголовка Accept-Language.

    :param ip: (str) IP-адрес пользователя.
    :param accept_language_header: (Optional[str]) Заголовок Accept-Language из HTTP-запроса.
    :return: (str) Двухбуквенный код языка ('ru' или 'en').
    """
    country_code = await get_country_by_ip(ip)
    if country_code:
        ru_countries = {"RU", "BY", "KZ", "KG", "AM", "AZ", "TJ", "TM", "UZ", "MD", "GE"}
        if country_code.upper() in ru_countries:
            return "ru"
        else:
            return "en"
    if accept_language_header:
        lang_lower = accept_language_header.lower()
        if any(code in lang_lower for code in ["ru", "be", "uk", "kk"]):
            return "ru"
    return "ru"


def get_current_tg_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Проверяет авторизацию пользователя Telegram по токену initData.

    :param authorization: (Optional[str]) Заголовок авторизации с токеном initData Telegram WebApp.
    :return: (dict) Словарь с данными авторизованного пользователя Telegram.
    """
    # Зависимость для проверки аутентификации из initData
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    token = authorization[7:]
    # Разрешить имитация входа для локальной разработки и тестирования
    if token.startswith("mock_"):
        try:
            mock_id = int(token.split("_")[1])
            return {
                "id": mock_id,
                "first_name": "Test",
                "last_name": "User",
                "username": f"test_user_{mock_id}",
                "language_code": "ru",
                "is_mock": True
            }
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid mock token")
    try:
        params = dict(urllib.parse.parse_qsl(token, keep_blank_values=True))
        if 'hash' not in params:
            raise HTTPException(status_code=401, detail="Missing hash parameter")
        auth_hash = params.pop('hash')
        sorted_params = sorted(params.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_params)
        # Проверить хеш
        secret_key = hmac.new("WebAppData".encode(), BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated_hash, auth_hash):
            logger.warning(
                "Telegram auth failed: hash mismatch. BOT_TOKEN in .env does not match the Telegram bot used to open WebApp.")
            raise HTTPException(status_code=401, detail="Invalid Telegram signature")
        user_data = json.loads(params['user'])
        return user_data
    except Exception as e:
        logger.exception(f"Telegram auth failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")


# Глобальный словарь статуса администратора для показа прогресса в работе администратора в веб-интерфейсе

admin_task_status = {
    "action": "none",  # "categorize", "lang_detect", "check_accounts", "actualize", "none"
    "progress": 0,
    "total": 0,
    "status": "idle",  # "running", "completed", "error"
    "message": ""
}

# Множество подсоединённых сессий для устранения дублирующего спама в логах при регулярном поллинге каждые 5 сек

logged_user_sessions = set()


def init_web_directories():
    """
    Создает необходимые директории для статических файлов веб-сервера.

    :return: None
    """
    # Убедитесь, что каталоги существуют
    os.makedirs("web/static", exist_ok=True)
    os.makedirs("web/static/css", exist_ok=True)
    os.makedirs("web/static/js", exist_ok=True)


init_web_directories()


# ==================== ПУБЛИЧНЫЕ API-ЭНДПОИНТЫ ====================


@app.get("/api/status")
async def get_status(request: Request, user_data: dict = Depends(get_current_tg_user)):
    """
    Возвращает статус пользователя, настройки языка и статистику системы.

    :param request: (Request) Объект HTTP-запроса.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Словарь со статистикой, статусом отслеживания и настройками пользователя.
    """
    try:
        client_ip = get_client_ip(request)
        logger.info(f"User {user_data['id']} connected from {client_ip}")
        # Получить пользователя
        user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
        if not user:
            detected_lang = await detect_language_by_ip(client_ip, request.headers.get("accept-language"))
            user = UsersPersonalTrackings.create(
                user_id=user_data["id"],
                user_username=user_data.get("username"),
                user_firstname=user_data.get("first_name"),
                user_last_name=user_data.get("last_name"),
                language=detected_lang
            )

        elif user.language == "unset":
            detected_lang = await detect_language_by_ip(client_ip, request.headers.get("accept-language"))
            user.language = detected_lang
            user.save()

        # Получите статистику
        groups_count = getting_number_records_database()
        session_count = get_session_count(user_id=user_data["id"])
        tracked_channels = get_group_count(user_id=user_data["id"])  # Отслеживаемые каналы
        keywords_count = get_keywords_count(user_id=user_data["id"])

        # Получите целевую группу (группу уведомлений) пользователя
        pt = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
        target_group = pt.created_group_link if pt else None

        tracking_active = str(user_data["id"]) in active_clients
        is_admin = int(user_data["id"]) == int(ADMIN_USER_ID)
        session_key = (user_data["id"], client_ip)
        if session_key not in logged_user_sessions:
            logged_user_sessions.add(session_key)
            logger.info(
                f"👤 Пользователь {user_data.get('first_name', '')} {user_data.get('last_name', '')} (@{user_data.get('username', 'без username')}, ID: {user_data['id']}) | IP: {client_ip} | Язык: {user.language}. Администратор: {is_admin}")

        return {
            "user_id": user_data["id"],
            "username": user.username,
            "first_name": user.first_name,
            "language": user.language,
            "stars": user.stars,
            "is_admin": is_admin,
            "stats": {
                "version": "0.1.0",
                "db_total_groups": groups_count,
                "connected_accounts": session_count,
                "target_groups": 1 if target_group else 0,
                "tracked_channels": tracked_channels,
                "keywords": keywords_count,
                "target_group_username": target_group
            },
            "tracking_active": tracking_active
        }

    except Exception as e:
        logger.exception(f"Error getting status: {e}")


@app.post("/api/settings/language")
async def update_language(lang: str, user_data: dict = Depends(get_current_tg_user)):
    """
    Обновляет языковые настройки текущего пользователя.

    :param lang: (str) Код выбранного языка (из SUPPORTED_LANGUAGES).
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Результат операции и установленный язык.
    """
    from locales.locales import SUPPORTED_LANGUAGES
    if lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Invalid language code")
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.language = lang
    user.save()
    return {"status": "ok", "language": lang}


@app.post("/api/tracking/start")
async def start_user_tracking(
        background_tasks: BackgroundTasks,
        account_id: Optional[int] = Query(None),
        user_data: dict = Depends(get_current_tg_user)
):
    """
    Запускает процесс отслеживания сообщений для пользователя через веб-интерфейс.
    Поддерживает запуск конкретного аккаунта/кампании.

    :param background_tasks: (BackgroundTasks) Менеджер фоновых задач FastAPI.
    :param account_id: (Optional[int]) ID аккаунта (если запускается конкретная кампания).
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус запуска отслеживания.
    """
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_key = f"{user_data['id']}_{account_id}" if account_id else str(user_data["id"])
    if user_key in active_clients:
        return {"status": "already_running"}

    mock_msg = MockMessage(user_id=user_data["id"], username=user.username)
    background_tasks.add_task(filter_messages, message=mock_msg, user_id=user_data["id"], account_id=account_id)
    return {"status": "starting"}


@app.post("/api/tracking/stop")
async def stop_user_tracking(
        account_id: Optional[int] = Query(None),
        user_data: dict = Depends(get_current_tg_user)
):
    """
    Останавливает процесс отслеживания сообщений для пользователя через веб-интерфейс.
    Поддерживает остановку конкретного аккаунта/кампании.

    :param account_id: (Optional[int]) ID аккаунта для остановки.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус остановки отслеживания.
    """
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    mock_msg = MockMessage(user_id=user_data["id"], username=user.username)
    await stop_tracking(user_id=user_data["id"], message=mock_msg, account_id=account_id)
    return {"status": "stopping"}


@app.get("/api/keywords")
async def list_keywords(user_data: dict = Depends(get_current_tg_user)):
    """
    Возвращает список ключевых слов текущего пользователя.

    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: Список словарей с идентификаторами и ключевыми словами пользователя.
    """
    return get_user_keywords_with_id(user_id=user_data["id"])


@app.post("/api/keywords")
async def add_keyword(keyword: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Добавляет новое ключевое слово для отслеживания.

    :param keyword: (str) Добавляемое ключевое слово.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус добавления, идентификатор записи и ключевое слово.
    """
    keyword = keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    kw_obj, _ = UsersKeywords.get_or_create(
        user_id=user_data["id"],
        user_keyword=keyword
    )
    return {"status": "ok", "id": kw_obj.id, "keyword": keyword}


@app.delete("/api/keywords/{kw_id}")
async def delete_keyword(kw_id: int, user_data: dict = Depends(get_current_tg_user)):
    """
    Удаляет ключевое слово пользователя по его идентификатору.

    :param kw_id: (int) Идентификатор ключевого слова в базе данных.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус выполнения операции.
    """
    deleted = (
        UsersKeywords.delete()
        .where(
            (UsersKeywords.id == kw_id) &
            (UsersKeywords.user_id == user_data["id"])
        )
        .execute()
    )
    if deleted:
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Keyword not found")


@app.get("/api/channels")
async def list_channels(user_data: dict = Depends(get_current_tg_user)):
    """
    Возвращает список отслеживаемых каналов пользователя.

    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: Список словарей с информацией об отслеживаемых каналах.
    """
    # Управление отслеживаемыми каналами
    records = list(
        UsersGroups.select().where(UsersGroups.user_id == user_data["id"]).order_by(UsersGroups.date_added.desc()))
    return [{"id": ch.id, "username": ch.username_group, "date_added": ch.date_added.strftime("%Y-%m-%d %H:%M:%S")} for
            ch in
            records]


@app.post("/api/channels")
async def add_channel(username: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Добавляет новый канал в список отслеживаемых.

    :param username: (str) Юзернейм добавляемого канала.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус добавления и юзернейм канала.
    """
    username_group = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    if not username.startswith("@"):
        username_group = f"@{username}"
    try:
        UsersGroups.create(user_id=user_data["id"], username_group=username_group)
        return {"status": "ok", "username": username}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Channel already tracked")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/channels/{ch_id}")
async def delete_channel(ch_id: int, user_data: dict = Depends(get_current_tg_user)):
    """
    Удаляет канал из списка отслеживаемых по идентификатору.

    :param ch_id: (int) Идентификатор записи канала в базе данных.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус выполнения операции.
    """
    deleted = UsersGroups.delete().where(UsersGroups.user_id == user_data["id"], UsersGroups.id == ch_id).execute()
    if deleted:
        return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Channel not found")


@app.post("/api/channels/upload")
async def upload_channels_file(file: UploadFile = File(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Загружает список каналов из текстового файла.

    :param file: (UploadFile) Текстовый файл со списком каналов.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статистика добавленных, пропущенных каналов и ошибок.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    contents = await file.read()
    try:
        text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = contents.decode("utf-8", errors="ignore")
    channel_lines = [line.strip() for line in text.splitlines() if line.strip()]
    added_count = 0
    skipped_count = 0
    errors_count = 0
    for channel in channel_lines:
        target_username = channel if channel.startswith("@") else f"@{channel}"
        try:
            UsersGroups.create(user_id=user_data["id"], username_group=target_username)
            added_count += 1
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                skipped_count += 1
            else:
                errors_count += 1
    return {
        "status": "ok",
        "added": added_count,
        "skipped": skipped_count,
        "errors": errors_count
    }


@app.get("/api/target-group")
async def get_target_group(user_data: dict = Depends(get_current_tg_user)):
    """
    Возвращает текущую целевую группу пользователя для пересылки сообщений.

    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Словарь с юзернеймом или ссылкой на целевую группу.
    """
    pt = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if pt and pt.created_group_link:
        return {"username": pt.created_group_link}
    return {"username": None}


@app.post("/api/target-group")
async def set_target_group(username: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Устанавливает целевую группу пользователя для пересылки сообщений.

    :param username: (str) Юзернейм или ссылка целевой группы.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус обновления и установленный юзернейм группы.
    """
    username = username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    pt, _ = UsersPersonalTrackings.get_or_create(user_id=user_data["id"])
    pt.created_group_link = username
    pt.save()
    return {"status": "ok", "username": username}


@app.get("/api/accounts")
async def list_accounts(user_data: dict = Depends(get_current_tg_user)):
    """
    Возвращает список подключенных Telegram-аккаунтов и кампаний пользователя.

    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: Список словарей с подробными данными аккаунтов.
    """
    records = list(
        UsersAccounts.select()
        .where(UsersAccounts.user_id == user_data["id"])
        .order_by(UsersAccounts.date_added.desc())
    )
    result = []
    for acc in records:
        user_key = f"{user_data['id']}_{acc.id}"
        is_running = user_key in active_clients or (bool(acc.is_active) and str(user_data['id']) in active_clients)
        result.append({
            "id": acc.id,
            "phone_number": acc.phone_number_session_string or "unknown",
            "account_title": acc.account_title or f"Аккаунт {acc.phone_number_session_string or acc.id}",
            "target_group_id": acc.target_group_id,
            "target_group_link": acc.target_group_link or "",
            "track_all_chats": bool(acc.track_all_chats),
            "is_active": is_running,
            "created_at": acc.date_added.strftime("%Y-%m-%d %H:%M:%S") if acc.date_added else ""
        })
    return result


@app.post("/api/accounts/{account_id}/settings")
async def update_account_web_settings(
        account_id: int,
        account_title: Optional[str] = Form(None),
        track_all_chats: Optional[bool] = Form(None),
        user_data: dict = Depends(get_current_tg_user)
):
    """
    Обновляет параметры кампании (название/тему и режим отслеживания всех чатов).
    """
    acc = UsersAccounts.get_or_none(
        (UsersAccounts.id == account_id) & (UsersAccounts.user_id == user_data["id"])
    )
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    if account_title is not None:
        acc.account_title = account_title.strip()
    if track_all_chats is not None:
        acc.track_all_chats = track_all_chats
    acc.save()
    return {"status": "ok", "account_title": acc.account_title, "track_all_chats": acc.track_all_chats}


@app.post("/api/accounts/{account_id}/sync-dialogs")
async def sync_account_web_dialogs(
        account_id: int,
        user_data: dict = Depends(get_current_tg_user)
):
    """
    Синхронизирует диалоги (включая приватные и закрытые группы) из аккаунта в список отслеживания.
    """
    acc = UsersAccounts.get_or_none(
        (UsersAccounts.id == account_id) & (UsersAccounts.user_id == user_data["id"])
    )
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    checker = CheckingAccountsValidity()
    client = await checker.client_connect_string_session(acc.user_session_string)
    if not client:
        raise HTTPException(status_code=400, detail="Failed to connect to Telegram account")

    try:
        from database.users_groups import sync_account_dialogs_to_db
        synced = await sync_account_dialogs_to_db(
            client=client,
            user_id=user_data["id"],
            user_session_string=acc.user_session_string,
            user_username=user_data.get("username") or "",
            user_firstname=user_data.get("first_name") or ""
        )
        await client.disconnect()
        return {"status": "ok", "count": len(synced), "synced": synced}
    except Exception as e:
        logger.error(f"Error syncing dialogs via web: {e}")
        try:
            await client.disconnect()
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/accounts/upload")
async def upload_account_session(file: UploadFile = File(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Загружает и подключает новый файл сессии Telegram-аккаунта.

    :param file: (UploadFile) Загружаемый файл сессии (.session).
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус подключения и информация об аккаунте.
    """
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not file.filename.endswith(".session"):
        raise HTTPException(status_code=400, detail="Only .session files are supported")
    # Создать временный каталог счетов
    sessions_dir = Path("accounts")
    sessions_dir.mkdir(exist_ok=True)
    # Дезинфицируйте и записывайте сессионный файл
    safe_name = "".join(c for c in file.filename if c.isalnum() or c in "._-")
    temp_path = sessions_dir / f"temp_{user_data["id"]}_{safe_name}"
    client = None
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        session_path_without_ext = str(temp_path.with_suffix(""))
        mock_msg = MockMessage(user_id=user_data["id"], username=user.username)
        checker = CheckingAccountsValidity(path=session_path_without_ext)
        client = await checker.connect_client()
        if client:
            try:
                account_info = await get_account_info(client)
                # phone = account_info.get("phone") or "unknown"
                session_string = StringSession.save(client.session)
                # Сохранить аккаунт в пользовательскую таблицу
                write_account_to_user_table(
                    user_id=user_data["id"],
                    session_string=session_string,
                    phone_number=account_info.get("phone"),
                    user_username=user_data.get("username") or "",
                    user_firstname=user_data.get("first_name") or ""
                )
                await client.disconnect()
                # Отправьте уведомление через бота
                # Определяем язык пользователя, который пользователь выбрал при старте бота
                user_lang = determines_user_language(message_or_callback=user_data["id"])
                await mock_msg.answer(
                    text=t("session_connected_success",
                           lang=user_lang,
                           filename=safe_name,
                           phone=account_info.get("phone"),
                           name=account_info.get("first_name")
                           )
                )
                return {"status": "ok", "phone": account_info.get("phone"), "name": account_info.get("first_name")}
            finally:
                if client and client.is_connected():
                    await client.disconnect()
        else:
            raise HTTPException(status_code=400, detail="Session file is invalid or not authorized")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing session file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as pe:
                logger.warning(f"Could not delete temporary session file {temp_path}: {pe}")


@app.delete("/api/accounts/{account_id_or_phone}")
async def delete_account(account_id_or_phone: str, user_data: dict = Depends(get_current_tg_user)):
    """
    Удаляет подключенный аккаунт пользователя по ID или номеру телефона.

    :param account_id_or_phone: (str) ID или номер телефона удаляемого аккаунта.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус выполнения операции.
    """
    user_id = user_data["id"]
    account = None
    if account_id_or_phone.isdigit():
        account = UsersAccounts.get_or_none(
            (UsersAccounts.user_id == user_id) & (UsersAccounts.id == int(account_id_or_phone))
        )
    if not account:
        account = UsersAccounts.get_or_none(
            (UsersAccounts.user_id == user_id) &
            (UsersAccounts.phone_number_session_string == account_id_or_phone)
        )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    session_to_delete = account.user_session_string

    # Останавливаем мониторинг этого аккаунта
    await stop_tracking(user_id=user_id, account_id=account.id)

    # Удаление из таблицы users_accounts
    deleted = account.delete_instance()

    # Очищаем сессию в таблице users_personal_trackings, если там был привязан этот аккаунт
    UsersPersonalTrackings.update(personal_account="").where(
        (UsersPersonalTrackings.user_id == user_id) &
        (UsersPersonalTrackings.personal_account == session_to_delete)
    ).execute()

    if deleted:
        # Также отключаем от глобальных активных клиентов, если подключен
        if str(user_id) in active_clients:
            # Нужно отключить активного клиента
            client = active_clients.pop(str(user_id))
            if client.is_connected():
                await client.disconnect()
            if str(user_id) in stop_flags:
                stop_flags.pop(str(user_id))
        return {"status": "ok"}
    raise HTTPException(status_code=500, detail="Failed to delete account")


@app.post("/api/payment/stars-topup")
async def create_topup_invoice(amount: int = Query(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Создает инвойс-ссылку на пополнение баланса звездами Telegram Stars.

    :param amount: (int) Количество покупаемых звезд Telegram Stars.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Словарь со ссылкой на оплату инвойса.
    """
    # Ссылка на счет пополнения Stars
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=user_data["id"])
    try:
        # TODO Сделать проверку на валидность ссылки
        invoice_link = await bot.create_invoice_link(
            title=t("stars_invoice_title", lang=user_lang),
            description=t("stars_invoice_desc", lang=user_lang, amount=amount),
            payload=f"topup_stars_{amount}",
            provider_token="",  # must be empty for Telegram Stars
            currency="XTR",
            prices=[LabeledPrice(label="Stars", amount=amount)]
        )
        return {"invoice_link": invoice_link}
    except Exception as e:
        logger.exception(f"Error creating invoice link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/searchs/ai")
async def trigger_ai_searchs(query: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Массовый поиск групп в Telegram по запросу пользователя с помощью AI.

    :param query: (str) Запрос пользователя для поиска групп или каналов в Telegram.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус выполнения и список найденных групп.
    """
    logger.info(
        f"Запрос пользователя {user_data['id']} {user_data.get('last_name', '')} {user_data.get('first_name', '')} {user_data.get('username', '')}: {query}")
    all_saved_groups = []
    words = re.findall(r'\w+', query)
    for word in words:
        logger.info(f"Поиск группы: {word}")
        try:
            # mock_msg = MockMessage(user_id=user_data["id"], username=user_data["username"])
            # Парсим ввод в список запросов (query - запросс пользователя)
            search_terms = parse_search_input(user_input=word)
            if not search_terms:
                return
            try:
                # 🔄 Обрабатываем КАЖДЫЙ запрос через НОВЫЙ случайный аккаунт
                for idx, term in enumerate(search_terms, 1):
                    logger.info(f"[{idx}/{len(search_terms)}] Запрос: '{term}'")
                    # ✅ Создаем checker БЕЗ path (он не нужен для работы с БД)
                    checker = CheckingAccountsValidity()  # path=None по умолчанию
                    try:
                        client = await checker.start_random_client()
                        if not client:
                            logger.warning(f"⚠️ Не удалось запустить клиент для '{term}', пропускаю")
                            continue
                        # Получаем варианты названий от AI
                        answer = await get_groq_response(term)
                        # Чистим и фильтруем названия
                        group_names = parse_ai_group_names(answer)
                        logger.info(f"🔍 Ищу {len(group_names)} вариантов для '{term}'")
                        # Ищем группы в Telegram
                        results = await search_groups_in_telegram(
                            client=client,
                            group_names=group_names
                        )
                        logger.info(f"✅ Найдено {len(results)} групп для '{term}'")
                        # Сохраняем в БД
                        for group_data in results:
                            saved_group = save_group_to_db(group_data)
                            if saved_group:
                                all_saved_groups.append(saved_group)
                        # 🔌 Обязательно отключаем клиент после каждого запроса
                        if client:
                            await client.disconnect()
                            logger.info(f"🔌 Клиент для '{term}' отключён")
                        # Пауза между запросами (защита от лимитов API и Telegram)
                        if idx < len(search_terms):
                            await asyncio.sleep(2)
                    except Exception as e:
                        logger.warning(f"⚠️ Ошибка при обработке '{term}': {e}")
                        continue  # Продолжаем со следующим запросом

            except Exception as e:
                logger.error(f"❌ Критическая ошибка: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при обработке '{term}': {e}")

    # ✅ Проверяем, были ли найдены и сохранены группы
    if all_saved_groups:
        # 📤 Формируем и отправляем Excel-файл пользователю в Telegram чат
        try:
            # Определяем язык пользователя, который пользователь выбрал при старте бота
            user_lang = determines_user_language(message_or_callback=user_data["id"])
            excel_bytes = create_excel_file(all_saved_groups, lang=user_lang)
            filename = f"telegram_groups_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_file = BufferedInputFile(excel_bytes, filename=filename)
            caption_text = t("found_groups_caption", lang=user_lang, count=len(all_saved_groups))
            # Отправка итогового файла через бота
            await bot.send_document(chat_id=user_data["id"], document=excel_file, caption=caption_text)
            logger.info(f"✅ Итоговый Excel-файл отправлен пользователю {user_data['id']}")
        except Exception as send_err:
            logger.warning(f"⚠️ Не удалось отправить Excel-файл пользователю {user_data['id']}: {send_err}")
    else:
        # ❌ Сообщение выводится только если группы действительно НЕ были найдены
        logger.info(t("global_search_no_results", lang="ru"))
    return {"status": "ok", "groups": all_saved_groups}


@app.post("/api/search/ai")
async def trigger_ai_search(query: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Ищет группы в Telegram по запросу пользователя с помощью AI.

    :param query: (str) Запрос пользователя для генерации названий и поиска групп.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Статус выполнения и список найденных групп.
    """
    logger.info(
        f"Запрос пользователя {user_data['id']} {user_data.get('last_name', '')} {user_data.get('first_name', '')}: {query}")
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        answer = await get_groq_response(query)
        group_names = parse_ai_group_names(answer)
        if not group_names:
            return {"status": "no_names_generated", "groups": []}
        checker = CheckingAccountsValidity()
        client = await checker.start_random_client()
        if not client:
            raise HTTPException(status_code=400, detail="В поиске нет активных аккаунтов Telegram.")
        saved_groups = []
        try:
            for name in group_names:
                results = await search_groups_in_telegram(client=client, group_names=[name])
                logger.info(f"Результаты поиска: {results}")
                for group_data in results:
                    saved = save_group_to_db(group_data)
                    if saved:
                        saved_groups.append({
                            "id": saved.id,
                            "telegram_id": saved.telegram_id or saved.id,
                            "name": saved.name,
                            "username": saved.username,
                            "participants": saved.participants,
                            "group_type": saved.group_type,
                            "availability": saved.availability,
                            "link": saved.link
                        })
        finally:
            await client.disconnect()
        return {"status": "ok", "groups": saved_groups}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"AI search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search/export_excel")
async def export_search_results_excel(telegram_ids: str = Form(...), user_data: dict = Depends(get_current_tg_user)):
    """
    Экспортирует результаты поиска групп в файл Excel.

    :param telegram_ids: (str) Строка с разделенными запятыми идентификаторами групп.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (Response) HTTP-ответ с файлом таблицы Excel.
    """
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    raw_ids = [i.strip() for i in telegram_ids.split(",") if i.strip()]
    ids = []
    for item in raw_ids:
        try:
            ids.append(int(item))
        except ValueError:
            pass
    if not ids:
        raise HTTPException(status_code=400, detail="No valid group IDs provided")
    groups = list(TelegramGroups.select().where(
        (TelegramGroups.id.in_(ids)) | (TelegramGroups.telegram_id.in_(ids))
    ))
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=user_data["id"])
    excel_bytes = create_excel_file(groups, lang=user_lang)
    filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    # Отправляем документ также напрямую в чат Telegram пользователю
    try:
        doc = BufferedInputFile(excel_bytes, filename=filename)
        caption_text = t("excel_export_caption", lang=user_lang)
        await bot.send_document(chat_id=user_data["id"], document=doc, caption=caption_text)
        logger.info(f"Excel-файл с результатами поиска отправлен в чат Telegram {user_data["id"]}")
    except Exception as e:
        logger.warning(f"Не удалось отправить Excel-файл с результатами поиска в чат {user_data["id"]}: {e}")
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/export/check")
async def check_export_status(user_data: dict = Depends(get_current_tg_user)):
    """
    Проверяет возможность бесплатной выгрузки базы данных и баланс звезд.

    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (dict) Данные о бесплатной выгрузке, оставшемся времени и балансе звезд.
    """
    # Получить базу данных / Экспортировать XLSX Endpoint
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    is_free, remaining = can_user_download_free(user)
    return {
        "is_free": is_free,
        "remaining_seconds": remaining,
        "stars_balance": user.stars
    }


@app.post("/api/export/download")
async def download_database(
        export_type: str = Form("all"),  # "all", "channels", "groups"
        category: Optional[str] = Form(None),  # e.g. "investments"
        user_data: dict = Depends(get_current_tg_user)
):
    """
    Выполняет выгрузку базы данных Telegram-групп в файл Excel.

    :param export_type: (str) Тип выгрузки ("all", "channels" или "groups").
    :param category: (Optional[str]) Фильтр по категории групп.
    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (Response) HTTP-ответ с файлом выгрузки Excel.
    """
    user = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_data["id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Проверьте, бесплатная ли загрузка или требуется ли звёздочки.
    is_free, remaining = can_user_download_free(user)
    if not is_free:
        # Нужно вычесть 5 звёзд из баланса
        if user.stars < 5:
            raise HTTPException(
                status_code=402,
                detail="Payment required: Need 5 Telegram Stars to download before 24h limit expires"
            )
        # Deduct
        user.stars -= 5
        user.save()
        logger.info(f"Deducted 5 Stars from {user_data["id"]}. New balance: {user.stars}")
    else:
        # Record free download timestamp
        user.last_free_download_at = datetime.now()
        user.save()
    # Группы запросов
    query = TelegramGroups.select()
    if export_type == "channels":
        query = query.where(TelegramGroups.group_type == "Канал")
    elif export_type == "groups":
        query = query.where(TelegramGroups.group_type != "Канал")
    if category and category != "all":
        query = query.where(TelegramGroups.category == category.lower())
    groups = list(query)
    # Создать Excel в памяти
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=user_data["id"])
    excel_bytes = create_excel_file(groups, lang=user_lang)
    filename = f"db_export_{export_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    # Отправляем документ также напрямую в чат Telegram пользователю
    try:
        doc = BufferedInputFile(excel_bytes, filename=filename)
        caption_text = t("db_export_caption", lang=user_lang)
        await bot.send_document(chat_id=user_data["id"], document=doc, caption=caption_text)
        logger.info(f"Excel-файл базы данных отправлен в чат Telegram {user_data["id"]}")
    except Exception as e:
        logger.warning(f"Не удалось отправить Excel-файл базы данных в чат {user_data["id"]}: {e}")
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


def io_bytes_stream(data: bytes):
    """
    Генерирует поток байтов из буфера в памяти для передачи файла.

    :param data: (bytes) Байтовые данные для генерации потока.
    :yield: Части байтового потока.
    """
    stream = io.BytesIO(data)
    yield from stream


# ==================== КОНЕЧНЫЕ ТОЧКИ API ПАНЕЛИ АДМИНИСТРАТОРА ====================


def require_admin(user_data: dict = Depends(get_current_tg_user)):
    """
    Проверяет наличие прав администратора у текущего пользователя.

    :param user_data: (dict) Данные авторизованного пользователя Telegram.
    :return: (int) Идентификатор администратора.
    """
    is_admin = int(user_data["id"]) == int(ADMIN_USER_ID)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Access denied: Admin only")
    return user_data["id"]


@app.get("/api/admin/status")
async def get_admin_status(_: int = Depends(require_admin)):
    """
    Возвращает статус фоновых административных задач и системную статистику.

    :return: (dict) Статистика по группам без категории, аккаунтам и состоянию фоновой задачи.
    """
    # Рассчитать группы без категории
    uncategorized_count = TelegramGroups.select().where(
        (TelegramGroups.username.is_null(False)) &
        ((TelegramGroups.category == '') | (TelegramGroups.category.is_null()))
    ).count()
    # Получить общее количество счетов
    total_accounts = UsersAccounts.select().count()
    return {
        "uncategorized_count": uncategorized_count,
        "total_accounts": total_accounts,
        "task": admin_task_status
    }


# Фоновые задачи администрирования


async def bg_check_accounts():
    """
    Фоновая задача проверки свободных аккаунтов на валидность.

    :return: None
    """
    logger.info("Начинаем проверку аккаунтов...")
    global admin_task_status
    admin_task_status["action"] = "check_accounts"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Starting account verification..."
    try:
        available_sessions = getting_free_account()
        total = len(available_sessions)
        admin_task_status["total"] = total
        checker = CheckingAccountsValidity()
        for idx, session in enumerate(available_sessions, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Checking session {idx}/{total}..."
            await checker.verify_free_account(session_name=session, user_lang="ru")
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = "Account check completed successfully!"
    except Exception as e:
        logger.exception(f"Error in bg_check_accounts: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"


async def bg_actualize_db():
    """
    Фоновая задача актуализации базы данных групп и каналов.

    :return: None
    """
    admin_task_status["action"] = "actualize"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Initializing database actualization..."
    try:
        available_sessions = getting_free_account()  # Получение свободных аккаунтов из базы данных
        if not available_sessions:
            raise Exception("Нет активных сеансов Telegram.")
        # Получение всех данных из таблицы telegram_groups, что бы в дальнейшем, актуализировать весь список и
        # заполнить недостающие данные.
        data = get_all_data_telegram_groups()
        total = len(data)  # Количество групп в базе данных
        admin_task_status["total"] = total
        admin_task_status["progress"] = 0
        admin_task_status["message"] = f"Проверка групп: 0 / {total}"
        for index, group in enumerate(data, start=1):
            admin_task_status["progress"] = index
            admin_task_status["message"] = (
                f"Проверка группы {index} / {total}: {group['username']}"
            )
            logger.info(
                f"{group['telegram_id']} | {group['group_hash']} | {group['name']} | {group['username']} | {group['description']} | {group['participants']} | {group['category']} | {group['group_type']} | {group['language']} | {group['link']} | {group['availability']} | {group['date_added']}"
            )
            """
            Определение категории группы / канала
            """
            if group['category'] == '':  # Проверка наличия категории у группы (если пустая строка, то пропускаем).
                logger.info(f"Найдена группа {group['username']} без категории, определяем категорию")
                client = AsyncGroq(api_key=GROQ_API_KEY)
                # Рандомно выбираем модель для определения категории
                models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
                model = random.choice(models)
                result = await category_assignment(
                    group_data=group,
                    client=client,
                    model=model
                )
                if result.get("success") and result.get("category"):
                    # ✅ Сразу пишем в БД (в нижнем регистре)
                    category_lower = result["category"].lower()
                    await sync_to_async(
                        lambda cat=category_lower, tid=result["telegram_id"]: TelegramGroups.update(category=cat)
                        .where(TelegramGroups.telegram_id == tid)
                        .execute(),
                        thread_sensitive=True
                    )()
                    logger.info(f"✅ {group['name']} → {category_lower}")
                else:
                    logger.warning(f"❌ {group['name']} — AI не определил")
                # Пауза только для g4f (чтобы не блокировали)
                if type(client).__name__ == 'Client':  # g4f клиент
                    await asyncio.sleep(0.5)
            # TODO убрать дублирование кода
            """
            Определение языка групп / каналов и запись в базу данных
            """
            if group['language'] == '':  # Проверка наличия языка в гуппах / каналах
                logger.info(f"Найдена группа {group['username']} без языка, определяем язык")
                lang_code = detect_language(group['name'])
                if lang_code:
                    logger.info(f"Определён язык для группы {group['username']}: {lang_code}")
                    # ✅ Сразу пишем в БД (в нижнем регистре)
                    await sync_to_async(
                        lambda lcode=lang_code, tid=group['telegram_id']: TelegramGroups.update(language=lcode)
                        .where(TelegramGroups.telegram_id == tid)
                        .execute(),
                        thread_sensitive=True
                    )()
                    logger.info(f"✅ {group['name']} → {lang_code}")
                else:
                    logger.warning(f"Язык для группы {group['username']} не определён")
            """
            Определение типа группы и запись в базу данных
            """
            if group['group_type'] == '':  # Проверка наличия типа в группах / каналах
                logger.info(f"Найдена группа {group['username']} без типа, определяем тип")
                checker = CheckingAccountsValidity()  # path=None по умолчанию
                client = await checker.start_random_client()
                if not client:
                    logger.error(f"Не удалось запустить клиент для группы {group['username']}")
                    continue
                try:
                    account_info = await get_account_info(client)
                    if account_info:
                        logger.info(
                            f"Используется аккаунт: {account_info.get('id')}, {account_info.get('phone')}, {account_info.get('first_name')}, {account_info.get('last_name')}, @{account_info.get('username')}")
                        admin_task_status[
                            "message"] = f"Подключение к аккаунту: {account_info.get('id')}, {account_info.get('phone')}, @{account_info.get('username')}..."
                    entity = await client.get_entity(group['username'])
                    logger.info(entity)
                    # Получить полную информацию
                    data_full = await get_full_info_group(client, entity)
                    logger.info(f"Полная информация: {data_full}")
                    logger.info(f"Описание: {data_full.get('description', '')}")
                    # Обновить базу данных
                    update_group_channels_data_base(data_full, entity, group)
                except UsernameInvalidError:
                    logger.error(f"Не валидный username {group['username']}")
                except ValueError:
                    logger.error(f"Не валидный username {group['username']}")
                except FloodWaitError as e:
                    logger.warning(f"FloodWait для {group['username']}: нужно подождать {e.seconds} секунд.")
                except AuthKeyUnregisteredError:
                    logger.error(f"Не валидная сессия для проверки группы {group['username']}")
                except Exception as e:
                    logger.exception(f"Не удалось обновить группу {group['username']}: {e}")
                finally:
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                await asyncio.sleep(1.5)
            admin_task_status["progress"] = index
        admin_task_status["status"] = "completed"
    except Exception as e:
        logger.exception(f"Error in bg_actualize_db: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"


async def bg_categorize_db(method: str):
    """
    Выполняет фоновую классификацию групп по категориям с помощью нейросетей.

    :param method: (str) Выбранный метод классификации ("fast", "openrouter" или "groq").
    :return: None
    """
    global admin_task_status
    admin_task_status["action"] = "categorize"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Initializing category assignment..."
    try:
        # 1. Настройка клиента на основе метода
        if method == "fast":
            client = Client()
            model = await get_best_g4f_model(client)
        elif method == "openrouter":
            client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=OPENROUTER_API_KEY)
            model = "deepseek/deepseek-v4-flash"
        elif method == "groq":
            client = AsyncGroq(api_key=GROQ_API_KEY)
            model = "llama-3.1-8b-instant"
        else:
            raise Exception(f"Unknown categorization method: {method}")
        groups_to_process = await get_groups_without_category()
        total = len(groups_to_process)
        admin_task_status["total"] = total
        if total == 0:
            admin_task_status["status"] = "completed"
            admin_task_status["message"] = "All groups already have categories!"
            return
        for idx, group_data in enumerate(groups_to_process, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Categorizing {group_data['name']} ({idx}/{total})..."
            try:
                result = await category_assignment(group_data, client, model)
                if result.get("success") and result.get("category"):
                    category_lower = result["category"].lower()

                    TelegramGroups.update(category=category_lower).where(

                        TelegramGroups.telegram_id == result["telegram_id"]

                    ).execute()

            except Exception as e:

                logger.exception(f"Failed to categorize {group_data['name']}: {e}")

            if method == "fast":

                await asyncio.sleep(0.5)

            else:

                await asyncio.sleep(0.2)
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = f"Category assignment finished! Categorized {total} groups."
    except Exception as e:
        logger.exception(f"Error in bg_categorize_db: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"


async def bg_detect_language():
    """
    Выполняет фоновое определение языка групп с помощью нейросетей.

    :return: None
    """
    global admin_task_status
    admin_task_status["action"] = "lang_detect"
    admin_task_status["status"] = "running"
    admin_task_status["progress"] = 0
    admin_task_status["message"] = "Initializing language detection..."
    try:
        groups_to_detect = list(TelegramGroups.select().where(
            (TelegramGroups.username.is_null(False)) &
            ((TelegramGroups.language == '') | (TelegramGroups.language.is_null()))
        ))
        total = len(groups_to_detect)
        admin_task_status["total"] = total
        if total == 0:
            admin_task_status["status"] = "completed"
            admin_task_status["message"] = "All groups already have language set!"
            return
        for idx, group in enumerate(groups_to_detect, 1):
            admin_task_status["progress"] = idx
            admin_task_status["message"] = f"Detecting language for {group.name or group.username} ({idx}/{total})..."
            group_data = {
                "group_hash": group.group_hash,
                "name": group.name,
                "username": group.username,
                "description": group.description or ""
            }
            try:
                res = await asyncio.to_thread(ai_llama_fri, group_data, lang="ru")
                if res.get("success") and res.get("language"):
                    TelegramGroups.update(language=res["language"]).where(
                        TelegramGroups.group_hash == res["group_hash"]
                    ).execute()
            except Exception as e:
                logger.exception(f"Failed to detect language for {group.name}: {e}")
            await asyncio.sleep(2.0)
        admin_task_status["status"] = "completed"
        admin_task_status["message"] = f"Language detection finished! Processed {total} groups."
    except Exception as e:
        logger.exception(f"Error in bg_detect_language: {e}")
        admin_task_status["status"] = "error"
        admin_task_status["message"] = f"Error: {e}"


@app.post("/api/admin/check-accounts")
async def admin_check_accounts(background_tasks: BackgroundTasks, _: int = Depends(require_admin)):
    """
    Запускает административную задачу проверки валидности всех аккаунтов.

    :param background_tasks: (BackgroundTasks) Менеджер фоновых задач FastAPI.
    :return: (dict) Статус запуска задачи.
    """
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_check_accounts)
    return {"status": "started"}


@app.post("/api/admin/actualize")
async def admin_actualize_db(background_tasks: BackgroundTasks, _: int = Depends(require_admin)):
    """
    Запускает административную задачу актуализации базы групп через Telegram.

    :param background_tasks: (BackgroundTasks) Менеджер фоновых задач FastAPI.
    :return: (dict) Статус запуска задачи.
    """
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_actualize_db)
    return {"status": "started"}


@app.post("/api/admin/categorize")
async def admin_categorize_db(
        method: str = Query("fast"),
        background_tasks: BackgroundTasks = BackgroundTasks(),
        _: int = Depends(require_admin)
):
    """
    Запускает административную задачу категоризации групп с помощью AI.

    :param method: (str) Метод категоризации ("fast", "openrouter", "groq").
    :param background_tasks: (BackgroundTasks) Менеджер фоновых задач FastAPI.
    :return: (dict) Статус запуска задачи.
    """
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_categorize_db, method=method)
    return {"status": "started"}


@app.post("/api/admin/detect-language")
async def admin_detect_language(background_tasks: BackgroundTasks, _: int = Depends(require_admin)):
    """
    Запускает административную задачу определения языков групп через AI.

    :param background_tasks: (BackgroundTasks) Менеджер фоновых задач FastAPI.
    :return: (dict) Статус запуска задачи.
    """
    if admin_task_status["status"] == "running":
        return {"status": "busy", "task": admin_task_status}
    background_tasks.add_task(bg_detect_language)
    return {"status": "started"}


@app.get("/api/admin/export-questions")
async def admin_export_questions(_: int = Depends(require_admin)):
    """
    Экспортирует вопросы пользователей из базы данных в CSV-файл.

    :return: (StreamingResponse) Потоковый ответ с CSV-файлом вопросов.
    """
    questions = get_all_questions()
    if not questions:
        raise HTTPException(status_code=404, detail="No questions found in database")
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "question_number", "user_id", "user_username", "user_firstname",
            "user_question", "answer_ai", "status_question", "date_added"
        ],
        extrasaction="ignore"
    )
    writer.writeheader()
    for q in questions:
        writer.writerow(q)
    filename = f"questions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        io_bytes_stream(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/admin/logs")
async def admin_download_logs(_: int = Depends(require_admin)):
    """
    Отдает файл логов бота администратору.

    :return: (FileResponse) Файл логов приложения.
    """
    log_path = "logs/log.log"
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    return FileResponse(log_path, media_type="text/plain", filename="bot_log.txt")


@app.get("/api/admin/nightly-check")
async def get_admin_nightly_check(_: int = Depends(require_admin)):
    """
    Возвращает текущие настройки и статус ночной проверки базы данных.
    """
    from handlers.admin.nightly_check import get_nightly_check_settings
    settings = get_nightly_check_settings()
    remaining_no_cat = TelegramGroups.select().where(
        (TelegramGroups.category.is_null()) | (TelegramGroups.category == '')
    ).count()
    remaining_no_lang = TelegramGroups.select().where(
        (TelegramGroups.language.is_null()) | (TelegramGroups.language == '')
    ).count()
    return {
        "status": "ok",
        "settings": settings,
        "remaining_no_cat": remaining_no_cat,
        "remaining_no_lang": remaining_no_lang
    }


@app.post("/api/admin/nightly-check/toggle")
async def toggle_admin_nightly_check(_: int = Depends(require_admin)):
    """
    Включает или выключает автоматическую ночную проверку базы данных в 01:00.
    """
    from handlers.admin.nightly_check import toggle_nightly_check, get_nightly_check_settings
    new_state = toggle_nightly_check()
    settings = get_nightly_check_settings()
    return {"status": "ok", "enabled": new_state, "settings": settings}


@app.post("/api/admin/nightly-check/run")
async def trigger_admin_nightly_check(background_tasks: BackgroundTasks, _: int = Depends(require_admin)):
    """
    Запускает проверку и актуализацию базы данных прямо сейчас в фоновом режиме.
    """
    from handlers.admin.nightly_check import run_database_integrity_check
    background_tasks.add_task(run_database_integrity_check, manual=True)
    return {"status": "started", "message": "Проверка базы данных запущена в фоне"}


# Роутер для статичных файлов и веб-интерфейса

static_router = APIRouter()


@static_router.get("/")
async def serve_index(request: Request):
    """
    Отдает главную HTML-страницу веб-интерфейса Mini App.

    :param request: (Request) Входящий HTTP-запрос.
    :return: (FileResponse) HTML-страница приложения.
    """
    user_str = "Анонимный пользователь"
    auth_header = request.headers.get("Authorization")
    query_params = dict(request.query_params)
    token = auth_header or query_params.get("tgWebAppData") or query_params.get("initData") or query_params.get(
        "init_data") or query_params.get("token")
    user_data = None
    if token:
        if token.startswith("Bearer "):
            token = token[7:]
        if token.startswith("mock_"):
            try:
                mock_id = int(token.split("_")[1])
                user_data = {"id": mock_id, "username": f"test_user_{mock_id}", "first_name": "Test"}
            except Exception:
                pass
        else:
            try:
                params = dict(urllib.parse.parse_qsl(token, keep_blank_values=True))
                if 'user' in params:
                    user_data = json.loads(params['user'])
            except Exception:
                pass
    if not user_data and ("user_id" in query_params or "id" in query_params):
        uid = query_params.get("user_id") or query_params.get("id")
        user_data = {
            "id": uid,
            "username": query_params.get("username"),
            "first_name": query_params.get("first_name", "")
        }
    client_ip = get_client_ip(request)
    detected_lang = await detect_language_by_ip(client_ip, request.headers.get("accept-language"))
    if user_data:
        uid = user_data.get("id", "неизвестен")
        username = user_data.get("username")
        username_str = f"@{username}" if username else "без username"
        first_name = user_data.get("first_name", "")
        user_str = f"{first_name} ({username_str}, ID: {uid})"
    else:
        user_str = "Гость"
    session_key = (user_str, client_ip)
    if session_key not in logged_user_sessions:
        logged_user_sessions.add(session_key)
        logger.info(
            f"🌐 Пользователь {user_str} [IP: {client_ip}, Язык по IP: {detected_lang}] перешел на начальную страницу")
    return FileResponse("web/static/index.html")


@static_router.get("/{file_path:path}")
async def serve_static(file_path: str):
    """
    Отдает статические файлы веб-интерфейса Mini App.

    :param file_path: (str) Путь к запрашиваемому статическому файлу.
    :return: (FileResponse) Статический файл или index.html для SPA маршрутизации.
    """
    target_path = os.path.join("web/static", file_path)
    if os.path.isfile(target_path):
        return FileResponse(target_path)
    index_path = os.path.join("web/static", "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="File not found")


app.include_router(static_router)
