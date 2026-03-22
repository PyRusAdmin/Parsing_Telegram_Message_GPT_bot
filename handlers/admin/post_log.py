# -*- coding: utf-8 -*-
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import Message

from keyboards.user.keyboards import back_keyboard

router = Router(name=__name__)


@router.message(F.text == "📄 Получить лог файл")
async def log(message: Message, state: FSMContext):
    """
    Обработчик команды для отправки файла логов администратору.

    При вызове:
    - сбрасывает текущее состояние FSM;
    - считывает файл логов 'logs/log.log';
    - отправляет его пользователю в виде документа Telegram с HTML‑капшном и клавиатурой.

    Используется для:
    - диагностики ошибок в работе системы;
    - мониторинга текущего состояния приложения.

    Особенности реализации:
    - Файл логов ограничен по размеру и хранится не более 1 дня (согласно настройкам логгера).
    - Доступ к команде имеют только администраторы;
    - Обработка исключений не реализована: при отсутствии файла или ошибках отправки исключение не перехватывается,
    что может привести к аварийному завершению обработчика.

    :param message: (Message) Входящее сообщение с командой «📄 Получить лог файл».
    :param state: (FSMContext) Контекст машины состояний. Сбрасывается в начале выполнения.
    :return: None
    :raises:
        Exception: Может возникнуть при отсутствии файла 'logs/log.log' или ошибках отправки документа через Telegram Bot API.
        В текущей реализации исключения не обрабатываются.
    """
    await state.clear()  # Сбрасываем текущее состояние FSM

    document = FSInputFile("logs/log.log")

    await message.answer_document(
        document=document,  # Файл логов для отправки
        caption=f"📄 Лог файл с ошибками.",  # Текст под файлом
        parse_mode="HTML",  # Режим разметки для капшна
        reply_markup=back_keyboard(),  # Клавиатура с кнопкой «Назад»
    )
