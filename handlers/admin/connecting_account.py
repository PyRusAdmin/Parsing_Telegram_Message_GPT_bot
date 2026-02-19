# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity
from database.database import write_account_to_db
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
                f"🧹 Очищаю временные файлы..."
            )
            # Отправляем сообщение с началом очистки
            cleanup_msg = await message.answer(summary, parse_mode="HTML")

            # ✅ Запускаем очистку
            cleanup_result = cleanup_session_files(
                parsing_dir="accounts/parsing",
                root_dirs=[".", "accounts", "data", "sessions"]  # Укажите ваши корневые папки
            )

            # ✅ Обновляем сообщение с результатом очистки
            # cleanup_summary = ""
            # if cleanup_result["parsing_dir_deleted"]:
            #     cleanup_summary += "🗑️ Папка `accounts/parsing` удалена\n"
            # if cleanup_result["root_files_deleted"] > 0:
            #     cleanup_summary += f"🗑️ Удалено файлов из корня: {cleanup_result['root_files_deleted']}\n"
            # if cleanup_result["errors"]:
            #     cleanup_summary += f"⚠️ Ошибки: {len(cleanup_result['errors'])}\n"

            # if cleanup_summary:
            await message.answer(
                f"📊 <b>Обработка завершена!</b>\n",
                # f"✅ Успешно: {success_count}\n"
                # f"❌ Ошибки: {fail_count}\n\n"
                # f"<b>🧹 Результат очистки:</b>\n"
                # f"{cleanup_summary}\n"
                # f"Можете отправить ещё файлы или нажать «Назад»",
                parse_mode="HTML",
                reply_markup=back_keyboard()
            )
            # else:
            # await message.answer(
            #     f"📊 <b>Обработка завершена!</b>\n",
            # f"✅ Успешно: {success_count}\n"
            # f"❌ Ошибки: {fail_count}\n\n"
            # f"✅ Временные файлы уже очищены.\n"
            # f"Можете отправить ещё файлы или нажать «Назад»",
            # parse_mode="HTML",
            # reply_markup=back_keyboard()
            # )

        # ✅ Очищаем очередь в состоянии
        await state.update_data(received_files=[], processed_count=0, success_count=0, fail_count=0)


def cleanup_session_files(parsing_dir: str = "accounts/parsing", root_dirs: list[str] | None = None):
    """
    Полная очистка временных .session файлов

    :param parsing_dir: Папка с временными сессиями (будет удалена полностью)
    :param root_dirs: Список корневых папок для поиска "забытых" .session файлов
    :return: dict со статистикой очистки
    """
    result = {
        "parsing_dir_deleted": False,
        "root_files_deleted": 0,
        "errors": []
    }

    # ✅ 1. Удаляем папку accounts/parsing целиком
    try:
        parsing_path = Path(parsing_dir)
        if parsing_path.exists() and parsing_path.is_dir():
            shutil.rmtree(parsing_path)
            logger.info(f"🗑️ Папка удалена: {parsing_dir}")
            result["parsing_dir_deleted"] = True
        else:
            logger.debug(f"Папка {parsing_dir} не существует — пропускаем")
    except Exception as e:
        error_msg = f"Ошибка удаления {parsing_dir}: {e}"
        logger.exception(error_msg)
        result["errors"].append(error_msg)

    # ✅ 2. Очищаем корневые папки от "забытых" .session файлов
    dirs_to_scan = root_dirs or [".", "accounts", "data"]  # Папки для сканирования по умолчанию

    for root_dir in dirs_to_scan:
        try:
            root_path = Path(root_dir)
            if not root_path.exists():
                continue

            # Ищем .session файлы ТОЛЬКО в этой папке (не рекурсивно!)
            for session_file in root_path.glob("*.session"):
                # ❌ Пропускаем важные системные файлы, если нужно
                if session_file.name.startswith("bot_session") or session_file.name.startswith("main_"):
                    logger.debug(f"⏭️ Пропущен системный файл: {session_file.name}")
                    continue

                # ✅ Удаляем найденный файл
                session_file.unlink()
                result["root_files_deleted"] += 1
                logger.info(f"🗑️ Удалён файл из корня: {session_file.name}")

        except Exception as e:
            error_msg = f"Ошибка очистки папки {root_dir}: {e}"
            logger.exception(error_msg)
            result["errors"].append(error_msg)

    # ✅ Логируем итог
    if result["parsing_dir_deleted"] or result["root_files_deleted"] > 0:
        logger.success(
            f"🧹 Очистка завершена: "
            f"parsing_dir={'✅' if result['parsing_dir_deleted'] else '⏭️'}, "
            f"root_files={result['root_files_deleted']}"
        )
    else:
        logger.debug("🧹 Нечего очищать — папки и файлы уже удалены")

    return result


def register_handlers_admin_connect_account():
    """✅ Регистрируем оба хендлера"""
    router.message.register(admin_connecting_account)
    router.message.register(receive_session_file)
