# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity, get_account_info
from database.database import write_account_to_db, User
from handlers.user.connect_account import creates_temporary_folder_for_accounts, sanitization_file_name
from keyboards.user.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.message(F.text == "🔐 Подключение аккаунта")
async def admin_connecting_account(message: Message, state: FSMContext):
    """Админ нажимает кнопку → бот просит .session файл(ы)"""
    await state.clear()
    telegram_id = message.from_user.id

    # ✅ Инициализируем очередь файлов в состоянии
    await state.update_data(received_files=[], processed_count=0, success_count=0, fail_count=0)

    await state.set_state(MyStates.waiting_for_session_file)
    await message.answer(
        t("connect_account_ask_session", lang="ru"),
        reply_markup=back_keyboard()
    )
    logger.info(f"Админ {telegram_id} начал добавление новых сессий")


MAX_SESSIONS_PER_BATCH = 10  # Максимум файлов за одну сессию


@router.message(MyStates.waiting_for_session_file, F.document)
async def receive_session_file(message: Message, state: FSMContext):
    """Получаем .session файл(ы) от админа и обрабатываем по очереди"""
    user_id = message.from_user.id  # получаем id пользователя
    user = User.get(User.user_id == user_id)
    document = message.document  # получаем файл сессии
    logger.info(f"User {user_id} отправил файл: {document.file_name}")

    # ✅ Проверяем расширение
    if not document.file_name.endswith('.session'):
        await message.answer(t("connect_account_invalid_file", lang=user.language))
        return

    # ✅ Получаем данные из состояния
    data = await state.get_data()

    if len(data.get("received_files", [])) >= MAX_SESSIONS_PER_BATCH:
        await message.answer(
            t("connect_account_limit_reached", lang=user.language, max=MAX_SESSIONS_PER_BATCH)
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
        await message.answer(
            t("connect_account_file_queued", lang=user.language, filename=document.file_name, total=total))
    try:
        # ✅ Создаём папку для временного хранения
        sessions_dir = creates_temporary_folder_for_accounts()
        # ✅ Санитизация имени файла

        local_file_path, safe_file_name = sanitization_file_name(document, sessions_dir)

        # ✅ Скачиваем файл
        await message.bot.download(document, destination=local_file_path)
        # ✅ Извлекаем путь без расширения для Telethon
        session_path_without_ext = str(local_file_path.with_suffix(""))
        # ✅ Проверяем валидность аккаунта
        checker = CheckingAccountsValidity(message=message, path=session_path_without_ext)
        client = await checker.connect_client()

        if client:
            account_info = await get_account_info(client)
            phone = account_info["phone"] or "unknown"
            first_name = account_info["first_name"] or ""

            # ✅ Конвертируем в StringSession и сохраняем в БД
            session_string = StringSession.save(client.session)
            write_account_to_db(session_string=session_string, phone_number=phone)
            await client.disconnect()
            # ✅ Удаляем временный .session файл
            if local_file_path.exists():
                local_file_path.unlink()
            # ✅ Обновляем статистику
            success_count += 1
            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            # ✅ Отправляем результат для этого файла
            await message.answer(
                t("connect_account_success", lang=user.language, filename=safe_file_name, phone=phone, name=first_name),
                parse_mode="HTML"
            )
        else:
            # ❌ Файл не валиден — удаляем
            if local_file_path.exists():
                local_file_path.unlink()
            fail_count += 1
            logger.warning(f"❌ Сессия не валидна: {safe_file_name}")
            await message.answer(t("connect_account_failed", lang=user.language, filename=safe_file_name),
                                 parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Ошибка при обработке {document.file_name}: {e}")
        fail_count += 1
        if local_file_path.exists():
            local_file_path.unlink()
        await message.answer(t("connect_account_error", lang=user.language, filename=safe_file_name), parse_mode="HTML")

    finally:
        # ✅ Обновляем состояние: файл обработан
        processed_count += 1
        await state.update_data(
            processed_count=processed_count,
            success_count=success_count,
            fail_count=fail_count
        )

        # dir_del = ['accounts/parsing', 'accounts/parsing_grup', 'accounts/ai', 'accounts/free']
        # for dir in dir_del:
        # ✅ Запускаем очистку
        # cleanup_session_files(
        #     parsing_dir=dir,
        #     root_dirs=[".", "accounts", "data", "sessions"]  # Укажите ваши корневые папки
        # )

        await message.answer(
            t("connect_account_processing_done", lang=user.language),
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )

    # ✅ Очищаем очередь в состоянии
    await state.update_data(received_files=[], processed_count=0, success_count=0, fail_count=0)


def cleanup_session_files(parsing_dir: str, root_dirs: list[str] | None = None):
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

    logger.debug("🧹 Очистка завершена")
