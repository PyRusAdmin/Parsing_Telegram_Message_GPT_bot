from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from loguru import logger

from database.database import User
from locales.locales import t

router = Router(name=__name__)


@router.message(F.text == "📖 Инструкция по использованию")
async def send_instruction(message: Message, state: FSMContext):
    """
    Обработчик команды "Инструкция по использованию".

    Отправляет пользователю Markdown-файл с подробной инструкцией по использованию бота.
    Файл берётся из локальной директории 'doc/'. В случае успеха добавляет ссылку на онлайн-документацию.
    Обрабатывает ошибки, если файл отсутствует или произошла ошибка отправки.

    :param message: (Message) Входящее сообщение от пользователя.
    :param state: (FSMContext) Контекст машины состояний, сбрасывается перед отправкой.
    :return: None

    Raises:
        FileNotFoundError: Если файл 'doc/doc.md' не существует.
        Exception: При других ошибках отправки (например, проблемы с сетью).

    Notes:
        - Файл отправляется как документ Telegram.
        - Капшн содержит прямую ссылку на документ в репозитории (gitverse.ru).
    """
    await state.clear()  # Завершаем текущее состояние машины состояния
    user = User.get(User.user_id == message.from_user.id)

    text = t(
        "instruction_caption",
        lang=user.language,
        gitverse_link="https://gitverse.ru/pyadminru/AutoParseAlertBot/content/master/doc/doc.md",
        github_link="https://github.com/PyRusAdmin/AutoParseAlertBot/blob/master/doc/doc.md"
    )

    try:
        # Отправляем файл напрямую из файловой системы
        await message.answer_document(
            document=FSInputFile("doc/doc.md"),
            caption=text,
            parse_mode="html",
        )

    except FileNotFoundError:
        await message.answer(t("instruction_file_not_found", lang=user.language))

    except Exception as e:
        logger.exception(e)
        await message.answer(t("instruction_send_error", lang=user.language))
