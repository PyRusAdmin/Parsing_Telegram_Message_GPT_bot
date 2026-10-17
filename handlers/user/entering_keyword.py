from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from database.database import Keywords, get_keywords_count, add_user_keywords
from handlers.user_language import determines_user_language
from keyboards.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


@router.callback_query(F.data == "settings_enter_keyword")
async def handle_enter_keyword_menu_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🔍 Ввод ключевого слова".
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    logger.info(
        f"Пользователь {callback.from_user.id} {callback.from_user.username} {callback.from_user.first_name} {callback.from_user.last_name} перешел в меню 🔍 Ввод ключевого слова"
    )

    await callback.message.answer(
        t("enter_keyword", lang=user_lang),
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings")
    )
    await state.set_state(MyStates.entering_keyword)
    await callback.answer()


@router.message(MyStates.entering_keyword)
async def handle_keywords_submission(message: Message, state: FSMContext):
    """
    Обработчик ввода ключевых слов пользователем.

    Принимает текст, разбивает его по строкам, очищает от пустых элементов
    и добавляет каждое ключевое слово в таблицу базы данных пользователя.
    Поддерживает массовую загрузку (несколько слов через перенос строки).

    После добавления отправляет пользователю подтверждение с общим количеством слов
    и сбрасывает состояние FSM.

    :param message: (Message) Объект входящего сообщения с ключевыми словами.
    :param state: (FSMContext) Контекст машины состояний, используется для сброса состояния после обработки.
    :return: None
    """
    user_lang = determines_user_language(message_or_callback=message.from_user.id)

    # Защита на случай, если прислали не текст (фото, стикер и т.д.)
    if not message.text:
        await message.answer(text=t("no_keywords_entered", lang=user_lang))
        return

    raw_input = message.text.strip()
    logger.info(f"Пользователь {message.from_user.id} ввёл ключевые слова: {raw_input}")

    keywords_list = [
        keyword.strip()
        for keyword in raw_input.split('\n')
        if keyword.strip()
    ]

    if not keywords_list:
        await message.answer(
            text=t("no_keywords_entered", lang=user_lang)
        )
        await state.clear()
        return
    # Безопасно добавляет список ключевых слов, пропуская дубликаты.
    add_user_keywords(user_id=message.from_user.id, keywords=keywords_list)

    await message.answer(
        text=f"✅ Ключевые слова добавлены.\n\n📊 Всего ключевых слов: <b>{get_keywords_count(user_id=message.from_user.id)}</b>",
        reply_markup=back_keyboard(lang=user_lang, callback_data="menu_settings"),
        parse_mode="HTML"
    )

    logger.info(
        f"Пользователь {message.from_user.id} добавил ключевые слова. Всего ключевых слов у пользователя {get_keywords_count(user_id=message.from_user.id)}")
    await state.clear()  # Завершаем текущее состояние машины состояния
