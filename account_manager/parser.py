# -*- coding: utf-8 -*-
import asyncio
import random
from datetime import datetime

from aiogram.types import Message
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import events, types
from telethon.errors import (
    FloodWaitError, UserAlreadyParticipantError, InviteRequestSentError, ChannelPrivateError
)
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest

from account_manager.auth import CheckingAccountsValidity
from database.database import (
    create_keywords_model, create_group_model, TelegramGroup, get_user_accounts, get_user_channel_usernames, Groups
)
from keyboards.user.keyboards import menu_launch_tracking_keyboard, connect_grup_keyboard_tech
from locales.locales import get_text

# 🧠 Простейший трекер сообщений (в памяти)
forwarded_messages = set()

# 🛑 Словарь активных клиентов и флагов остановки
active_clients = {}  # {user_id: client}
stop_flags = {}  # {user_id: asyncio.Event}


async def join_target_group(client, user_id, message):
    """
    Подписывает клиента Telethon на целевую группу пользователя для пересылки сообщений.

    Получает username целевой группы из персональной таблицы пользователя в базе данных и пытается присоединиться к ней.
    Возвращает идентификатор группы для дальнейшей отправки.

    - Использует модель `create_group_model` для доступа к данным пользователя.
    - Предполагается, что в таблице всегда одна запись (первый элемент списка).

    :param client: (TelegramClient) Активный клиент Telethon для выполнения запросов.
    :param user_id: (int) Уникальный идентификатор пользователя Telegram.
    :param message: (Message) Сообщение, которое вызвало команду (для ответа).
    :return: int or None: Идентификатор целевой группы (entity.id) или None при ошибке.

    :raises UserAlreadyParticipantError: Если клиент уже участник группы (обрабатывается).
    :raises FloodWaitError: Если достигнут лимит запросов (обрабатывается с задержкой).
    :raises InviteRequestSentError: Если требуется подтверждение приглашения.
    :raises Exception: Логируется при любых других ошибках.
    """
    GroupModel = create_group_model(user_id=user_id)
    logger.info(f"🔍 Проверяю целевую группу... {GroupModel}")
    if not GroupModel.table_exists():
        GroupModel.create_table()
        return None
    groups = list(GroupModel.select())
    logger.info(f"🔍 Проверяю целевую группу... {groups}")
    if not groups:
        logger.warning(f"❌ Не найдена целевая группа для пользователя {user_id}")
        # Если группа не найдена, то высылаем сообщение пользователю группы, что такой группы нет и клавиатуру для добавления группы для пересылки
        await message.answer(
            text="❌ Не найдена целевая группа для пользователя. Подключите группу, для того, что бы я мог пересылать туда сообщения, найденные по вашим ключевым словам.",
            reply_markup=connect_grup_keyboard_tech()
        )
        return None  # Возвращаем None, если группа не найдена
    target_username = groups[0].user_group
    if not target_username:
        logger.error(f"❌ Целевая группа имеет пустой username для user_id={user_id}")
        await message.answer(
            text="❌ Не найдена целевая группа для пользователя. Подключите группу, для того, что бы я мог пересылать туда сообщения, найденные по вашим ключевым словам.",
            reply_markup=connect_grup_keyboard_tech()
        )
        return None
    try:
        target_usernames = f'https://t.me/{target_username.lstrip("@")}'
        await client(JoinChannelRequest(target_usernames))
        # await subscription_telegram(client, target_usernames)  # Подписываемся на группу
        # Получаем ID группы
        entity = await client.get_entity(target_username)
        return entity.id
    except FloodWaitError as e:
        logger.error(f"⚠️ FloodWait {e.seconds} сек.")
        await asyncio.sleep(e.seconds)
        try:
            await client(JoinChannelRequest(target_usernames))
        except InviteRequestSentError:
            logger.error(f"✉️ Приглашение уже отправлено: {target_usernames}")
    except Exception as e:
        logger.exception(f"❌ Не удалось присоединиться к целевой группе {target_username}: {e}")
        return None


async def process_message(client, message: Message, chat_id: int, user_id, target_group_id):
    """
    Обрабатывает входящее сообщение, проверяет его на совпадение с ключевыми словами и пересылает в целевую группу с
    контекстом при совпадении.

    Контекст включает название источника, ссылку на сообщение и сам текст.
    Использует глобальный set `forwarded_messages` для предотвращения дубликатов.

    - Сообщение пересылается только один раз (проверка по chat_id-message.id).
    - Ссылка формируется по разным правилам для супергрупп и обычных чатов.
    - Ключевые слова загружаются динамически из базы данных пользователя.

    :param client: (TelegramClient) Активный клиент для отправки сообщений.
    :param message: (Message) Входящее сообщение для обработки.
    :param chat_id: (int) Идентификатор чата-источника.
    :param user_id: (int) Идентификатор пользователя, чьи ключевые слова используются.
    :param target_group_id: (int) Идентификатор целевой группы для пересылки.
    :return: None
    :raises Exception: Логируется при ошибках отправки сообщения.
    """
    if not message.message:
        return

    message_text = message.message.lower()
    msg_key = f"{chat_id}-{message.id}"

    if msg_key in forwarded_messages:
        return

    # Получаем ключевые слова из базы данных для данного пользователя
    Keywords = create_keywords_model(user_id=user_id)

    # Создаем таблицу, если она не существует
    if not Keywords.table_exists():
        Keywords.create_table()
        logger.info(f"Создана таблица ключевых слов для пользователя {user_id}")
        return  # Таблица только что создана, ключевых слов еще нет

    keywords = [keyword.user_keyword for keyword in Keywords.select() if keyword.user_keyword]

    # Если нет ключевых слов, выходим
    if not keywords:
        return

    # Приводим ключевые слова к нижнему регистру для поиска
    keywords_lower = [keyword.lower() for keyword in keywords]

    # Используем ключевые слова из базы данных
    if any(keyword in message_text for keyword in keywords_lower):
        logger.info(f"📌 Найдено совпадение. Пересылаю сообщение ID={message.id}")
        try:
            # Получаем информацию о чате-источнике
            try:
                chat_entity = await client.get_entity(chat_id)
                chat_title = getattr(chat_entity, "title", None) or getattr(chat_entity, "username",
                                                                            None) or "Неизвестно"
            except Exception as e:
                logger.warning(f"Не удалось получить название чата: {e}")
                chat_title = "Неизвестно"

            # Формируем ссылку на сообщение
            # Для супергрупп/каналов (chat_id начинается с -100)
            if str(chat_id).startswith("-100"):
                # Удаляем префикс -100 и получаем чистый ID
                clean_chat_id = str(chat_id)[4:]
                message_link = f"https://t.me/c/{clean_chat_id}/{message.id}"
            else:
                # Для чатов с username (если есть)
                try:
                    chat_entity = await client.get_entity(chat_id)
                    if chat_entity.username:
                        message_link = f"https://t.me/{chat_entity.username}/{message.id}"
                    else:
                        message_link = "Ссылка недоступна (нет username)"
                except Exception:
                    message_link = "Ссылка недоступна"

            # Формируем итоговое сообщение с контекстом
            context_text = (
                f"📥 **Новое сообщение**\n\n"
                f"**Источник:** {chat_title}\n"
                f"**Ссылка:** {message_link}\n\n"
                f"**Текст сообщения:**\n{message.message}"
            )

            # Отправляем в целевую группу
            await client.send_message(target_group_id, context_text)
            await client.forward_messages(target_group_id, message)
            logger.info(f"✅ Сообщение переслано в целевую группу (ID={target_group_id})")

            forwarded_messages.add(msg_key)
        except Exception as e:
            logger.exception(f"❌ Ошибка при отправке сообщения с контекстом: {e}")


def determine_telegram_chat_type(entity):
    """
    Определяет тип чата в Telegram по сущности.

    Поддерживаемые типы:
    - 'Группа (супергруппа)' — если это мегагруппа
    - 'Канал' — если это канал (broadcast)
    - 'Обычный чат (группа старого типа)' — обычные группы без username

    :param entity: (Channel, Chat) Объект сущности из Telethon.
    :return: str Тип чата как строка.
    """
    if entity.megagroup:
        return 'Группа (супергруппа)'
    elif entity.broadcast:
        return 'Канал'
    else:
        return 'Обычный чат (группа старого типа)'


async def get_grup_accaunt(client):
    """
    Собирает и обновляет данные о группах и каналах из аккаунта пользователя.

    Проходит по всем диалогам, фильтрует супергруппы и каналы, получает полную информацию
    (участники, описание, ссылка), определяет тип чата и сохраняет/обновляет запись в базе данных.

    Пропускает личные чаты и обычные группы без username.
    Добавлена защита от ошибок и ограничений Telegram API.

    :param client: (TelegramClient) Активный клиент Telethon.
    :return: set — множество username (@username), на которые подписан аккаунт
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

                # Собираем username
                if entity.username:
                    subscribed_usernames.add(f"@{entity.username.lower()}")

                # Получаем полную информацию через GetFullChannelRequest
                try:
                    full_entity = await client(GetFullChannelRequest(channel=entity))
                    participants_count = full_entity.full_chat.participants_count or 0
                    description = full_entity.full_chat.about or ""
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось получить полные данные для {entity.username or entity.id}: {e}")
                    participants_count = 0
                    description = ""

                actual_username = f"@{entity.username}" if entity.username else ""
                link = f"https://t.me/{entity.username}" if entity.username else None
                title = entity.title or "Без названия"
                new_group_type = determine_telegram_chat_type(entity)

                logger.info(
                    f"👥 {participants_count} | 📝 {title} | Тип: {new_group_type} | 🔗 {link} | 💬 {description}")

                # Сохранение или обновление в базе
                TelegramGroup.insert(
                    group_hash=entity.access_hash,
                    name=title,
                    username=actual_username,
                    description=description,
                    participants=participants_count,
                    group_type=new_group_type,
                    link=link or "",
                    date_added=datetime.now()
                ).on_conflict(
                    conflict_target=[TelegramGroup.group_hash],
                    update={
                        TelegramGroup.name: title,
                        TelegramGroup.username: actual_username,
                        TelegramGroup.description: description,
                        TelegramGroup.participants: participants_count,
                        TelegramGroup.group_type: new_group_type,
                        TelegramGroup.link: link or "",
                    }
                ).execute()

                logger.debug(f"🔄 Обновлена группа: {title}")

                await asyncio.sleep(1)
            except Exception as e:
                logger.exception(f"⚠️ Ошибка при обработке диалога {getattr(entity, 'id', 'unknown')}: {e}")
                continue
    except Exception as error:
        logger.exception(f"🔥 Критическая ошибка в get_grup_accaunt: {error}")

    return subscribed_usernames


async def join_required_channels(client, user_id, message):
    """
    Подписывает аккаунт Telegram на все отслеживаемые каналы и группы пользователя из базы данных.

    Получает список username из персональной таблицы пользователя и пытается присоединиться к каждому. При успехе
    уведомляет пользователя. Невалидные ссылки удаляются из базы данных.

    - Между подписками добавляется задержка в диапазоне от 1 до 10 секунд для избежания Flood.
    - Использует модель `create_groups_model` для доступа к данным.

    :param client: (TelegramClient) Активный клиент для выполнения запросов.
    :param user_id: (int) Идентификатор пользователя, чьи каналы нужно подключить.
    :param message: (Message) Объект сообщения aiogram для отправки уведомлений.
    :return: None
    """
    db_channels, total_count = get_user_channel_usernames(user_id=user_id)  # Получаем все username из базы данных
    already_subscribed = await get_grup_accaunt(client)  # Получаем список каналов, где аккаунт уже состоит

    # ✅ Приводим к set для операции вычитания
    db_channels = set(db_channels)

    logger.info(f"📊 Всего каналов для подписки: {total_count}, уже подписан на: {len(already_subscribed)}")
    if total_count == 0:
        await message.answer("📭 У вас нет добавленных каналов для отслеживания.")
        return

    if len(list(db_channels - already_subscribed)) > 500:
        await message.answer(
            f"⚠️ Найдено {len(list(db_channels - already_subscribed))} каналов. "
            f"Подписка будет выполнена только на первые {500}."
        )

    for channel in list(db_channels - already_subscribed)[:500]:  # Ограничиваем до 500 записей
        random_delay = random.choice(
            [
                15, 16, 17, 18, 19,
                20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
                40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
                50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
                60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
                70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
                80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
                90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
                120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
                130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
                140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
                150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                160, 161, 162, 163, 164, 165, 166, 167, 168, 169,
                170, 171, 172, 173, 174, 175, 176, 177, 178, 179,
                180, 181, 182, 183, 184, 185, 186, 187, 188, 189,
                190, 191, 192, 193, 194, 195, 196, 197, 198, 199,
                200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
                300, 301, 302, 303, 304, 305, 306, 307, 308, 309,
                310, 311, 312, 313, 314, 315, 316, 317, 318, 319,
                320, 321, 322, 323, 324, 325, 326, 327, 328, 329
            ]
        )
        try:
            logger.warning(f"🔗 Подписка на {channel}")
            await client(JoinChannelRequest(channel))
            await message.answer(
                f"✅ Подписка на {channel} выполнена\n"
                f"⏳ Следующая попытка через {random_delay} сек."
            )
            await asyncio.sleep(random_delay)
        except ChannelPrivateError:
            logger.error(f"⚠️ Канал {channel} приватный")
        except UserAlreadyParticipantError:
            logger.error(f"ℹ️ Уже подписан на {channel}")
        except FloodWaitError as e:
            logger.error(f"⚠️ FloodWait {e.seconds} сек.")
            await asyncio.sleep(e.seconds)
            try:
                await client(JoinChannelRequest(channel))
            except InviteRequestSentError:
                logger.error(f"✉️ Приглашение уже отправлено: {channel}")
        except InviteRequestSentError:
            logger.error(f"✉️ Приглашение уже отправлено: {channel}")
        except ValueError:
            logger.error(f"❌ Невалидный username: {channel}")
            # delete_group_by_username(user_id, channel)  # Удаляем невалидный канал / группу
        except Exception as e:
            logger.exception(f"❌ Ошибка при подписке на {channel}: {e}")


async def ensure_joined_target_group(client, message, user_id: int):
    """
    Обеспечивает подключение клиента Telethon к целевой группе пользователя.

    Обёртка вокруг `join_target_group`, которая проверяет успешность подключения и при необходимости отправляет
    пользователю сообщение об ошибке.

    - Если подключение не удалось, функция возвращает None (клиент НЕ отключается).
    - Используется для упрощения логики в функции `filter_messages`.

    :param client: (TelegramClient) Активный клиент для выполнения запросов.
    :param message: (Message) Объект сообщения aiogram для отправки уведомления об ошибке.
    :param user_id: (int) Уникальный идентификатор пользователя Telegram.
    :return: int or None: Идентификатор целевой группы (entity.id) при успехе, иначе None.
    """
    logger.info("Подключаемся к целевой группе для пересылки")
    target_group_id = await join_target_group(client=client, user_id=user_id, message=message)

    if not target_group_id:
        text_error = "❌ Аккаунту не удалось присоединиться к целевой группе, проверьте подключенную группу"
        logger.error(text_error)
        await message.answer(
            text=text_error,
            reply_markup=connect_grup_keyboard_tech()
        )
        # НЕ отключаем клиент здесь — это будет сделано в finally блоке filter_messages
        return None

    return target_group_id


async def get_user_channels_or_notify(user_id: int, user, message, client):
    channels = [group.username for group in Groups.select().where(Groups.user_id == user_id)]

    if not channels:
        logger.warning(f"⚠️ Список каналов пуст для пользователя {user_id}.")
        await client.disconnect()
        await message.answer(
            get_text(user.language, "tracking_launch_error"),
            reply_markup=menu_launch_tracking_keyboard()
        )
        return None

    return channels


async def filter_messages(message, user_id, user):
    """
    Основная функция запуска процесса отслеживания сообщений в Telegram.

    1️⃣ Читает каналы из БД — мгновенно, без запросов к Telegram.
    2️⃣ Параллельно запускает:
        - прослушивание новых сообщений (сразу)
        - подписку на целевую группу и новые каналы (в фоне)

    :param message: (Message) Объект сообщения aiogram для взаимодействия с пользователем.
    :param user_id: (int) Идентификатор пользователя Telegram.
    :param user: (User) Модель пользователя из базы данных (для языка и данных).
    :return: None
    :raises Exception: Логируется при ошибках инициализации или подключения.
    """
    logger.info(f"🚀 Запуск бота для user_id={str(user_id)}...")
    client = None
    try:
        # === Проверка аккаунтов ===
        # Проверка на наличие подключенного аккаунта у пользователя для избежания ошибки
        # Получаем все аккаунты пользователя из его персональной таблицы
        accounts = get_user_accounts(user_id)
        if not accounts:
            logger.warning(f"⚠️ У пользователя {user_id} нет подключённых аккаунтов в БД")
            await message.answer(
                "❌ У вас нет подключённых аккаунтов.\n\n"
                "Отправьте файл сессии `.session` или нажмите «Подключение аккаунта» в меню.",
                reply_markup=menu_launch_tracking_keyboard()
            )
            return None
        logger.info(f"📦 Найдено {len(accounts)} аккаунтов в БД для пользователя {user_id}")

        # === Подключаем клиент ===
        # ✅ Сохраняем активный клиент
        checker = CheckingAccountsValidity(message=message)
        client = await checker.client_connect_string_session(accounts[0]['session_string'])
        active_clients[str(user_id)] = client

        # === Подключаемся к целевой группе для пересылки ===
        # target_group_id = await ensure_joined_target_group(client=client, message=message, user_id=int(user_id))
        # Если не удалось подключиться к целевой группе — выходим
        # if not target_group_id:
        #     return

        # === 1️⃣ Читаем каналы из БД — быстро, без запросов к Telegram ===
        channels = await get_user_channels_or_notify(user_id=int(user_id), user=user, message=message, client=client)
        # Если каналов нет — выходим
        if not channels:
            return

        # === 2️⃣ Инициализируем флаг остановки ===
        stop_event = asyncio.Event()
        stop_flags[str(user_id)] = stop_event

        # === Функция прослушивания — стартует сразу ===
        async def listen():
            # Получаем target_group_id из БД (без Telegram запроса) для регистрации хендлера
            GroupModel = create_group_model(user_id=user_id)
            if not GroupModel.table_exists():
                logger.warning("❌ Таблица целевой группы не найдена")
                return
            groups = list(GroupModel.select())
            if not groups:
                logger.warning("❌ Целевая группа не задана в БД")
                await message.answer(
                    "❌ Не найдена целевая группа для пользователя. Подключите группу.",
                    reply_markup=connect_grup_keyboard_tech()
                )
                return

            # Получаем entity целевой группы через Telegram (быстро — один запрос)
            target_username = groups[0].user_group
            try:
                entity = await client.get_entity(target_username)
                target_group_id = entity.id
            except FloodWaitError as e:
                logger.warning(f"FloodWaitError: {e}")
                await asyncio.sleep(e.value)
                entity = await client.get_entity(target_username)
                target_group_id = entity.id
            except Exception as e:
                logger.exception(f"❌ Не удалось получить целевую группу: {e}")
                await message.answer(
                    "❌ Не удалось получить целевую группу. Проверьте подключение.",
                    reply_markup=connect_grup_keyboard_tech()
                )
                return

            # ✅ Резолвим каналы заранее — фильтруем невалидные
            valid_channels = []
            for channel in channels:
                try:
                    entity = await client.get_input_entity(channel)
                    logger.info(entity)
                    valid_channels.append(entity)
                except ValueError:
                    logger.warning(f"⚠️ Канал не найден, пропускаем: {channel}")
                except FloodWaitError as e:
                    logger.warning(f"⚠️ FloodWait при резолве {channel}: {e.seconds} сек.")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка резолва {channel}: {e}")

            if not valid_channels:
                logger.warning("❌ Нет валидных каналов для прослушивания")
                await message.answer(
                    "❌ Ни один канал не удалось подключить. Проверьте список каналов.",
                    reply_markup=menu_launch_tracking_keyboard()
                )
                return

            logger.info(f"✅ Валидных каналов для прослушивания: {len(valid_channels)} из {len(channels)}")

            @client.on(events.NewMessage(chats=valid_channels))
            async def handle_new_message(event: events.NewMessage.Event):
                try:
                    await process_message(
                        client=client,
                        message=event.message,
                        chat_id=event.chat_id,
                        user_id=str(user_id),
                        target_group_id=target_group_id
                    )
                except Exception as e:
                    logger.exception(f"Не удалось обработать сообщение: {e}")

            logger.info("👂 Бот слушает новые сообщения...")
            await message.answer(
                text="👂 Бот слушает новые сообщения...",
                reply_markup=menu_launch_tracking_keyboard()
            )

            # Держим клиент живым до флага остановки
            await stop_event.wait()

            logger.info(f"🛑 Прослушивание остановлено для user_id={user_id}")
            await message.answer("🛑 Отслеживание сообщений остановлено.")

        # === Функция подписки — работает параллельно в фоне ===
        async def subscribe():
            await ensure_joined_target_group(client=client, message=message, user_id=int(user_id))
            await join_required_channels(client=client, user_id=str(user_id), message=message)

        # 🚀 Запускаем одновременно: прослушивание + подписка
        await asyncio.gather(listen(), subscribe())

    except Exception as e:
        logger.exception(f"❌ Критическая ошибка в filter_messages: {e}")
    finally:
        # ✅ Очищаем ресурсы
        if user_id in active_clients:
            client = active_clients.pop(str(user_id))
            if client.is_connected():
                await client.disconnect()
                logger.info(f"🛑 Клиент для user_id={str(user_id)} отключён.")
        if user_id in stop_flags:
            stop_flags.pop(str(user_id))
            logger.info(f"🗑️ Флаг остановки для user_id={str(user_id)} удалён.")


async def stop_tracking(user_id, message):
    """
    Останавливает процесс отслеживания сообщений для пользователя.

    Устанавливает флаг остановки для активной сессии пользователя, что приводит к
    завершению цикла прослушивания в функции `filter_messages`.

    - Не создаёт новое подключение к сессии (избегает блокировки SQLite).
    - Использует глобальный словарь `stop_flags` для управления состоянием.
    - Безопасно обрабатывает случаи, когда отслеживание уже остановлено.

    :param user_id: (int) Идентификатор пользователя Telegram.
    :param message: (Message) Объект сообщения aiogram для отправки подтверждения.
    :return: None
    """
    user_id = str(user_id)  # <-- ✅ преобразуем в строку

    logger.info(f"🛑 Запрос на остановку отслеживания для user_id={user_id}")

    # ✅ Проверяем, есть ли активное отслеживание для этого пользователя
    if user_id not in stop_flags:
        logger.warning(f"⚠️ Отслеживание для user_id={user_id} не активно или уже остановлено.")
        await message.answer(
            "⚠️ Отслеживание не запущено или уже остановлено.",
            reply_markup=menu_launch_tracking_keyboard()
        )
        return

    # ✅ Устанавливаем флаг остановки
    stop_event = stop_flags[user_id]
    stop_event.set()

    logger.info(f"✅ Флаг остановки установлен для user_id={user_id}")
    await message.answer(
        "🛑 Команда остановки отправлена. Отслеживание будет остановлено в течение нескольких секунд.",
        reply_markup=menu_launch_tracking_keyboard()
    )
