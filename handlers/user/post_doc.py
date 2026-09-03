import os
import re

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from groq import AsyncGroq
from loguru import logger

from account_manager.utilit import choosing_random_ai_model
from core.config import GROQ_API_KEY
from core.proxy import setup_proxy
from database.database import User, add_question
from handlers.user.handlers import handle_back_to_main_menu
from keyboards.user.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


def clean_ai_response(text: str) -> str:
    """
    Очищает ответ ИИ от блоков рассуждений <think>...</think> и незакрытых тегов <think>.
    
    Некоторые модели (например, DeepSeek-R1 или Qwen-Reasoning) возвращают мыслительный процесс
    внутри тегов <think>, что приводит к ошибке 'Unsupported start tag "think"' при попытке
    отправить сообщение в Telegram с parse_mode="HTML".

    :param text: (str) Исходный текст ответа ИИ.
    :return: (str) Очищенный текст для отправки пользователю.
    """
    if not text:
        return ""

    # Удаляем парные блоки рассуждений <think>...</think> (включая многострочные)
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Удаляем незакрытый тег <think> до конца текста (в случае обрыва ответа)
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
    # Удаляем оставшиеся одиночные теги <think> и </think>
    cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)
    # Удалит и <p>, и </p> (буква 'i' в ignorecase позволит ловить и <P>, и </P>)
    cleaned = re.sub(r'</?p>', '', cleaned, flags=re.IGNORECASE)
    # Удалит и <li>, и </li> (буква 'i' в ignorecase позволит ловить и <li>, и </li>)
    cleaned = re.sub(r'</?li>', '', cleaned, flags=re.IGNORECASE)
    # Удалит и <strong>, и </strong> (буква 'i' в ignorecase позволит ловить и <strong>, и </strong>)
    cleaned = re.sub(r'</?strong>', '', cleaned, flags=re.IGNORECASE)
    # Удалит и <ul>, и </ul> (буква 'i' в ignorecase позволит ловить и <ul>, и </ul>)
    cleaned = re.sub(r'</?ul>', '', cleaned, flags=re.IGNORECASE)
    # Удалит и <code>, и </code> (буква 'i' в ignorecase позволит ловить и <code>, и </code>)
    cleaned = re.sub(r'</?code>', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()


# Чтение базы знаний
def load_knowledge_base():
    """Загружает содержимое файла базы знаний."""
    if os.path.exists("doc/doc.md"):
        with open("doc/doc.md", "r", encoding="utf-8") as file:
            return file.read()
    else:
        return "База знаний не найдена. Пожалуйста, создайте файл doc/doc.md."


@router.message((F.text == t('instruction_button', 'ru')) | (F.text == t('instruction_button', 'en')))
async def send_instruction(message: Message, state: FSMContext):
    """
    Обработчик команды "Инструкция по использованию".
    Отправляет файл инструкции и переводит пользователя в состояние ожидания вопроса к ИИ.
    """
    await state.clear()
    user = User.get(User.user_id == message.from_user.id)
    user_lang = user.language if user.language != "unset" else "ru"

    try:
        # Отправляем файл инструкции
        await message.answer(
            text=t("instruction_question_prompt", lang=user_lang),
            parse_mode="html",
            reply_markup=back_keyboard(lang=user_lang)
        )
        # Устанавливаем состояние для ожидания вопроса
        await state.set_state(MyStates.waiting_for_instruction_question)

    except FileNotFoundError:
        await message.answer(t("instruction_file_not_found", lang=user_lang))
    except Exception as e:
        logger.exception(e)
        await message.answer(t("instruction_send_error", lang=user_lang))


@router.message(MyStates.waiting_for_instruction_question)
async def handle_instruction_question(message: Message, state: FSMContext):
    """
    Обрабатывает вопросы пользователя по инструкции с использованием Groq AI.
    """
    text_question = message.text  # Получаем вопрос пользователя
    user_db = User.get(User.user_id == message.from_user.id)
    user_lang = user_db.language if user_db.language != "unset" else "ru"

    if message.text == t('back_button', lang=user_lang):
        await handle_back_to_main_menu(message, state)
        return

    knowledge_base_content = load_knowledge_base()  # Загружаем базу знаний из файла doc/doc.md

    # Индикация того, что бот "печатает"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        setup_proxy()
        client = AsyncGroq(api_key=GROQ_API_KEY)

        system_prompt = t('ai_support_assistant_system_prompt', lang=user_lang)

        model = choosing_random_ai_model()
        logger.debug(f"Выбранная модель: {model} для дальнейшего консультативного ответа на вопрос: {text_question}")

        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\nБАЗА ЗНАНИЙ:\n{knowledge_base_content}"},
                {"role": "user", "content": text_question},
            ],
            model=model,
        )

        raw_answer = chat_completion.choices[0].message.content
        logger.info(f"Ответ от {model}: {raw_answer}")

        # Очищаем ответ ИИ от тегов мышления <think>...</think>, вызвающих ошибки парсинга Telegram
        answer = clean_ai_response(raw_answer)

        # Сохраняем вопрос пользователя и очищенный ответ в базу данных
        add_question(user_id=message.from_user.id, question=text_question, answer=answer)

        # Отправляем ответ пользователю. Если возникнет ошибка парсинга HTML, отправляем без parse_mode
        try:
            await message.answer(text=answer, parse_mode="HTML", reply_markup=back_keyboard(lang=user_lang))
        except TelegramBadRequest as parse_err:
            logger.warning(f"Ошибка парсинга HTML от Telegram ({parse_err}). Отправляем ответ с parse_mode=None")
            await message.answer(text=answer, parse_mode=None, reply_markup=back_keyboard(lang=user_lang))

    except Exception as e:
        logger.exception(e)
        await message.answer(t("instruction_send_error", lang=user_db.language))
