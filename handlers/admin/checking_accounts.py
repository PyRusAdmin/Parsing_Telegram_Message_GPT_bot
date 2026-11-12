from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from database.account_free import getting_free_account
from handlers.user_language import determines_user_language
from locales.locales import t

router = Router(name=__name__)


@router.callback_query(F.data == "admin_check_accounts")
async def checking_accounts_cb(callback: CallbackQuery, state: FSMContext):
    """
    Проверка свободных аккаунтов администратора (account_free) на валидность и бан.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await callback.answer()

    try:
        await state.clear()
        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=callback.from_user.id)
        records = getting_free_account()
        logger.info(f"Получено свободных аккаунтов для проверки: {len(records)}")

        await callback.message.answer(t("checking_accounts_start", lang=user_lang, count=len(records)), parse_mode="HTML")

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
        await callback.message.answer(result_text, parse_mode="HTML")

    except Exception as e:
        logger.exception(e)
