import random
import shutil
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity, get_account_info
from core.config import MAX_SESSIONS_PER_BATCH
from database.database import User, AccountFree
from database.personal_tracking import write_account_to_db
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


# async def connect_account_free_internal(message: Message, user_tg, state: FSMContext):
#     """Подключает случайный свободный аккаунт пользователю"""
#     await state.clear()
#
#     user, created = User.get_or_create(
#         user_id=user_tg.id,
#         defaults={
#             "username": user_tg.username,
#             "first_name": user_tg.first_name,
#             "last_name": user_tg.last_name,
#             "language": "unset"
#         }
#     )
#     # Определяем язык пользователя, который пользователь выбрал при старте бота
#     user_lang = determines_user_language(message_or_callback=message.from_user.id)
#
#     free_accounts = list(AccountFree.select())
#     if not free_accounts:
#         logger.warning(f"Нет доступных свободных аккаунтов для пользователя {user.user_id}")
#         await message.answer(
#             text=t("no_free_accounts", lang=user_lang),
#             reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
#         )
#         return
#
#     selected_account = random.choice(free_accounts)
#     session_string = selected_account.session_string
#     phone_number = selected_account.phone_number
#
#     logger.info(f"Подключаем свободный аккаунт {phone_number} пользователю {user.user_id}")
#
#     write_account_to_db(
#         session_string=session_string,
#         user_id=user.user_id
#     )
#
#     selected_account.delete_instance()
#
#     await message.answer(
#         text=t("account_connected_free", lang=user_lang),
#         reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
#     )


# @router.message((F.text == t('connect_free_account_button', 'ru')) | (F.text == t('connect_free_account_button', 'en')))
# async def handle_connect_account_free(message: Message, state: FSMContext):
#     """
#     Обработчик команды "🔐 Подключить свободный аккаунт" (текст).
#     """
#     await connect_account_free_internal(message, message.from_user, state)


@router.callback_query(F.data == "account_connect_free")
async def handle_connect_account_free_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🔐 Подключить свободный аккаунт".
    Подключает случайный свободный аккаунт пользователю
    """
    await callback.answer()
    # await connect_account_free_internal(callback.message, callback.from_user, state)
    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    user, created = User.get_or_create(
        user_id=callback.from_user.id,
        defaults={
            "username": callback.from_user.username,
            "first_name": callback.from_user.first_name,
            "last_name": callback.from_user.last_name,
            "language": "unset"
        }
    )

    free_accounts = list(AccountFree.select())
    if not free_accounts:
        logger.warning(f"Нет доступных свободных аккаунтов для пользователя {user.user_id}")
        await message.answer(
            text=t("no_free_accounts", lang=user_lang),
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
        )
        return

    selected_account = random.choice(free_accounts)
    session_string = selected_account.session_string
    phone_number = selected_account.phone_number

    logger.info(f"Подключаем свободный аккаунт {phone_number} пользователю {user.user_id}")

    write_account_to_db(
        session_string=session_string,
        user_id=user.user_id
    )

    selected_account.delete_instance()

    await message.answer(
        text=t("account_connected_free", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )


def creates_temporary_folder_for_accounts():
    """
    Создание временной папки для аккаунтов пользователя.
    :return:
    """
    sessions_dir = Path("accounts")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir


def sanitization_file_name(document, sessions_dir):
    """
    Очистка имени файла от недопустимых символов (файлов сессии).
    :return:
    """
    safe_file_name = "".join(c for c in document.file_name if c.isalnum() or c in "._-")
    local_file_path = sessions_dir / safe_file_name
    return local_file_path, safe_file_name


# async def connect_account_internal(message: Message, user_tg, state: FSMContext):
#     """Запрашивает у пользователя файл сессии для подключения аккаунта"""
#     await state.clear()
#     user, created = User.get_or_create(
#         user_id=user_tg.id,
#         defaults={
#             "username": user_tg.username,
#             "first_name": user_tg.first_name,
#             "last_name": user_tg.last_name,
#             "language": "unset"
#         }
#     )
#     # Определяем язык пользователя, который пользователь выбрал при старте бота
#     user_lang = determines_user_language(message_or_callback=message.from_user.id)
#     await message.answer(
#         text=t("connect_account", lang=user_lang),
#         reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
#     )
#     await state.set_state(MyStates.waiting_for_session_file_user)


@router.callback_query(F.data.in_({"settings_connect_account", "account_connect"}))
async def handle_connect_account_cb(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает команду подключения аккаунта (инлайн)"""
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.answer()
    # await connect_account_internal(callback.message, callback.from_user, state)
    await state.clear()
    user, created = User.get_or_create(
        user_id=callback.from_user.id,
        defaults={
            "username": callback.from_user.username,
            "first_name": callback.from_user.first_name,
            "last_name": callback.from_user.last_name,
            "language": "unset"
        }
    )
    await message.answer(
        text=t("connect_account", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.waiting_for_session_file_user)


# ✅ Фильтр: только документы И только в нужном состоянии
@router.message(MyStates.waiting_for_session_file_user, F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """Обработчик приёма файла сессии (.session) от пользователя"""
    local_file_path = None  # для безопасного удаления в finally

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    try:
        logger.info(f"User {message.from_user.id} отправил файл: {message.document.file_name}")

        # ✅ Проверяем расширение — если не .session, остаёмся в состоянии
        if not message.document.file_name.endswith('.session'):
            await message.answer(t("invalid_session_file", lang=user_lang))
            return  # state НЕ сбрасываем — ждём правильный файл

        sessions_dir = creates_temporary_folder_for_accounts()
        local_file_path, safe_file_name = sanitization_file_name(message.document, sessions_dir)

        await message.bot.download(message.document, destination=local_file_path)
        logger.info(f"✅ Файл скачан: {local_file_path}")

        await message.answer(t("session_file_received", lang=user_lang, filename=safe_file_name))

        session_path_without_ext = str(local_file_path.with_suffix(""))

        checker = CheckingAccountsValidity(path=session_path_without_ext)
        client = await checker.connect_client()

        if client:
            account_info = await get_account_info(client)
            phone = account_info["phone"] or "unknown"
            first_name = account_info["first_name"] or ""

            session_string = StringSession.save(client.session)
            write_account_to_db(
                session_string=session_string,
                user_id=message.from_user.id
            )
            await client.disconnect()

            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            await message.answer(
                t("session_connected_success", lang=user_lang, filename=safe_file_name, phone=phone,
                  name=first_name),
                parse_mode="HTML"
            )
        else:
            logger.warning(f"❌ Сессия {safe_file_name} не валидна для пользователя {message.from_user.id}")
            await message.answer(
                t("session_validation_failed", lang=user_lang, filename=safe_file_name),
                parse_mode="HTML"
            )
    except Exception as e:
        logger.exception(f"Ошибка при обработке сессии пользователя {message.from_user.id}: {e}")
        await message.answer(t("session_check_error", lang=user_lang))
    finally:
        # ✅ Удаляем временный файл в любом случае
        if local_file_path and local_file_path.exists():
            try:
                local_file_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete session file {local_file_path}: {e}")
        # ✅ Сбрасываем состояние только в конце
        await state.clear()


@router.callback_query(F.data == "admin_connect_account")
async def admin_connecting_account_cb(callback: CallbackQuery, state: FSMContext):
    """Админ нажимает кнопку → бот просит .session файл(ы) (инлайн). Инициирует процесс добавления сессий администратором"""
    await callback.answer()

    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    # ✅ Инициализируем очередь файлов в состоянии
    await state.update_data(received_files=[], processed_count=0, success_count=0, fail_count=0)

    await state.set_state(MyStates.waiting_for_session_file)
    await message.answer(
        t("connect_account_ask_session", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
    )
    logger.info(f"Админ {callback.from_user.id} начал добавление новых сессий")


@router.message(MyStates.waiting_for_session_file, F.document)
async def receive_session_file(message: Message, state: FSMContext):
    """Получаем .session файл(ы) от админа и обрабатываем по очереди"""
    # user_id = message.from_user.id  # получаем id пользователя
    # TODO Сделать единое определение языка пользователя во всем проекте
    # user = User.get(User.user_id == user_id)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    document = message.document  # получаем файл сессии
    logger.info(f"User {message.from_user.id} отправил файл: {document.file_name}")

    # ✅ Проверяем расширение
    if not document.file_name.endswith('.session'):
        await message.answer(t("connect_account_invalid_file", lang=user_lang))
        return

    # ✅ Получаем данные из состояния
    data = await state.get_data()

    if len(data.get("received_files", [])) >= MAX_SESSIONS_PER_BATCH:
        await message.answer(
            t("connect_account_limit_reached", lang=user_lang, max=MAX_SESSIONS_PER_BATCH)
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
            t("connect_account_file_queued", lang=user_lang, filename=document.file_name, total=total))
    try:
        # ✅ Создаём папку для временного хранения
        sessions_dir = creates_temporary_folder_for_accounts()
        # ✅ Санитизация имени файла

        local_file_path, safe_file_name = sanitization_file_name(document, sessions_dir)

        # ✅ Скачиваем файл
        # ToDo проверить в будущем document.file_id вместо document
        await message.bot.download(document, destination=local_file_path)
        # ✅ Извлекаем путь без расширения для Telethon
        session_path_without_ext = str(local_file_path.with_suffix(""))
        # ✅ Проверяем валидность аккаунта
        checker = CheckingAccountsValidity(path=session_path_without_ext)
        client = await checker.connect_client()

        if client:
            account_info = await get_account_info(client)
            phone = account_info["phone"] or "unknown"
            first_name = account_info["first_name"] or ""

            # ✅ Конвертируем в StringSession и сохраняем в БД
            session_string = StringSession.save(client.session)
            write_account_to_db(session_string=session_string, user_id=message.from_user.id)
            await client.disconnect()
            # ✅ Удаляем временный .session файл
            if local_file_path.exists():
                try:
                    local_file_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete session file {local_file_path}: {e}")
            # ✅ Обновляем статистику
            success_count += 1
            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            # ✅ Отправляем результат для этого файла
            await message.answer(
                t("connect_account_success", lang=user_lang, filename=safe_file_name, phone=phone, name=first_name),
                parse_mode="HTML"
            )
        else:
            # ❌ Файл не валиден — удаляем
            if local_file_path.exists():
                try:
                    local_file_path.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete session file {local_file_path}: {e}")
            fail_count += 1
            logger.warning(f"❌ Сессия не валидна: {safe_file_name}")
            await message.answer(t("connect_account_failed", lang=user_lang, filename=safe_file_name),
                                 parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Ошибка при обработке {document.file_name}: {e}")
        fail_count += 1
        if local_file_path.exists():
            try:
                local_file_path.unlink()
            except Exception as pe:
                logger.warning(f"Could not delete session file {local_file_path}: {pe}")
        await message.answer(t("connect_account_error", lang=user_lang, filename=safe_file_name), parse_mode="HTML")

    finally:
        # ✅ Обновляем состояние: файл обработан
        processed_count += 1
        await state.update_data(
            processed_count=processed_count,
            success_count=success_count,
            fail_count=fail_count
        )

        await message.answer(
            t("connect_account_processing_done", lang=user_lang),
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang)
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
