from datetime import datetime
from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
)
from loguru import logger
from peewee import AutoField, BigIntegerField, CharField, DateTimeField, IntegerField, Model, TextField, fn
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, PasswordHashInvalidError, PhoneCodeExpiredError, PhoneCodeInvalidError,
    PhoneNumberInvalidError, SessionPasswordNeededError, UsernameNotOccupiedError, UsernameInvalidError,
    ChannelPrivateError
)
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, CreateChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChatAdminRights
import telethon.utils as utils

from account_manager.auth import CheckingAccountsValidity
from core.config import API_ID, API_HASH, mobile_device
from database.database import db, write_account_to_db, User
from keyboards.keyboards import personal_tracking_menu_kb, tracking_list_keyboard, emoji_code_keypad_kb

from system.dispatcher import bot

router = Router(name="personal_tracking")

username_bot = "@Botzzzz_admin_bot"  # Бот администратор, который будет пересылать сообщения по ключевому слову.


# ==================== МОДЕЛИ БАЗЫ ДАННЫХ ====================

class PersonalTracking(Model):
    """Модель базы данных для хранения настроек персонального отслеживания"""
    id = AutoField()
    user_id = BigIntegerField(index=True)
    target_link = CharField()
    created_group_link = CharField(null=True)
    created_group_id = BigIntegerField(null=True)
    keywords = TextField()  # Ключевые слова через запятую
    last_changed_at = DateTimeField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """Метаданные таблицы персонального отслеживания"""
        database = db
        table_name = "personal_tracking"


class PersonalTrackingStats(Model):
    """Модель базы данных для хранения статистики персонального отслеживания"""
    id = AutoField()
    user_id = BigIntegerField(index=True)
    event_type = CharField()  # 'group_connected', 'slot_purchased', 'changed_target'
    stars_amount = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        """Метаданные таблицы статистики персонального отслеживания"""
        database = db
        table_name = "personal_tracking_stats"


def init_personal_tracking_db():
    """Инициализация таблиц для персонального отслеживания"""
    if db.is_closed():
        db.connect(reuse_if_open=True)
    db.create_tables([PersonalTracking, PersonalTrackingStats], safe=True)
    logger.info("✅ Таблицы персонального отслеживания (personal_tracking) готовы.")


init_personal_tracking_db()


# ==================== МАШИНА СОСТОЯНИЙ ====================

class PersonalTrackingState(StatesGroup):
    """Группа состояний FSM для настройки персонального отслеживания"""
    waiting_for_target_link = State()
    waiting_for_keywords = State()
    editing_slot_link = State()
    editing_slot_keywords = State()
    waiting_for_phone_number = State()
    waiting_for_auth_code = State()
    waiting_for_2fa_password = State()


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================

def get_user_allowed_slots(user_id: int) -> int:
    """
    Возвращает количество доступных слотов пользователя (1 бесплатный + купленные)
    :param user_id: ID пользователя в Telegram
    """
    purchased_slots = PersonalTrackingStats.select().where(
        (PersonalTrackingStats.user_id == user_id) &
        (PersonalTrackingStats.event_type == 'slot_purchased')
    ).count()
    return 1 + purchased_slots


def get_user_used_slots(user_id: int) -> int:
    """Возвращает количество задействованных слотов пользователя"""
    return PersonalTracking.select().where(PersonalTracking.user_id == user_id).count()


def can_user_change_tracking(tracking_record: PersonalTracking) -> tuple[bool, float]:
    """Проверяет ограничение на смену группы/ключевых слов (не чаще 1 раза в 24ч)"""
    if not tracking_record or not tracking_record.last_changed_at:
        return True, 0.0

    diff_seconds = (datetime.now() - tracking_record.last_changed_at).total_seconds()
    if diff_seconds >= 86400:  # 24 часа
        return True, 0.0

    hours_left = round((86400 - diff_seconds) / 3600, 1)
    return False, hours_left


async def connect_target_and_create_group(target_input: str, user_id: int):
    """
    1. Подключает рабочую сессию Telethon.
    2. Проверяет подписку на целевую группу/канал (подписывается при необходимости).
    3. Создает приватную группу для сообщений и выгружает ссылку-приглашение.
    """
    # checker = CheckingAccountsValidity()
    client = await CheckingAccountsValidity().start_random_client()
    if not client:
        return False, "⚠️ Нет доступных рабочих сессий для поиска. Попробуйте позже.", None, None

    try:
        # Получаем сущность отслеживаемого объекта
        clean_target = target_input.strip()
        entity = await client.get_entity(clean_target)

        # Проверяем и подписываемся на целевую группу/канал
        try:
            await client(JoinChannelRequest(channel=entity))
            logger.info(f"✅ Сессия Telethon подписалась на целевой объект {clean_target}")
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
        except Exception as e:
            logger.exception(e)
        return False, "Указанная группа или канал не существует. Проверьте правильность ссылки/юзернейма.", None, None
    except ChannelPrivateError:
        logger.warning(f"⚠️ Целевая группа/канал {target_input} приватная или доступ ограничен")
        try:
            await client.disconnect()
        except Exception as e:
            logger.exception(e)
        return False, "Указанная группа является приватной или к ней нет доступа.", None, None
    except Exception as e:
        logger.exception(f"❌ Ошибка Telethon при подключении группы {target_input}: {e}")
        try:
            await client.disconnect()
        except Exception as e:
            logger.exception(e)
        return False, f"Ошибка подключения к целевой группе: {e}", None, None


# ==================== ОБРАБОТЧИКИ (HANDLERS) ====================

"""Меню персонального отслеживания группы / канала на основе ключевых слов пользователя"""


def determines_user_language(message_or_callback):
    """
    Определяет язык пользователя, который выбрал в первый раз, при запуске бота. Данные берем из базы данных data/bot.db
    """
    user = User.get(User.user_id == message_or_callback)
    return user.language if user.language != "unset" else "ru"  # Возвращаем язык пользователя


@router.callback_query(F.data == "menu_personal_tracking")
async def cmd_personal_tracking_main(callback: CallbackQuery, state: FSMContext):
    """Главный экран 🎯 Персональное отслеживание"""
    try:
        logger.info(
            f"Пользователь {callback.from_user.last_name} {callback.from_user.first_name} {callback.from_user.username} {callback.from_user.id} перешел в меню 🎯 Персональное отслеживание")
        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=callback.from_user.id)
        await state.clear()  # Сбрасываем состояние, если осталось у пользователя от других действий
        allowed = get_user_allowed_slots(
            callback.from_user.id
        )  # Возвращает количество доступных слотов пользователя (1 бесплатный + купленные)
        used = get_user_used_slots(callback.from_user.id)  # Возвращает количество задействованных слотов пользователя
        # Текст для пользователя в меню 🎯 Персональное отслеживание
        text = (
            "🎯 <b>Персональное отслеживание ключевых слов</b>\n\n"
            "Вы можете привязать группу или канал для отслеживания сигналов по Вашим ключевым словам.\n\n"
            f"📊 <b>Ваши слоты:</b> {used} из {allowed} занято.\n"
            "💡 <i>Бесплатно предоставляется 1 слот. Дополнительный слот стоит всего 2 Telegram Stars. Или подключите свой аккаунт для отслеживания ключевых сообщений.</i>"
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=personal_tracking_menu_kb(user_id=callback.from_user.id, lang=user_lang),
            parse_mode="HTML"
        )
        await callback.answer()  # обязательно: убирает «часики» загрузки у кнопки
    except Exception as e:
        logger.exception(e)


# @router.callback_query(F.data == "menu_personal_tracking")
# async def cb_personal_tracking_menu(callback: CallbackQuery, state: FSMContext):
#     """Инлайн-вход в главное меню Персонального отслеживания"""
#
#     # Определяем язык пользователя, который пользователь выбрал при старте бота
#     user_lang = determines_user_language(message_or_callback=callback.from_user.id)
#
#     await state.clear()
#     user_id = callback.from_user.id
#     allowed = get_user_allowed_slots(user_id)
#     used = get_user_used_slots(user_id)
#
#     text = (
#         "🎯 <b>Персональное отслеживание ключевых слов</b>\n\n"
#         "Вы можете привязать группу или канал для отслеживания сигналов по Вашим ключевым словам.\n\n"
#         f"📊 <b>Ваши слоты:</b> {used} из {allowed} занято.\n"
#         "💡 <i>Бесплатно предоставляется 1 слот. Дополнительный слот стоит всего 2 Telegram Stars. Или подключите свой аккаунт для отслеживания ключевых сообщений.</i>"
#     )
#
#     try:
#         await callback.message.edit_text(
#             text,
#             reply_markup=personal_tracking_menu_kb(user_id=user_id, lang=user_lang),
#             parse_mode="HTML"
#         )
#     except Exception:
#         await callback.message.answer(
#             text,
#             reply_markup=personal_tracking_menu_kb(user_id=user_id, lang=user_lang),
#             parse_mode="HTML"
#         )
#     await callback.answer()


@router.callback_query(F.data == "pt_add_tracking")
async def cb_add_tracking(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает добавление новой группы для персонального отслеживания (Кнопка (InlineKey): ➕ Добавить отслеживание группы)"""
    # user_id = callback.from_user.id
    allowed = get_user_allowed_slots(callback.from_user.id)
    used = get_user_used_slots(callback.from_user.id)

    if used >= allowed:
        await callback.answer("⚠️ Все слоты задействованы! Докупите дополнительный слот.", show_alert=True)
        return
    # Сначала устанавливаем состояние
    await state.set_state(PersonalTrackingState.waiting_for_target_link)
    # Потом отправляем инструкцию
    await callback.message.edit_text(
        "🔗 <b>Отправьте ссылку или username группы/канала для отслеживания</b>\n\n"
        "Например: <code>https://t.me/python_jobs</code> или <code>@python_jobs</code>",
        parse_mode="HTML"
    )
    # И только потом подтверждаем callback (чтобы убрать «часики»)
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_target_link)
async def process_target_link_input(message: Message, state: FSMContext):
    """Обрабатывает ввод ссылки или юзернейма группы для персонального отслеживания"""
    target_input = message.text.strip()
    if not target_input.startswith("http") and not target_input.startswith("@"):
        await message.answer("⚠️ Пожалуйста, введите корректную ссылку (https://t.me/...) или @username группы/канала.")
        return

    status_msg = await message.answer("🔄 <i>Подключаем рабочую сессию и создаем персональную группу...</i>",
                                      parse_mode="HTML")

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
    await status_msg.edit_text(
        f"✅ <b>Группа создана!</b>\n\n"
        f"1. Перейдите по ссылке и вступите в созданную группу: <a href='{invite_link}'>{invite_link}</a>\n"
        f"<i>(Бот {username_bot} уже назначен администратором группы)</i>\n\n"
        f"<b>Шаг 2:</b> Введите ключевые слова для отслеживания в этой группе (через запятую):\n"
        f"<i>Пример: python, вакансия, удаленка</i>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(PersonalTrackingState.waiting_for_keywords)
async def process_keywords_input(message: Message, state: FSMContext):
    """Обрабатывает ввод ключевых слов и сохраняет персональное отслеживание"""
    keywords_text = message.text.strip()
    data = await state.get_data()

    # user_id = message.from_user.id
    target_link = data.get("target_link")
    invite_link = data.get("invite_link")
    created_group_id = data.get("created_group_id")

    # Сохраняем запись в таблицу personal_tracking
    rec = PersonalTracking.create(
        user_id=message.from_user.id,
        target_link=target_link,
        created_group_link=invite_link,
        created_group_id=created_group_id,
        keywords=keywords_text,
        last_changed_at=datetime.now()
    )

    # Фиксируем статистику подключения группы
    PersonalTrackingStats.create(
        user_id=message.from_user.id,
        event_type="group_connected",
        stars_amount=0
    )

    await state.clear()

    await message.answer(
        f"🎉 <b>Персональное отслеживание успешно настроено!</b>\n\n"
        f"📌 <b>Отслеживаемый объект:</b> {target_link}\n"
        f"🔑 <b>Ключевые слова:</b> {keywords_text}\n"
        f"🔗 <b>Группа для результатов:</b> <a href='{invite_link}'>Перейти в группу</a>\n\n"
        f"<i>Уведомления о найденных совпадениях будут приходить прямо в Вашу созданную группу!</i>",
        parse_mode="HTML"
    )


# ==================== ОПЛАТА ЗВЕЗДАМИ TELEGRAM (STARS) ====================

@router.callback_query(F.data == "pt_buy_slot")
async def cb_buy_slot(callback: CallbackQuery):
    """Отправляет инвойс для покупки дополнительного слота отслеживания за Telegram Stars"""
    user_id = callback.from_user.id
    prices = [LabeledPrice(label="Дополнительный слот отслеживания", amount=2)]

    await bot.send_invoice(
        chat_id=user_id,
        title="⭐ +1 Слот отслеживания",
        description="Позволяет отслеживать еще 1 группу/канал персонально",
        payload=f"personal_tracking_slot_{user_id}",
        currency="XTR",
        prices=prices
    )
    await callback.answer()


@router.pre_checkout_query(F.invoice_payload.startswith("personal_tracking_slot_"))
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    """Подтверждает предварительный платеж за покупку слота персонального отслеживания"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    """Обрабатывает успешную оплату слота персонального отслеживания"""
    # user = User.get(User.user_id == message.from_user.id)
    # user_lang = user.language if user.language != "unset" else "ru"
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    payload = message.successful_payment.invoice_payload
    if payload.startswith("personal_tracking_slot_"):
        user_id = message.from_user.id

        # Фиксируем оплату в статистике
        PersonalTrackingStats.create(
            user_id=user_id,
            event_type="slot_purchased",
            stars_amount=2
        )

        allowed = get_user_allowed_slots(user_id)
        await message.answer(
            f"🎉 <b>Оплата 2 Telegram Stars прошла успешно!</b>\n\n"
            f"Вам добавлен +1 слот отслеживания. Теперь доступно слотов: <b>{allowed}</b>.",
            reply_markup=personal_tracking_menu_kb(user_id=user_id, lang=user_lang),
            parse_mode="HTML"
        )


# ==================== СПИСОК И СТАТИСТИКА ====================

@router.callback_query(F.data == "pt_list_tracking")
async def cb_list_tracking(callback: CallbackQuery):
    """Отображает список групп персонального отслеживания пользователя"""
    user_id = callback.from_user.id
    records = list(
        PersonalTracking.select().where(PersonalTracking.user_id == user_id)
    )

    if not records:
        await callback.message.answer("ℹ️ У Вас пока нет активных персональных отслеживаний.")
        await callback.answer()
        return

    text = "📋 <b>Ваши персональные отслеживания:</b>\n\n"

    for idx, r in enumerate(records, start=1):
        can_change, hours_left = can_user_change_tracking(r)

        status_limit = (
            "✅ Доступно изменение"
            if can_change
            else f"⏳ Изменение через {hours_left} ч."
        )

        keywords = escape(str(r.keywords or ""))
        target_link = escape(str(r.target_link or ""))
        group_link = str(r.created_group_link or "")

        text += (
            f"<b>{idx}. {target_link}</b>\n"
            f"🔑 Ключевые слова: <code>{keywords}</code>\n"
            f"🔗 Группа: <a href='{group_link}'>Ссылка</a>\n"
            f"Статус: {status_limit}\n\n"
        )

    await callback.message.answer(
        text,
        reply_markup=tracking_list_keyboard(records),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pt_edit_"))
async def cb_edit_tracking_item(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор группы персонального отслеживания для редактирования"""
    rec_id = int(callback.data.split("_")[2])
    rec = PersonalTracking.get_or_none(PersonalTracking.id == rec_id)

    if not rec:
        await callback.answer("Ошибка: Запись не найдена", show_alert=True)
        return

    can_change, hours_left = can_user_change_tracking(rec)
    if not can_change:
        await callback.answer(
            f"⚠️ Изменение запрещено! Вы можете изменять отслеживание не чаще 1 раза в 24 часа. Осталось: {hours_left} ч.",
            show_alert=True
        )
        return

    await state.set_state(PersonalTrackingState.editing_slot_link)
    await state.update_data(edit_rec_id=rec_id)
    await callback.message.answer(
        f"⚙️ <b>Редактирование отслеживания #{rec_id}</b>\n\n"
        f"Отправьте НОВУЮ ссылку на группу/канал (или текущую: <code>{rec.target_link}</code>):",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PersonalTrackingState.editing_slot_link)
async def process_edit_link(message: Message, state: FSMContext):
    """Обрабатывает изменение ссылки целевой группы персонального отслеживания"""
    new_target = message.text.strip()
    data = await state.get_data()
    rec_id = data.get("edit_rec_id")

    rec = PersonalTracking.get_or_none(PersonalTracking.id == rec_id)
    if not rec:
        await message.answer("Ошибка записи.")
        await state.clear()
        return

    status_msg = await message.answer("🔄 <i>Обновляем подписку и группу...</i>", parse_mode="HTML")
    success, err_msg, invite_link, chat_id = await connect_target_and_create_group(new_target, message.from_user.id)

    if not success:
        await status_msg.edit_text(f"❌ {err_msg}")
        await state.clear()
        return

    rec.target_link = new_target
    rec.created_group_link = invite_link
    rec.created_group_id = chat_id
    rec.last_changed_at = datetime.now()
    rec.save()

    await state.set_state(PersonalTrackingState.editing_slot_keywords)
    await status_msg.edit_text("🔑 Введите новые ключевые слова через запятую:")


@router.message(PersonalTrackingState.editing_slot_keywords)
async def process_edit_keywords(message: Message, state: FSMContext):
    """Обрабатывает изменение ключевых слов персонального отслеживания"""
    new_keywords = message.text.strip()
    data = await state.get_data()
    rec_id = data.get("edit_rec_id")

    rec = PersonalTracking.get_or_none(PersonalTracking.id == rec_id)
    if rec:
        rec.keywords = new_keywords
        rec.last_changed_at = datetime.now()
        rec.save()

        # Фиксируем в статистике
        PersonalTrackingStats.create(
            user_id=message.from_user.id,
            event_type="changed_target",
            stars_amount=0
        )

    await state.clear()
    await message.answer("✅ <b>Настройки отслеживания успешно обновлены!</b>", parse_mode="HTML")


@router.callback_query(F.data == "pt_stats")
async def cb_stats(callback: CallbackQuery):
    """Отображает административную статистику персонального отслеживания"""
    total_tracking_users = PersonalTracking.select(PersonalTracking.user_id).distinct().count()
    total_paid_users = PersonalTrackingStats.select(PersonalTrackingStats.user_id).where(
        PersonalTrackingStats.event_type == "slot_purchased"
    ).distinct().count()

    total_stars_query = PersonalTrackingStats.select(fn.SUM(PersonalTrackingStats.stars_amount)).where(
        PersonalTrackingStats.event_type == "slot_purchased"
    ).scalar()
    total_stars = total_stars_query if total_stars_query else 0

    text = (
        "📊 <b>Статистика персонального отслеживания:</b>\n\n"
        f"👥 Пользователей подключили группы: <b>{total_tracking_users}</b>\n"
        f"⭐ Пользователей оплатили доп. слоты: <b>{total_paid_users}</b>\n"
        f"✨ Всего получено Stars: <b>{total_stars} ⭐</b>"
    )

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


# ==================== ОПУБЛИКОВАНИЕ УВЕДОМЛЕНИЙ БОТОМ ====================

async def send_personal_tracking_alert(user_id: int, matched_keyword: str, message_text: str, message_link: str):
    """
    Отправляет уведомление бота в персональную группу пользователя.
    """
    records = PersonalTracking.select().where(PersonalTracking.user_id == user_id)
    for r in records:
        keywords_list = [k.strip().lower() for k in r.keywords.split(",") if k.strip()]
        if matched_keyword.lower() in keywords_list:
            if r.created_group_id:
                alert_text = (
                    f"🎯 <b>Найдено ключевое слово:</b> <code>{matched_keyword}</code>\n\n"
                    f"💬 <b>Текст сообщения:</b>\n{message_text[:500]}\n\n"
                    f"🔗 <a href='{message_link}'>Перейти к сообщению</a>"
                )
                try:
                    await bot.send_message(
                        chat_id=r.created_group_id,
                        text=alert_text,
                        parse_mode="HTML",
                        disable_web_page_preview=False
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить алерт в группу {r.created_group_id}: {e}")


# ==================== АВТОРИЗАЦИЯ АККАУНТА ПО НОМЕРУ ТЕЛЕФОНА ====================

@router.callback_query(F.data == "pt_auth_phone")
async def cb_start_phone_auth(callback: CallbackQuery, state: FSMContext):
    """Начало шага ввода номера телефона"""
    await state.set_state(PersonalTrackingState.waiting_for_phone_number)
    await callback.message.answer(
        "📱 <b>Подключение Telegram-аккаунта по номеру телефона</b>\n\n"
        "Пожалуйста, введите Ваш номер телефона в международном формате.\n"
        "<i>Пример: <code>+79991234567</code> или <code>+380991234567</code></i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_phone_number)
async def process_phone_number_input(message: Message, state: FSMContext):
    """Обработка ввода номера телефона и запрос 5-значного кода через Telethon"""
    phone = message.text.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    if len(phone) < 10 or not phone[1:].isdigit():
        await message.answer(
            "⚠️ Некорректный формат номера. Введите номер начиная со знака + (например, <code>+79991234567</code>):",
            parse_mode="HTML")
        return

    status_msg = await message.answer(
        "🔄 <i>Запрашиваем код подтверждения у Telegram... Пожалуйста, подождите до прихода кода. Если код не пришел, попробуйте позже.</i>",
        parse_mode="HTML")

    client = TelegramClient(
        StringSession(),
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
        send_code = await client.send_code_request(phone)
        session_str = client.session.save()
        await client.disconnect()

        await state.update_data(
            phone_number=phone,
            phone_code_hash=send_code.phone_code_hash,
            session_str=session_str,
            current_code=""
        )
        await state.set_state(PersonalTrackingState.waiting_for_auth_code)

        await status_msg.edit_text(
            f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
            f"📱 <b>Номер:</b> <code>{phone}</code>\n"
            f"🔢 <b>Введенный код:</b> <code>_ _ _ _ _</code>\n\n"
            f"⚠️ <i>Используйте эмодзи-клавиатуру ниже для выбора цифр кода, чтобы избежать блокировки от Telegram:</i>",
            reply_markup=emoji_code_keypad_kb(),
            parse_mode="HTML"
        )
    except PhoneNumberInvalidError:
        await status_msg.edit_text("❌ Введен недействительный номер телефона. Попробуйте еще раз.")
        await state.clear()
    except FloodWaitError as fwe:
        await status_msg.edit_text(f"⏳ Слишком много попыток. Пожалуйста, подождите {fwe.seconds} секунд.")
        await state.clear()
    except Exception as e:
        logger.exception(f"❌ Ошибка отправки кода на номер {phone}: {e}")
        await status_msg.edit_text(f"❌ Ошибка при запросе кода: {e}")
        await state.clear()


@router.callback_query(F.data.startswith("pt_digit_"), PersonalTrackingState.waiting_for_auth_code)
async def cb_handle_emoji_digit(callback: CallbackQuery, state: FSMContext):
    """Обработка ввода цифр кода с помощью эмодзи-клавиатуры"""
    action = callback.data.replace("pt_digit_", "")
    data = await state.get_data()
    current_code = data.get("current_code", "")

    if action == "clear":
        current_code = current_code[:-1]
    elif action == "submit":
        if len(current_code) < 5:
            await callback.answer("⚠️ Введите все 5 цифр кода подтверждения!", show_alert=True)
            return
        await execute_sign_in(callback, state, current_code)
        return
    elif action.isdigit():
        if len(current_code) < 5:
            current_code += action

    await state.update_data(current_code=current_code)

    digits_display = " ".join(list(current_code) + ["_"] * (5 - len(current_code)))
    phone = data.get("phone_number", "")

    try:
        await callback.message.edit_text(
            f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
            f"📱 <b>Номер:</b> <code>{phone}</code>\n"
            f"🔢 <b>Введенный код:</b> <code>{digits_display}</code>\n\n"
            f"⚠️ <i>Используйте эмодзи-клавиатуру ниже для выбора цифр кода:</i>",
            reply_markup=emoji_code_keypad_kb(),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer()

    # Авто-отправка при вводе 5 цифр
    if len(current_code) == 5:
        await execute_sign_in(callback, state, current_code)


async def execute_sign_in(callback: CallbackQuery, state: FSMContext, code: str):
    """Выполнение входа Telethon по коду"""
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
        me = await client.get_me()
        final_session = client.session.save()
        await client.disconnect()

        # Сохраняем авторизованную сессию в БД
        write_account_to_db(
            session_string=final_session,
            user_id=callback.from_user.id,
            phone_number=me.phone or phone
        )

        await state.clear()
        await callback.message.edit_text(
            f"🎉 <b>Аккаунт успешно авторизован и подключен!</b>\n\n"
            f"👤 <b>Имя:</b> {me.first_name or ''} {me.last_name or ''}\n"
            f"📱 <b>Телефон:</b> +{me.phone}\n"
            f"🆔 <b>Telegram ID:</b> <code>{me.id}</code>\n\n"
            f"✅ Сессия сохранена в базе и готова к отслеживанию.",
            parse_mode="HTML"
        )
    except PhoneCodeInvalidError:
        await callback.answer("❌ Неверный код подтверждения! Попробуйте еще раз.", show_alert=True)
        await state.update_data(current_code="")
        try:
            await callback.message.edit_text(
                f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
                f"📱 <b>Номер:</b> <code>{phone}</code>\n"
                f"🔢 <b>Введенный код:</b> <code>_ _ _ _ _</code>\n\n"
                f"❌ <b>Ошибка: Неверный код. Попробуйте выбрать цифры заново:</b>",
                reply_markup=emoji_code_keypad_kb(),
                parse_mode="HTML"
            )
        except Exception:
            pass
    except PhoneCodeExpiredError:
        await callback.answer("❌ Срок действия кода истек! Запросите код заново.", show_alert=True)
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
                "🔐 <b>На Вашем аккаунте включена двухэтапная аутентификация (2FA)!</b>\n\n"
                "Пожалуйста, введите Ваш облачный пароль текстом в ответном сообщении:",
                parse_mode="HTML"
            )
        except Exception:
            pass
    except Exception as e:
        logger.exception(f"❌ Ошибка входа Telethon по коду: {e}")
        await callback.answer(f"❌ Ошибка входа: {e}", show_alert=True)
        try:
            await client.disconnect()
        except Exception:
            pass


@router.message(PersonalTrackingState.waiting_for_2fa_password)
async def process_2fa_password_input(message: Message, state: FSMContext):
    """Обработка ввода 2FA облачного пароля"""
    password = message.text.strip()
    data = await state.get_data()
    session_str = data.get("session_str")
    phone = data.get("phone_number")

    status_msg = await message.answer("🔄 <i>Проверяем 2FA пароль...</i>", parse_mode="HTML")

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
        me = await client.get_me()
        final_session = client.session.save()
        await client.disconnect()

        # Сохраняем аккаунт в БД
        write_account_to_db(
            session_string=final_session,
            user_id=message.from_user.id,
            phone_number=me.phone or phone
        )

        await state.clear()
        await status_msg.edit_text(
            f"🎉 <b>Аккаунт успешно авторизован с 2FA паролем!</b>\n\n"
            f"👤 <b>Имя:</b> {me.first_name or ''} {me.last_name or ''}\n"
            f"📱 <b>Телефон:</b> +{me.phone}\n"
            f"🆔 <b>Telegram ID:</b> <code>{me.id}</code>\n\n"
            f"✅ Сессия успешно сохранена в базе данных.",
            parse_mode="HTML"
        )
    except PasswordHashInvalidError:
        await status_msg.edit_text(
            "❌ <b>Неверный 2FA пароль!</b>\n\nПожалуйста, введите корректный облачный пароль текстом:")
    except Exception as e:
        logger.exception(f"❌ Ошибка 2FA авторизации: {e}")
        await status_msg.edit_text(f"❌ Ошибка авторизации: {e}")
        try:
            await client.disconnect()
        except Exception:
            pass


@router.callback_query(F.data == "pt_cancel_auth")
async def cb_cancel_auth(callback: CallbackQuery, state: FSMContext):
    """Отмена процедуры авторизации"""
    await state.clear()
    await callback.message.edit_text("🚫 Авторизация отменена.")
    await callback.answer()
