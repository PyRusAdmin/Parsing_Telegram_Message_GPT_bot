# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

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
    text = (
        "📘 <b>Инструкция по использованию</b>\n\n"
        "Прикреплён подробный руководство по функционалу бота.\n\n"
        "🔗 <b>Онлайн-документация:</b>\n"
        "• <a href=\"https://gitverse.ru/pyadminru/AutoParseAlertBot/content/master/doc/doc.md\">GitVerse</a>\n"
        "• <a href=\"https://github.com/PyRusAdmin/AutoParseAlertBot/blob/master/doc/doc.md\">GitHub</a>\n\n"
        "Рекомендуем ознакомиться для эффективного использования всех возможностей бота."
    )

    try:
        # Отправляем файл напрямую из файловой системы
        await message.answer_document(
            document=FSInputFile("doc/doc.md"),
            caption=text,
            parse_mode="html",
        )

    except FileNotFoundError:
        await message.answer("Файл инструкции не найден на сервере.")

    except Exception as e:
        await message.answer(f"Произошла ошибка при отправке файла: {e}")
