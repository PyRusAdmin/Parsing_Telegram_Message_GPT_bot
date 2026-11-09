import math

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.users_groups import (
    dell_group, clear_all_user_groups, get_user_groups_paginated, get_user_channel_usernames,
)
from database.users_keywords import get_user_keywords_paginated, get_keywords_count
from database.users_personal_trackings import UsersPersonalTrackings
from handlers.user_language import determines_user_language
from keyboards.keyboards import (
    settings_keyboard, settings_menu_tracking_channels, settings_keywords_submenu_kb, settings_notification_group_kb,
    channels_list_keyboard, keywords_list_inline_kb, confirm_clear_keyboard, back_keyboard,
)
from locales.locales import t

router = Router(name=__name__)

PAGE_SIZE = 5  # Количество элементов на странице


# ==================== ГЛАВНОЕ МЕНЮ НАСТРОЕК ====================

@router.callback_query(F.data == "menu_settings")
async def handle_settings_menu_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки перехода в меню "Настройки".

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    await callback.message.edit_text(
        text=t("settings_message", lang=user_lang),
        reply_markup=settings_keyboard(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== 🌐 КАНАЛЫ ОТСЛЕЖИВАНИЯ ====================

@router.callback_query(F.data == "settings_section_channels")
async def handle_channels_section(callback: CallbackQuery, state: FSMContext):
    """
    Отображает подменю управления каналами отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    _, total = get_user_channel_usernames(callback.from_user.id)
    await callback.message.edit_text(
        text=t("settings_channels_title", lang=user_lang, total=total),
        reply_markup=settings_menu_tracking_channels(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_channels_list")
async def handle_channels_list(callback: CallbackQuery, state: FSMContext):
    """
    Отображает первую страницу списка каналов отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await _show_channels_page(callback, page=0)


@router.callback_query(F.data.startswith("ch_page:"))
async def handle_channels_page(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик пагинации списка каналов отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса с номером страницы.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    page = int(callback.data.split(":")[1])
    await _show_channels_page(callback, page=page)


async def _show_channels_page(callback: CallbackQuery, page: int):
    """
    Вспомогательная функция: отображает страницу со списком каналов отслеживания.

    :param callback: (CallbackQuery) Объект входящего callback-запроса.
    :param page: (int) Номер текущей страницы (начиная с 0).
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    records, total = get_user_groups_paginated(
        user_id=callback.from_user.id, page=page, page_size=PAGE_SIZE
    )

    if total == 0:
        await callback.answer(t("settings_channels_empty", lang=user_lang), show_alert=True)
        return

    total_pages = math.ceil(total / PAGE_SIZE)

    lines = [t("settings_channels_list_title", lang=user_lang, page=page + 1, total_pages=total_pages, total=total)]
    for i, rec in enumerate(records, start=page * PAGE_SIZE + 1):
        lines.append(f"{i}. <code>{rec.username_group}</code>")
    lines.append(t("settings_channels_list_hint", lang=user_lang))

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=channels_list_keyboard(records, page, total_pages, lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ch_del:"))
async def handle_channel_delete(callback: CallbackQuery, state: FSMContext):
    """
    Удаление выбранного канала отслеживания по кнопке.

    :param callback: (CallbackQuery) Объект входящего callback-запроса с username канала.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    username_group = callback.data[len("ch_del:"):]

    result = dell_group(user_id=callback.from_user.id, username_group=username_group)
    if result:
        await callback.answer(t("settings_channel_deleted", lang=user_lang, channel=username_group), show_alert=False)
    else:
        await callback.answer(t("settings_channel_not_found", lang=user_lang), show_alert=True)
        return

    # Обновляем список (возвращаемся на страницу 0)
    records, total = get_user_groups_paginated(
        user_id=callback.from_user.id, page=0, page_size=PAGE_SIZE
    )
    if total == 0:
        await callback.message.edit_text(
            text=f"{t('settings_channels_title', lang=user_lang, total=0)}\n\n{t('settings_channels_empty', lang=user_lang)}",
            reply_markup=settings_menu_tracking_channels(lang=user_lang),
            parse_mode="HTML"
        )
        return

    total_pages = math.ceil(total / PAGE_SIZE)
    lines = [t("settings_channels_list_title", lang=user_lang, page=1, total_pages=total_pages, total=total)]
    for i, rec in enumerate(records, start=1):
        lines.append(f"{i}. <code>{rec.username_group}</code>")
    lines.append(t("settings_channels_list_hint", lang=user_lang))

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=channels_list_keyboard(records, 0, total_pages, lang=user_lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings_channels_clear_confirm")
async def handle_channels_clear_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Запрос подтверждения пользователя на полную очистку списка каналов.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    _, total = get_user_channel_usernames(callback.from_user.id)
    await callback.message.edit_text(
        text=t("settings_channels_clear_confirm", lang=user_lang, total=total),
        reply_markup=confirm_clear_keyboard(
            confirm_cb="settings_channels_clear_do",
            cancel_cb="settings_section_channels",
            lang=user_lang
        ),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_channels_clear_do")
async def handle_channels_clear_do(callback: CallbackQuery, state: FSMContext):
    """
    Выполняет полную очистку всех каналов отслеживания пользователя.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    deleted = clear_all_user_groups(user_id=callback.from_user.id)
    await callback.message.edit_text(
        text=t("settings_channels_cleared", lang=user_lang, count=deleted),
        reply_markup=settings_menu_tracking_channels(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== 🔍 КЛЮЧЕВЫЕ СЛОВА ====================

@router.callback_query(F.data == "settings_section_keywords")
async def handle_keywords_section(callback: CallbackQuery, state: FSMContext):
    """
    Отображает подменю управления ключевыми словами.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    count = get_keywords_count(user_id=callback.from_user.id)
    await callback.message.edit_text(
        text=t("settings_keywords_title", lang=user_lang, total=count),
        reply_markup=settings_keywords_submenu_kb(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_keywords_list_inline")
async def handle_keywords_list_inline(callback: CallbackQuery, state: FSMContext):
    """
    Отображает первую страницу списка ключевых слов.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await _show_keywords_page(callback, page=0)


@router.callback_query(F.data.startswith("kw_page:"))
async def handle_keywords_page(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик пагинации списка ключевых слов.

    :param callback: (CallbackQuery) Объект входящего callback-запроса с номером страницы.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    page = int(callback.data.split(":")[1])
    await _show_keywords_page(callback, page=page)


async def _show_keywords_page(callback: CallbackQuery, page: int):
    """
    Вспомогательная функция: отображает страницу списка ключевых слов пользователя.

    :param callback: (CallbackQuery) Объект входящего callback-запроса.
    :param page: (int) Номер страницы (начиная с 0).
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    records, total = get_user_keywords_paginated(
        user_id=callback.from_user.id, page=page, page_size=PAGE_SIZE
    )

    if total == 0:
        await callback.answer(t("settings_keywords_empty", lang=user_lang), show_alert=True)
        return

    total_pages = math.ceil(total / PAGE_SIZE)

    lines = [t("settings_keywords_list_title", lang=user_lang, page=page + 1, total_pages=total_pages, total=total)]
    for i, rec in enumerate(records, start=page * PAGE_SIZE + 1):
        lines.append(f"{i}. <code>{rec.user_keyword}</code>")
    lines.append(t("settings_keywords_list_hint", lang=user_lang))

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=keywords_list_inline_kb(records, page, total_pages, lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("kw_del:"))
async def handle_keyword_delete(callback: CallbackQuery, state: FSMContext):
    """
    Удаление выбранного ключевого слова по кнопке ❌.

    :param callback: (CallbackQuery) Объект входящего callback-запроса с ID ключевого слова.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    from database.users_keywords import UsersKeywords
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    kw_id = int(callback.data.split(":")[1])

    try:
        kw_obj = UsersKeywords.get_by_id(kw_id)
        kw_text = kw_obj.user_keyword
        kw_obj.delete_instance()
        await callback.answer(t("settings_keyword_deleted", lang=user_lang, keyword=kw_text), show_alert=False)
    except Exception:
        await callback.answer(t("settings_keyword_not_found", lang=user_lang), show_alert=True)
        return

    # Обновляем список
    records, total = get_user_keywords_paginated(
        user_id=callback.from_user.id, page=0, page_size=PAGE_SIZE
    )
    if total == 0:
        await callback.message.edit_text(
            text=f"{t('settings_keywords_title', lang=user_lang, total=0)}\n\n{t('settings_keywords_empty', lang=user_lang)}",
            reply_markup=settings_keywords_submenu_kb(lang=user_lang),
            parse_mode="HTML"
        )
        return

    total_pages = math.ceil(total / PAGE_SIZE)
    lines = [t("settings_keywords_list_title", lang=user_lang, page=1, total_pages=total_pages, total=total)]
    for i, rec in enumerate(records, start=1):
        lines.append(f"{i}. <code>{rec.user_keyword}</code>")
    lines.append(t("settings_keywords_list_hint", lang=user_lang))

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=keywords_list_inline_kb(records, 0, total_pages, lang=user_lang),
        parse_mode="HTML"
    )


# ==================== 📢 ГРУППА УВЕДОМЛЕНИЙ ====================

@router.callback_query(F.data == "settings_section_notification")
async def handle_notification_section(callback: CallbackQuery, state: FSMContext):
    """
    Отображает подменю управления группой уведомлений.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    user_id = callback.from_user.id

    rec = UsersPersonalTrackings.get_or_none(UsersPersonalTrackings.user_id == user_id)
    group_link = str(rec.created_group_link or "") if rec else ""

    if group_link:
        info_text = t("settings_notification_created", lang=user_lang, link=group_link)
    else:
        info_text = t("settings_notification_not_created", lang=user_lang)

    await callback.message.edit_text(
        text=info_text,
        reply_markup=settings_notification_group_kb(lang=user_lang, group_link=group_link),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "settings_notification_no_group")
async def handle_notification_no_group(callback: CallbackQuery):
    """
    Уведомление во всплывающем окне, если группа ещё не была создана.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.answer(
        t("settings_notification_alert_no_group", lang=user_lang),
        show_alert=True
    )


@router.callback_query(F.data == "settings_notification_recreate")
async def handle_notification_recreate(callback: CallbackQuery, state: FSMContext):
    """
    Отображает инструкцию по пересозданию группы уведомлений.

    :param callback: (CallbackQuery) Объект входящего callback-запроса от пользователя.
    :param state: (FSMContext) Контекст машины состояний FSM.
    """
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text=t("settings_notification_recreate_text", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="settings_section_notification"),
        parse_mode="HTML"
    )
    await callback.answer()
