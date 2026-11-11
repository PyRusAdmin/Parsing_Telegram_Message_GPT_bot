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
from telethon.tl.functions.channels import JoinChannelRequest

from account_manager.auth import CheckingAccountsValidity, get_account_info
from core.config import MAX_SESSIONS_PER_BATCH, mobile_device, API_HASH, API_ID
from database.account_free import AccountFree
from database.users_groups import UsersGroups
from database.users_personal_trackings import (
    UsersPersonalTrackings, write_account_to_db, set_user_shared_account, clear_user_account
)
from database.users_accounts import write_account_to_user_table
from handlers.user.personal_tracking import PersonalTrackingState, execute_sign_in
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard, connect_account_keyboard, emoji_code_keypad_kb
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


def render_account_connect_text(user_id: int, lang: str = "ru") -> tuple[str, bool, bool]:
    """
    Формирует текст и состояние для экрана подключения аккаунтов.

    :param user_id: (int) ID пользователя Telegram.
    :param lang: (str) Код языка интерфейса.
    :return: (tuple[str, bool, bool]) Текст сообщения, has_account, is_shared.
    """
    rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    has_personal = bool(rec and rec.personal_account)
    has_shared = bool(rec and rec.shared_account and not rec.personal_account)
    has_account = has_personal or has_shared

    if has_personal:
        text = t("account_connect_personal", lang=lang)
    elif has_shared:
        text = t("account_connect_shared", lang=lang)
    else:
        text = t("account_connect_none", lang=lang)

    return text, has_account, has_shared


@router.callback_query(F.data == "account_connect_free")
async def handle_connect_account_free_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик подключения / переподключения свободного аккаунта от администратора.
    Проверяет валидность сессий, останавливает старое отслеживание при переподключении,
    выбирает рабочий аккаунт из пула AccountFree и подписывает его на отслеживаемый канал.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)

    # Проверяем, переподключение ли это
    rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    current_session = (rec.shared_account or "") if rec else ""
    is_reconnect = bool(rec and rec.shared_account)

    # Если было активно отслеживание — останавливаем старый клиент
    from account_manager.parser import stop_tracking, active_clients
    if str(user_id) in active_clients:
        try:
            await stop_tracking(user_id=user_id, message=callback.message)
            logger.info(f"🛑 Предыдущее отслеживание остановлено перед переподключением для user_id={user_id}")
        except Exception as st_err:
            logger.warning(f"Ошибка при остановке отслеживания перед переподключением: {st_err}")

    free_accounts = list(AccountFree.select())
    if not free_accounts:
        logger.warning(f"Нет доступных свободных аккаунтов для пользователя {user_id}")
        alert_text = t("no_free_accounts_detailed", lang=user_lang)
        kb = connect_account_keyboard(lang=user_lang, has_account=False, is_shared=False)
        try:
            await callback.message.edit_text(text=alert_text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await callback.message.answer(text=alert_text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
        return

    # При переподключении ставим другие аккаунты из пула в приоритет
    if is_reconnect and len(free_accounts) > 1:
        candidates = [acc for acc in free_accounts if acc.session_string != current_session] + [acc for acc in free_accounts if acc.session_string == current_session]
    else:
        candidates = free_accounts

    # Ищем первый рабочий и авторизованный аккаунт
    checker = CheckingAccountsValidity()
    selected_account = None
    account_info = None

    for candidate in candidates:
        try:
            client = await checker.client_connect_string_session(candidate.session_string)
            if client and await client.is_user_authorized():
                account_info = await get_account_info(client)
                await client.disconnect()
                selected_account = candidate
                break
            else:
                logger.warning(f"⚠️ Бесплатный аккаунт {candidate.phone_number} не авторизован или заблокирован. Удаляем из пула...")
                try:
                    candidate.delete_instance()
                except Exception:
                    pass
        except Exception as conn_err:
            logger.warning(f"Ошибка проверки аккаунта {candidate.phone_number}: {conn_err}")

    if not selected_account:
        logger.warning(f"Все свободные аккаунты не прошли проверку валидности для user_id={user_id}")
        alert_text = t("no_free_accounts_detailed", lang=user_lang)
        kb = connect_account_keyboard(lang=user_lang, has_account=False, is_shared=False)
        try:
            await callback.message.edit_text(text=alert_text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            await callback.message.answer(text=alert_text, reply_markup=kb, parse_mode="HTML")
        await callback.answer()
        return

    session_string = selected_account.session_string
    phone_number = selected_account.phone_number
    logger.info(f"{'Переподключаем' if is_reconnect else 'Назначаем'} свободный аккаунт {phone_number} пользователю {user_id}")

    set_user_shared_account(user_id=user_id, session_string=session_string)

    # Синхронизируем подписку на отслеживаемый канал пользователя, если он уже настроен
    user_groups = list(UsersGroups.select().where(UsersGroups.user_id == user_id))
    if user_groups:
        for g in user_groups:
            ch_link = (g.username_group or "").strip()
            if ch_link:
                try:
                    client = await checker.client_connect_string_session(session_string)
                    if client:
                        try:
                            entity = await client.get_entity(ch_link)
                            await client(JoinChannelRequest(channel=entity))
                            logger.info(f"✅ Новый бесплатный аккаунт подписан на отслеживаемый объект {ch_link}")
                        except Exception as join_err:
                            logger.debug(f"Уведомление при подписке на {ch_link}: {join_err}")
                        finally:
                            await client.disconnect()
                except Exception as sync_err:
                    logger.warning(f"Ошибка синхронизации канала {ch_link} для нового бесплатного аккаунта: {sync_err}")

    # Формируем имя и телефон для отображения
    phone_display = f"+{account_info.get('phone')}" if account_info and account_info.get('phone') else phone_number
    first_name = (account_info.get('first_name') or '') if account_info else ''
    last_name = (account_info.get('last_name') or '') if account_info else ''
    name_display = f"{first_name} {last_name}".strip() or "Telegram User"

    if is_reconnect:
        success_text = t(
            "free_account_reconnected_success",
            lang=user_lang,
            phone=phone_display,
            name=name_display
        )
        answer_text = "🔄 Свободный аккаунт переподключен!" if user_lang == "ru" else "🔄 Free account reconnected!"
    else:
        success_text = t(
            "free_account_connected_success",
            lang=user_lang,
            phone=phone_display,
            name=name_display
        )
        answer_text = "✅ Свободный аккаунт подключен!" if user_lang == "ru" else "✅ Free account connected!"

    kb = connect_account_keyboard(lang=user_lang, has_account=True, is_shared=True)
    try:
        await callback.message.edit_text(text=success_text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text=success_text, reply_markup=kb, parse_mode="HTML")
    await callback.answer(answer_text, show_alert=False)


def sanitization_file_name(document, account_id):
    """
    Очистка имени файла сессии от недопустимых символов и генерация безопасного пути.

    :param document: Объект входящего документа Telegram с файлом сессии.
    :param account_id: (int | str) ID аккаунта пользователя для формирования директории.
    :return: (tuple[Path, str] | tuple[None, None]) Кортеж (путь к локальному файлу, безопасное имя файла).
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


def delete_directory(folder_path, retries: int = 5, delay: float = 0.2):
    """
    Безопасно удаляет директорию и всё её содержимое рекурсивно с повторными попытками
    для корректного освобождения дескрипторов файлов в Windows.

    :param folder_path: (str | Path) Путь к удаляемой папке или файлу.
    :param retries: (int) Количество повторных попыток при блокировке файлов.
    :param delay: (float) Задержка между попытками в секундах.
    """
    if not folder_path:
        return
    import gc
    import time
    import stat
    import os

    gc.collect()
    path = Path(folder_path)
    if path.is_file():
        path = path.parent
    if not path.exists():
        return

    def _remove_readonly(func, p, excinfo):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    for attempt in range(retries):
        try:
            shutil.rmtree(path, onerror=_remove_readonly)
            logger.info(f"Папка {path} и всё её содержимое удалены.")
            return
        except FileNotFoundError:
            return
        except (PermissionError, OSError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
                gc.collect()
            else:
                logger.debug(f"Временная папка {path} временно занята процессом: {e}")


"""Меню подключения аккаунтов"""


@router.callback_query(F.data == "account_connect_menu")
async def handle_account_connect_menu(callback: CallbackQuery, state: FSMContext):
    """
    Отображает единое меню выбора способа подключения Telegram-аккаунта.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)

    text, has_account, is_shared = render_account_connect_text(user_id=user_id, lang=user_lang)
    kb = connect_account_keyboard(lang=user_lang, has_account=has_account, is_shared=is_shared)

    try:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text=text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "account_disconnect")
async def handle_account_disconnect_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик отключения текущего подключенного аккаунта пользователя.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_id = callback.from_user.id
    user_lang = determines_user_language(message_or_callback=user_id)

    # Если было активно отслеживание — останавливаем
    from account_manager.parser import stop_tracking
    await stop_tracking(user_id=user_id, message=callback.message)
    clear_user_account(user_id=user_id)

    text = (
        "✅ <b>Аккаунт успешно отключен.</b>\n\n"
        "Теперь вы можете подключить другой аккаунт (личный или свободный от администратора)."
        if user_lang == "ru"
        else "✅ <b>Account successfully disconnected.</b>\n\n"
             "You can now connect another account (personal or administrator's free account)."
    )
    kb = connect_account_keyboard(lang=user_lang, has_account=False, is_shared=False)
    try:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        await callback.message.answer(text=text, reply_markup=kb, parse_mode="HTML")
    await callback.answer("Аккаунт отключен" if user_lang == "ru" else "Account disconnected", show_alert=False)


"""Подключение аккаунта через сессию Telethon"""


@router.callback_query(F.data == "connect_account_session")
async def handle_connect_account_cb(callback: CallbackQuery, state: FSMContext):
    """
    Инициирует подключение аккаунта через файл .session Telethon.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.answer()

    await callback.message.answer(
        text=t("connect_account", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="account_connect_menu")
    )
    await state.set_state(MyStates.waiting_for_session_file_user)


# ✅ Фильтр: только документы И только в нужном состоянии
@router.message(MyStates.waiting_for_session_file_user, F.document)
async def handle_account_file(message: Message, state: FSMContext):
    """
    Обработчик приёма и валидации файла сессии (.session) от пользователя.

    :param message: (Message) Входящее сообщение Telegram с прикрепленным документом сессии.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """

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
            import gc
            gc.collect()
            delete_directory(folder_path=local_file_path.parent)
        # ✅ Сбрасываем состояние только в конце
        await state.clear()


@router.callback_query(F.data == "admin_connect_account")
async def admin_connecting_account_cb(callback: CallbackQuery, state: FSMContext):
    """
    Инициирует процесс добавления сессий администратором (инлайн).

    :param callback: (CallbackQuery) Объект входящего callback-запроса от администратора.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
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
    """
    Получает файл(ы) сессий от администратора и обрабатывает их последовательно.

    :param message: (Message) Входящее сообщение Telegram с прикрепленным .session файлом.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
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
            import gc
            gc.collect()
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
    Полная очистка временных .session файлов.

    :param parsing_dir: (str) Папка с временными сессиями (удаляется полностью).
    :param root_dirs: (list[str] | None) Список корневых папок для поиска "забытых" файлов сессий.
    :return: (dict) Словарь со статистикой очистки (parsing_dir_deleted, root_files_deleted, errors).
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
    Начало шага авторизации Telegram-аккаунта по номеру телефона.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await state.set_state(PersonalTrackingState.waiting_for_phone_number)
    await callback.message.answer(
        t("pt_phone_prompt", lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(PersonalTrackingState.waiting_for_phone_number)
async def process_phone_number_input(message: Message, state: FSMContext):
    """
    Обработка ввода номера телефона и запрос кода подтверждения через Telethon.

    :param message: (Message) Объект входящего сообщения Telegram с номером телефона.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    phone = message.text.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    if len(phone) < 10 or not phone[1:].isdigit():
        await message.answer(
            t("pt_phone_invalid", lang=user_lang),
            parse_mode="HTML")
        return

    status_msg = await message.answer(
        t("pt_sending_code_status", lang=user_lang, phone=phone),
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

        msg_body = (
            f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
            f"📱 <b>Номер:</b> <code>{phone}</code>\n"
            f"🔢 <b>Введенный код:</b> <code>_ _ _ _ _</code>\n\n"
            f"⚠️ <i>Используйте эмодзи-клавиатуру ниже для выбора цифр кода, чтобы избежать блокировки от Telegram:</i>"
        ) if user_lang == "ru" else (
            f"📩 <b>Verification code sent to your Telegram!</b>\n\n"
            f"📱 <b>Number:</b> <code>{phone}</code>\n"
            f"🔢 <b>Entered code:</b> <code>_ _ _ _ _</code>\n\n"
            f"⚠️ <i>Use the emoji keypad below to select code digits:</i>"
        )

        await status_msg.edit_text(
            msg_body,
            reply_markup=emoji_code_keypad_kb(lang=user_lang),
            parse_mode="HTML"
        )
    except PhoneNumberInvalidError:
        await status_msg.edit_text(t("pt_phone_invalid", lang=user_lang))
        await state.clear()
    except FloodWaitError as fwe:
        await status_msg.edit_text(t("pt_phone_flood", lang=user_lang, seconds=fwe.seconds))
        await state.clear()
    except Exception as e:
        logger.exception(f"❌ Ошибка отправки кода на номер {phone}: {e}")
        await status_msg.edit_text(t("pt_code_request_error", lang=user_lang, error=str(e)))
        await state.clear()


@router.callback_query(F.data.startswith("pt_digit_"), PersonalTrackingState.waiting_for_auth_code)
async def cb_handle_emoji_digit(callback: CallbackQuery, state: FSMContext):
    """
    Обработка ввода цифр кода подтверждения с помощью защищённой эмодзи-клавиатуры.

    :param callback: (CallbackQuery) Объект входящего callback-запроса с нажатой кнопкой.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    action = callback.data.replace("pt_digit_", "")
    data = await state.get_data()
    current_code = data.get("current_code", "")

    if action == "clear":
        current_code = current_code[:-1]
    elif action == "submit":
        if len(current_code) < 5:
            await callback.answer(t("pt_code_need_5_digits", lang=user_lang), show_alert=True)
            return
        await execute_sign_in(callback, state, current_code)
        return
    elif action.isdigit():
        if len(current_code) < 5:
            current_code += action

    await state.update_data(current_code=current_code)

    digits_display = " ".join(list(current_code) + ["_"] * (5 - len(current_code)))
    phone = data.get("phone_number", "")

    code_disp_text = (
        f"📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>\n\n"
        f"📱 <b>Номер:</b> <code>{phone}</code>\n"
        f"🔢 <b>Введенный код:</b> <code>{digits_display}</code>\n\n"
        f"⚠️ <i>Используйте эмодзи-клавиатуру ниже для выбора цифр кода:</i>"
    ) if user_lang == "ru" else (
        f"📩 <b>Verification code sent to your Telegram!</b>\n\n"
        f"📱 <b>Number:</b> <code>{phone}</code>\n"
        f"🔢 <b>Entered code:</b> <code>{digits_display}</code>\n\n"
        f"⚠️ <i>Use the emoji keypad below to select code digits:</i>"
    )

    try:
        await callback.message.edit_text(
            code_disp_text,
            reply_markup=emoji_code_keypad_kb(lang=user_lang),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.answer()

    # Авто-отправка при вводе 5 цифр
    if len(current_code) == 5:
        await execute_sign_in(callback, state, current_code)
