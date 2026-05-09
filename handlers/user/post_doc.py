import os

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from groq import AsyncGroq
from loguru import logger

from core.config import GROQ_API_KEY
from core.proxy import setup_proxy
from database.database import User, add_question
from handlers.user.handlers import handle_back_to_main_menu
from keyboards.user.keyboards import back_keyboard
from locales.locales import t
from states.states import MyStates

router = Router(name=__name__)


# Чтение базы знаний
def load_knowledge_base():
    """Загружает содержимое файла базы знаний."""
    if os.path.exists("doc/doc.md"):
        with open("doc/doc.md", "r", encoding="utf-8") as file:
            return file.read()
    else:
        return "База знаний не найдена. Пожалуйста, создайте файл doc/doc.md."


@router.message(F.text == "📖 Инструкция по использованию")
async def send_instruction(message: Message, state: FSMContext):
    """
    Обработчик команды "Инструкция по использованию".
    Отправляет файл инструкции и переводит пользователя в состояние ожидания вопроса к ИИ.
    """
    await state.clear()
    user = User.get(User.user_id == message.from_user.id)

    try:
        # Отправляем файл инструкции
        await message.answer(
            text=f"🤖 <b>Вы можете задать мне любой вопрос по использованию бота, и я отвечу вам!</b>",
            parse_mode="html",
            reply_markup=back_keyboard()
        )
        # Устанавливаем состояние для ожидания вопроса
        await state.set_state(MyStates.waiting_for_instruction_question)

    except FileNotFoundError:
        await message.answer(t("instruction_file_not_found", lang=user.language))
    except Exception as e:
        logger.exception(e)
        await message.answer(t("instruction_send_error", lang=user.language))


@router.message(MyStates.waiting_for_instruction_question)
async def handle_instruction_question(message: Message, state: FSMContext):
    """
    Обрабатывает вопросы пользователя по инструкции с использованием Groq AI.
    """
    text_question = message.text  # Получаем вопрос пользователя

    if message.text == "⬅️ Назад":
        await handle_back_to_main_menu(message, state)
        return

    knowledge_base_content = load_knowledge_base()  # Загружаем базу знаний из файла doc/doc.md
    user_db = User.get(User.user_id == message.from_user.id)

    # Индикация того, что бот "печатает"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        setup_proxy()
        client = AsyncGroq(api_key=GROQ_API_KEY)

        system_prompt = (
            "Вы — квалифицированный помощник службы поддержки Telegram-бота AutoParseAlertBot. "
            "Ваша задача — отвечать на вопросы пользователей, основываясь СТРОГО на предоставленной базе знаний. "
            "Если ответа нет в базе знаний, вежливо сообщите, что вы не обладаете данной информацией и "
            "посоветуйте обратиться в поддержку. "
            "Отвечайте на языке пользователя. Используйте HTML-разметку для оформления ответа."
        )

        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\nБАЗА ЗНАНИЙ:\n{knowledge_base_content}"},
                {"role": "user", "content": text_question},
            ],
            model="llama-3.3-70b-versatile",
        )

        answer = chat_completion.choices[0].message.content

        add_question(user_id=message.from_user.id, question=text_question, answer=answer)

        await message.answer(answer, parse_mode="HTML", reply_markup=back_keyboard())

    except Exception as e:
        logger.exception(e)
        await message.answer(t("instruction_send_error", lang=user_db.language))
