import asyncio
import random
import re
from datetime import datetime
from html import escape

import telethon.utils as utils
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, PasswordHashInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError, SessionPasswordNeededError,
    UsernameNotOccupiedError, UsernameInvalidError, ChannelPrivateError, UserRestrictedError, ChannelsTooMuchError,
    UserAlreadyParticipantError, InviteHashExpiredError, InviteHashInvalidError
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, CreateChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ExportChatInviteRequest, ImportChatInviteRequest
from telethon.tl.types import ChatAdminRights

from account_manager.auth import CheckingAccountsValidity, get_account_info
from account_manager.parser import active_clients, filter_messages, stop_tracking
from core.config import API_ID, API_HASH, mobile_device, ADMIN_USER_ID, create_background_task, active_tasks
from database.account_free import write_account_to_db_free, getting_free_account

from database.users_accounts import (
    write_account_to_user_table, get_user_accounts_list,
    get_account_by_id, delete_account_by_id, UsersAccounts
)
from database.users_groups import UsersGroups, add_user_group, sync_account_dialogs_to_db
from database.users_keywords import add_user_keywords, UsersKeywords, get_user_keywords
from database.users_personal_trackings import (
    get_user_accounts, UsersPersonalTrackings, write_account_to_db, set_user_shared_account
)
from handlers.user_language import determines_user_language
from keyboards.keyboards import personal_tracking_menu_kb, tracking_list_keyboard, emoji_code_keypad_kb, back_button
from locales.locales import t
from system.dispatcher import bot

router = Router(name="personal_tracking")

username_bot = "@Botzzzz_admin_bot"  # Бот администратор, который будет пересылать сообщения по ключевому слову.

"""

Таблица с ключевыми словами от пользователей для дальнейшего поиска в сообщения Групп и Каналов users_keywords data/bot.db

Модуль персонального отслеживания ключевых слов (Personal Tracking).
=====================================================================

Назначение
----------
Раздел меню для подключения аккаунта Telegram (личного или общего) и
настройки автоматического мониторинга целевых групп/каналов по
ключевым словам с уведомлением в персональную техническую группу.


Архитектура
-----------
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Пользователь │────▶│  Бот (aiogram)   │────▶│  Telegram API   │
└──────────────┘     └────────┬─────────┘     └─────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Telethon-клиент   │  ← рабочая сессия
                    │  (StringSession)   │     аккаунта
                    └─────────┬──────────┘
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
     │ Целевая      │ │ Персональная │ │ @Botzzzz_admin   │
     │ группа/канал │ │ тех. группа  │ │ _bot (админ)     │
     │ (мониторинг) │ │ (уведомления)│ │ (формирование    │
     │              │ │              │ │  сообщений)      │
     └──────────────┘ └──────────────┘ └──────────────────┘


Модели БД
---------
PersonalTracking      — настройки отслеживания (users_personal_tracking)
User                  — профиль пользователя (язык, баланс Stars)
Account               — персональные сессии пользователей (users_accounts)
AccountFree           — общие сессии от администратора


Слоты (Slots)
-------------
• Бесплатно: 1 слот (1 группа/канал для отслеживания)
• Платно:  +1 слот за 2 Telegram Stars
• Лимит:   get_user_allowed_slots() = 1 + купленные_слоты
• Проверка: get_user_used_slots() <= get_user_allowed_slots()


Механизм работы
---------------
1. ПОДКЛЮЧЕНИЕ АККАУНТА
   а) Пользователь нажимает «Подключить свой аккаунт»
   б) Вводит номер телефона → Telethon запрашивает код
   в) Вводит 5-значный код (эмодзи-клавиатура) или 2FA-пароль
   г) Сессия (StringSession) сохраняется в БД:
      - Обычный пользователь → UserAccountsTable
      - Администратор         → AccountFree (общая таблица)

2. СОЗДАНИЕ ОТСЛЕЖИВАНИЯ
   а) Пользователь выбирает «➕ Добавить отслеживание»
   б) Отправляет ссылку/username целевой группы
   в) Система подключает рабочую сессию (личную или случайную из общих):
      CheckingAccountsValidity.start_random_client()
   г) Проверяет подписку на целевую группу (подписывается автоматически)
   д) Создаёт приватную супергруппу «Отслеживание: {название}»
   е) Назначает @Botzzzz_admin_bot администратором новой группы
   ж) Экспортирует ссылку-приглашение
   з) Пользователь вводит ключевые слова
   и) Запись сохраняется в PersonalTracking


Проверка изменения (Cooldown)
-----------------------------
• Смена группы/ключевых слов: не чаще 1 раза в 24 часа
• can_user_change_tracking() → (allowed, hours_left)


Уведомления (Alerts)
--------------------
• send_personal_tracking_alert() — вызывается при нахождении
  сообщения с ключевым словом
• Формирует сообщение с текстом, словом-совпадением и ссылкой
• Отправляет в созданную персональную группу (created_group_id)


Потоки состояний (FSM)
-----------------------
waiting_for_target_link   → ввод ссылки целевой группы
waiting_for_keywords      → ввод ключевых слов
editing_slot_link         → редактирование ссылки
editing_slot_keywords     → редактирование ключевых слов
waiting_for_phone_number  → ввод номера телефона
waiting_for_auth_code     → ввод 5-значного кода
waiting_for_2fa_password  → ввод 2FA-пароля
"""


# Модель PersonalTracking определена в database.personal_tracking


# ==================== МАШИНА СОСТОЯНИЙ ====================

class PersonalTrackingState(StatesGroup):
    """Группа состояний FSM для настройки персонального отслеживания и авторизации аккаунта"""

    # --- Поток создания/редактирования отслеживания ---
    waiting_for_target_link = State()  # Ожидание ссылки или username целевой группы/канала от пользователя
    waiting_for_keywords = State()  # Ожидание ввода ключевых слов для фильтрации сообщений
    editing_slot_link = State()  # Редактирование существующей ссылки отслеживаемой группы
    editing_slot_keywords = State()  # Редактирование существующих ключевых слов

    # --- Поток авторизации Telegram-аккаунта по номеру телефона ---
    waiting_for_phone_number = State()  # Ожидание ввода номера телефона в международном формате
    waiting_for_auth_code = State()  # Ожидание ввода 5-значного кода из SMS/пуш-уведомления Telegram
    waiting_for_2fa_password = State()  # Ожидание ввода облачного пароля (если включена 2FA)

    # --- Управление мульти-аккаунтами и кампаниями (диваны, холодильники...) ---
    waiting_for_acc_title = State()  # Ожидание ввода названия/темы для кампании
    waiting_for_acc_keywords = State()  # Ожидание ввода ключевых слов конкретной кампании


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_user_allowed_slots(user_id: int) -> int:
    """
    Возвращает количество доступных слотов пользователя (базовый 1 + купленные за Telegram Stars).

    :param user_id: (int) ID пользователя в Telegram.
    :return: (int) Количество разрешённых слотов.
    """
    pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    stars = pt_rec.stars if pt_rec and pt_rec.stars else 0
    extra = stars // 2
    return 1 + extra


def get_user_used_slots(user_id: int) -> int:
    """
    Возвращает количество задействованных слотов (каналов) пользователя.

    :param user_id: (int) ID пользователя в Telegram.
    :return: (int) Количество занятых слотов.
    """
    return UsersGroups.select().where(UsersGroups.user_id == user_id).count()


def can_user_change_tracking(tracking_record) -> tuple[bool, float]:
    """
    Проверяет ограничение на смену группы/ключевых слов (не чаще 1 раза в 24ч).

    :param tracking_record: Экземпляр записи отслеживания.
    :return: (tuple[bool, float]) Кортеж (разрешено_ли_изменение, часов_до_следующей_возможности).
    """
    last_changed = getattr(tracking_record, 'last_changed_at', None) or getattr(tracking_record, 'date_added', None)
    if not tracking_record or not last_changed:
        return True, 0.0

    diff_seconds = (datetime.now() - last_changed).total_seconds()
    if diff_seconds >= 86400:  # 24 часа
        return True, 0.0

    hours_left = round((86400 - diff_seconds) / 3600, 1)
    return False, hours_left


async def connect_target_and_create_group(target_input: str, user_id: int):
    """
    Подключает целевую группу и создает приватную группу для уведомлений.

    1. Подключает рабочую сессию Telethon (личную или из пула общих).
    2. Проверяет подписку на целевую группу/канал (подписывается при необходимости).
    3. Создает приватную группу для сообщений и выгружает ссылку-приглашение.

    :param target_input: (str) Текстовое представление ссылки или юзернейма канала.
    :param user_id: (int) ID пользователя Telegram для привязки аккаунта.
    :return: (tuple[bool, str, str | None, int | None]) Кортеж (успех, сообщение, инвайт_ссылка, id_группы).
    """
    clean_target = target_input.strip()
    checker = CheckingAccountsValidity()

    # 1. Личные подключенные аккаунты пользователя (приоритет)
    user_accs = get_user_accounts(user_id)
    candidate_sessions = []
    for acc in user_accs:
        if acc.get("session_string"):
            candidate_sessions.append((acc["session_string"], "общий" if acc.get("is_shared") else "личный"))

    # 2. Общие аккаунты из пула администратора (перемешиваем для распределения нагрузки)
    shared_sessions = getting_free_account()
    random.shuffle(shared_sessions)
    existing_sessions = {cs[0] for cs in candidate_sessions}
    for s in shared_sessions:
        if s not in existing_sessions:
            candidate_sessions.append((s, "общий"))

    if not candidate_sessions:
        return False, "⚠️ Нет доступных рабочих сессий для поиска. Попробуйте позже.", None, None, None, None

    max_attempts = min(5, len(candidate_sessions))
    last_restriction_error = None

    for attempt_idx in range(max_attempts):
        session_str, acc_type = candidate_sessions[attempt_idx]
        client: TelegramClient | None = await checker.client_connect_string_session(session_str)
        if not client:
            continue

        try:
            entity = None

            # 1. Проверяем, является ли ссылка инвайтом в закрытую группу (+hash или joinchat/hash)
            invite_match = re.search(r'(?:joinchat/|\+)([A-Za-z0-9_\-]+)', clean_target)
            if invite_match:
                invite_hash = invite_match.group(1)
                try:
                    logger.info(f"🔗 Попытка вступления в закрытую группу по инвайт-хэшу {invite_hash}...")
                    res = await client(ImportChatInviteRequest(hash=invite_hash))
                    if hasattr(res, 'chats') and res.chats:
                        entity = res.chats[0]
                        logger.info(f"✅ Успешно вступили в закрытую группу по ссылке: {getattr(entity, 'title', '')}")
                except UserAlreadyParticipantError:
                    logger.info("ℹ️ Аккаунт уже состоит в этой закрытой группе")
                    async for dialog in client.iter_dialogs(limit=100):
                        if getattr(dialog.entity, 'megagroup', False) or getattr(dialog.entity, 'broadcast', False):
                            entity = dialog.entity
                            break
                except Exception as inv_err:
                    logger.warning(f"Ошибка вступления по инвайт-ссылке {invite_hash}: {inv_err}")

            # 2. Проверяем ввод по числовому ID закрытой группы (-100... или ...)
            if not entity:
                clean_num = clean_target.replace("https://t.me/", "").lstrip("@")
                if clean_num.lstrip("-").isdigit():
                    try:
                        int_id = int(clean_num)
                        entity = await client.get_entity(int_id)
                        logger.info(f"✅ Найдена закрытая группа по ID {int_id}: {getattr(entity, 'title', '')}")
                    except Exception:
                        pass

            # 3. Проверяем ввод по точному названию закрытого чата (когда аккаунт зашел через tdata)
            if not entity:
                clean_name = clean_target.strip().lower()
                async for dialog in client.iter_dialogs(limit=150):
                    d_title = (getattr(dialog.entity, 'title', '') or "").strip().lower()
                    if d_title and d_title == clean_name:
                        entity = dialog.entity
                        logger.info(f"✅ Найдена закрытая группа по названию «{clean_target}» в диалогах аккаунта")
                        break

            # 4. Публичный канал или супергруппа
            if not entity:
                clean_pub = clean_target.replace("https://t.me/", "@")
                entity = await client.get_entity(clean_pub)

            if not entity:
                raise ValueError("Целевая сущность не найдена")

            target_peer_id = utils.get_peer_id(entity)
            target_title_raw = getattr(entity, 'title', clean_target)

            # Проверяем и подписываемся на целевую группу/канал
            try:
                await client(JoinChannelRequest(channel=entity))
                logger.info(f"✅ Сессия Telethon ({acc_type}) подписалась на целевой объект {clean_target}")
            except Exception as join_err:
                logger.debug(f"Уведомление при подписке на {clean_target}: {join_err}")

            # Создаем приватную супергруппу для отправки найденных сообщений
            target_title = target_title_raw[:20]
            group_title = f"Отслеживание: {target_title}"

            created_channel = await client(CreateChannelRequest(
                title=group_title,
                about="Группа персонального отслеживания",
                megagroup=True
            ))

            new_chat = created_channel.chats[0]
            chat_id = utils.get_peer_id(new_chat)

            # Добавляем бота в группу администратором
            try:
                admin_rights = ChatAdminRights(
                    change_info=True,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=True,
                    manage_topics=True
                )
                await client(EditAdminRequest(
                    channel=new_chat,
                    user_id=username_bot,
                    admin_rights=admin_rights,
                    rank="AlertBot"
                ))
                logger.info(f"✅ Бот {username_bot} успешно добавлен администратором в группу {chat_id}")
            except Exception as admin_err:
                logger.error(f"❌ Ошибка добавления бота {username_bot} в администраторы: {admin_err}")

            # Создаем постоянную ссылку-приглашение без ограничений через бота (старшего администратора)
            invite_link = None
            try:
                bot_invite = await bot.create_chat_invite_link(
                    chat_id=chat_id,
                    name="PermanentAlertGroup",
                    expire_date=None,
                    member_limit=None,
                    creates_join_request=False
                )
                invite_link = bot_invite.invite_link
                logger.info(f"✅ Создана постоянная ссылка-приглашение без ограничений через бота: {invite_link}")
            except Exception as bot_inv_err:
                logger.warning(
                    f"Ошибка создания ссылки через бота ({bot_inv_err}). Пробуем через Telethon с usage_limit=None...")
                try:
                    invite_export = await client(ExportChatInviteRequest(
                        peer=new_chat,
                        expire_date=None,
                        usage_limit=None,
                        request_needed=False
                    ))
                    invite_link = invite_export.link
                except Exception as mt_err:
                    logger.error(f"Не удалось получить ссылку-приглашение: {mt_err}")

            await client.disconnect()

            # Если у пользователя еще не был сохранен аккаунт в профиле, сохраняем использованный
            pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
            if not (pt_rec and (pt_rec.personal_account or pt_rec.shared_account)):
                set_user_shared_account(user_id=user_id, session_string=session_str)

            return True, "Успешно", invite_link, chat_id, target_peer_id, target_title_raw

        except (UsernameNotOccupiedError, UsernameInvalidError, ValueError) as e:
            logger.warning(f"⚠️ Целевая группа/канал не существует или неверный юзернейм ({target_input}): {e}")
            try:
                await client.disconnect()
            except Exception:
                pass
            return False, "Указанная группа или канал не существует. Проверьте правильность ссылки/юзернейма.", None, None, None, None

        except ChannelPrivateError as cpe_err:
            logger.warning(
                f"⚠️ Аккаунт {attempt_idx + 1}/{max_attempts} ({acc_type}) получил ChannelPrivateError ({cpe_err}) для {clean_target} "
                f"(возможно, заблокирован в этой группе/канале). Пробуем следующий аккаунт..."
            )
            try:
                await client.disconnect()
            except Exception:
                pass
            if attempt_idx < max_attempts - 1:
                continue
            return False, "Указанная группа является приватной, не существует или все доступные аккаунты заблокированы в ней.", None, None, None, None

        except (UserRestrictedError, ChannelsTooMuchError, FloodWaitError) as tg_err:
            logger.warning(
                f"⚠️ Аккаунт {attempt_idx + 1}/{max_attempts} ({acc_type}) имеет ограничение Telegram: {tg_err}. Пробуем следующий аккаунт..."
            )
            last_restriction_error = str(tg_err)
            try:
                await client.disconnect()
            except Exception:
                pass
            continue

        except Exception as e:
            logger.warning(f"⚠️ Ошибка аккаунта ({acc_type}) при подключении группы {target_input}: {e}")
            try:
                await client.disconnect()
            except Exception:
                pass
            if attempt_idx < max_attempts - 1:
                continue
            return False, f"Ошибка подключения к целевой группе: {e}", None, None, None, None

    if last_restriction_error:
        return (
            False,
            "⚠️ Доступные рабочие аккаунты временно ограничены Telegram на создание каналов/групп (спам-репорт или лимит). "
            "Пожалуйста, подключите свой личный аккаунт через меню «🎯 Персональное отслеживание» ➔ «Подключить свой аккаунт» или повторите попытку позже.",
            None,
            None,
            None,
            None
        )

    return False, "⚠️ Не удалось подключиться к группе через доступные аккаунты. Попробуйте позже.", None, None, None, None


async def ensure_permanent_group_invite_link(user_id: int) -> str:
    """
    Проверяет и возвращает постоянную ссылку-приглашение без ограничений на группу результатов пользователя.
    Если ссылка отсутствует или устарела, генерирует новую постоянную ссылку через бота и сохраняет в БД.

    :param user_id: (int) ID пользователя Telegram.
    :return: (str) Постоянная ссылка-приглашение или пустая строка.
    """
    pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    if not pt_rec or not pt_rec.created_group_id:
        return ""

    group_id = pt_rec.created_group_id
    current_link = (pt_rec.created_group_link or "").strip()

    try:
        new_link_obj = await bot.create_chat_invite_link(
            chat_id=group_id,
            name="PermanentAlertLink",
            expire_date=None,
            member_limit=None,
            creates_join_request=False
        )
        if new_link_obj and new_link_obj.invite_link:
            pt_rec.created_group_link = new_link_obj.invite_link
            pt_rec.save()
            return new_link_obj.invite_link
    except TelegramForbiddenError as fe:
        logger.warning(f"⚠️ Бот был исключен из группы {group_id} ({fe}). Сбрасываем привязку устаревшей группы.")
        pt_rec.created_group_id = None
        pt_rec.created_group_link = None
        pt_rec.save()
        return ""
    except Exception as e:
        logger.debug(f"Не удалось обновить ссылку через бота для группы {group_id}: {e}")

    return current_link


async def sync_and_promote_account_for_tracking(user_id: int, session_string: str) -> tuple[bool, bool]:
    """
    Синхронизирует новый/переподключенный аккаунт с отслеживанием пользователя:
    1. Подписывает аккаунт на целевые группы/каналы отслеживания из UsersGroups.
    2. Вступает в персональную группу для пересылки сообщений (created_group_id / created_group_link).
    3. Бот-администратор (старший в группе) выдает новому аккаунту права администратора:
       ТОЛЬКО на публикацию сообщений (без прав на изменение инфо, удаление, добавление админов и т.д.),
       чтобы исключить возможность кражи или захвата группы.

    :param user_id: (int) ID пользователя Telegram.
    :param session_string: (str) Строка сессии Telethon для подключения.
    :return: (tuple[bool, bool]) (успех_синхронизации, является_владельцем_группы).
    """
    if not session_string:
        return False, False

    checker = CheckingAccountsValidity()
    client: TelegramClient | None = await checker.client_connect_string_session(session_string)
    if not client:
        logger.warning(f"⚠️ Не удалось подключить сессию для синхронизации отслеживания user_id={user_id}")
        return False, False

    try:
        account_info = await get_account_info(client)
        account_tg_id = account_info.get("id")
        logger.info(f"🔄 Синхронизация аккаунта {account_tg_id} (user_id={user_id}) с отслеживанием...")

        # 1. Подписываем аккаунт на целевой отслеживаемый канал/группу пользователя
        user_groups = list(UsersGroups.select().where(UsersGroups.user_id == user_id))
        for g in user_groups:
            target_link = (g.username_group or "").strip()
            if not target_link:
                continue

            entity = None
            peer_id = None
            title = ""

            # Проверяем, является ли ссылка инвайтом в приватную группу (+hash или joinchat/hash)
            invite_match = re.search(r'(?:joinchat/|\+)([A-Za-z0-9_\-]+)', target_link)
            if invite_match:
                invite_hash = invite_match.group(1)
                try:
                    logger.info(
                        f"🔗 Попытка вступления в приватную целевую группу {target_link} по хэшу {invite_hash}...")
                    res = await client(ImportChatInviteRequest(hash=invite_hash))
                    logger.info(f"✅ Аккаунт {account_tg_id} успешно вступил в приватную группу: {target_link}")
                    if hasattr(res, 'chats') and res.chats:
                        entity = res.chats[0]
                except UserAlreadyParticipantError:
                    logger.info(f"ℹ️ Аккаунт {account_tg_id} уже является участником приватной группы {target_link}")
                    try:
                        async for dialog in client.iter_dialogs(limit=50):
                            if g.id_group and (
                                    dialog.id == g.id_group or utils.get_peer_id(dialog.entity) == g.id_group):
                                entity = dialog.entity
                                break
                    except Exception:
                        pass
                except Exception as inv_err:
                    logger.warning(f"⚠️ Ошибка вступления в приватную целевую группу {target_link}: {inv_err}")
            else:
                # Публичный канал или супергруппа
                clean_target = target_link.replace("https://t.me/", "@")
                try:
                    entity = await client.get_entity(clean_target)
                    try:
                        await client(JoinChannelRequest(channel=entity))
                        logger.info(f"✅ Аккаунт {account_tg_id} подписан на целевой объект: {target_link}")
                    except UserAlreadyParticipantError:
                        logger.info(f"ℹ️ Аккаунт {account_tg_id} уже подписан на: {target_link}")
                    except Exception as join_err:
                        logger.debug(f"Уведомление при подписке на целевой объект {target_link}: {join_err}")
                except Exception as ent_err:
                    logger.warning(f"⚠️ Не удалось получить сущность для {target_link}: {ent_err}")

            if entity:
                peer_id = utils.get_peer_id(entity)
                title = getattr(entity, 'title', '')
            elif g.id_group:
                peer_id = g.id_group

            if peer_id:
                g.id_group = peer_id
                if title:
                    g.name_group = title
                g.save()
                logger.info(f"💾 Обновлен id_group={peer_id} для {target_link} (user_id={user_id})")

        # 2. Проверяем наличие и доступность группы результатов
        pt_rec, _ = UsersPersonalTrackings.get_or_create(user_id=user_id)
        group_id = pt_rec.created_group_id
        need_recreate = False

        if not group_id:
            # Если у пользователя уже настроены группы для отслеживания (UsersGroups),
            # но группа результатов отсутствует — нужно пересоздать её при подключении нового аккаунта!
            if user_groups:
                need_recreate = True
                logger.info(
                    f"ℹ️ У пользователя {user_id} настроено отслеживание, но отсутствует группа результатов. Пересоздаем...")
            else:
                logger.info(
                    f"У пользователя {user_id} еще нет настроенных отслеживаний для создания группы результатов")
                return True, False
        else:
            # Проверяем, существует ли группа и доступен ли в ней бот
            try:
                await bot.get_chat(group_id)
            except (TelegramForbiddenError, TelegramBadRequest) as chat_err:
                logger.warning(
                    f"⚠️ Группа результатов {group_id} недоступна ({chat_err}). Пересоздаем группу результатов...")
                need_recreate = True

        if need_recreate:
            # Определяем заголовок создаваемой группы
            target_title = "Персональная группа"
            if user_groups:
                g0 = user_groups[0]
                raw_title = getattr(g0, 'name_group', None) or getattr(g0, 'username_group', None) or "Отслеживание"
                target_title = str(raw_title).replace("https://t.me/", "@")[:20]
            group_title = f"Отслеживание: {target_title}"

            try:
                created_channel = await client(CreateChannelRequest(
                    title=group_title,
                    about="Группа персонального отслеживания",
                    megagroup=True
                ))
                new_chat = created_channel.chats[0]
                group_id = utils.get_peer_id(new_chat)

                # Добавляем бота администратором с правом назначать других администраторов
                admin_rights = ChatAdminRights(
                    change_info=True,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=True,
                    manage_topics=True
                )
                await client(EditAdminRequest(
                    channel=new_chat,
                    user_id=username_bot,
                    admin_rights=admin_rights,
                    rank="AlertBot"
                ))

                # Бот создает постоянную ссылку-приглашение без ограничений
                bot_invite = await bot.create_chat_invite_link(
                    chat_id=group_id,
                    name="PermanentAlertGroup",
                    expire_date=None,
                    member_limit=None,
                    creates_join_request=False
                )
                invite_link = bot_invite.invite_link

                # Сохраняем новую группу в профиль пользователя
                pt_rec.created_group_id = group_id
                pt_rec.created_group_link = invite_link
                pt_rec.last_changed_at = datetime.now()
                pt_rec.save()

                logger.info(
                    f"✅ Новая группа результатов для user_id={user_id} пересоздана: ID={group_id}, Link={invite_link}")

                # Оповещаем пользователя в ЛС бота о новой созданной группе результатов
                try:
                    user_lang = determines_user_language(message_or_callback=user_id)
                    notify_text = (
                        f"🎉 <b>Группа для результатов успешно создана!</b>\n\n"
                        f"🔗 <b>Ссылка для вступления:</b> <a href='{invite_link}'>Перейти в группу</a>\n\n"
                        f"<i>Все найденные совпадения по ключевым словам будут отправляться туда.</i>"
                    ) if user_lang == "ru" else (
                        f"🎉 <b>Results group successfully created!</b>\n\n"
                        f"🔗 <b>Invite link:</b> <a href='{invite_link}'>Go to group</a>\n\n"
                        f"<i>All keyword match alerts will be sent there.</i>"
                    )
                    await bot.send_message(chat_id=user_id, text=notify_text, parse_mode="HTML")
                except Exception as notify_err:
                    logger.debug(f"Не удалось отправить уведомление о новой группе: {notify_err}")

                return True, False
            except Exception as cr_err:
                logger.error(f"❌ Ошибка пересоздания группы результатов: {cr_err}")
                return False, False

        invite_link = (pt_rec.created_group_link or "").strip()

        # Разбаниваем аккаунт в группе через бота на случай, если он ранее был исключен
        if account_tg_id:
            try:
                await bot.unban_chat_member(chat_id=group_id, user_id=account_tg_id, only_if_banned=True)
            except Exception as unban_err:
                logger.debug(f"Проверка unban_chat_member в группе {group_id}: {unban_err}")

        # Проверяем участие аккаунта в группе результатов
        is_participant = False
        try:
            await client.get_entity(group_id)
            is_participant = True
        except Exception:
            is_participant = False

        if not is_participant:
            # Если нет ссылки или она невалидна, бот создает новую постоянную ссылку без ограничений
            if not invite_link or "t.me/" not in invite_link:
                try:
                    new_invite = await bot.create_chat_invite_link(
                        chat_id=group_id,
                        name="PermanentAlertLink",
                        expire_date=None,
                        member_limit=None,
                        creates_join_request=False
                    )
                    if new_invite and new_invite.invite_link:
                        invite_link = new_invite.invite_link
                        pt_rec.created_group_link = invite_link
                        pt_rec.save()
                except Exception as inv_err:
                    logger.warning(f"Ошибка создания новой инвайт-ссылки ботом для группы {group_id}: {inv_err}")

            # Вступаем по ссылке-приглашению
            if invite_link:
                clean_hash = invite_link.split("+")[-1].split("/")[-1]
                try:
                    await client(ImportChatInviteRequest(hash=clean_hash))
                    is_participant = True
                    logger.info(f"✅ Аккаунт {account_tg_id} вступил в группу результатов {group_id} по инвайт-ссылке")
                except UserAlreadyParticipantError:
                    is_participant = True
                except (InviteHashExpiredError, InviteHashInvalidError) as exp_err:
                    logger.warning(
                        f"⚠️ Ссылка {invite_link} устарела ({exp_err}). Генерируем новую постоянную ссылку без ограничений через бота...")
                    try:
                        new_invite = await bot.create_chat_invite_link(
                            chat_id=group_id,
                            name="PermanentAlertLink",
                            expire_date=None,
                            member_limit=None,
                            creates_join_request=False
                        )
                        if new_invite and new_invite.invite_link:
                            invite_link = new_invite.invite_link
                            pt_rec.created_group_link = invite_link
                            pt_rec.save()
                            new_clean_hash = invite_link.split("+")[-1].split("/")[-1]
                            await client(ImportChatInviteRequest(hash=new_clean_hash))
                            is_participant = True
                            logger.info(f"✅ Аккаунт {account_tg_id} вступил по новой постоянной ссылке {invite_link}")
                    except Exception as new_inv_err:
                        logger.warning(f"Ошибка вступления по новой постоянной ссылке: {new_inv_err}")
                except Exception as import_err:
                    logger.warning(
                        f"Не удалось вступить в группу {group_id} по хэшу: {import_err}. Пробуем JoinChannelRequest...")
                    try:
                        await client(JoinChannelRequest(channel=invite_link))
                        is_participant = True
                    except Exception as jc_err:
                        logger.warning(f"Ошибка вступления через JoinChannelRequest: {jc_err}")

        # 3. Бот-администратор (старший в группе) выдает права администратора новому аккаунту:
        # ТОЛЬКО на публикацию сообщений, чтобы аккаунт не мог угнать или изменить группу.
        if account_tg_id:
            # Проверяем, не является ли данный аккаунт создателем (owner) группы
            try:
                cm = await bot.get_chat_member(chat_id=group_id, user_id=account_tg_id)
                if getattr(cm, "status", None) == "creator":
                    logger.warning(
                        f"⚠️ Аккаунт {account_tg_id} является создателем (owner) группы {group_id}. "
                        f"Бот не может ограничить его права."
                    )
                    return False, True
            except Exception as cm_err:
                logger.debug(f"Проверка get_chat_member в группе {group_id}: {cm_err}")

            promoted = False
            try:
                # В супергруппе Telegram для назначения администратором ТРЕБУЕТСЯ хотя бы одно валидное супергрупповое право.
                # Выдаем can_pin_messages=True (закрепление сообщений),
                # при этом ВСЕ опасные права (изменение инфо, удаление, бан, назначение админов) отключены!
                await bot.promote_chat_member(
                    chat_id=group_id,
                    user_id=account_tg_id,
                    can_pin_messages=True,
                    can_change_info=False,
                    can_delete_messages=False,
                    can_invite_users=False,
                    can_restrict_members=False,
                    can_promote_members=False,
                    can_manage_video_chats=False,
                    can_manage_chat=False,
                    can_manage_topics=False
                )
                promoted = True
                logger.info(
                    f"✅ Бот-администратор успешно назначил аккаунт {account_tg_id} администратором в группе {group_id}"
                )
            except Exception as prom_err:
                err_str = str(prom_err).lower()
                if "chat owner" in err_str:
                    logger.warning(
                        f"⚠️ Аккаунт {account_tg_id} является создателем группы {group_id} ({prom_err}). Бот не может ограничить его права."
                    )
                    return False, True

                logger.warning(
                    f"⚠️ Первая попытка promote_chat_member в группе {group_id} ({prom_err}). Пробуем с can_manage_chat=True..."
                )
                try:
                    await bot.promote_chat_member(
                        chat_id=group_id,
                        user_id=account_tg_id,
                        can_manage_chat=True,
                        can_pin_messages=True,
                        can_change_info=False,
                        can_delete_messages=False,
                        can_invite_users=False,
                        can_restrict_members=False,
                        can_promote_members=False,
                        can_manage_video_chats=False,
                        can_manage_topics=False
                    )
                    promoted = True
                    logger.info(
                        f"✅ Бот-администратор назначил аккаунт {account_tg_id} администратором (can_manage_chat)"
                    )
                except Exception as fb_prom_err:
                    fb_str = str(fb_prom_err).lower()
                    if "chat owner" in fb_str:
                        logger.warning(
                            f"⚠️ Аккаунт {account_tg_id} является создателем группы {group_id} ({fb_prom_err}). Бот не может ограничить его права."
                        )
                        return False, True
                    logger.warning(f"Не удалось назначить права администратора через бота: {fb_prom_err}")

            if promoted:
                # Устанавливаем кастомный титул администратора
                try:
                    await bot.set_chat_administrator_custom_title(
                        chat_id=group_id,
                        user_id=account_tg_id,
                        custom_title="AlertSender"
                    )
                    logger.info(f"✅ Установлен титул 'AlertSender' для аккаунта {account_tg_id} в группе {group_id}")
                except Exception as tit_err:
                    logger.debug(f"Не удалось установить кастомный титул: {tit_err}")

        # Привязываем созданную/проверенную группу результатов к записи в users_accounts
        try:
            acc = UsersAccounts.get_or_none(UsersAccounts.user_session_string == session_string)
            if acc:
                acc.target_group_id = group_id
                acc.target_group_link = invite_link or acc.target_group_link
                acc.save()
        except Exception as acc_save_err:
            logger.debug(f"Привязка тех-группы к UsersAccounts: {acc_save_err}")

        return True, False

    except Exception as e:
        logger.exception(f"❌ Ошибка в sync_and_promote_account_for_tracking для user_id={user_id}: {e}")
        return False, False
    finally:
        try:
            if client and client.is_connected():
                await client.disconnect()
        except Exception:
            pass
        await asyncio.sleep(0.3)  # Пауза для корректного освобождения сессии и избежания AuthKeyDuplicatedError


# ==================== ОБРАБОТЧИКИ (HANDLERS) ====================

"""Единое меню отслеживания группы / канала на основе ключевых слов пользователя"""


def get_personal_tracking_text_and_kb(user_id: int, lang: str = 'ru'):
    """
    Формирует текст и инлайн-клавиатуру для единого экрана управления отслеживанием.

    :param user_id: (int) ID пользователя Telegram.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (tuple[str, InlineKeyboardMarkup]) Текст сообщения и клавиатура.
    """
    allowed = get_user_allowed_slots(user_id)
    used = get_user_used_slots(user_id)
    is_active = str(user_id) in active_clients

    rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    has_personal = bool(rec and rec.personal_account)
    has_shared = bool(rec and rec.shared_account and not rec.personal_account)

    if has_personal:
        acc_text = "📱 <b>Личный аккаунт</b> (без ограничений)"
        acc_text_en = "📱 <b>Personal account</b> (unlimited)"
    elif has_shared:
        acc_text = "🎁 <b>Бесплатный от админа</b> (лимит: 1 группа)"
        acc_text_en = "🎁 <b>Admin's free</b> (limit: 1 group)"
    else:
        acc_text = "⚠️ <b>Не подключен</b>"
        acc_text_en = "⚠️ <b>Not connected</b>"

    status_text = "🟢 <b>Активно</b>" if is_active else "🔴 <b>Остановлено</b>"
    status_text_en = "🟢 <b>Active</b>" if is_active else "🔴 <b>Stopped</b>"

    if lang == "ru":
        text = (
            "🎯 <b>Отслеживание ключевых слов</b>\n\n"
            f"📡 <b>Статус:</b> {status_text}\n"
            f"🔐 <b>Аккаунт:</b> {acc_text}\n"
            f"📊 <b>Ваши слоты:</b> {used} из {allowed} занято.\n\n"
            "Вы можете привязать группу или канал для отслеживания сигналов по Вашим ключевым словам, а также запускать или останавливать процесс мониторинга в любое время.\n\n"
            "💡 <i>Бесплатно предоставляется 1 слот. Дополнительный слот стоит всего 2 Telegram Stars.</i>"
        )
    else:
        text = (
            "🎯 <b>Keyword Tracking</b>\n\n"
            f"📡 <b>Status:</b> {status_text_en}\n"
            f"🔐 <b>Account:</b> {acc_text_en}\n"
            f"📊 <b>Your slots:</b> {used} of {allowed} used.\n\n"
            "You can link a group or channel to track signals based on your keywords, and start or stop monitoring at any time.\n\n"
            "💡 <i>1 slot is provided for free. An extra slot costs only 2 Telegram Stars.</i>"
        )

    kb = personal_tracking_menu_kb(user_id=user_id, is_active=is_active, lang=lang)
    return text, kb


@router.callback_query(F.data == "menu_personal_tracking")
async def cmd_personal_tracking_main(callback: CallbackQuery, state: FSMContext):
    """
    Главный экран "Персональное отслеживание ключевых слов".

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    try:
        user_id = callback.from_user.id
        logger.info(
            f"Пользователь {callback.from_user.last_name} {callback.from_user.first_name} {callback.from_user.username} {user_id} перешел в единое меню 🎯 Отслеживание")
        user_lang = determines_user_language(message_or_callback=user_id)
        await state.clear()
        text, kb = get_personal_tracking_text_and_kb(user_id=user_id, lang=user_lang)
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=kb,
                parse_mode="HTML"
            )
        except Exception:
            await callback.message.answer(
                text=text,
                reply_markup=kb,
                parse_mode="HTML"
            )
        await callback.answer()
    except Exception as e:
        logger.exception(e)


@router.callback_query(F.data == "pt_add_tracking")
async def cb_add_tracking(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает добавление новой группы для персонального отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    allowed = get_user_allowed_slots(callback.from_user.id)
    used = get_user_used_slots(callback.from_user.id)

    # Проверка лимита: при использовании бесплатного аккаунта от админа разрешена только 1 группа
    pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == callback.from_user.id)
    is_shared = bool(pt_rec and pt_rec.shared_account and not pt_rec.personal_account)
    if is_shared and used >= 1:
        alert_msg = (
            "⚠️ Вы используете бесплатный аккаунт от администратора. В этом режиме можно отслеживать только 1 группу. Подключите личный аккаунт для добавления других групп."
            if user_lang == "ru"
            else "⚠️ You are using the admin's free account. In this mode, only 1 group can be tracked. Please connect a personal account to track more groups."
        )
        await callback.answer(alert_msg, show_alert=True)
        return

    # Если все слоты уже использовались, то предлагаем пользователю купить дополнительные слоты для групп
    if used >= allowed:
        await callback.answer(t("pt_no_slots_alert", lang=user_lang), show_alert=True)
        return

    # Сначала устанавливаем состояние
    await state.set_state(PersonalTrackingState.waiting_for_target_link)
    # Потом отправляем инструкцию
    await callback.message.edit_text(
        t("pt_ask_link", lang=user_lang),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [back_button(user_lang, callback_data="menu_personal_tracking")]
            ]
        ),
        parse_mode="HTML"
    )
    # И только потом подтверждаем callback (чтобы убрать «часики»)
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_target_link)
async def process_target_link_input(message: Message, state: FSMContext):
    """
    Обрабатывает ввод ссылки или юзернейма группы для персонального отслеживания.

    :param message: (Message) Объект входящего сообщения Telegram со ссылкой.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    target_input = message.text.strip()
    # Проверяем формат ввода (ссылки либо начинается на http(s))
    if not target_input.startswith("http") and not target_input.startswith("@"):
        await message.answer(
            t("pt_invalid_link", lang=user_lang),
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [back_button(user_lang, callback_data="menu_personal_tracking")]
                ]
            )
        )
        return

    status_msg = await message.answer(
        text=t("pt_checking_group", lang=user_lang),
        parse_mode="HTML"
    )

    success, err_msg, invite_link, chat_id, *rest = await connect_target_and_create_group(target_input,
                                                                                          message.from_user.id)
    if not success:
        await status_msg.edit_text(
            f"❌ {err_msg}",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [back_button(user_lang, callback_data="menu_personal_tracking")]
                ]
            )
        )
        await state.clear()
        return

    target_id = rest[0] if rest else None
    target_name = rest[1] if len(rest) > 1 else ""

    await state.update_data(
        target_link=target_input,
        invite_link=invite_link,
        created_group_id=chat_id,
        target_peer_id=target_id,
        target_name=target_name
    )

    await state.set_state(PersonalTrackingState.waiting_for_keywords)
    step2_text = t(
        "pt_step2_created",
        lang=user_lang,
        link=invite_link,
        bot_name=username_bot
    )
    await status_msg.edit_text(
        step2_text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [back_button(user_lang, callback_data="menu_personal_tracking")]
            ]
        ),
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(PersonalTrackingState.waiting_for_keywords)
async def process_keywords_input(message: Message, state: FSMContext):
    """
    Обрабатывает ввод ключевых слов и сохраняет персональное отслеживание.

    :param message: (Message) Объект входящего сообщения Telegram с ключевыми словами.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    data = await state.get_data()

    target_link = data.get("target_link")
    invite_link = data.get("invite_link")
    created_group_id = data.get("created_group_id")
    target_peer_id = data.get("target_peer_id")
    target_name = data.get("target_name") or ""

    keywords_text = message.text.strip()
    keywords_list = [
        keyword.strip()
        for keyword in keywords_text.replace("\n", ",").split(',')
        if keyword.strip()
    ]

    # Безопасно добавляет список ключевых слов, пропуская дубликаты.
    add_user_keywords(user_id=message.from_user.id, keywords=keywords_list)

    # Сохраняем целевой канал в UsersGroups с ID группы и названием
    if target_link:
        add_user_group(
            user_id=message.from_user.id,
            group=[target_link],
            user_username=message.from_user.username or "",
            user_firstname=message.from_user.first_name or "",
            id_group=target_peer_id,
            name_group=target_name
        )

    # Обновляем профиль пользователя UsersPersonalTrackings (привязку группы уведомлений)
    pt_rec, _ = UsersPersonalTrackings.get_or_create(
        user_id=message.from_user.id,
        defaults={
            "user_username": message.from_user.username or "",
            "user_firstname": message.from_user.first_name or "",
            "language": user_lang
        }
    )
    if invite_link:
        pt_rec.created_group_link = invite_link
    if created_group_id:
        pt_rec.created_group_id = created_group_id
    pt_rec.last_changed_at = datetime.now()
    pt_rec.save()

    await state.clear()

    saved_text = t(
        "pt_configured_success",
        lang=user_lang,
        target=target_link,
        keywords=keywords_text,
        link=invite_link
    )

    success_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_to_tracking_menu", lang=user_lang),
                    callback_data="menu_personal_tracking"
                )
            ],
            [
                back_button(user_lang, callback_data="menu_personal_tracking"),
                InlineKeyboardButton(
                    text=t("btn_main_menu", lang=user_lang),
                    callback_data="menu_main"
                )
            ]
        ]
    )

    await message.answer(
        saved_text,
        reply_markup=success_kb,
        parse_mode="HTML"
    )

    # Автоматически запускаем фоновое отслеживание, если еще не запущено
    if str(message.from_user.id) not in active_clients:
        try:
            asyncio.create_task(
                filter_messages(
                    message=message,
                    user_id=message.from_user.id
                )
            )
            logger.info(f"🚀 Фоновое отслеживание автоматически запущено для user_id={message.from_user.id}")
        except Exception as e:
            logger.error(f"Не удалось автоматически запустить отслеживание: {e}")


# ==================== ОПЛАТА ЗВЕЗДАМИ TELEGRAM (STARS) ====================

@router.callback_query(F.data == "pt_buy_slot")
async def cb_buy_slot(callback: CallbackQuery):
    """
    Отправляет инвойс для покупки дополнительного слота отслеживания за Telegram Stars.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    title = "⭐ +1 Слот отслеживания" if user_lang == "ru" else "⭐ +1 Tracking Slot"
    description = "Позволяет отслеживать еще 1 группу/канал персонально" if user_lang == "ru" else "Allows tracking 1 more group/channel personally"
    label = "Дополнительный слот отслеживания" if user_lang == "ru" else "Extra tracking slot"
    prices = [LabeledPrice(label=label, amount=2)]

    invoice_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Оплатить 2 XTR" if user_lang == "ru" else "⭐ Pay 2 XTR",
                    pay=True
                )
            ],
            [
                back_button(user_lang, callback_data="menu_personal_tracking")
            ]
        ]
    )

    await bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=f"personal_tracking_slot_{user_id}",
        currency="XTR",
        prices=prices,
        reply_markup=invoice_kb
    )
    await callback.answer()


@router.pre_checkout_query(F.invoice_payload.startswith("personal_tracking_slot_"))
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """
    Подтверждает предварительный платеж за покупку слота персонального отслеживания.

    :param pre_checkout_query: (PreCheckoutQuery) Объект предварительного запроса платежа.
    """
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """
    Обрабатывает успешную оплату слота персонального отслеживания.

    :param message: (Message) Входящее сообщение Telegram с информацией об оплате.
    """
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    payload = message.successful_payment.invoice_payload
    if payload.startswith("personal_tracking_slot_"):
        user_id = message.from_user.id
        pt_rec, _ = UsersPersonalTrackings.get_or_create(user_id=user_id)
        pt_rec.stars = (pt_rec.stars or 0) + 2
        pt_rec.save()

        allowed = get_user_allowed_slots(user_id)
        paid_text = (
            f"🎉 <b>Оплата 2 Telegram Stars прошла успешно!</b>\n\n"
            f"Вам добавлен +1 слот отслеживания. Теперь доступно слотов: <b>{allowed}</b>."
        ) if user_lang == "ru" else (
            f"🎉 <b>Payment of 2 Telegram Stars was successful!</b>\n\n"
            f"+1 tracking slot added to your account. Slots now available: <b>{allowed}</b>."
        )
        _, kb = get_personal_tracking_text_and_kb(user_id=user_id, lang=user_lang)
        await message.answer(
            paid_text,
            reply_markup=kb,
            parse_mode="HTML"
        )


# ==================== СПИСОК И СТАТИСТИКА ====================

@router.callback_query(F.data == "pt_list_tracking")
async def cb_list_tracking(callback: CallbackQuery):
    """
    Отображает список каналов и групп отслеживания пользователя.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    records = list(
        UsersGroups.select().where(UsersGroups.user_id == user_id).order_by(UsersGroups.date_added.desc())
    )

    if not records:
        await callback.message.answer(
            t("pt_no_active_trackings", lang=user_lang),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=t("btn_pt_add_tracking", lang=user_lang), callback_data="pt_add_tracking")],
                [back_button(user_lang, callback_data="menu_personal_tracking")]
            ]), parse_mode="HTML"
        )
        await callback.answer()
        return

    # Получаем ключевые слова пользователя и ссылку на группу уведомлений
    user_kws = list(UsersKeywords.select().where(UsersKeywords.user_id == user_id))
    kw_str = ", ".join([k.user_keyword for k in user_kws]) if user_kws else "—"

    group_link = await ensure_permanent_group_invite_link(user_id)

    text = "📋 <b>Ваши персональные отслеживания:</b>\n\n" if user_lang == "ru" else "📋 <b>Your personal trackings:</b>\n\n"

    for idx, r in enumerate(records, start=1):
        can_change, hours_left = can_user_change_tracking(r)

        if user_lang == "ru":
            status_limit = (
                "✅ Доступно изменение"
                if can_change
                else f"⏳ Изменение через {hours_left} ч."
            )
            kw_label = "Ключевые слова"
            grp_label = "Группа"
            link_label = "Ссылка"
            stat_label = "Статус"
        else:
            status_limit = (
                "✅ Modification available"
                if can_change
                else f"⏳ Modification in {hours_left} h."
            )
            kw_label = "Keywords"
            grp_label = "Group"
            link_label = "Link"
            stat_label = "Status"

        channel_name = escape(str(r.username_group or r.name_group or "—"))
        text += (
            f"<b>{idx}. {channel_name}</b>\n"
            f"🔑 {kw_label}: <code>{escape(kw_str)}</code>\n"
        )
        if group_link:
            text += f"🔗 {grp_label}: <a href='{group_link}'>{link_label}</a>\n"
        text += f"{stat_label}: {status_limit}\n\n"

    await callback.message.answer(
        text,
        reply_markup=tracking_list_keyboard(records, lang=user_lang, group_link=group_link),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pt_edit_"))
async def cb_edit_tracking_item(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор группы персонального отслеживания для редактирования.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    rec_id = int(callback.data.split("_")[2])
    rec = UsersGroups.get_or_none(UsersGroups.id == rec_id)

    if not rec:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    can_change, hours_left = can_user_change_tracking(rec)
    if not can_change:
        cooldown_msg = f"⚠️ Изменение запрещено! Вы можете изменять отслеживание не чаще 1 раза в 24 часа. Осталось: {hours_left} ч." if user_lang == "ru" else f"⚠️ Editing cooldown! You can modify tracking once every 24 hours. Remaining: {hours_left} h."
        await callback.answer(
            cooldown_msg,
            show_alert=True
        )
        return

    await state.set_state(PersonalTrackingState.editing_slot_link)
    await state.update_data(edit_rec_id=rec_id)
    channel_name = rec.username_group or ""
    edit_header = (
        f"⚙️ <b>Редактирование отслеживания #{rec_id}</b>\n\n"
        f"Отправьте НОВУЮ ссылку на группу/канал (или текущую: <code>{channel_name}</code>):"
    ) if user_lang == "ru" else (
        f"⚙️ <b>Edit Tracking #{rec_id}</b>\n\n"
        f"Send a NEW link to group/channel (or current: <code>{channel_name}</code>):"
    )
    await callback.message.answer(
        edit_header,
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PersonalTrackingState.editing_slot_link)
async def process_edit_link(message: Message, state: FSMContext):
    """
    Обрабатывает изменение ссылки целевой группы персонального отслеживания.

    :param message: (Message) Объект входящего сообщения Telegram со ссылкой.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    new_target = message.text.strip()
    data = await state.get_data()
    rec_id = data.get("edit_rec_id")

    rec = UsersGroups.get_or_none(UsersGroups.id == rec_id)
    if not rec:
        await message.answer(t("pt_record_error", lang=user_lang))
        await state.clear()
        return

    status_msg = await message.answer(t("pt_updating_group", lang=user_lang), parse_mode="HTML")
    success, err_msg, invite_link, chat_id, *rest = await connect_target_and_create_group(new_target,
                                                                                          message.from_user.id)

    if not success:
        await status_msg.edit_text(f"❌ {err_msg}")
        await state.clear()
        return

    rec.username_group = new_target
    if rest and rest[0]:
        rec.id_group = rest[0]
    if len(rest) > 1 and rest[1]:
        rec.name_group = rest[1]
    rec.date_added = datetime.now()
    rec.save()

    # Обновляем профиль пользователя UsersPersonalTrackings, если создана новая группа
    if invite_link and chat_id:
        pt_rec, _ = UsersPersonalTrackings.get_or_create(user_id=message.from_user.id)
        pt_rec.created_group_link = invite_link
        pt_rec.created_group_id = chat_id
        pt_rec.last_changed_at = datetime.now()
        pt_rec.save()

    await state.set_state(PersonalTrackingState.editing_slot_keywords)
    await status_msg.edit_text(t("pt_ask_keywords", lang=user_lang))


@router.message(PersonalTrackingState.editing_slot_keywords)
async def process_edit_keywords(message: Message, state: FSMContext):
    """
    Обрабатывает изменение ключевых слов персонального отслеживания.

    :param message: (Message) Объект входящего сообщения Telegram с ключевыми словами.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    new_keywords_raw = message.text.strip()
    new_keywords = [k.strip() for k in new_keywords_raw.replace("\n", ",").split(",") if k.strip()]

    if new_keywords:
        add_user_keywords(user_id=message.from_user.id, keywords=new_keywords)

    pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == message.from_user.id)
    if pt_rec:
        pt_rec.last_changed_at = datetime.now()
        pt_rec.save()

    await state.clear()
    await message.answer(t("pt_updated_success", lang=user_lang), parse_mode="HTML")


@router.callback_query(F.data == "pt_stats")
async def cb_stats(callback: CallbackQuery):
    """
    Отображает административную статистику персонального отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    total_tracking_users = UsersGroups.select(UsersGroups.user_id).distinct().count()
    total_active_slots = UsersGroups.select().count()

    await callback.message.answer(
        t("pt_stats_msg", lang=user_lang, users=total_tracking_users, trackings=total_active_slots),
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== ОПУБЛИКОВАНИЕ УВЕДОМЛЕНИЙ БОТОМ ====================

async def send_personal_tracking_alert(user_id: int, matched_keyword: str, message_text: str, message_link: str, target_group_id: int | None = None, account_title: str = ""):
    """
    Отправляет уведомление бота в персональную группу пользователя при нахождении ключевого слова
    (с поддержкой конкретной технической группы кампании и тега темы).

    :param user_id: (int) ID пользователя Telegram.
    :param matched_keyword: (str) Найденное ключевое слово.
    :param message_text: (str) Текст сообщения из отслеживаемой группы.
    :param message_link: (str) Прямая ссылка на сообщение в Telegram.
    :param target_group_id: (int | None) ID конкретной технической группы для данного аккаунта/темы.
    :param account_title: (str) Название кампании (например, "Диваны", "Холодильники").
    """
    user_lang = determines_user_language(message_or_callback=user_id)
    dest_chat_id = target_group_id
    if not dest_chat_id:
        pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
        if pt_rec:
            dest_chat_id = pt_rec.created_group_id

    if dest_chat_id:
        alert_text = t(
            "pt_alert_message",
            lang=user_lang,
            keyword=matched_keyword,
            text=message_text[:500],
            link=message_link
        )
        if account_title:
            alert_text = f"🏷️ <b>[{account_title}]</b>\n{alert_text}"
        try:
            await bot.send_message(
                chat_id=dest_chat_id,
                text=alert_text,
                parse_mode="HTML",
                disable_web_page_preview=False
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить алерт в группу {dest_chat_id}: {e}")


async def execute_sign_in(callback: CallbackQuery, state: FSMContext, code: str):
    """
    Выполнение входа Telethon по коду подтверждения.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    :param code: (str) 5-значный код подтверждения авторизации.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    data = await state.get_data()
    phone = data.get("phone_number")
    phone_code_hash = data.get("phone_code_hash")
    session_str = data.get("session_str")

    client = TelegramClient(
        StringSession(session_str),
        api_id=int(API_ID) if API_ID else 0,
        api_hash=str(API_HASH) if API_HASH else "",
        device_model=mobile_device["device_model"],
        system_version=mobile_device["system_version"],
        app_version=mobile_device["app_version"],
        lang_code=mobile_device["lang_code"],
        system_lang_code=mobile_device["system_lang_code"]
    )

    try:
        await client.connect()
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        # Получаем информацию о клиенте
        account_info = await get_account_info(client)
        final_session = client.session.save()
        await client.disconnect()

        """
        Сохраняем авторизованную сессию в БД (Если это администратор, то данные будем записывать для всех пользователей, 
        что бы пользовались бесплатно или расширяли свой пакет)
        """

        if int(user_id) == int(ADMIN_USER_ID):
            # Сохраняем аккаунт в общую базу бесплатных аккаунтов
            write_account_to_db_free(
                session_string=final_session,  # Стринг сессия Telegram
                phone_number=account_info.get("phone") or ""  # Номер телефона подключаемого аккаунта
            )
        else:
            # Сохраняем аккаунт в персональную базу пользователя
            write_account_to_user_table(
                user_id=user_id,
                session_string=final_session,
                phone_number=account_info.get("phone") or "",
                user_username=callback.from_user.username or "",
                user_firstname=callback.from_user.first_name or ""
            )
            write_account_to_db(
                session_string=final_session,  # Стринг сессия Telegram
                user_id=user_id,  # ID пользователя Telegram
            )
            # Синхронизируем новый аккаунт с отслеживанием и группой результатов
            await sync_and_promote_account_for_tracking(user_id=user_id, session_string=final_session)

            # Автоматически запускаем отслеживание, если у пользователя настроены группы и ключевые слова
            has_groups = UsersGroups.select().where(UsersGroups.user_id == user_id).exists()
            has_keywords = UsersKeywords.select().where(UsersKeywords.user_id == user_id).exists()
            if has_groups and has_keywords:
                if str(user_id) in active_clients:
                    await stop_tracking(user_id=user_id, message=None)
                try:
                    create_background_task(
                        filter_messages(
                            message=callback.message,
                            user_id=user_id,
                            notify=True
                        ),
                        name=f"auth_track_{user_id}"
                    )
                    logger.info(
                        f"🚀 Фоновое отслеживание автоматически запущено для user_id={user_id} после авторизации")
                except Exception as e:
                    logger.error(f"Не удалось запустить отслеживание после авторизации: {e}")

        await state.clear()
        await callback.message.edit_text(
            t("pt_auth_success", lang=user_lang,
              name=f"{account_info.get("first_name") or ""} {account_info.get("last_name") or ""}".strip(),
              phone=str(account_info.get("phone") or ""),
              tg_id=str(account_info.get("id") or "")
              ),
            parse_mode="HTML"
        )
    except PhoneCodeInvalidError:
        await callback.answer(t("pt_invalid_code_alert", lang=user_lang), show_alert=True)
        await state.update_data(current_code="")
        try:
            await callback.message.edit_text(
                t("pt_auth_code_invalid_screen", lang=user_lang, phone=str(phone or "")),
                reply_markup=emoji_code_keypad_kb(lang=user_lang),
                parse_mode="HTML"
            )
        except Exception:
            pass
    except PhoneCodeExpiredError:
        await callback.answer(t("pt_code_expired_alert", lang=user_lang), show_alert=True)
        await state.clear()
    except SessionPasswordNeededError:
        # У пользователя включен 2FA пароль!
        updated_session = client.session.save()
        try:
            await client.disconnect()
        except Exception:
            pass

        await state.update_data(session_str=updated_session)
        await state.set_state(PersonalTrackingState.waiting_for_2fa_password)

        try:
            await callback.answer()
        except Exception:
            pass

        try:
            await callback.message.edit_text(
                t("pt_auth_2fa_prompt", lang=user_lang),
                parse_mode="HTML"
            )
        except Exception:
            pass
    except Exception as e:
        logger.exception(f"❌ Ошибка входа Telethon по коду: {e}")
        # await callback.answer(t("pt_login_error_alert", lang=user_lang, error=str(e)), show_alert=True)
        # try:
        await client.disconnect()
        # except Exception:
        #     pass


@router.message(PersonalTrackingState.waiting_for_2fa_password)
async def process_2fa_password_input(message: Message, state: FSMContext):
    """
    Обработка ввода облачного пароля двухфакторной аутентификации (2FA).

    :param message: (Message) Входящее текстовое сообщение с 2FA паролем.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    password = message.text.strip()
    data = await state.get_data()
    session_str = data.get("session_str")

    status_msg = await message.answer(t("pt_checking_2fa", lang=user_lang), parse_mode="HTML")

    client = TelegramClient(
        StringSession(session_str),
        api_id=int(API_ID) if API_ID else 0,
        api_hash=str(API_HASH) if API_HASH else "",
        device_model=mobile_device["device_model"],
        system_version=mobile_device["system_version"],
        app_version=mobile_device["app_version"],
        lang_code=mobile_device["lang_code"],
        system_lang_code=mobile_device["system_lang_code"]
    )

    try:
        await client.connect()
        await client.sign_in(password=password)
        # Получаем информацию о клиенте
        account_info = await get_account_info(client)
        final_session = client.session.save()
        await client.disconnect()

        if int(message.from_user.id) == int(ADMIN_USER_ID):
            # Сохраняем аккаунт в общую базу бесплатных аккаунтов
            write_account_to_db_free(
                session_string=final_session,  # Стринг сессия Telegram
                phone_number=account_info.get("phone") or ""  # Номер телефона подключаемого аккаунта
            )
        else:
            # Сохраняем аккаунт в персональную базу пользователя
            write_account_to_user_table(
                user_id=message.from_user.id,
                session_string=final_session,
                phone_number=account_info.get("phone") or "",
                user_username=message.from_user.username or "",
                user_firstname=message.from_user.first_name or ""
            )
            write_account_to_db(
                session_string=final_session,  # Стринг сессия Telegram
                user_id=message.from_user.id,  # ID пользователя Telegram
            )
            # Синхронизируем новый аккаунт с отслеживанием и группой результатов
            await sync_and_promote_account_for_tracking(user_id=message.from_user.id, session_string=final_session)

            # Автоматически запускаем отслеживание, если у пользователя настроены группы и ключевые слова
            has_groups = UsersGroups.select().where(UsersGroups.user_id == message.from_user.id).exists()
            has_keywords = UsersKeywords.select().where(UsersKeywords.user_id == message.from_user.id).exists()
            if has_groups and has_keywords:
                if str(message.from_user.id) in active_clients:
                    await stop_tracking(user_id=message.from_user.id, message=None)
                try:
                    create_background_task(
                        filter_messages(
                            message=message,
                            user_id=message.from_user.id,
                            notify=True
                        ),
                        name=f"2fa_track_{message.from_user.id}"
                    )
                    logger.info(
                        f"🚀 Фоновое отслеживание автоматически запущено для user_id={message.from_user.id} после ввода 2FA")
                except Exception as e:
                    logger.error(f"Не удалось запустить отслеживание после 2FA: {e}")

        await state.clear()
        first_name = account_info.get("first_name") or ""
        last_name = account_info.get("last_name") or ""
        full_name = f"{first_name} {last_name}".strip()
        auth_2fa_done = t(
            "pt_auth_2fa_success",
            lang=user_lang,
            name=full_name,
            phone=str(account_info.get("phone") or ""),
            tg_id=str(account_info.get("id") or "")
        )
        await status_msg.edit_text(
            auth_2fa_done,
            parse_mode="HTML"
        )
    except PasswordHashInvalidError:
        inv_2fa = t("pt_auth_2fa_invalid", lang=user_lang)
        await status_msg.edit_text(inv_2fa, parse_mode="HTML")
    except Exception as e:
        logger.exception(f"❌ Ошибка 2FA авторизации: {e}")
        # await status_msg.edit_text(t("pt_auth_error", lang=user_lang, error=str(e)))
        # try:
        await client.disconnect()
        # except Exception:
        #     pass


@router.callback_query(F.data == "pt_cancel_auth")
async def cb_cancel_auth(callback: CallbackQuery, state: FSMContext):
    """
    Отмена процедуры авторизации Telegram-аккаунта.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(t("pt_auth_cancelled", lang=user_lang), parse_mode="HTML")
    await callback.answer()


# ==================== МУЛЬТИ-АККАУНТЫ И КАМПАНИИ (ДИВАНЫ, ХОЛОДИЛЬНИКИ) ====================

@router.callback_query(F.data == "pt_accounts_list")
async def cb_accounts_list(callback: CallbackQuery, state: FSMContext):
    """
    Отображает список всех подключенных аккаунтов / кампаний пользователя.
    """
    await state.clear()
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    accounts = get_user_accounts_list(user_id)

    if not accounts:
        text = (
            "📱 <b>Ваши кампании и аккаунты</b>\n\n"
            "У вас пока нет подключенных личных аккаунтов.\n"
            "Подключите аккаунт через файл <code>.session</code> или номер телефона, чтобы настроить индивидуальные кампании (например, «Диваны», «Холодильники»)."
            if user_lang == "ru"
            else "📱 <b>Your Campaigns & Accounts</b>\n\nYou don't have any personal accounts connected yet.\nConnect an account via <code>.session</code> or phone number to set up individual campaigns (e.g. «Sofas», «Refrigerators»)."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=t("connect_account_button", lang=user_lang), callback_data="account_connect_menu")],
            [back_button(user_lang, callback_data="menu_personal_tracking")]
        ])
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
        return

    buttons = []
    text_lines = [
        "📱 <b>Ваши кампании и аккаунты</b>\n\n"
        "Выберите нужный аккаунт для настройки отдельной тех-группы, ключевых слов и списка чатов:\n"
        if user_lang == "ru"
        else "📱 <b>Your Campaigns & Accounts</b>\n\nSelect an account to configure its technical group, keywords, and chats:\n"
    ]

    for acc in accounts:
        is_active = f"{user_id}_{acc.id}" in active_clients
        status_ico = "🟢" if is_active else "🔴"
        title = acc.account_title or f"Аккаунт {acc.phone_number_session_string or acc.id}"
        phone = acc.phone_number_session_string or "без номера"

        text_lines.append(f"{status_ico} <b>{title}</b> ({phone})")
        btn_text = f"{status_ico} {title}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"pt_acc_{acc.id}")])

    text_lines.append(
        "\n💡 <i>Каждый аккаунт может мониторить свою нишу (например, один — диваны, другой — холодильники) и отправлять сигналы в свою тех-группу.</i>"
        if user_lang == "ru"
        else "\n💡 <i>Each account can monitor its own niche (e.g., one for sofas, another for refrigerators) and forward alerts to its own tech group.</i>"
    )

    buttons.append([
        InlineKeyboardButton(text=t("btn_pt_start_all", lang=user_lang), callback_data="pt_start_all_accs"),
        InlineKeyboardButton(text=t("btn_pt_stop_all", lang=user_lang), callback_data="pt_stop_all_accs")
    ])
    buttons.append([
        InlineKeyboardButton(text=t("connect_account_button", lang=user_lang), callback_data="account_connect_menu")
    ])
    buttons.append([back_button(user_lang, callback_data="menu_personal_tracking")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await callback.message.edit_text("\n".join(text_lines), reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer("\n".join(text_lines), reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("pt_acc_"))
async def cb_account_details(callback: CallbackQuery, state: FSMContext):
    """
    Детальная карточка управления конкретным аккаунтом/кампанией (диваны, холодильники).
    """
    await state.clear()
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_acc_", ""))
    acc = get_account_by_id(acc_id)

    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    is_running = f"{user_id}_{acc.id}" in active_clients
    status_str = "🟢 <b>Активно</b>" if is_running else "🔴 <b>Остановлено</b>"
    if user_lang != "ru":
        status_str = "🟢 <b>Active</b>" if is_running else "🔴 <b>Stopped</b>"

    title = acc.account_title or f"Аккаунт {acc.phone_number_session_string or acc.id}"
    phone = acc.phone_number_session_string or "без номера"

    # Считаем слова именно для этого аккаунта
    kw_list = get_user_keywords(user_id=user_id, user_session_string=acc.user_session_string)
    kw_count = len(kw_list)

    # Считаем группы
    groups_count = UsersGroups.select().where(
        (UsersGroups.user_id == user_id) &
        ((UsersGroups.user_session_string == acc.user_session_string) | (UsersGroups.user_session_string == '') | (UsersGroups.user_session_string.is_null()))
    ).count()

    all_chats_mode = "✅ ВКЛЮЧЕН" if acc.track_all_chats else "❌ ВЫКЛЮЧЕН (по списку)"
    if user_lang != "ru":
        all_chats_mode = "✅ ENABLED" if acc.track_all_chats else "❌ DISABLED (by list)"

    tech_group_display = f"<a href='{acc.target_group_link}'>Перейти в группу</a>" if acc.target_group_link else f"ID: {acc.target_group_id or 'не назначена'}"
    if not acc.target_group_id and not acc.target_group_link:
        pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
        if pt_rec and pt_rec.created_group_id:
            tech_group_display = f"Общая тех-группа (ID: {pt_rec.created_group_id})"

    card_text = t(
        "pt_acc_card",
        lang=user_lang,
        title=title,
        phone=phone,
        status=status_str,
        tech_group=tech_group_display,
        keywords_count=kw_count,
        groups_count=groups_count,
        all_chats_mode=all_chats_mode
    )

    toggle_btn = (
        InlineKeyboardButton(text=t("btn_pt_stop_acc", lang=user_lang), callback_data=f"pt_toggle_run_{acc.id}")
        if is_running
        else InlineKeyboardButton(text=t("btn_pt_start_acc", lang=user_lang), callback_data=f"pt_toggle_run_{acc.id}")
    )

    all_chats_btn_text = t("btn_pt_toggle_all_chats", lang=user_lang, status="ВЫКЛ" if acc.track_all_chats else "ВКЛ")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [toggle_btn],
        [
            InlineKeyboardButton(text=t("btn_pt_rename_acc", lang=user_lang), callback_data=f"pt_rename_acc_{acc.id}"),
            InlineKeyboardButton(text=all_chats_btn_text, callback_data=f"pt_toggle_all_chats_{acc.id}")
        ],
        [
            InlineKeyboardButton(text=t("btn_pt_sync_dialogs", lang=user_lang), callback_data=f"pt_sync_dialogs_{acc.id}")
        ],
        [
            InlineKeyboardButton(text=t("btn_pt_acc_keywords", lang=user_lang), callback_data=f"pt_acc_keywords_{acc.id}"),
            InlineKeyboardButton(text=t("btn_pt_acc_groups", lang=user_lang), callback_data="pt_list_tracking")
        ],
        [
            InlineKeyboardButton(text=t("btn_disconnect_account", lang=user_lang), callback_data=f"pt_disconnect_acc_{acc.id}")
        ],
        [
            back_button(user_lang, callback_data="pt_accounts_list")
        ]
    ])

    try:
        await callback.message.edit_text(card_text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(card_text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("pt_toggle_all_chats_"))
async def cb_toggle_all_chats(callback: CallbackQuery, state: FSMContext):
    """
    Переключает режим "Все чаты аккаунта" (отслеживать открытые + закрытые чаты, где состоит аккаунт).
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_toggle_all_chats_", ""))
    acc = get_account_by_id(acc_id)
    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    acc.track_all_chats = not acc.track_all_chats
    acc.save()

    status_str = "ВКЛЮЧЕН" if acc.track_all_chats else "ВЫКЛЮЧЕН"
    await callback.answer(t("pt_toggle_all_chats_done", lang=user_lang, title=acc.account_title or "", status=status_str), show_alert=True)
    await cb_account_details(callback, state)


@router.callback_query(F.data.startswith("pt_rename_acc_"))
async def cb_rename_acc(callback: CallbackQuery, state: FSMContext):
    """
    Запрашивает новое название/тему кампании (например, "Диваны", "Холодильники").
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_rename_acc_", ""))
    acc = get_account_by_id(acc_id)
    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    await state.update_data(editing_account_id=acc_id)
    await state.set_state(PersonalTrackingState.waiting_for_acc_title)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [back_button(user_lang, callback_data=f"pt_acc_{acc_id}")]
    ])
    await callback.message.edit_text(t("pt_ask_rename_acc", lang=user_lang), reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_acc_title)
async def process_rename_acc_input(message: Message, state: FSMContext):
    """
    Сохраняет новое название/тему кампании.
    """
    user_id = message.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    data = await state.get_data()
    acc_id = data.get("editing_account_id")
    await state.clear()

    if not acc_id:
        return

    acc = get_account_by_id(acc_id)
    if acc and acc.user_id == user_id:
        new_title = (message.text or "").strip()
        if new_title:
            acc.account_title = new_title
            acc.save()
            await message.answer(t("pt_acc_renamed", lang=user_lang, title=new_title), parse_mode="HTML")

    # Возвращаемся к карточке аккаунта
    mock_cb = CallbackQuery(
        id="0",
        from_user=message.from_user,
        chat_instance="0",
        message=message,
        data=f"pt_acc_{acc_id}"
    )
    await cb_account_details(mock_cb, state)


@router.callback_query(F.data.startswith("pt_acc_keywords_"))
async def cb_acc_keywords(callback: CallbackQuery, state: FSMContext):
    """
    Запрашивает ввод ключевых слов конкретно для этой кампании.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_acc_keywords_", ""))
    acc = get_account_by_id(acc_id)
    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    await state.update_data(editing_account_id=acc_id)
    await state.set_state(PersonalTrackingState.waiting_for_acc_keywords)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [back_button(user_lang, callback_data=f"pt_acc_{acc_id}")]
    ])
    title = acc.account_title or f"Аккаунт #{acc.id}"
    await callback.message.edit_text(t("pt_ask_acc_keywords", lang=user_lang, title=title), reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_acc_keywords)
async def process_acc_keywords_input(message: Message, state: FSMContext):
    """
    Сохраняет ключевые слова с привязкой к сессии конкретного аккаунта.
    """
    user_id = message.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    data = await state.get_data()
    acc_id = data.get("editing_account_id")
    await state.clear()

    if not acc_id:
        return

    acc = get_account_by_id(acc_id)
    if acc and acc.user_id == user_id:
        raw_text = (message.text or "").strip()
        keywords = [k.strip() for k in raw_text.replace("\n", ",").split(",") if k.strip()]
        add_user_keywords(
            user_id=user_id,
            keywords=keywords,
            user_username=message.from_user.username or "",
            user_firstname=message.from_user.first_name or "",
            user_session_string=acc.user_session_string
        )
        title = acc.account_title or f"Аккаунт #{acc.id}"
        await message.answer(t("pt_acc_keywords_saved", lang=user_lang, title=title, count=len(keywords)), parse_mode="HTML")

    mock_cb = CallbackQuery(
        id="0",
        from_user=message.from_user,
        chat_instance="0",
        message=message,
        data=f"pt_acc_{acc_id}"
    )
    await cb_account_details(mock_cb, state)


@router.callback_query(F.data.startswith("pt_sync_dialogs_"))
async def cb_sync_dialogs(callback: CallbackQuery, state: FSMContext):
    """
    Сканирует все диалоги аккаунта (включая приватные и закрытые группы из tdata) и синхронизирует их в базу данных.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_sync_dialogs_", ""))
    acc = get_account_by_id(acc_id)
    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    await callback.answer(t("pt_dialogs_syncing", lang=user_lang), show_alert=False)
    status_msg = await callback.message.answer(t("pt_dialogs_syncing", lang=user_lang))

    checker = CheckingAccountsValidity()
    client = await checker.client_connect_string_session(acc.user_session_string)
    if not client:
        await status_msg.edit_text("❌ Не удалось подключить клиент для синхронизации диалогов.")
        return

    try:
        synced = await sync_account_dialogs_to_db(
            client=client,
            user_id=user_id,
            user_session_string=acc.user_session_string,
            user_username=callback.from_user.username or "",
            user_firstname=callback.from_user.first_name or ""
        )
        await client.disconnect()
        await status_msg.edit_text(t("pt_dialogs_synced", lang=user_lang, count=len(synced)), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка синхронизации: {e}")
        try:
            await client.disconnect()
        except Exception:
            pass
        await status_msg.edit_text(f"❌ Ошибка: {e}")

    await asyncio.sleep(1)
    await cb_account_details(callback, state)


@router.callback_query(F.data.startswith("pt_toggle_run_"))
async def cb_toggle_run_acc(callback: CallbackQuery, state: FSMContext):
    """
    Запускает или останавливает мониторинг конкретного аккаунта/кампании.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_toggle_run_", ""))
    acc = get_account_by_id(acc_id)
    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    user_key = f"{user_id}_{acc.id}"
    if user_key in active_clients:
        await stop_tracking(user_id=user_id, message=callback.message, account_id=acc.id)
        await callback.answer(f"🛑 Аккаунт {acc.account_title or acc.id} остановлен", show_alert=False)
    else:
        user_key = f"{user_id}_{acc.id}"
        task = create_background_task(
            filter_messages(
                message=callback.message,
                user_id=user_id,
                notify=True,
                account_id=acc.id
            ),
            name=f"task_{user_key}"
        )
        active_tasks[user_key] = task
        await callback.answer(f"🚀 Аккаунт {acc.account_title or acc.id} запущен", show_alert=False)

    await asyncio.sleep(0.5)
    await cb_account_details(callback, state)


@router.callback_query(F.data.startswith("pt_disconnect_acc_"))
async def cb_disconnect_specific_acc(callback: CallbackQuery, state: FSMContext):
    """
    Отключает и удаляет конкретный аккаунт пользователя.
    """
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)
    acc_id = int(callback.data.replace("pt_disconnect_acc_", ""))
    acc = get_account_by_id(acc_id)
    if not acc or acc.user_id != user_id:
        await callback.answer(t("pt_record_not_found", lang=user_lang), show_alert=True)
        return

    await stop_tracking(user_id=user_id, account_id=acc.id)
    delete_account_by_id(acc.id)
    await callback.answer("✅ Аккаунт отключен", show_alert=True)
    await cb_accounts_list(callback, state)


@router.callback_query(F.data == "pt_start_all_accs")
async def cb_start_all_accs(callback: CallbackQuery, state: FSMContext):
    """
    Запускает мониторинг по всем настроенным аккаунтам пользователя.
    """
    user_id = callback.from_user.id
    create_background_task(
        filter_messages(
            message=callback.message,
            user_id=user_id,
            notify=True
        ),
        name=f"start_all_{user_id}"
    )
    await callback.answer("🚀 Все аккаунты запущены!", show_alert=False)
    await asyncio.sleep(0.5)
    await cb_accounts_list(callback, state)


@router.callback_query(F.data == "pt_stop_all_accs")
async def cb_stop_all_accs(callback: CallbackQuery, state: FSMContext):
    """
    Останавливает мониторинг по всем аккаунтам пользователя.
    """
    user_id = callback.from_user.id
    await stop_tracking(user_id=user_id, message=callback.message)
    await callback.answer("🛑 Все аккаунты остановлены!", show_alert=False)
    await asyncio.sleep(0.5)
    await cb_accounts_list(callback, state)
