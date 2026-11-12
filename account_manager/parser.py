import asyncio
import random

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import events, types
from telethon.tl.functions.channels import GetFullChannelRequest

from account_manager.auth import CheckingAccountsValidity
from account_manager.subscription import subscription_telegram
from account_manager.utilit import detect_language
from core.config import forwarded_messages, active_clients, stop_flags
from database.database import TelegramGroups
from database.users_groups import get_user_channel_usernames, get_user_channels_or_notify
from database.users_keywords import get_user_keywords
from database.users_personal_trackings import get_group_id_with_personal_tracking, UsersPersonalTrackings
from handlers.user_language import determines_user_language
from keyboards.keyboards import menu_launch_tracking_keyboard
from locales.locales import t


async def get_full_info_group(client, entity):
    """
    Получение полной информации о группе или канале Telegram.

    :param client: (TelegramClient) Активный клиент Telethon.
    :param entity: (Channel | Chat) Сущность группы или канала из Telethon.
    :return: (dict | None) Словарь с данными группы (description, participants, link, group_type, actual_username, title) или None при ошибке.
    """
    try:

        full_channel = await client(GetFullChannelRequest(channel=entity))
        description = full_channel.full_chat.about or ""
        participants = full_channel.full_chat.participants_count or 0
        link = f"https://t.me/{entity.username}" if entity.username else None or ""
        new_group_type = determine_telegram_chat_type(entity)
        actual_username = f"@{entity.username}" if entity.username else ""
        title = entity.title or "Без названия"

        return {
            "description": description,
            "participants": participants,
            "link": link,
            "group_type": new_group_type,
            "actual_username": actual_username,
            "title": title
        }

    except Exception as e:

        logger.exception(f"⚠️ Не удалось получить полные данные для {entity.username or entity.id}: {e}")


def _clean_tg_id(val) -> str:
    """Нормализует Telegram ID, удаляя префиксы -100 и -."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.startswith("-100"):
        return s[4:]
    if s.startswith("-"):
        return s[1:]
    return s


def is_chat_monitored_by_user(chat_id: int, chat_username: str, user_id: int, entity=None, session_string: str = None, track_all_chats: bool = False) -> bool:
    """
    Проверяет, входит ли чат в список отслеживаемых групп/каналов пользователя (с поддержкой закрытых групп и мульти-аккаунтов).

    :param chat_id: (int) ID чата из Telethon.
    :param chat_username: (str) Username чата (если есть).
    :param user_id: (int) ID пользователя.
    :param entity: Сущность чата (если доступна).
    :param session_string: (str | None) Фильтр по строке сессии конкретного аккаунта.
    :param track_all_chats: (bool) Если True, отслеживаются ВСЕ чаты/группы аккаунта (открытые и закрытые).
    :return: (bool) True, если чат отслеживается данным пользователем.
    """
    if track_all_chats:
        return True

    try:
        from database.users_groups import UsersGroups
        query = UsersGroups.select().where(UsersGroups.user_id == user_id)
        if session_string:
            acc_groups = list(query.where(UsersGroups.user_session_string == session_string))
            user_groups = acc_groups if acc_groups else list(query)
        else:
            user_groups = list(query)

        if not user_groups:
            return False

        clean_chat_id = _clean_tg_id(chat_id)
        entity_clean_id = _clean_tg_id(getattr(entity, 'id', None)) if entity else ""
        clean_user_chat = (chat_username or "").lower().lstrip("@")
        chat_title = (getattr(entity, 'title', None) or "").strip().lower()

        for g in user_groups:
            # 1. Проверка по сохраненному id_group (для закрытых чатов)
            if g.id_group:
                clean_g_id = _clean_tg_id(g.id_group)
                if clean_g_id and (clean_g_id == clean_chat_id or (entity_clean_id and clean_g_id == entity_clean_id)):
                    return True

            # 2. Проверка по названию закрытой группы (когда аккаунт зашел через tdata без инвайт-ссылки)
            if g.name_group and chat_title:
                if g.name_group.strip().lower() == chat_title:
                    if not g.id_group and chat_id:
                        try:
                            g.id_group = chat_id
                            g.save()
                        except Exception:
                            pass
                    return True

            # 3. Проверка по username_group / ссылке
            stored = (g.username_group or "").strip()
            if not stored:
                continue

            stored_target = stored.rstrip("/").split("/")[-1].lower().lstrip("@")

            # 3.1 Проверка по юзернейму
            if clean_user_chat and stored_target == clean_user_chat:
                if not g.id_group and chat_id:
                    try:
                        g.id_group = chat_id
                        g.save()
                    except Exception:
                        pass
                return True

            # 3.2 Проверка по числовому ID
            stored_id = _clean_tg_id(stored_target)
            if stored_id and (stored_id == clean_chat_id or (entity_clean_id and stored_id == entity_clean_id)):
                if not g.id_group and chat_id:
                    try:
                        g.id_group = chat_id
                        g.save()
                    except Exception:
                        pass
                return True

        return False
    except Exception as e:
        logger.error(f"Ошибка проверки отслеживания чата {chat_id}: {e}")
        return True


async def process_message(client, message: Message, chat_id: int, user_id, target_group_id=None, session_string=None, track_all_chats=False, account_title=""):
    """
    Обрабатывает входящее сообщение, проверяет его на совпадение с ключевыми словами и пересылает в целевую группу с
    контекстом при совпадении (с поддержкой закрытых групп и мульти-кампаний).

    :param client: (TelegramClient) Активный клиент Telethon.
    :param message: (Message) Входящее сообщение для обработки.
    :param chat_id: (int) Идентификатор чата-источника.
    :param user_id: (int | str) Идентификатор пользователя, чьи ключевые слова используются.
    :param target_group_id: (int | None) Идентификатор целевой группы для пересылки.
    :param session_string: (str | None) Фильтр по сессии для персональных ключевых слов.
    :param track_all_chats: (bool) Флаг отслеживания всех чатов аккаунта.
    :param account_title: (str) Название кампании (например, "Диваны", "Холодильники").
    :return: None
    """
    if not message.message:
        return

    # Защита от бесконечного цикла: игнорируем сообщения из группы для уведомлений
    if not target_group_id:
        target_group_id = get_group_id_with_personal_tracking(int(user_id))
    if target_group_id and (chat_id == target_group_id or str(chat_id) == str(target_group_id)):
        return

    # Получаем информацию о чате-источнике (сначала из message.chat, затем через client.get_entity)
    chat_entity = getattr(message, "chat", None)
    if not chat_entity:
        try:
            chat_entity = await client.get_entity(chat_id)
        except Exception as e:
            logger.debug(f"Не удалось получить сущность для чата {chat_id}: {e}")

    chat_username = ""
    if chat_entity:
        chat_username = getattr(chat_entity, "username", None) or ""

    # Проверяем, отслеживает ли пользователь данный чат
    if not is_chat_monitored_by_user(
        chat_id=chat_id,
        chat_username=chat_username,
        user_id=int(user_id),
        entity=chat_entity,
        session_string=session_string,
        track_all_chats=track_all_chats
    ):
        return

    message_text = message.message.lower()
    msg_key = f"{chat_id}-{message.id}"

    if msg_key in forwarded_messages:
        return

    # Получаем ключевые слова из базы данных для данного пользователя (с привязкой к сессии аккаунта)
    keywords = get_user_keywords(user_id=int(user_id), user_session_string=session_string)
    if not keywords:
        return

    keywords_lower = [keyword.lower() for keyword in keywords]
    matched_keyword = next((keyword for keyword in keywords_lower if keyword in message_text), None)

    if matched_keyword:
        logger.info(f"📌 Найдено совпадение по ключевому слову '{matched_keyword}'. Сообщение ID={message.id}")
        forwarded_messages.add(msg_key)

        try:
            # Формируем ссылку на сообщение (предпочитаем публичный username, иначе приватный /c/)
            if chat_username:
                message_link = f"https://t.me/{chat_username}/{message.id}"
            elif str(chat_id).startswith("-100"):
                clean_chat_id = str(chat_id)[4:]
                message_link = f"https://t.me/c/{clean_chat_id}/{message.id}"
            else:
                clean_chat_id = str(chat_id).lstrip("-")
                message_link = f"https://t.me/c/{clean_chat_id}/{message.id}"

            # 1. Отправляем форматированное уведомление через бота напрямую в созданную группу
            try:
                from handlers.user.personal_tracking import send_personal_tracking_alert
                await send_personal_tracking_alert(
                    user_id=int(user_id),
                    matched_keyword=matched_keyword,
                    message_text=message.message,
                    message_link=message_link,
                    target_group_id=target_group_id,
                    account_title=account_title
                )
                logger.info(f"✅ Алерт отправлен ботом в группу уведомлений пользователя {user_id}")
            except Exception as alert_err:
                logger.error(f"❌ Ошибка отправки алерта ботом: {alert_err}")

            # 2. Пересылаем сообщение через клиент Telethon в целевую группу результатов
            if target_group_id:
                try:
                    # Разрешаем сущность группы назначения
                    try:
                        target_entity = await client.get_input_entity(int(target_group_id))
                    except Exception:
                        target_entity = await client.get_entity(int(target_group_id))

                    # 1. Пробуем пересылку по message.id с from_peer
                    fwd_ok = False
                    try:
                        await client.forward_messages(
                            entity=target_entity,
                            messages=message.id,
                            from_peer=chat_id
                        )
                        fwd_ok = True
                    except Exception as fwd_err1:
                        logger.debug(
                            f"Попытка пересылки по ID не удалась ({fwd_err1}). Пробуем через объект сообщения...")
                        try:
                            await client.forward_messages(
                                entity=target_entity,
                                messages=message
                            )
                            fwd_ok = True
                        except Exception as fwd_err2:
                            logger.warning(
                                f"⚠️ Не удалось переслать сообщение через Telethon в группу {target_group_id}: {fwd_err2}")

                    if fwd_ok:
                        logger.info(
                            f"✅ Сообщение {message.id} успешно переслано клиентом Telethon в целевую группу (ID={target_group_id})")
                except Exception as ent_err:
                    logger.warning(
                        f"⚠️ Не удалось разрешить целевую группу {target_group_id} для пересылки через Telethon: {ent_err}")

        except Exception as e:
            logger.exception(f"❌ Ошибка при отправке уведомления о сообщении: {e}")


def determine_telegram_chat_type(entity):
    """
    Определяет тип чата в Telegram по сущности.

    Поддерживаемые типы:
    - 'Группа (супергруппа)' — если это мегагруппа
    - 'Канал' — если это канал (broadcast)
    - 'Обычный чат (группа старого типа)' — обычные группы без username

    :param entity: (Channel | Chat) Объект сущности из Telethon.
    :return: (str) Тип чата в виде строки.
    """
    if entity.megagroup:
        return 'Группа (супергруппа)'
    elif entity.broadcast:
        return 'Канал'
    else:

        return 'Обычный чат (группа старого типа)'


async def sync_account_channels(client):
    """
    Собирает и обновляет данные о группах и каналах из аккаунта пользователя.

    :param client: (TelegramClient) Активный клиент Telethon.
    :return: (set[str]) Множество username (@username), на которые подписан аккаунт.
    """
    subscribed_usernames = set()
    try:
        async for dialog in client.iter_dialogs():
            try:
                # Используем entity напрямую — он уже содержит всю нужную информацию
                entity = dialog.entity
                # Пропускаем личные чаты (User)
                if isinstance(entity, types.User):
                    logger.debug(f"💬 Пропущен личный чат: {entity.id}")
                    continue
                # Проверяем, является ли супергруппой или каналом
                if not getattr(entity, 'megagroup', False) and not getattr(entity, 'broadcast', False):
                    continue
                # Собираем username и идентификаторы
                if entity.username:
                    u_clean = entity.username.lower().lstrip("@")
                    subscribed_usernames.add(f"@{u_clean}")
                    subscribed_usernames.add(f"https://t.me/{u_clean}")
                    subscribed_usernames.add(u_clean)
                if getattr(entity, 'id', None):
                    subscribed_usernames.add(str(entity.id))
                    subscribed_usernames.add(f"-100{entity.id}")
                # Получаем полную информацию через GetFullChannelRequest
                data = await get_full_info_group(client, entity)
                if data:
                    logger.info(
                        f"👥 {data.get('participants', 0)} | 📝 {data.get('title', '')} | Тип: {data.get('group_type', '')} | 🔗 {data.get('link', '')} | 💬 {data.get('description', '')}"

                    )
                    # 1. Сохраняем/обновляем основные данные группы (название, участники, тип) в БД
                    update_group_channels_data_base(data, entity)
                    # 2. Проверяем и записываем язык группы (если еще не указан в БД)
                    await sync_to_async(ensure_group_language, thread_sensitive=True)(
                        telegram_id=entity.id,
                        name=data.get('title') or getattr(entity, 'title', None),
                        description=data.get('description'),
                        username=entity.username

                    )
                    # 3. Проверяем и записываем категорию группы через AI (если еще не указана в БД)
                    group_data_for_ai = {
                        "telegram_id": entity.id,
                        "name": data.get('title') or getattr(entity, 'title', ''),
                        "description": data.get('description', ''),
                        "username": entity.username or '',
                        "group_type": data.get('group_type', '')
                    }
                    await ensure_group_category(group_data_for_ai)
                await asyncio.sleep(1)
            except Exception as e:
                logger.exception(f"⚠️ Ошибка при обработке диалога {getattr(entity, 'id', 'unknown')}: {e}")
                continue

    except Exception as error:
        logger.exception(f"🔥 Критическая ошибка в get_grup_accaunt: {error}")
    return subscribed_usernames


async def ensure_group_category(group_data: dict) -> str | None:
    """
    Проверяет наличие категории у группы в базе данных и определяет её через AI при отсутствии.

    :param group_data: (dict) Словарь с данными группы (telegram_id, name, description, username, group_type).
    :return: (str | None) Название категории в нижнем регистре или None.
    """
    from ai.ai import category_assignment
    from core.config import GROQ_API_KEY
    from groq import AsyncGroq
    telegram_id = group_data.get("telegram_id")
    username = group_data.get("username")
    if not telegram_id and not username:
        return None

    # 1. Поиск группы в БД для проверки имеющейся категории
    tg_group = None
    if telegram_id:
        tg_group = await sync_to_async(TelegramGroups.get_or_none, thread_sensitive=True)(
            TelegramGroups.telegram_id == telegram_id)
    if not tg_group and username:
        clean_user = username.lstrip('@')
        tg_group = await sync_to_async(TelegramGroups.get_or_none, thread_sensitive=True)(
            (TelegramGroups.username == clean_user) | (TelegramGroups.username == f"@{clean_user}")
        )
    # 2. Если категория уже заполнена в БД — НЕ ТРОГАЕМ
    if tg_group and tg_group.category and tg_group.category.strip():
        logger.debug(
            f"ℹ️ Категория для {group_data.get('name') or telegram_id} уже есть в БД ({tg_group.category}), пропускаем AI.")
        return tg_group.category
    # 3. Запускаем AI определение категории через AsyncGroq
    if not GROQ_API_KEY:
        logger.warning("⚠️ GROQ_API_KEY не установлен, определение категории пропущено.")
        return None
    try:
        logger.info(f"🔍 Определяем категорию через AI для {group_data.get('name') or username or telegram_id}...")
        groq_client = AsyncGroq(api_key=GROQ_API_KEY)
        models = ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768"]
        model = random.choice(models)
        result = await category_assignment(
            group_data=group_data,
            client=groq_client,
            model=model
        )
        if result.get("success") and result.get("category"):
            category_lower = result["category"].lower()
            # 4. Сохранение категории в БД (в нижнем регистре)
            if tg_group:
                def _update_tg_group():
                    """
                    Обновляет категорию группы в базе данных.
                    """
                    tg_group.category = category_lower
                    tg_group.save()

                await sync_to_async(_update_tg_group, thread_sensitive=True)()
            else:
                if telegram_id:
                    await sync_to_async(
                        lambda: TelegramGroups.update(category=category_lower)
                        .where(TelegramGroups.telegram_id == telegram_id)
                        .execute(),
                        thread_sensitive=True
                    )()
                elif username:

                    clean_user = username.lstrip('@')
                    await sync_to_async(
                        lambda: TelegramGroups.update(category=category_lower)
                        .where((TelegramGroups.username == clean_user) | (TelegramGroups.username == f"@{clean_user}"))
                        .execute(),
                        thread_sensitive=True
                    )()
            logger.info(f"✅ Успешно присвоена категория: {group_data.get('name')} → {category_lower}")
            return category_lower
        else:
            logger.warning(f"❌ AI не смог определить категорию для {group_data.get('name') or telegram_id}")
    except Exception as e:
        logger.exception(f"❌ Ошибка при автоопределении категории для {group_data.get('name') or telegram_id}: {e}")
    return None


def ensure_group_language(telegram_id: int = None, name: str = None, description: str = None,
                          username: str = None) -> str | None:
    """
    Проверяет наличие языка группы в базе данных и определяет его через lingua-py при отсутствии.

    :param telegram_id: (int | None) Telegram ID группы или канала.
    :param name: (str | None) Название группы или канала.
    :param description: (str | None) Описание группы или канала (опционально).
    :param username: (str | None) Юзернейм группы или канала (опционально).
    :return: (str | None) Код языка (например, 'ru', 'en') или None.
    """

    if not telegram_id and not username:
        return None

    # 1. Ищем группу в БД по telegram_id или username
    tg_group = None
    if telegram_id:
        tg_group = TelegramGroups.get_or_none(TelegramGroups.telegram_id == telegram_id)
    if not tg_group and username:
        clean_user = username.lstrip('@')
        tg_group = TelegramGroups.get_or_none(
            (TelegramGroups.username == clean_user) | (TelegramGroups.username == f"@{clean_user}"))
    # 2. Если в БД язык уже заполнен — НЕ ТРОГАЕМ
    if tg_group and tg_group.language and tg_group.language.strip():
        logger.debug(f"ℹ️ Язык для {name or telegram_id} уже указан в БД ({tg_group.language}), детекция пропущена.")
        return tg_group.language
    # 3. Собираем текст для анализа
    text_parts = []
    if name:
        text_parts.append(name)
    elif tg_group and tg_group.name:
        text_parts.append(tg_group.name)
    if description:
        text_parts.append(description)
    elif tg_group and tg_group.description:
        text_parts.append(tg_group.description)
    text_to_detect = " ".join(text_parts).strip()
    if not text_to_detect:
        logger.warning(f"⚠️ Нет текста для определения языка группы ({name or username or telegram_id})")
        return None
    # 4. Детекция языка
    try:
        lang_code = detect_language(text_to_detect)
        if lang_code:
            logger.info(f"🌐 Определен новый язык '{lang_code}' для группы {name or username or telegram_id}")
            # 5. Запись в БД
            if tg_group:
                tg_group.language = lang_code
                tg_group.save()
            else:
                if telegram_id:
                    TelegramGroups.update(language=lang_code).where(
                        TelegramGroups.telegram_id == telegram_id).execute()
                elif username:
                    clean_user = username.lstrip('@')
                    TelegramGroups.update(language=lang_code).where(
                        (TelegramGroups.username == clean_user) | (TelegramGroups.username == f"@{clean_user}")
                    ).execute()
            logger.info(f"✅ Успешно записан язык {lang_code} в БД для {name or telegram_id}")
            return lang_code
        else:
            logger.warning(f"⚠️ Не удалось определить язык для {name or username or telegram_id}")
    except Exception as e:
        logger.exception(f"❌ Ошибка при автоматическом определении языка ({name or telegram_id}): {e}")
    return None


def update_group_channels_data_base(data, entity, group=None):
    """
    Обновляет данные в базе данных для каналов и групп.

    :param data: (dict) Данные для сохранения или обновления в базе данных.
    :param entity: (types.TypeChat | types.TypeUser) Сущность Telegram (User или Channel).
    :param group: (dict | Any | None) Группа или канал Telegram (объект или словарь, опционально).
    """
    if not data or not entity:
        return
    if group is not None:
        if isinstance(group, dict):
            group_hash = group.get('group_hash')
            telegram_id = group.get('telegram_id')
        else:
            group_hash = getattr(group, 'group_hash', None)
            telegram_id = getattr(group, 'telegram_id', None)
    else:
        group_hash = getattr(entity, 'access_hash', None)
        telegram_id = getattr(entity, 'id', None)
    target_id = telegram_id or getattr(entity, 'id', None)
    target_hash = group_hash or getattr(entity, 'access_hash', None)
    try:
        query = TelegramGroups.update(
            telegram_id=target_id,
            group_hash=str(target_hash) if target_hash else None,
            group_type=data.get("group_type", ""),
            username=data.get("actual_username", ""),
            description=data.get("description", ""),
            participants=data.get("participants", 0),
            name=getattr(entity, 'title', None) or data.get("title", ""),
            availability=''  # Группа активна
        )
        if target_id:
            query = query.where(
                (TelegramGroups.telegram_id == target_id) | (TelegramGroups.username == data.get("actual_username")))
        elif target_hash:
            query = query.where(TelegramGroups.group_hash == str(target_hash))
        elif data.get("actual_username"):
            query = query.where(TelegramGroups.username == data.get("actual_username"))
        else:
            logger.warning(f"⚠️ Не удалось определить фильтр для обновления TelegramGroup ({entity})")
            return
        query.execute()
        logger.info(
            f"ID: {target_id} | Тип: {data.get('group_type', '')} | Описание: {data.get('description', '')} | Участники: {data.get('participants', 0)}"
        )
        logger.debug(f"🔄 Обновлена группа: {data.get('title', '')}")
    except Exception as e:
        logger.exception(f"❌ Ошибка при обновлении записи TelegramGroup в БД: {e}")


async def _send_msg(message, user_id, text, reply_markup=None, parse_mode="HTML"):
    """
    Безопасно отправляет сообщение пользователю:
    через message.answer (если объект сообщения aiogram доступен),
    либо напрямую через bot.send_message по user_id.
    """
    try:
        if message and hasattr(message, "answer"):
            return await message.answer(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
        elif user_id:
            from system.dispatcher import bot
            return await bot.send_message(chat_id=int(user_id), text=text, reply_markup=reply_markup,
                                          parse_mode=parse_mode)
    except Exception as e:
        logger.debug(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    return None


async def join_required_channels(client, user_id, message, already_subscribed):
    """
    Подписывает аккаунт Telegram на все отслеживаемые каналы и группы пользователя из базы данных.

    Получает список username из персональной таблицы пользователя и пытается присоединиться к каждому. При успехе
    уведомляет пользователя.

    - Между подписками добавляется задержка в диапазоне от 1 до 10 секунд для избежания Flood.
    - Использует модель `create_groups_model` для доступа к данным.

    :param client: (TelegramClient) Активный клиент для выполнения запросов.
    :param user_id: (int) Идентификатор пользователя, чьи каналы нужно подключить.
    :param message: (Message | None) Объект сообщения aiogram для отправки уведомлений.
    :param already_subscribed: (set) Список каналов, где аккаунт уже состоит.
    :return: None
    """
    user_lang = determines_user_language(message_or_callback=int(user_id))
    db_channels, total_count = get_user_channel_usernames(user_id=user_id)
    db_channels = set(db_channels)
    logger.info(f"📊 Всего каналов для подписки: {total_count}, уже подписан на: {len(already_subscribed)}")

    if total_count == 0:
        await _send_msg(message, user_id, t("no_channels_to_track", lang=user_lang))
        return

    to_subscribe = list(db_channels - already_subscribed)
    if len(to_subscribe) > 500:
        await _send_msg(
            message, user_id,
            t("too_many_channels", lang=user_lang, total=len(to_subscribe), limit=500)
        )
    for channel in to_subscribe[:500]:
        random_delay = random.randint(15, 60)
        try:
            logger.info(f"🔗 Попытка подписки на канал {channel}")
            is_subscribed = await subscription_telegram(client=client, target_username=channel)
            if is_subscribed:
                await _send_msg(
                    message, user_id,
                    t("channel_subscribed", lang=user_lang, channel=channel, delay=random_delay)
                )
                await asyncio.sleep(random_delay)
            else:
                logger.warning(f"⚠️ Не удалось подписаться на {channel}. Пропускаем...")
        except Exception as e:
            logger.exception(f"❌ Ошибка в цикле подписки на {channel}: {e}")


async def filter_messages_for_account(user_id: int, account_record, message=None, notify=True):
    """
    Запускает независимый мониторинг сообщений для конкретного аккаунта пользователя
    (с его собственной технической группой, персональными ключевыми словами и целевыми чатами).

    :param user_id: (int) ID пользователя в Telegram.
    :param account_record: (UsersAccounts) Запись аккаунта из БД.
    :param message: (Message | None) Объект сообщения aiogram для ответов.
    :param notify: (bool) Отправлять ли пользователю уведомление о старте/остановке.
    """
    user_id = int(user_id)
    acc_id = account_record.id
    user_key = f"{user_id}_{acc_id}"
    acc_title = account_record.account_title or f"Аккаунт {account_record.phone_number_session_string or acc_id}"
    logger.info(f"🚀 Запуск отслеживания для user_id={user_id}, аккаунт #{acc_id} ({acc_title})...")
    client = None
    user_lang = determines_user_language(message_or_callback=user_id)

    try:
        session_string = account_record.user_session_string
        if not session_string:
            logger.warning(f"⚠️ У аккаунта #{acc_id} нет session_string")
            return None

        target_group_id = account_record.target_group_id or get_group_id_with_personal_tracking(user_id)
        if not target_group_id:
            logger.warning(f"⚠️ У аккаунта #{acc_id} ({acc_title}) нет целевой группы уведомлений в БД")
            if notify:
                create_group_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("btn_pt_create_notification_group", lang=user_lang),
                                callback_data="menu_personal_tracking"
                            )
                        ]
                    ]
                )
                await _send_msg(
                    message, user_id,
                    t("parser_notification_group_missing", lang=user_lang),
                    reply_markup=create_group_kb
                )
            return None

        checker = CheckingAccountsValidity()
        client = await checker.client_connect_string_session(session_string)
        if not client:
            logger.warning(f"⚠️ Не удалось подключить клиент для аккаунта #{acc_id} ({acc_title})")
            if notify:
                await _send_msg(
                    message, user_id,
                    f"⚠️ <b>Не удалось подключить аккаунт «{acc_title}».</b>\nПроверьте валидность сессии."
                    if user_lang == "ru"
                    else f"⚠️ <b>Failed to connect account «{acc_title}».</b>\nPlease check session validity."
                )
            return None

        active_clients[user_key] = client
        stop_event = asyncio.Event()
        stop_flags[user_key] = stop_event
        account_record.is_active = True
        account_record.save()

        # Предзагрузка диалогов
        already_subscribed = set()
        try:
            dialogs = await client.get_dialogs(limit=250)
            for d in dialogs:
                ent = d.entity
                if getattr(ent, 'username', None):
                    u_clean = ent.username.lower().lstrip("@")
                    already_subscribed.add(f"@{u_clean}")
                    already_subscribed.add(f"https://t.me/{u_clean}")
                    already_subscribed.add(u_clean)
                if getattr(ent, 'id', None):
                    already_subscribed.add(str(ent.id))
                    already_subscribed.add(f"-100{ent.id}")
            logger.info(f"✅ Диалоги загружены в кэш Telethon ({len(already_subscribed)} записей) для аккаунта #{acc_id}")
        except Exception as dial_err:
            logger.debug(f"Ошибка предварительной загрузки диалогов: {dial_err}")

        track_all = bool(account_record.track_all_chats)

        async def listen():
            @client.on(events.NewMessage())
            async def handle_new_message(event: events.NewMessage.Event):
                try:
                    await process_message(
                        client=client,
                        message=event.message,
                        chat_id=event.chat_id,
                        user_id=user_id,
                        target_group_id=target_group_id,
                        session_string=session_string,
                        track_all_chats=track_all,
                        account_title=acc_title
                    )
                except Exception as e:
                    logger.exception(f"Не удалось обработать сообщение: {e}")

            logger.info(f"👂 Бот слушает новые сообщения для аккаунта #{acc_id} ({acc_title})...")
            if notify:
                start_txt = (
                    f"🚀 <b>Мониторинг запущен для аккаунта:</b> {acc_title}\n\n"
                    f"📣 <b>Тех-группа:</b> ID {target_group_id}\n"
                    f"🌐 <b>Все чаты аккаунта:</b> {'ВКЛ (открытые + закрытые)' if track_all else 'По списку групп'}"
                    if user_lang == "ru"
                    else f"🚀 <b>Monitoring started for account:</b> {acc_title}\n\n"
                         f"📣 <b>Tech group:</b> ID {target_group_id}\n"
                         f"🌐 <b>All account chats:</b> {'ON (open + closed)' if track_all else 'By group list'}"
                )
                await _send_msg(message, user_id, start_txt)

            await stop_event.wait()
            logger.info(f"🛑 Прослушивание остановлено для аккаунта #{acc_id} ({acc_title})")
            if notify:
                stop_txt = (
                    f"🛑 Мониторинг остановлен для аккаунта: {acc_title}"
                    if user_lang == "ru"
                    else f"🛑 Monitoring stopped for account: {acc_title}"
                )
                await _send_msg(message, user_id, stop_txt)

        async def subscribe():
            if not track_all:
                try:
                    await join_required_channels(
                        client=client,
                        user_id=str(user_id),
                        message=message,
                        already_subscribed=already_subscribed
                    )
                except Exception as sub_err:
                    logger.debug(f"Фоновая подписка для аккаунта #{acc_id}: {sub_err}")

        await asyncio.gather(listen(), subscribe())

    except Exception as e:
        logger.exception(f"❌ Ошибка в filter_messages_for_account #{acc_id}: {e}")
    finally:
        user_key = f"{user_id}_{acc_id}"
        if user_key in active_clients:
            c = active_clients.pop(user_key)
            try:
                if c and c.is_connected():
                    await c.disconnect()
            except Exception:
                pass
        stop_flags.pop(user_key, None)
        try:
            account_record.is_active = False
            account_record.save()
        except Exception:
            pass
        logger.info(f"🛑 Сессия Telethon завершена для аккаунта #{acc_id}")


async def filter_messages(message=None, user_id=None, notify=True, account_id=None):
    """
    Основная функция запуска процесса отслеживания сообщений в Telegram.
    Поддерживает как мульти-аккаунтный режим (кампании), так и одиночный режим.

    :param message: (Message | None) Объект сообщения aiogram.
    :param user_id: (int | str) Идентификатор пользователя Telegram.
    :param notify: (bool) Отправлять ли пользователю сервисные сообщения о старте/остановке.
    :param account_id: (int | None) ID конкретного аккаунта из UsersAccounts (если запускается один аккаунт).
    :return: None
    """
    from database.users_accounts import UsersAccounts
    user_id = int(user_id)

    # 1. Если передан конкретный account_id, запускаем только его
    if account_id:
        acc = UsersAccounts.get_or_none((UsersAccounts.id == account_id) & (UsersAccounts.user_id == user_id))
        if acc:
            return await filter_messages_for_account(user_id=user_id, account_record=acc, message=message, notify=notify)

    # 2. Проверяем, есть ли зарегистрированные аккаунты в UsersAccounts
    user_accs = list(UsersAccounts.select().where(UsersAccounts.user_id == user_id))
    if user_accs:
        for acc in user_accs:
            user_key = f"{user_id}_{acc.id}"
            if user_key not in active_clients:
                asyncio.create_task(
                    filter_messages_for_account(user_id=user_id, account_record=acc, message=message, notify=notify)
                )
        return None

    # 3. Fallback: Одиночный режим / общий бесплатный аккаунт
    user_key = str(user_id)
    logger.info(f"🚀 Запуск одиночного отслеживания для user_id={user_id} (notify={notify})...")
    client = None
    user_lang = determines_user_language(message_or_callback=user_id)

    try:
        # === Проверка группы уведомлений ===
        target_group_id = get_group_id_with_personal_tracking(user_id)
        if not target_group_id:
            logger.warning(f"⚠️ У пользователя {user_id} нет целевой группы уведомлений в БД")
            if notify:
                create_group_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("btn_pt_create_notification_group", lang=user_lang),
                                callback_data="menu_personal_tracking"
                            )
                        ]
                    ]
                )
                await _send_msg(
                    message, user_id,
                    t("parser_notification_group_missing", lang=user_lang),
                    reply_markup=create_group_kb
                )
            return None

        # === Проверка аккаунтов ===
        pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
        is_shared_account = bool(pt_rec and pt_rec.shared_account and not pt_rec.personal_account)
        session_string = (pt_rec.personal_account or pt_rec.shared_account) if pt_rec else None
        if not session_string:
            logger.warning(f"⚠️ У пользователя {user_id} нет подключённого аккаунта в БД")
            if notify:
                await _send_msg(
                    message, user_id,
                    t("no_accounts", lang=user_lang),
                    reply_markup=menu_launch_tracking_keyboard(lang=user_lang, user_id=user_id)
                )
            return None

        # === Подключаем клиент ===
        checker = CheckingAccountsValidity()
        client = await checker.client_connect_string_session(session_string)
        if not client:
            if is_shared_account and notify:
                logger.warning(
                    f"⚠️ Не удалось подключиться к бесплатному аккаунту для user_id={user_id}. Предлагаем переподключение."
                )
                reconnect_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("btn_reconnect_free_account", lang=user_lang),
                                callback_data="account_connect_free"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=t("btn_to_tracking_menu", lang=user_lang),
                                callback_data="menu_personal_tracking"
                            )
                        ]
                    ]
                )
                msg_text = (
                    "⚠️ <b>Бесплатный аккаунт временно недоступен или ограничен Telegram.</b>\n\n"
                    "Вы можете прямо сейчас переподключить другой рабочий бесплатный аккаунт нажатием одной кнопки:"
                    if user_lang == "ru"
                    else "⚠️ <b>Free account is temporarily unavailable or restricted by Telegram.</b>\n\n"
                         "You can reconnect a working free account right now by clicking the button below:"
                )
                await _send_msg(message, user_id, msg_text, reply_markup=reconnect_kb)
            return None

        active_clients[user_key] = client
        stop_event = asyncio.Event()
        stop_flags[user_key] = stop_event

        # Быстро загружаем диалоги в кэш Telethon (0.2 сек)
        already_subscribed = set()
        try:
            dialogs = await client.get_dialogs(limit=200)
            for d in dialogs:
                ent = d.entity
                if getattr(ent, 'username', None):
                    u_clean = ent.username.lower().lstrip("@")
                    already_subscribed.add(f"@{u_clean}")
                    already_subscribed.add(f"https://t.me/{u_clean}")
                    already_subscribed.add(u_clean)
                if getattr(ent, 'id', None):
                    already_subscribed.add(str(ent.id))
                    already_subscribed.add(f"-100{ent.id}")
            logger.info(f"✅ Диалоги загружены в кэш Telethon ({len(already_subscribed)} записей) для user_id={user_id}")
        except Exception as dial_err:
            logger.debug(f"Ошибка предварительной загрузки диалогов: {dial_err}")

        # === 1. Читаем каналы из БД ===
        channels = await get_user_channels_or_notify(user_id=user_id, message=message, client=client,
                                                     user_lang=user_lang)
        if not channels:
            return None

        # === 1.1. Проверка лимитов для общего бесплатного аккаунта ===
        if is_shared_account and len(channels) > 1:
            logger.warning(
                f"⚠️ Пользователь {user_id} использует общий аккаунт и превысил лимит каналов ({len(channels)} > 1)"
            )
            if notify:
                buy_stars_kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=t("btn_pt_buy_stars_slots", lang=user_lang),
                                callback_data="settings_topup_stars"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=t("btn_pt_connect_personal", lang=user_lang),
                                callback_data="menu_personal_tracking"
                            )
                        ]
                    ]
                )
                await _send_msg(message, user_id, t("parser_free_account_limit", lang=user_lang),
                                reply_markup=buy_stars_kb)
            return None

        # === Функция прослушивания — стартует сразу ===
        async def listen():
            @client.on(events.NewMessage())
            async def handle_new_message(event: events.NewMessage.Event):
                try:
                    await process_message(
                        client=client,
                        message=event.message,
                        chat_id=event.chat_id,
                        user_id=user_id,
                        target_group_id=target_group_id,
                        session_string=session_string,
                        track_all_chats=False
                    )
                except Exception as e:
                    logger.exception(f"Не удалось обработать сообщение: {e}")

            logger.info(f"👂 Бот слушает новые сообщения для user_id={user_id}...")
            if notify:
                await _send_msg(
                    message, user_id,
                    text=t("bot_listening", lang=user_lang),
                    reply_markup=menu_launch_tracking_keyboard(lang=user_lang, user_id=user_id)
                )

            await stop_event.wait()
            logger.info(f"🛑 Прослушивание остановлено для user_id={user_id}")
            if notify:
                await _send_msg(message, user_id, t("tracking_stopped", lang=user_lang))

        # === Функция подписки — работает параллельно в фоне ===
        async def subscribe():
            try:
                await join_required_channels(
                    client=client,
                    user_id=str(user_id),
                    message=message,
                    already_subscribed=already_subscribed
                )
            except Exception as sub_err:
                logger.debug(f"Фоновая подписка завершилась с ошибкой: {sub_err}")

        await asyncio.gather(listen(), subscribe())

    except Exception as e:
        logger.exception(f"❌ Критическая ошибка в filter_messages для user_id={user_id}: {e}")
    finally:
        user_key = str(user_id)
        if user_key in active_clients:
            c = active_clients.pop(user_key)
            try:
                if c and c.is_connected():
                    await c.disconnect()
            except Exception:
                pass
        stop_flags.pop(user_key, None)
        logger.info(f"🛑 Сессия Telethon завершена и очищена из active_clients для user_id={user_id}")


async def stop_tracking(user_id, message=None, account_id=None):
    """
    Останавливает процесс отслеживания сообщений для пользователя.
    Поддерживает остановку конкретного аккаунта/кампании или всех аккаунтов пользователя.

    :param user_id: (int | str) Идентификатор пользователя Telegram.
    :param message: (Message | None) Объект сообщения aiogram для отправки подтверждения (опционально).
    :param account_id: (int | None) ID аккаунта из UsersAccounts (если останавливается один аккаунт).
    """
    from database.users_accounts import UsersAccounts
    user_id = int(user_id)
    user_lang = determines_user_language(message_or_callback=user_id)

    if account_id:
        user_key = f"{user_id}_{account_id}"
        logger.info(f"🛑 Запрос на остановку отслеживания для аккаунта #{account_id} (user_id={user_id})")
        if user_key in stop_flags:
            try:
                stop_flags[user_key].set()
            except Exception:
                pass
        client = active_clients.pop(user_key, None)
        if client:
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
        stop_flags.pop(user_key, None)
        UsersAccounts.update(is_active=False).where(UsersAccounts.id == account_id).execute()
        if message:
            await _send_msg(message, user_id, t("tracking_stopped", lang=user_lang))
        return

    # Останавливаем все аккаунты пользователя
    logger.info(f"🛑 Запрос на остановку всех потоков отслеживания для user_id={user_id}")
    keys_to_stop = [k for k in list(active_clients.keys()) if k == str(user_id) or k.startswith(f"{user_id}_")]
    for k in keys_to_stop:
        if k in stop_flags:
            try:
                stop_flags[k].set()
            except Exception:
                pass
        client = active_clients.pop(k, None)
        if client:
            try:
                if client.is_connected():
                    await client.disconnect()
            except Exception:
                pass
        stop_flags.pop(k, None)

    UsersAccounts.update(is_active=False).where(UsersAccounts.user_id == user_id).execute()

    if message:
        await _send_msg(
            message, user_id,
            t("tracking_stop_requested", lang=user_lang),
            reply_markup=menu_launch_tracking_keyboard(lang=user_lang, user_id=user_id)
        )


async def restore_all_user_trackings():
    """
    Автоматически восстанавливает и запускает отслеживание сообщений для всех пользователей и аккаунтов
    при старте или перезапуске бота.
    """
    logger.info("🔄 Проверка и автоматический запуск отслеживания для всех пользователей и аккаунтов...")
    try:
        from database.users_accounts import UsersAccounts
        from database.users_personal_trackings import UsersPersonalTrackings
        from database.users_groups import UsersGroups
        from database.users_keywords import UsersKeywords

        started_count = 0

        # 1. Запуск всех активных аккаунтов из таблицы users_accounts
        try:
            active_accs = list(UsersAccounts.select().where(UsersAccounts.is_active == True))
            for acc in active_accs:
                user_key = f"{acc.user_id}_{acc.id}"
                if user_key in active_clients:
                    continue
                target_gid = acc.target_group_id or get_group_id_with_personal_tracking(acc.user_id)
                if not target_gid:
                    continue
                try:
                    logger.info(f"🚀 Авто-восстановление отслеживания для аккаунта #{acc.id} ({acc.account_title or acc.phone_number_session_string})...")
                    asyncio.create_task(
                        filter_messages_for_account(
                            user_id=acc.user_id,
                            account_record=acc,
                            message=None,
                            notify=False
                        )
                    )
                    started_count += 1
                except Exception as acc_err:
                    logger.error(f"❌ Ошибка авто-запуска аккаунта #{acc.id}: {acc_err}")
        except Exception as e:
            logger.debug(f"Проверка active_accs: {e}")

        # 2. Обратная совместимость с UsersPersonalTrackings (одиночный/общий аккаунт)
        candidates = list(
            UsersPersonalTrackings.select().where(
                UsersPersonalTrackings.created_group_id.is_null(False)
            )
        )

        for rec in candidates:
            uid = rec.user_id
            # Если для пользователя уже работают аккаунты из users_accounts, пропускаем
            if any(k == str(uid) or k.startswith(f"{uid}_") for k in active_clients):
                continue

            session_str = rec.personal_account or rec.shared_account
            if not session_str:
                continue

            has_groups = UsersGroups.select().where(UsersGroups.user_id == uid).exists()
            has_keywords = UsersKeywords.select().where(UsersKeywords.user_id == uid).exists()
            if not (has_groups and has_keywords):
                continue

            try:
                logger.info(f"🚀 Авто-восстановление одиночного отслеживания для user_id={uid}...")
                asyncio.create_task(
                    filter_messages(
                        message=None,
                        user_id=uid,
                        notify=False
                    )
                )
                started_count += 1
            except Exception as u_err:
                logger.error(f"❌ Ошибка авто-запуска отслеживания для user_id={uid}: {u_err}")

        logger.info(f"✅ Авто-запуск отслеживания завершен. Запущено потоков: {started_count}")
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка в restore_all_user_trackings: {e}")
