import math

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import PersonalTracking
from database.group_user_database import (
    dell_group,
    clear_all_user_groups,
    get_user_groups_paginated,
    get_user_channel_usernames,
)
from database.keywords_user_database import (
    get_user_keywords_paginated,
    get_keywords_count,
)
from handlers.user_language import determines_user_language
from keyboards.keyboards import (
    settings_keyboard,
    settings_menu_tracking_channels,
    settings_keywords_submenu_kb,
    settings_notification_group_kb,
    channels_list_keyboard,
    keywords_list_inline_kb,
    confirm_clear_keyboard,
    back_keyboard,
)
from locales.locales import t

router = Router(name=__name__)

PAGE_SIZE = 5  # Количество элементов на странице


# ==================== ГЛАВНОЕ МЕНЮ НАСТРОЕК ====================

@router.callback_query(F.data == "menu_settings")
async def handle_settings_menu_cb(callback: CallbackQuery, state: FSMContext):
    """Обработчик инлайн-кнопки ⚙️ Настройки"""
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
    """Подменю 🌐 Каналы отслеживания"""
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    _, total = get_user_channel_usernames(callback.from_user.id)
    await callback.message.edit_text(
        text=f"🌐 <b>Каналы отслеживания</b>\n\n📊 Всего каналов: <b>{total}</b>\n\nВыберите действие:",
        reply_markup=settings_menu_tracking_channels(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_channels_list")
async def handle_channels_list(callback: CallbackQuery, state: FSMContext):
    """Список каналов с пагинацией — страница 0"""
    await _show_channels_page(callback, page=0)


@router.callback_query(F.data.startswith("ch_page:"))
async def handle_channels_page(callback: CallbackQuery, state: FSMContext):
    """Переключение страниц списка каналов"""
    page = int(callback.data.split(":")[1])
    await _show_channels_page(callback, page=page)


async def _show_channels_page(callback: CallbackQuery, page: int):
    """Вспомогательная функция: показывает страницу списка каналов."""
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    records, total = get_user_groups_paginated(
        user_id=callback.from_user.id, page=page, page_size=PAGE_SIZE
    )

    if total == 0:
        await callback.answer("📭 Список каналов пуст.", show_alert=True)
        return

    total_pages = math.ceil(total / PAGE_SIZE)

    lines = [f"📋 <b>Список каналов</b> (стр. {page + 1}/{total_pages}) · всего: {total}\n"]
    for i, rec in enumerate(records, start=page * PAGE_SIZE + 1):
        lines.append(f"{i}. <code>{rec.username_group}</code>")
    lines.append("\n<i>Нажмите ❌ на канале, чтобы удалить его.</i>")

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=channels_list_keyboard(records, page, total_pages, lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("ch_del:"))
async def handle_channel_delete(callback: CallbackQuery, state: FSMContext):
    """Удаление одного канала по нажатию на кнопку ❌"""
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    username_group = callback.data[len("ch_del:"):]

    result = dell_group(user_id=callback.from_user.id, username_group=username_group)
    if result:
        await callback.answer(f"✅ Канал удалён: {username_group}", show_alert=False)
    else:
        await callback.answer("⚠️ Канал не найден.", show_alert=True)
        return

    # Обновляем список (возвращаемся на страницу 0)
    records, total = get_user_groups_paginated(
        user_id=callback.from_user.id, page=0, page_size=PAGE_SIZE
    )
    if total == 0:
        await callback.message.edit_text(
            text="🌐 <b>Каналы отслеживания</b>\n\n📭 Список каналов пуст.",
            reply_markup=settings_menu_tracking_channels(lang=user_lang),
            parse_mode="HTML"
        )
        return

    total_pages = math.ceil(total / PAGE_SIZE)
    lines = [f"📋 <b>Список каналов</b> (стр. 1/{total_pages}) · всего: {total}\n"]
    for i, rec in enumerate(records, start=1):
        lines.append(f"{i}. <code>{rec.username_group}</code>")
    lines.append("\n<i>Нажмите ❌ на канале, чтобы удалить его.</i>")

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=channels_list_keyboard(records, 0, total_pages, lang=user_lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings_channels_clear_confirm")
async def handle_channels_clear_confirm(callback: CallbackQuery, state: FSMContext):
    """Запрос подтверждения очистки списка каналов"""
    _, total = get_user_channel_usernames(callback.from_user.id)
    await callback.message.edit_text(
        text=f"🧹 <b>Очистить весь список каналов?</b>\n\n"
             f"Будет удалено <b>{total}</b> канал(ов). Это действие нельзя отменить.",
        reply_markup=confirm_clear_keyboard(
            confirm_cb="settings_channels_clear_do",
            cancel_cb="settings_section_channels"
        ),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_channels_clear_do")
async def handle_channels_clear_do(callback: CallbackQuery, state: FSMContext):
    """Выполняет очистку всех каналов"""
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    deleted = clear_all_user_groups(user_id=callback.from_user.id)
    await callback.message.edit_text(
        text=f"✅ <b>Список каналов очищен.</b>\n\nУдалено каналов: <b>{deleted}</b>",
        reply_markup=settings_menu_tracking_channels(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ==================== 🔍 КЛЮЧЕВЫЕ СЛОВА ====================

@router.callback_query(F.data == "settings_section_keywords")
async def handle_keywords_section(callback: CallbackQuery, state: FSMContext):
    """Подменю 🔍 Ключевые слова"""
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    count = get_keywords_count(user_id=callback.from_user.id)
    await callback.message.edit_text(
        text=f"🔍 <b>Ключевые слова</b>\n\n📊 Всего слов: <b>{count}</b>\n\nВыберите действие:",
        reply_markup=settings_keywords_submenu_kb(lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_keywords_list_inline")
async def handle_keywords_list_inline(callback: CallbackQuery, state: FSMContext):
    """Список ключевых слов с пагинацией — страница 0"""
    await _show_keywords_page(callback, page=0)


@router.callback_query(F.data.startswith("kw_page:"))
async def handle_keywords_page(callback: CallbackQuery, state: FSMContext):
    """Переключение страниц списка ключевых слов"""
    page = int(callback.data.split(":")[1])
    await _show_keywords_page(callback, page=page)


async def _show_keywords_page(callback: CallbackQuery, page: int):
    """Вспомогательная функция: показывает страницу ключевых слов."""
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    records, total = get_user_keywords_paginated(
        user_id=callback.from_user.id, page=page, page_size=PAGE_SIZE
    )

    if total == 0:
        await callback.answer("📭 Список ключевых слов пуст.", show_alert=True)
        return

    total_pages = math.ceil(total / PAGE_SIZE)

    lines = [f"🔍 <b>Ключевые слова</b> (стр. {page + 1}/{total_pages}) · всего: {total}\n"]
    for i, rec in enumerate(records, start=page * PAGE_SIZE + 1):
        lines.append(f"{i}. <code>{rec.user_keyword}</code>")
    lines.append("\n<i>Нажмите ❌ на слове, чтобы удалить его.</i>")

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=keywords_list_inline_kb(records, page, total_pages, lang=user_lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("kw_del:"))
async def handle_keyword_delete(callback: CallbackQuery, state: FSMContext):
    """Удаление одного ключевого слова по нажатию ❌"""
    from database.keywords_user_database import Keywords
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    kw_id = int(callback.data.split(":")[1])

    try:
        kw_obj = Keywords.get_by_id(kw_id)
        kw_text = kw_obj.user_keyword
        kw_obj.delete_instance()
        await callback.answer(f"✅ Удалено: {kw_text}", show_alert=False)
    except Exception:
        await callback.answer("⚠️ Слово не найдено.", show_alert=True)
        return

    # Обновляем список
    records, total = get_user_keywords_paginated(
        user_id=callback.from_user.id, page=0, page_size=PAGE_SIZE
    )
    if total == 0:
        await callback.message.edit_text(
            text="🔍 <b>Ключевые слова</b>\n\n📭 Список пуст.",
            reply_markup=settings_keywords_submenu_kb(lang=user_lang),
            parse_mode="HTML"
        )
        return

    total_pages = math.ceil(total / PAGE_SIZE)
    lines = [f"🔍 <b>Ключевые слова</b> (стр. 1/{total_pages}) · всего: {total}\n"]
    for i, rec in enumerate(records, start=1):
        lines.append(f"{i}. <code>{rec.user_keyword}</code>")
    lines.append("\n<i>Нажмите ❌ на слове, чтобы удалить его.</i>")

    await callback.message.edit_text(
        text="\n".join(lines),
        reply_markup=keywords_list_inline_kb(records, 0, total_pages, lang=user_lang),
        parse_mode="HTML"
    )


# ==================== 📢 ГРУППА УВЕДОМЛЕНИЙ ====================

@router.callback_query(F.data == "settings_section_notification")
async def handle_notification_section(callback: CallbackQuery, state: FSMContext):
    """Подменю 📢 Группа уведомлений"""
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    user_id = callback.from_user.id

    rec = PersonalTracking.get_or_none(PersonalTracking.user_id == user_id)
    group_link = str(rec.created_group_link or "") if rec else ""

    if group_link:
        info_text = (
            f"📢 <b>Группа уведомлений</b>\n\n"
            f"✅ Группа создана.\n"
            f"🔗 <a href='{group_link}'>Перейти в группу</a>"
        )
    else:
        info_text = (
            "📢 <b>Группа уведомлений</b>\n\n"
            "❌ Группа ещё не создана.\n\n"
            "<i>Создайте группу через раздел «🎯 Персональное отслеживание».</i>"
        )

    await callback.message.edit_text(
        text=info_text,
        reply_markup=settings_notification_group_kb(lang=user_lang, group_link=group_link),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "settings_notification_no_group")
async def handle_notification_no_group(callback: CallbackQuery):
    """Уведомление когда группа не создана"""
    await callback.answer(
        "❌ Группа не создана. Перейдите в «🎯 Персональное отслеживание» для её создания.",
        show_alert=True
    )


@router.callback_query(F.data == "settings_notification_recreate")
async def handle_notification_recreate(callback: CallbackQuery, state: FSMContext):
    """Пересоздание группы уведомлений — переход в персональное отслеживание"""
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    await callback.message.edit_text(
        text=(
            "🔄 <b>Пересоздать группу уведомлений</b>\n\n"
            "Для пересоздания группы перейдите в раздел "
            "«🎯 Персональное отслеживание» → «➕ Добавить отслеживание группы».\n\n"
            "<i>Новая группа будет создана автоматически при добавлении нового отслеживания.</i>"
        ),
        reply_markup=back_keyboard(lang=user_lang, callback_data="settings_section_notification"),
        parse_mode="HTML"
    )
    await callback.answer()
