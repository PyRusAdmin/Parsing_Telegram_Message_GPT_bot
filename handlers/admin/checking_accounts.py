from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from account_manager.auth import CheckingAccountsValidity
from database.database import getting_account, User
from locales.locales import t

router = Router(name=__name__)


async def checking_accounts_internal(message: Message, user_id: int, state: FSMContext):
    try:
        await state.clear()
        user = User.get(User.user_id == user_id)
        records = getting_account()
        logger.info(f"Получено аккаунтов: {len(records)}")

        await message.answer(t("checking_accounts_start", lang=user.language, count=len(records)))

        for session_name in records:
            logger.info(f"✅ Проверка аккаунта на валидность: {session_name}")
            checker = CheckingAccountsValidity(
                message=message,
            )
            await checker.verify_account(session_name)

        await message.answer(
            t("checking_accounts_complete", lang=user.language)
        )

    except Exception as e:
        logger.exception(e)


@router.message((F.text == t('check_accounts_button', 'ru')) | (F.text == t('check_accounts_button', 'en')))
async def checking_accounts_handler(message: Message, state: FSMContext):
    """✅ Проверка аккаунтов на валидность (текст)"""
    await checking_accounts_internal(message, message.from_user.id, state)


@router.callback_query(F.data == "admin_check_accounts")
async def checking_accounts_cb(callback: CallbackQuery, state: FSMContext):
    """✅ Проверка аккаунтов на валидность (инлайн)"""
    await callback.answer()
    await checking_accounts_internal(callback.message, callback.from_user.id, state)
