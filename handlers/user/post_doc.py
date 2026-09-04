import os
import re

import groq
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from groq import AsyncGroq
from loguru import logger

from account_manager.utilit import choosing_random_ai_model
from core.config import GROQ_API_KEY, ADMIN_USER_ID
from core.proxy import setup_proxy
from database.database import User, add_question
from handlers.user.handlers import handle_back_to_main_menu
from keyboards.user.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


def clean_ai_response(text: str) -> str:
    """
    Очищает ответ ИИ от блоков рассуждений <think>...</think>, Markdown-разметки (###, **, *, `, _)
    и HTML-тегов, чтобы пользователь получал чистый простой текст без разметки.
    """
    if not text:
        return ""

    # Удаляем парные блоки рассуждений <think>...</think> (включая многострочные)
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Удаляем незакрытый тег <think> до конца текста (в случае обрыва ответа)
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)

    # Удаляем заголовки Markdown (###, ##, #)
    cleaned = re.sub(r'^#{1,6}\s*', '', cleaned, flags=re.MULTILINE)

    # Удаляем жирный шрифт и курсив Markdown (**текст**, *текст*, __текст__, _текст_)
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)
    cleaned = re.sub(r'__(.*?)__', r'\1', cleaned)
    cleaned = re.sub(r'_(.*?)_', r'\1', cleaned)

    # Удаляем обратные кавычки и блоки кода (`текст` или ```текст```)
    cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)

    # Удаляем любые HTML-теги (<p>, <strong>, <code>, <ul>, <li> и т.д.)
    cleaned = re.sub(r'<[^>]+>', '', cleaned)

    # Нормализуем дублирующиеся переносы строк
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

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

        # Отправляем очищенный простой текст пользователю без разметки
        await message.answer(text=answer, parse_mode=None, reply_markup=back_keyboard(lang=user_lang))

    except groq.RateLimitError as e:
        logger.error(f"Ошибка ограничения скорости запросов к Groq AI: {e}")
        # Отправляем сообщение администратору с ошибкой от Groq AI
        await message.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"Модель {model} недоступна. Ошибка: {e}",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.exception(e)
        await message.answer(t("instruction_send_error", lang=user_db.language))
