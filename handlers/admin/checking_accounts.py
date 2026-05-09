from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from account_manager.auth import CheckingAccountsValidity
from database.database import getting_account, User
from locales.locales import t

router = Router(name=__name__)


@router.message((F.text == t('check_accounts_button', 'ru')) | (F.text == t('check_accounts_button', 'en')))
async def checking_accounts_handler(message: Message, state: FSMContext):
    """✅ Проверка аккаунтов на валидность"""
    try:
        await state.clear()  # Сбрасываем текущее состояние FSM

        user = User.get(User.user_id == message.from_user.id)

        records = getting_account()  # Получаем все аккаунты в базе данных
        logger.info(f"Получено аккаунтов: {len(records)}")

        await message.answer(t("checking_accounts_start", lang=user.language, count=len(records)))

        for session_name in records:
            logger.info(f"✅ Проверка аккаунта на валидность: {session_name}")

            # ✅ Проверка аккаунтов на валидность
            checker = CheckingAccountsValidity(
                message=message,
                # path=path
            )

            await checker.verify_account(session_name)

        await message.answer(
            t("checking_accounts_complete", lang=user.language)
        )

    except Exception as e:
        logger.exception(e)
