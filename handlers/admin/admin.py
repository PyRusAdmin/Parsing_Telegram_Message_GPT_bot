import csv
import os
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from loguru import logger  # https://github.com/Delgan/loguru

from account_manager.auth import CheckingAccountsValidity
from database.database import getting_account, get_all_questions
from handlers.user_language import determines_user_language
from locales.locales import t
import asyncio
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from core.config import ADMIN_USER_ID
from database.database import User
from keyboards.keyboards import admin_keyboard, category_method_keyboard, broadcast_preview_keyboard, back_keyboard
from states.states import CategoryMethod, BroadcastState


router = Router(name=__name__)


# async def export_questions_internal(message: Message):
#     """Экспортирует вопросы и ответы из базы данных в CSV-файл"""
#
#     # Определяем язык пользователя, который пользователь выбрал при старте бота
#     user_lang = determines_user_language(message_or_callback=message.from_user.id)
#
#     try:
#         questions = get_all_questions()
#         if not questions:
#             await message.answer(t("no_questions_in_db", lang=user_lang))
#             return
#
#         if not os.path.exists("exports"):
#             os.makedirs("exports")
#
#         file_path = f"exports/questions_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
#
#         with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
#             fieldnames = ["user_id", "question", "answer"]
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#             writer.writeheader()
#             for question_data in questions:
#                 writer.writerow(question_data)
#
#         await message.answer_document(FSInputFile(file_path), caption=t("questions_export_caption", lang=user_lang))
#         os.remove(file_path)
#
#     except Exception as e:
#         logger.exception(e)
#         await message.answer(t("export_error", lang=user_lang, error=str(e)))


@router.callback_query(F.data == "admin_export_questions")
async def export_questions_cb(callback: CallbackQuery):
    """
    Экспортирует вопросы и ответы из базы данных в CSV файл (инлайн).
    """
    await callback.answer()
    # await export_questions_internal(callback.message)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    try:
        questions = get_all_questions()
        if not questions:
            await message.answer(t("no_questions_in_db", lang=user_lang))
            return

        if not os.path.exists("exports"):
            os.makedirs("exports")

        file_path = f"exports/questions_export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["user_id", "question", "answer"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for question_data in questions:
                writer.writerow(question_data)

        await message.answer_document(FSInputFile(file_path), caption=t("questions_export_caption", lang=user_lang))
        os.remove(file_path)

    except Exception as e:
        logger.exception(e)
        await message.answer(t("export_error", lang=user_lang, error=str(e)))


# async def show_admin_panel(message: Message, user_id: int, state: FSMContext, edit: bool = False):
#     """Отображает главное меню панели администратора"""
#     try:
#         await state.clear()
#         try:
#             user = User.get(User.user_id == user_id)
#             user_lang = user.language if user.language != "unset" else "ru"
#         except Exception as e:
#             logger.exception(e)
#             user_lang = "ru"
#
#         if edit:
#             try:
#                 await callback.message.edit_text(text=t("admin_panel_message", lang=user_lang), parse_mode="HTML",
#                                         reply_markup=admin_keyboard(lang=user_lang))
#                 return
#             except Exception:
#                 pass
#
#         await message.answer(text=t("admin_panel_message", lang=user_lang), parse_mode="HTML",
#                              reply_markup=admin_keyboard(lang=user_lang))
#     except Exception as e:
#         logger.exception(e)


@router.callback_query(F.data == "menu_admin_panel")
async def admin_panel_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик команды Панель администратора (инлайн)"""
    # await show_admin_panel(callback.message, callback.from_user.id, state, edit=True)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    # try:
    await state.clear()
    # try:
    #     user = User.get(User.user_id == user_id)
    #     user_lang = user.language if user.language != "unset" else "ru"
    # except Exception as e:
    #     logger.exception(e)
    #     user_lang = "ru"

    # if edit:
    #     try:
    await callback.message.edit_text(text=t("admin_panel_message", lang=user_lang), parse_mode="HTML",
                            reply_markup=admin_keyboard(lang=user_lang))
    # return
    # except Exception:
    #     pass

    # await message.answer(text=t("admin_panel_message", lang=user_lang), parse_mode="HTML",
    #                      reply_markup=admin_keyboard(lang=user_lang))

    # except Exception as e:
    #     logger.exception(e)

    await callback.answer()


# @router.message(F.text == "🔄 Актуализация базы данных")
# async def update_db(message: Message):
#     """
#     🔄 Актуализация базы данных:
#     обновление ID и типа групп/каналов.
#
#     Последовательность действий:
#      - Сканирует папку accounts/parsing для поиска доступных сессий;
#      - Подключается к Telegram API для получения метаданных по username;
#      - Определяет тип сущности (канал, супергруппа и т.д.);
#      - Обновляет записи в базе через прямой UPDATE-запрос;
#      - При FloodWaitError переключается на следующий аккаунт;
#      - Отправляет прогресс и статистику в чат администратора.
#
#      Особенности:
#      - Доступ только для администраторов;
#      - Автоматическое переключение между аккаунтами при FloodWait;
#      - Используется режим WAL для избежания блокировок БД.
#
#      :param message: (Message) Входящее сообщение от администратора.
#      :return: None
#      """
#
#     available_sessions = getting_account()  # Получаем все аккаунты в базе данных
#     user = User.get(User.user_id == message.from_user.id)
#
#     await message.answer(
#         t("admin_found_accounts", lang=user.language, count=len(available_sessions))
#     )
#
#     try:
#         # 3. Убедимся, что БД подключена
#         if db.is_closed():
#             db.connect()
#
#         # 4. Получаем записи с username и group_type='group', которые ещё НЕ обновлены
#         groups_to_update = list(TelegramGroup.select().where(
#             (TelegramGroup.username.is_null(False)) &
#             (TelegramGroup.group_type == '')
#         ))
#
#         total_count = len(groups_to_update)
#         logger.info(f"Найдено {total_count} групп для обновления")
#
#         # Отправляем начальное сообщение
#         await message.answer(t("admin_db_actualization_start", lang=user.language, total=total_count))
#
#         processed = 0
#         updated = 0
#         errors = 0
#         current_session_index = 0
#
#         # 5. Основной цикл обработки групп
#         while processed < total_count and current_session_index < len(available_sessions):
#             # Подключаемся к текущему аккаунту
#
#             try:
#                 # ✅ Создаем checker БЕЗ path (он не нужен для работы с БД)
#                 checker = CheckingAccountsValidity(message=message)  # path=None по умолчанию
#                 client = await checker.start_random_client()
#
#                 await asyncio.sleep(1)
#
#                 current_account = available_sessions[current_session_index].split('/')[-1]
#                 logger.info(f"Используется аккаунт: {current_account}")
#                 await message.answer(t("admin_using_account", lang=user.language, account=current_account))
#
#                 # Обрабатываем группы с текущим аккаунтом
#                 for group in groups_to_update[processed:]:
#                     try:
#                         await asyncio.sleep(2)
#
#                         # Получаем сущность Telegram по username
#                         entity = await client.get_entity(group.username)
#                         logger.info(entity)
#
#                         if hasattr(entity, 'bot') or not hasattr(entity, 'broadcast'):
#                             logger.warning(
#                                 f"Пропускаем username {group.username}: это пользователь, а не канал/группа.")
#                             errors += 1
#                             processed += 1
#
#                             TelegramGroup.update(
#                                 group_type="Это пользователь, а не канал/группа.",
#                                 availability=''  # Группа неактивна
#                                 # ИЛИ, если используете status:Недействительный username
#                                 # status='invalid_username'
#                             ).where(TelegramGroup.group_hash == group.group_hash).execute()
#                             continue
#
#                         # Получаем полную информацию
#                         data = await get_full_info_group(client, entity)
#
#                         logger.info(f"Описание: {data["description"]}")
#
#                         update_group_channels_data_base(data, entity, group)
#
#                         processed += 1
#                         updated += 1
#
#                         logger.info(
#                             f"[{processed}/{total_count}] Обновлено: {group.username} | "
#                             f"ID: {entity.id} | Тип: {data["group_type"]} | Описание: {data["description"]} | Участники: {data["participants"]} | Аккаунт: {current_account}"
#                         )
#
#                         # Каждые 10 обновлений отправляем прогресс
#                         if processed % 10 == 0:
#                             await message.answer(
#                                 f"📊 Прогресс: {processed}/{total_count}\n"
#                                 f"✅ Обновлено: {updated}\n"
#                                 f"❌ Ошибок: {errors}\n"
#                                 f"📱 Аккаунт: {current_account}"
#                             )
#
#                         # Пауза для избежания бана от Telegram
#                         await asyncio.sleep(5)
#                     except TypeNotFoundError:
#                         logger.warning(
#                             "Не удалось определить тип сущности. Пропускаем... Попробуйте актуализировать Telethon")
#
#                     except peewee.IntegrityError:
#                         logger.warning(
#                             f"Пропускаем дубликат username {group.username} (аккаунт {current_account})"
#                         )
#                         TelegramGroup.update(
#                             group_type="Дублирующийся username",
#                             availability='inactive'  # Группа неактивна
#                             # ИЛИ, если используете status:Недействительный username
#                             # status='invalid_username'
#                         ).where(TelegramGroup.group_hash == group.group_hash).execute()
#                         errors += 1
#                         processed += 1
#                         continue  # переходим к следующей группе
#                     except FloodWaitError as e:
#                         wait_time = e.seconds
#                         errors += 1
#                         processed += 1  # Пропускаем группу
#
#                         logger.warning(
#                             f"FloodWait для {group.username} (аккаунт {current_account}): "
#                             f"нужно подождать {wait_time} секунд ({wait_time / 3600:.1f} часов)"
#                         )
#
#                         # Отправляем уведомление о FloodWait
#                         await message.answer(
#                             f"⚠️ FloodWait на аккаунте {current_account}\n\n"
#                             f"📊 Обработано: {processed}/{total_count}\n"
#                             f"✅ Обновлено: {updated}\n"
#                             f"❌ Ошибок: {errors}\n\n"
#                             f"⏱ Ожидание: {wait_time / 3600:.1f} ч ({wait_time} сек)"
#                         )
#
#                         # Переключаемся на следующий аккаунт
#                         current_session_index += 1
#
#                         if current_session_index < len(available_sessions):
#                             await message.answer(
#                                 f"🔄 Переключаюсь на аккаунт "
#                                 f"{available_sessions[current_session_index].split('/')[-1]}"
#                             )
#                         else:
#                             await message.answer(
#                                 "❌ Все аккаунты исчерпаны. Актуализация остановлена."
#                             )
#
#                         break  # Выходим из цикла групп, переключаемся на новый аккаунт
#
#                     except AuthKeyUnregisteredError:
#                         logger.error(f"Не валидный session файл: {current_account}")
#                         break  # Выходим из цикла групп, переключаемся на новый аккаунт
#                     except UsernameInvalidError:
#                         logger.warning(f"Недействительный username: {group.username}")
#                         # Помечаем как невалидный, чтобы не обрабатывать в будущем
#                         TelegramGroup.update(
#                             group_type="Недействительный username",
#                             availability=''  # Группа неактивна
#                             # ИЛИ, если используете status:Недействительный username
#                             # status='invalid_username'
#                         ).where(TelegramGroup.group_hash == group.group_hash).execute()
#                         errors += 1
#                         processed += 1
#                         continue  # переходим к следующей группе
#                     except UsernameNotOccupiedError:
#                         logger.warning(f"Недействительный username: {group.username}")
#                         # Помечаем как невалидный, чтобы не обрабатывать в будущем
#                         TelegramGroup.update(
#                             group_type="Недействительный username",
#                             availability=''  # Группа неактивна
#                             # ИЛИ, если используете status:Недействительный username
#                             # status='invalid_username'
#                         ).where(TelegramGroup.group_hash == group.group_hash).execute()
#                         errors += 1
#                         processed += 1
#                         continue  # переходим к следующей группе
#                     except ValueError as e:
#                         logger.warning(f"Недействительный username: {group.username} — {e}")
#                         TelegramGroup.update(
#                             group_type="Недействительный username",
#                             availability=''  # Группа неактивна
#                             # ИЛИ, если используете status:Недействительный username
#                             # status='invalid_username'
#                         ).where(TelegramGroup.group_hash == group.group_hash).execute()
#                     except Exception as e:
#                         logger.exception(e)
#             except Exception as e:
#                 logger.exception(e)
#                 await message.answer(
#                     t("admin_account_error", lang=user.language, account=current_account, error=str(e)))
#                 current_session_index += 1
#             finally:
#                 await client.disconnect()
#
#         # Финальная статистика
#         if processed >= total_count:
#             await message.answer(
#                 f"✅ Актуализация завершена!\n\n"
#                 f"📊 Всего обработано: {processed}/{total_count}\n"
#                 f"✅ Успешно обновлено: {updated}\n"
#                 f"❌ Ошибок: {errors}\n"
#                 f"📱 Использовано аккаунтов: {current_session_index + 1}/{len(available_sessions)}"
#             )
#         else:
#             await message.answer(
#                 f"⚠️ Актуализация остановлена.\n\n"
#                 f"📊 Обработано: {processed}/{total_count}\n"
#                 f"✅ Успешно обновлено: {updated}\n"
#                 f"❌ Ошибок: {errors}\n"
#                 f"📱 Все {len(available_sessions)} аккаунтов исчерпаны"
#             )
#
#     except Exception as e:
#         logger.exception(f"Критическая ошибка: {e}")
#         await message.answer(t("admin_critical_error", lang=user.language, error=str(e)))
#
#     finally:
#         if not db.is_closed():
#             db.close()
#
#         logger.info("Актуализация завершена.")


@router.message((F.text == t('check_accounts_button', 'ru')) | (F.text == t('check_accounts_button', 'en')))
async def checking_accounts_handler(message: Message, state: FSMContext):
    """✅ Проверка аккаунтов на валидность"""
    try:
        await state.clear()  # Сбрасываем текущее состояние FSM
        # user = User.get(User.user_id == message.from_user.id)
        # Определяем язык пользователя, который пользователь выбрал при старте бота
        user_lang = determines_user_language(message_or_callback=message.from_user.id)
        records = getting_account()  # Получаем все аккаунты в базе данных
        logger.info(f"Получено аккаунтов: {len(records)}")
        await message.answer(t("checking_accounts_start", lang=user_lang, count=len(records)))
        for session_name in records:
            logger.info(f"✅ Проверка аккаунта на валидность: {session_name}")
            # ✅ Проверка аккаунтов на валидность
            checker = CheckingAccountsValidity(
                message=message,
                # path=path
            )
            await checker.verify_account(session_name)
        await message.answer(
            t("checking_accounts_complete", lang=user_lang)
        )
    except Exception as e:
        logger.exception(e)


@router.message((F.text == t('assign_category_button', 'ru')) | (F.text == t('assign_category_button', 'en')))
async def checking_group_for_ai_db(message: Message, state: FSMContext):
    """Предлагает выбор метода присвоения категорий"""
    await state.set_state(CategoryMethod.waiting_for_method)
    # user = User.get(User.user_id == message.from_user.id)
    # Определяем язык пользователя, который пользователь выбрал при старте бота
    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    await message.answer(
        t("ai_category_select_method", lang=user_lang),
        reply_markup=category_method_keyboard(lang=user_lang),
        parse_mode="HTML"
    )


# ==================== 📢 МОДУЛЬ РАССЫЛКИ СООБЩЕНИЙ ====================

@router.callback_query(F.data == "admin_broadcast_start")
async def broadcast_start_cb(callback: CallbackQuery, state: FSMContext):
    """
    Старт процесса рассылки: запрос текста/медиа сообщения от администратора.
    """
    if callback.from_user.id not in ADMIN_USER_ID:
        await callback.answer("⛔ Доступ только для администраторов", show_alert=True)
        return

    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await state.set_state(BroadcastState.waiting_for_broadcast_message)

    await callback.message.edit_text(
        text=(
            "📢 <b>Рассылка сообщений пользователям</b>\n\n"
            "Отправьте сообщение, которое хотите разослать всем пользователям бота.\n\n"
            "• Поддерживается форматирование <b>HTML</b> (жирный, курсив, ссылки).\n"
            "• Можно прикрепить фото, видео, анимацию или документ с подписью.\n\n"
            "<i>Для отмены нажмите кнопку «Назад» ниже.</i>"
        ),
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
    )
    await callback.answer()


@router.message(BroadcastState.waiting_for_broadcast_message)
async def broadcast_message_received(message: Message, state: FSMContext):
    """
    Принимает сообщение для рассылки, сохраняет его параметры и отображает предпросмотр.
    """
    if message.from_user.id not in ADMIN_USER_ID:
        return

    user_lang = determines_user_language(message_or_callback=message.from_user.id)
    total_users = User.select().count()

    # Сохраняем ID сообщения и чата для последующего копирования через copy_message
    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
        total_recipients=total_users
    )
    await state.set_state(BroadcastState.waiting_for_broadcast_confirmation)

    # Отправляем предпросмотр (копию сообщения администратора)
    await message.answer("👁️ <b>Предпросмотр сообщения для рассылки:</b>", parse_mode="HTML")
    await message.copy_to(chat_id=message.chat.id)

    # Клавиатура подтверждения
    await message.answer(
        text=(
            f"📊 <b>Параметры рассылки:</b>\n\n"
            f"👥 Всего получателей в базе данных: <b>{total_users}</b>\n\n"
            f"Подтвердите отправку или отмените действие:"
        ),
        parse_mode="HTML",
        reply_markup=broadcast_preview_keyboard(lang=user_lang)
    )


@router.callback_query(BroadcastState.waiting_for_broadcast_confirmation, F.data == "admin_broadcast_cancel")
async def broadcast_cancel_cb(callback: CallbackQuery, state: FSMContext):
    """
    Отмена рассылки
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text="❌ <b>Рассылка отменена.</b>",
        parse_mode="HTML",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
    )
    await callback.answer()


@router.callback_query(BroadcastState.waiting_for_broadcast_confirmation, F.data == "admin_broadcast_send")
async def broadcast_send_cb(callback: CallbackQuery, state: FSMContext, bot):
    """
    Запуск цикла рассылки по всем зарегистрированным пользователям таблицы User.
    """
    if callback.from_user.id not in ADMIN_USER_ID:
        await callback.answer("⛔ Доступ только для администраторов", show_alert=True)
        return

    data = await state.get_data()
    source_chat_id = data.get("broadcast_chat_id")
    source_message_id = data.get("broadcast_message_id")
    await state.clear()

    if not source_chat_id or not source_message_id:
        await callback.answer("⚠️ Ошибка: сообщение для рассылки не найдено.", show_alert=True)
        return

    status_msg = await callback.message.edit_text(
        text="🚀 <b>Рассылка запущена... Пожалуйста, подождите.</b>",
        parse_mode="HTML"
    )
    await callback.answer()

    # Запрашиваем ID всех пользователей из таблицы User
    users = list(User.select(User.user_id))
    total = len(users)

    sent_count = 0
    blocked_count = 0
    error_count = 0

    logger.info(f"Администратор {callback.from_user.id} запустил рассылку для {total} пользователей")

    for idx, u in enumerate(users, start=1):
        target_user_id = u.user_id
        try:
            await bot.copy_message(
                chat_id=target_user_id,
                from_chat_id=source_chat_id,
                message_id=source_message_id
            )
            sent_count += 1
            # Небольшая задержка во избежание flood limits Telegram (30 сообщений/сек)
            await asyncio.sleep(0.05)

        except TelegramForbiddenError:
            # Пользователь заблокировал бота или удалил аккаунт
            blocked_count += 1
            logger.warning(f"Рассылка: пользователь {target_user_id} заблокировал бота")

        except TelegramRetryAfter as e:
            # Превышен лимит запросов, ждём требуемое количество секунд
            logger.warning(f"Рассылка: Flood limit! Сон {e.retry_after} сек.")
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(
                    chat_id=target_user_id,
                    from_chat_id=source_chat_id,
                    message_id=source_message_id
                )
                sent_count += 1
            except Exception as retry_err:
                logger.error(f"Рассылка: повторная ошибка для {target_user_id}: {retry_err}")
                error_count += 1

        except Exception as e:
            error_count += 1
            logger.error(f"Рассылка: ошибка отправки пользователю {target_user_id}: {e}")

        # Обновляем прогресс каждые 25 пользователей или в конце
        if idx % 25 == 0 or idx == total:
            try:
                await status_msg.edit_text(
                    text=(
                        f"🚀 <b>Выполняется рассылка...</b>\n\n"
                        f"Прогресс: <b>{idx}/{total}</b>\n"
                        f"✅ Отправлено: {sent_count}\n"
                        f"🚫 Заблокировали бота: {blocked_count}\n"
                        f"⚠️ Ошибок: {error_count}"
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass

    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    report_text = (
        f"🏁 <b>Рассылка завершена!</b>\n\n"
        f"📊 <b>Итоговый отчёт:</b>\n"
        f"• Всего получателей: <b>{total}</b>\n"
        f"• ✅ Успешно доставлено: <b>{sent_count}</b>\n"
        f"• 🚫 Бот заблокирован пользователем: <b>{blocked_count}</b>\n"
        f"• ⚠️ Другие ошибки: <b>{error_count}</b>"
    )

    try:
        await status_msg.edit_text(
            text=report_text,
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
        )
    except Exception:
        await callback.message.answer(
            text=report_text,
            parse_mode="HTML",
            reply_markup=back_keyboard(lang=user_lang, callback_data="menu_admin_panel")
        )

    logger.info(f"Рассылка завершена. Доставлено: {sent_count}, Заблокировали: {blocked_count}, Ошибок: {error_count}")
