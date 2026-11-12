import asyncio
import csv
import os
from datetime import datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from core.config import ADMIN_USER_ID

from database.users_personal_trackings import UsersPersonalTrackings
from database.account_free import getting_free_account
from database.users_questions import get_all_questions
from handlers.user_language import determines_user_language
from keyboards.keyboards import admin_keyboard, broadcast_preview_keyboard, back_keyboard
from locales.locales import t
from states.states import BroadcastState

router = Router(name=__name__)


@router.callback_query(F.data == "admin_export_questions")
async def export_questions_cb(callback: CallbackQuery):
    """
    Экспортирует вопросы и ответы из базы данных в CSV файл (инлайн).

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    """
    await callback.answer()

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    try:
        questions = get_all_questions()
        if not questions:
            await callback.message.answer(
                t("no_questions_in_db", lang=user_lang), parse_mode="HTML"
            )
            return

        if not os.path.exists("exports"):
            os.makedirs("exports")

        file_path = f"exports/questions_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "question_number", "user_id", "user_username", "user_firstname",
                "user_question", "answer_ai", "status_question", "date_added"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")

            writer.writeheader()
            for question_data in questions:
                writer.writerow(question_data)

        await callback.message.answer_document(FSInputFile(file_path),
                                               caption=t("questions_export_caption", lang=user_lang))
        os.remove(file_path)

    except Exception as e:
        logger.exception(e)
        await callback.message.answer(t("export_error", lang=user_lang, error=str(e)), parse_mode="HTML")


@router.callback_query(F.data == "menu_admin_panel")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик команды "Панель администратора" (инлайн).

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(
        text=t("admin_panel_message", lang=user_lang),
        parse_mode="HTML",
        reply_markup=admin_keyboard(lang=user_lang)
    )
    await callback.answer()


@router.callback_query(F.data == "admin_toggle_nightly_check")
async def toggle_nightly_check_cb(callback: CallbackQuery):
    """
    Переключает активность автоматической ночной проверки базы данных в 01:00.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    """
    from handlers.admin.nightly_check import toggle_nightly_check
    new_state = toggle_nightly_check()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    alert_msg = t("nightly_check_toggled_on", lang=user_lang) if new_state else t("nightly_check_toggled_off",
                                                                                  lang=user_lang)
    await callback.answer(alert_msg, show_alert=True)
    try:
        await callback.message.edit_reply_markup(reply_markup=admin_keyboard(lang=user_lang))
    except Exception:
        pass


@router.message((F.text == t('check_accounts_button', 'ru')) | (F.text == t('check_accounts_button', 'en')))
async def checking_accounts_handler(message: Message, state: FSMContext):
    """
    Проверка аккаунтов на валидность по текстовой команде администратора.

    :param message: (Message) Объект входящего сообщения от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    try:
        await state.clear()  # Сбрасываем текущее состояние FSM
        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=message.from_user.id)
        records = getting_free_account()  # Получаем все свободные аккаунты в базе данных
        logger.info(f"Получено свободных аккаунтов: {len(records)}")
        await message.answer(t("checking_accounts_start", lang=user_lang, count=len(records)))
        checker = CheckingAccountsValidity()
        valid_count = 0
        banned_count = 0
        for session_name in records:
            logger.info("🔍 Проверка свободного аккаунта на валидность...")
            is_valid = await checker.verify_free_account(session_name=session_name, user_lang=user_lang)
            if is_valid:
                valid_count += 1
            else:
                banned_count += 1
        result_text = (
            f"✅ <b>Проверка свободных аккаунтов завершена!</b>\n\n"
            f"📊 Всего проверено: <b>{len(records)}</b>\n"
            f"🟢 Активных: <b>{valid_count}</b>\n"
            f"🔴 Невалидных/забаненных (удалены из базы): <b>{banned_count}</b>"
            if user_lang == "ru"
            else f"✅ <b>Free accounts verification completed!</b>\n\n"
                 f"📊 Total checked: <b>{len(records)}</b>\n"
                 f"🟢 Active: <b>{valid_count}</b>\n"
                 f"🔴 Invalid/banned (removed from database): <b>{banned_count}</b>"
        )
        await message.answer(result_text, parse_mode="HTML")
    except Exception as e:
        logger.exception(e)


# ==================== 📢 МОДУЛЬ РАССЫЛКИ СООБЩЕНИЙ ====================

@router.callback_query(F.data == "admin_broadcast_start")
async def broadcast_start_cb(callback: CallbackQuery, state: FSMContext):
    """
    Старт процесса рассылки: запрос текста/медиа сообщения от администратора.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    if int(callback.from_user.id) != int(ADMIN_USER_ID):
        await callback.answer(t("admin_access_denied", lang=user_lang), show_alert=True)
        return

    await state.clear()
    await state.set_state(BroadcastState.waiting_for_broadcast_message)

    await callback.message.edit_text(
        text=t("admin_broadcast_prompt", lang=user_lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
    )
    await callback.answer()


@router.message(BroadcastState.waiting_for_broadcast_message)
async def broadcast_message_received(message: Message, state: FSMContext):
    """
    Принимает сообщение для рассылки, сохраняет его параметры и отображает предпросмотр.

    :param message: (Message) Объект входящего сообщения от администратора с контентом рассылки.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    if int(message.from_user.id) != int(ADMIN_USER_ID):
        return

    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    # total_users = User.select().count()
    total_users = UsersPersonalTrackings.select().count()

    # Сохраняем ID сообщения и чата для последующего копирования через copy_message
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
        total_recipients=total_users
    )
    await state.set_state(BroadcastState.waiting_for_broadcast_confirmation)

    # Отправляем предпросмотр (копию сообщения администратора)
    await message.answer(t("admin_broadcast_preview_title", lang=user_lang), parse_mode="HTML")
    await message.copy_to(chat_id=message.chat.id)

    # Клавиатура подтверждения
    await message.answer(
        text=t("admin_broadcast_preview_params", lang=user_lang, total=total_users),
        parse_mode="HTML",
        reply_markup=broadcast_preview_keyboard(lang=user_lang)
    )


@router.callback_query(BroadcastState.waiting_for_broadcast_confirmation, F.data == "admin_broadcast_cancel")
async def broadcast_cancel_cb(callback: CallbackQuery, state: FSMContext):
    """
    Отмена рассылки администратором.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text=t("admin_broadcast_cancelled", lang=user_lang),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
    )
    await callback.answer()


@router.callback_query(BroadcastState.waiting_for_broadcast_confirmation, F.data == "admin_broadcast_send")
async def broadcast_send_cb(callback: CallbackQuery, state: FSMContext, bot):
    """
    Запуск цикла рассылки по всем зарегистрированным пользователям таблицы User/UsersPersonalTrackings.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    :param bot: Экземпляр бота Aiogram для отправки сообщений.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    if int(callback.from_user.id) != int(ADMIN_USER_ID):
        await callback.answer(t("admin_access_denied", lang=user_lang), show_alert=True)
        return

    data = await state.get_data()
    source_chat_id = data.get("broadcast_chat_id")
    source_message_id = data.get("broadcast_message_id")
    await state.clear()

    if not source_chat_id or not source_message_id:
        await callback.answer(t("admin_broadcast_not_found", lang=user_lang), show_alert=True)
        return

    status_msg = await callback.message.edit_text(
        text=t("admin_broadcast_started", lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()

    # Запрашиваем ID всех пользователей из таблицы users_personal_trackings (ранее User)
    # users = list(User.select(User.user_id))
    users = list(UsersPersonalTrackings.select(UsersPersonalTrackings.user_id))
    total = len(users)

    sent_count = 0
    blocked_count = 0
    error_count = 0

    logger.info(f"Администратор {callback.from_user.id} запустил рассылку для {total} пользователей")

    for idx, u in enumerate(users, start=1):
        target_user_id = u.user_id
        try:
            await bot.copy_message(
                chat_id=target_user_id,
                from_chat_id=source_chat_id,
                message_id=source_message_id
            )
            sent_count += 1
            # Небольшая задержка во избежание flood limits Telegram (30 сообщений/сек)
            await asyncio.sleep(0.05)

        except TelegramForbiddenError:
            # Пользователь заблокировал бота или удалил аккаунт
            blocked_count += 1
            logger.warning(f"Рассылка: пользователь {target_user_id} заблокировал бота")

        except TelegramRetryAfter as e:
            # Превышен лимит запросов, ждём требуемое количество секунд
            logger.warning(f"Рассылка: Flood limit! Сон {e.retry_after} сек.")
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(
                    chat_id=target_user_id,
                    from_chat_id=source_chat_id,
                    message_id=source_message_id
                )
                sent_count += 1
            except Exception as retry_err:
                logger.error(f"Рассылка: повторная ошибка для {target_user_id}: {retry_err}")
                error_count += 1

        except Exception as e:
            error_count += 1
            logger.error(f"Рассылка: ошибка отправки пользователю {target_user_id}: {e}")

        # Обновляем прогресс каждые 25 пользователей или в конце
        if idx % 25 == 0 or idx == total:
            try:
                await status_msg.edit_text(
                    text=t("admin_broadcast_progress", lang=user_lang, current=idx, total=total, sent=sent_count,
                           blocked=blocked_count, errors=error_count),
                    parse_mode="HTML"
                )
            except Exception:
                pass

    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    report_text = t("admin_broadcast_report", lang=user_lang, total=total, sent=sent_count, blocked=blocked_count,
                    errors=error_count)

    try:
        await status_msg.edit_text(
            text=report_text,
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
        )
    except Exception:
        await callback.message.answer(
            text=report_text,
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
        )

    logger.info(f"Рассылка завершена. Доставлено: {sent_count}, Заблокировали: {blocked_count}, Ошибок: {error_count}")
