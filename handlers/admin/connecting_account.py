# -*- coding: utf-8 -*-
import os

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

    # Проверка, что это админ (можно по ID или по полю в БД)
    # try:
    #     user = User.get(User.user_id == telegram_id)
    #     if not user.is_admin:  # если у тебя есть такое поле
    #         await message.answer("⛔ У вас нет прав администратора.")
    #         return
    # except:
    #     await message.answer("⛔ Только администраторы могут подключать аккаунты.")
    #     return

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

        # Создаём папку accounts/parsing, если её нет
        sessions_dir = "accounts/parsing"
        os.makedirs(sessions_dir, exist_ok=True)
        # Путь для сохранения
        file_path = os.path.join(sessions_dir, document.file_name)
        logger.debug(file_path)
        # Скачиваем файл
        await message.bot.download(document, destination=file_path)
        await message.answer(f"✅ Файл сохранён: `{document.file_name}`\n\nПроверяю аккаунт...")

        # Проверяем валидность аккаунта
        checker = CheckingAccountsValidity(message=message, path=file_path)
        result = checker.check_single_account(file_path)  # подставь свой метод, если называется иначе

        if result.get("valid", False):
            await message.answer(
                f"✅ Аккаунт успешно подключён!\n"
                f"📱 Номер: {result.get('phone', 'неизвестно')}\n"
                f"👤 Имя: {result.get('first_name', '')}",
                reply_markup=back_keyboard()
            )
            logger.success(f"Новая сессия добавлена: {document.file_name}")
        else:
            await message.answer(
                f"❌ Аккаунт не прошёл проверку:\n{result.get('error', 'Неизвестная ошибка')}\n\n"
                f"Можете попробовать другой файл.",
                reply_markup=back_keyboard()
            )
            # Удаляем невалидный файл
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        logger.exception(e)
    finally:
        await state.clear()


def register_handlers_admin_connect_account():
    router.message.register(admin_connecting_account)
