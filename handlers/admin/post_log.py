from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import Message

from database.database import User
from keyboards.user.keyboards import back_keyboard
from locales.locales import t

router = Router(name=__name__)


@router.message((F.text == t('get_log_file_button', 'ru')) | (F.text == t('get_log_file_button', 'en')))
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

    user = User.get(User.user_id == message.from_user.id)

    document = FSInputFile("logs/log.log")

    await message.answer_document(
        document=document,  # Файл логов для отправки
        caption=t("log_file_caption", lang=user.language),  # Текст под файлом
        parse_mode="HTML",  # Режим разметки для капшна
        reply_markup=back_keyboard(lang=user.language),  # Клавиатура с кнопкой «Назад»
    )
