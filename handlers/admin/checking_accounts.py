from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from database.users_accounts import getting_account
from handlers.user_language import determines_user_language
from locales.locales import t

router = Router(name=__name__)


@router.callback_query(F.data == "admin_check_accounts")
async def checking_accounts_cb(callback: CallbackQuery, state: FSMContext):
    """
    Проверка аккаунтов на валидность (инлайн-обработчик).

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await callback.answer()

    try:
        await state.clear()
        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=callback.from_user.id)
        records = getting_account()
        logger.info(f"Получено аккаунтов: {len(records)}")

        await callback.message.answer(t("checking_accounts_start", lang=user_lang, count=len(records)))

        for session_name in records:
            logger.info(f"✅ Проверка аккаунта на валидность: {session_name}")
            checker = CheckingAccountsValidity()
            await checker.verify_account(session_name)

        await callback.message.answer(
            t("checking_accounts_complete", lang=user_lang)
        )

    except Exception as e:
        logger.exception(e)
