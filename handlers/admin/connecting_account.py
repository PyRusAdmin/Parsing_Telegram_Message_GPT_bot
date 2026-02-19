# -*- coding: utf-8 -*-
from pathlib import Path

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from telethon.sessions import StringSession
from database.database import write_account_to_db
from account_manager.auth import CheckingAccountsValidity
from keyboards.user.keyboards import back_keyboard
from states.states import MyStates
from system.dispatcher import router


@router.message(F.text == "Подключение аккаунта")
async def admin_connecting_account(message: Message, state: FSMContext):
    """Админ нажимает кнопку → бот просит .session файл(ы)"""
    await state.clear()
    telegram_id = message.from_user.id

    # ✅ Инициализируем очередь файлов в состоянии
    await state.update_data(received_files=[], processed_count=0, success_count=0, fail_count=0)

    await state.set_state(MyStates.waiting_for_session_file)
    await message.answer(
        "📤 Отправьте мне файл(ы) сессии Telethon (должны заканчиваться на `.session`)\n\n"
        "Можно отправить сразу несколько файлов — бот обработает их по очереди.\n"
        "Когда закончите — нажмите кнопку «Назад» или отправьте /start",
        reply_markup=back_keyboard()
    )
    logger.info(f"Админ {telegram_id} начал добавление новых сессий")


MAX_SESSIONS_PER_BATCH = 10  # Максимум файлов за одну сессию


@router.message(MyStates.waiting_for_session_file, F.document)
async def receive_session_file(message: Message, state: FSMContext):
    """Получаем .session файл(ы) от админа и обрабатываем по очереди"""
    document = message.document

    # ✅ Проверяем расширение
    if not document.file_name.endswith('.session'):
        await message.answer("❌ Это не файл сессии! Отправьте файл с расширением `.session`")
        return

    # ✅ Получаем данные из состояния
    data = await state.get_data()

    if len(data.get("received_files", [])) >= MAX_SESSIONS_PER_BATCH:
        await message.answer(
            f"⚠️ Достигнут лимит: {MAX_SESSIONS_PER_BATCH} файлов за раз.\n"
            f"Обработайте текущие и отправьте остальные позже."
        )
        return

    received_files = data.get("received_files", [])
    processed_count = data.get("processed_count", 0)
    success_count = data.get("success_count", 0)
    fail_count = data.get("fail_count", 0)

    # ✅ Добавляем файл в очередь
    received_files.append(document)
    await state.update_data(received_files=received_files)

    # ✅ Показываем прогресс, если файлов больше 1
    total = len(received_files)
    if total > 1:
        await message.answer(f"📥 Файл принят: `{document.file_name}`\n"
                             f"📊 В очереди: {total} файл(ов). Обрабатываю...")
    try:
        # ✅ Создаём папку для временного хранения
        sessions_dir = Path("accounts/parsing")
        sessions_dir.mkdir(parents=True, exist_ok=True)
        # ✅ Санитизация имени файла
        safe_file_name = "".join(c for c in document.file_name if c.isalnum() or c in "._-")
        file_path = sessions_dir / safe_file_name
        # ✅ Скачиваем файл
        await message.bot.download(document, destination=file_path)
        # ✅ Извлекаем путь без расширения для Telethon
        session_path_without_ext = str(file_path.with_suffix(""))
        # ✅ Проверяем валидность аккаунта
        checker = CheckingAccountsValidity(message=message, path=session_path_without_ext)
        client = await checker.connect_client()

        if client:
            me = await client.get_me()
            phone = me.phone or "unknown"
            first_name = me.first_name or ""

            # ✅ Конвертируем в StringSession и сохраняем в БД
            session_string = StringSession.save(client.session)
            write_account_to_db(session_string=session_string, phone_number=phone)
            await client.disconnect()
            # ✅ Удаляем временный .session файл
            if file_path.exists():
                file_path.unlink()
            # ✅ Обновляем статистику
            success_count += 1
            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            # ✅ Отправляем результат для этого файла
            await message.answer(
                f"✅ <b>{safe_file_name}</b> — успешно!\n"
                f"📱 {phone} | 👤 {first_name}",
                parse_mode="HTML"
            )
        else:
            # ❌ Файл не валиден — удаляем
            if file_path.exists():
                file_path.unlink()
            fail_count += 1
            logger.warning(f"❌ Сессия не валидна: {safe_file_name}")
            await message.answer(f"❌ <b>{safe_file_name}</b> — не прошёл проверку", parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Ошибка при обработке {document.file_name}: {e}")
        fail_count += 1
        if file_path.exists():
            file_path.unlink()
        await message.answer(f"⚠️ <b>{safe_file_name}</b> — ошибка обработки", parse_mode="HTML")

    finally:
        # ✅ Обновляем состояние: файл обработан
        processed_count += 1
        await state.update_data(
            processed_count=processed_count,
            success_count=success_count,
            fail_count=fail_count
        )

        # ✅ Если это был последний файл в очереди — показываем сводку
        if processed_count == len(received_files):
            summary = (
                f"📊 <b>Обработка завершена!</b>\n"
                f"✅ Успешно: {success_count}\n"
                f"❌ Ошибки: {fail_count}\n\n"
                f"Можете отправить ещё файлы или нажать «Назад»"
            )
            await message.answer(summary, parse_mode="HTML", reply_markup=back_keyboard())
            # ✅ Очищаем очередь, но оставляем состояние для приёма новых файлов
            await state.update_data(received_files=[], processed_count=0, success_count=0, fail_count=0)


def register_handlers_admin_connect_account():
    """✅ Регистрируем оба хендлера"""
    router.message.register(admin_connecting_account)
    router.message.register(receive_session_file)
