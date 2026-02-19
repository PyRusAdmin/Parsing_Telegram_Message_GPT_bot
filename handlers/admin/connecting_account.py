# -*- coding: utf-8 -*-
from pathlib import Path

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from account_manager.auth import CheckingAccountsValidity
from keyboards.user.keyboards import back_keyboard
from states.states import MyStates
from system.dispatcher import router


@router.message(F.text == "Подключение аккаунта")
async def admin_connecting_account(message: Message, state: FSMContext):
    """Админ нажимает кнопку → бот просит .session файл"""
    await state.clear()
    telegram_id = message.from_user.id
    await state.set_state(MyStates.waiting_for_session_file)
    await message.answer(
        "📤 Отправьте мне файл сессии Telethon (должен заканчиваться на `.session`)\n\n"
        "После загрузки бот автоматически проверит аккаунт.",
        reply_markup=back_keyboard()
    )
    logger.info(f"Админ {telegram_id} начал добавление новой сессии")


@router.message(MyStates.waiting_for_session_file, F.document)
async def receive_session_file(message: Message, state: FSMContext):
    """Получаем .session файл от админа"""
    document = message.document
    try:
        # Проверяем расширение
        if not document.file_name.endswith('.session'):
            await message.answer("❌ Это не файл сессии! Отправьте файл с расширением `.session`")
            return

        # ✅ Создаём папку accounts/parsing, если её нет
        sessions_dir = Path("accounts/parsing")
        sessions_dir.mkdir(parents=True, exist_ok=True)

        # ✅ Санитизация имени файла (убираем опасные символы)
        safe_file_name = "".join(c for c in document.file_name if c.isalnum() or c in "._-")
        file_path = sessions_dir / safe_file_name

        logger.debug(f"Сохраняем файл в: {file_path}")

        # ✅ Скачиваем файл
        await message.bot.download(document, destination=file_path)
        await message.answer(f"✅ Файл сохранён: `{safe_file_name}`\n\nПроверяю аккаунт...")

        # ✅ Извлекаем имя сессии без расширения
        session_name = file_path.stem

        # ✅ Проверяем валидность аккаунта
        checker = CheckingAccountsValidity(message=message, path=str(sessions_dir))
        client = await checker.connect_client(session_name=session_name)

        if client:
            me = await client.get_me()
            phone = me.phone or "unknown"

            # ✅ Переименовываем файл сессии в phone.session для удобства
            new_session_path = sessions_dir / f"{phone}.session"
            if file_path != new_session_path and not new_session_path.exists():
                file_path.rename(new_session_path)
                logger.info(f"📁 Сессия переименована: {safe_file_name} → {phone}.session")

            await client.disconnect()

            await message.answer(
                f"✅ Аккаунт успешно подключён!\n"
                f"📱 Номер: `{phone}`\n"
                f"👤 Имя: `{me.first_name or ''}`",
                reply_markup=back_keyboard()
            )
            logger.success(f"Новая сессия добавлена: {phone}.session | ID: {me.id}")
        else:
            # ❌ Если проверка не прошла — удаляем файл
            if file_path.exists():
                file_path.unlink()
            await message.answer(
                "❌ Аккаунт не прошёл проверку.\n\nМожете попробовать другой файл.",
                reply_markup=back_keyboard()
            )

    except Exception as e:
        logger.exception(f"Ошибка при обработке сессии: {e}")
        await message.answer("⚠️ Произошла ошибка при проверке аккаунта.")
    finally:
        await state.clear()


def register_handlers_admin_connect_account():
    """✅ Регистрируем оба хендлера"""
    router.message.register(admin_connecting_account)
    router.message.register(receive_session_file)
