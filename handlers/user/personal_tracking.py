import random
from datetime import datetime
from html import escape

import telethon.utils as utils
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, LabeledPrice, Message, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, PasswordHashInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError, SessionPasswordNeededError,
    UsernameNotOccupiedError, UsernameInvalidError, ChannelPrivateError, UserRestrictedError, ChannelsTooMuchError
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, CreateChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChatAdminRights

from account_manager.auth import CheckingAccountsValidity, get_account_info
from account_manager.parser import active_clients
from core.config import API_ID, API_HASH, mobile_device, ADMIN_USER_ID
from database.account_free import write_account_to_db_free

from database.users_accounts import getting_account, write_account_to_user_table
from database.users_groups import UsersGroups, add_user_group
from database.users_keywords import add_user_keywords, UsersKeywords
from database.users_personal_trackings import get_user_accounts, UsersPersonalTrackings, write_account_to_db
from handlers.user_language import determines_user_language
from keyboards.keyboards import (
    personal_tracking_menu_kb, tracking_list_keyboard, emoji_code_keypad_kb, back_button
)
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
            candidate_sessions.append((acc["session_string"], "личный"))

    # 2. Общие аккаунты из пула администратора (перемешиваем для распределения нагрузки)
    shared_sessions = getting_account()
    random.shuffle(shared_sessions)
    for s in shared_sessions:
        candidate_sessions.append((s, "общий"))

    if not candidate_sessions:
        return False, "⚠️ Нет доступных рабочих сессий для поиска. Попробуйте позже.", None, None

    max_attempts = min(5, len(candidate_sessions))
    last_restriction_error = None

    for attempt_idx in range(max_attempts):
        session_str, acc_type = candidate_sessions[attempt_idx]
        client: TelegramClient | None = await checker.client_connect_string_session(session_str)
        if not client:
            continue

        try:
            # Получаем сущность отслеживаемого объекта
            entity = await client.get_entity(clean_target)

            # Проверяем и подписываемся на целевую группу/канал
            try:
                await client(JoinChannelRequest(channel=entity))
                logger.info(f"✅ Сессия Telethon ({acc_type}) подписалась на целевой объект {clean_target}")
            except Exception as join_err:
                logger.debug(f"Уведомление при подписке на {clean_target}: {join_err}")

            # Создаем приватную супергруппу для отправки найденных сообщений
            target_title = getattr(entity, 'title', clean_target)[:20]
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

            # Экспортируем ссылку-приглашение в созданную группу
            invite_export = await client(ExportChatInviteRequest(peer=new_chat))
            invite_link = invite_export.link

            await client.disconnect()
            return True, "Успешно", invite_link, chat_id

        except (UsernameNotOccupiedError, UsernameInvalidError, ValueError) as e:
            logger.warning(f"⚠️ Целевая группа/канал не существует или неверный юзернейм ({target_input}): {e}")
            try:
                await client.disconnect()
            except Exception:
                pass
            return False, "Указанная группа или канал не существует. Проверьте правильность ссылки/юзернейма.", None, None

        except ChannelPrivateError:
            logger.warning(f"⚠️ Целевая группа/канал {target_input} приватная или доступ ограничен")
            try:
                await client.disconnect()
            except Exception:
                pass
            return False, "Указанная группа является приватной или к ней нет доступа.", None, None

        except (UserRestrictedError, ChannelsTooMuchError, FloodWaitError) as re:
            logger.warning(
                f"⚠️ Аккаунт {attempt_idx + 1}/{max_attempts} ({acc_type}) имеет ограничение Telegram: {re}. Пробуем следующий аккаунт..."
            )
            last_restriction_error = str(re)
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
            return False, f"Ошибка подключения к целевой группе: {e}", None, None

    if last_restriction_error:
        return (
            False,
            "⚠️ Доступные рабочие аккаунты временно ограничены Telegram на создание каналов/групп (спам-репорт или лимит). "
            "Пожалуйста, подключите свой личный аккаунт через меню «🎯 Персональное отслеживание» ➔ «Подключить свой аккаунт» или повторите попытку позже.",
            None,
            None
        )

    return False, "⚠️ Не удалось подключиться к группе через доступные аккаунты. Попробуйте позже.", None, None


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
        await message.answer(t("pt_invalid_link", lang=user_lang))
        return

    status_msg = await message.answer(
        text=t("pt_checking_group", lang=user_lang),
        parse_mode="HTML"
    )

    success, err_msg, invite_link, chat_id = await connect_target_and_create_group(target_input, message.from_user.id)
    if not success:
        await status_msg.edit_text(f"❌ {err_msg}")
        await state.clear()
        return

    await state.update_data(
        target_link=target_input,
        invite_link=invite_link,
        created_group_id=chat_id
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

    keywords_text = message.text.strip()
    keywords_list = [
        keyword.strip()
        for keyword in keywords_text.replace("\n", ",").split(',')
        if keyword.strip()
    ]

    # Безопасно добавляет список ключевых слов, пропуская дубликаты.
    add_user_keywords(user_id=message.from_user.id, keywords=keywords_list)

    # Сохраняем целевой канал в UsersGroups
    if target_link:
        add_user_group(
            user_id=message.from_user.id,
            group=[target_link],
            user_username=message.from_user.username or "",
            user_firstname=message.from_user.first_name or ""
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
    await message.answer(
        saved_text,
        parse_mode="HTML"
    )


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

    await bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=f"personal_tracking_slot_{user_id}",
        currency="XTR",
        prices=prices
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
            ])
        )
        await callback.answer()
        return

    # Получаем ключевые слова пользователя и ссылку на группу уведомлений
    user_kws = list(UsersKeywords.select().where(UsersKeywords.user_id == user_id))
    kw_str = ", ".join([k.user_keyword for k in user_kws]) if user_kws else "—"

    pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    group_link = pt_rec.created_group_link if pt_rec and pt_rec.created_group_link else ""

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
        reply_markup=tracking_list_keyboard(records, lang=user_lang),
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
    success, err_msg, invite_link, chat_id = await connect_target_and_create_group(new_target, message.from_user.id)

    if not success:
        await status_msg.edit_text(f"❌ {err_msg}")
        await state.clear()
        return

    rec.username_group = new_target
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

async def send_personal_tracking_alert(user_id: int, matched_keyword: str, message_text: str, message_link: str):
    """
    Отправляет уведомление бота в персональную группу пользователя при нахождении ключевого слова.

    :param user_id: (int) ID пользователя Telegram.
    :param matched_keyword: (str) Найденное ключевое слово.
    :param message_text: (str) Текст сообщения из отслеживаемой группы.
    :param message_link: (str) Прямая ссылка на сообщение в Telegram.
    """
    user_lang = determines_user_language(message_or_callback=user_id)
    pt_rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    if pt_rec and pt_rec.created_group_id:
        alert_text = t(
            "pt_alert_message",
            lang=user_lang,
            keyword=matched_keyword,
            text=message_text[:500],
            link=message_link
        )
        try:
            await bot.send_message(
                chat_id=pt_rec.created_group_id,
                text=alert_text,
                parse_mode="HTML",
                disable_web_page_preview=False
            )
        except Exception as e:
            logger.warning(f"Не удалось отправить алерт в группу {pt_rec.created_group_id}: {e}")


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
            err_code_text = t("pt_auth_code_invalid_screen", lang=user_lang, phone=str(phone or ""))
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
        await callback.answer(t("pt_login_error_alert", lang=user_lang, error=str(e)), show_alert=True)
        try:
            await client.disconnect()
        except Exception:
            pass


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
        await status_msg.edit_text(t("pt_auth_error", lang=user_lang, error=str(e)))
        try:
            await client.disconnect()
        except Exception:
            pass


@router.callback_query(F.data == "pt_cancel_auth")
async def cb_cancel_auth(callback: CallbackQuery, state: FSMContext):
    """
    Отмена процедуры авторизации Telegram-аккаунта.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(t("pt_auth_cancelled", lang=user_lang))
    await callback.answer()
