import os
from datetime import datetime
from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
from loguru import logger
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from database.database import User, get_user_channel_usernames
from locales.locales import t

router = Router(name=__name__)


def create_excel_file(data: list, headers: list, filename: str, sheet_name: str) -> str:
    """
    Создаёт Excel-файл с заданными данными, оформлением и автоматической подгонкой ширины столбцов.

    Функция формирует .xlsx файл с синей шапкой заголовков, центрированным жирным белым шрифтом,
    подгоняет ширину столбцов под содержимое и сохраняет файл в директорию 'exports/'.

    Используется для экспорта данных пользователей (ключевые слова, ссылки).

    - Используется библиотека `openpyxl`.
    - Максимальная ширина столбца ограничена 50 символами.
    - Папка 'exports/' создаётся автоматически при необходимости.

    :param data: (list) Список кортежей, представляющих строки таблицы (например, [(1, 'слово'), ...]).
    :param headers: (list) Список строк, представляющих заголовки столбцов (например, ['№', 'Ключевое слово']).
    :param filename: (str) Имя создаваемого файла (например, "keywords_12345_20250420.xlsx").
    :param sheet_name: (str) Название листа в Excel-файле.
    :return: (str) Абсолютный путь к созданному Excel-файлу.

    Raises:
        Exception: Может быть выброшено при ошибках записи файла (например, нет доступа к папке).
            Ожидается обработка вызывающей стороной.
    """
    # Создаём новый Excel-файл (рабочую книгу)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name  # Название листа

    # Настройки оформления заголовков таблицы
    header_font = Font(bold=True, color="FFFFFF", size=12)  # Жирный белый шрифт
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")  # Синий фон
    header_alignment = Alignment(horizontal="center", vertical="center")  # Центрирование текста

    # Запись заголовков в первую строку
    for col_num, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # Запись данных (начиная со второй строки)
    for row_num, row_data in enumerate(data, start=2):
        for col_num, cell_value in enumerate(row_data, start=1):
            cell = sheet.cell(row=row_num, column=col_num)
            cell.value = cell_value
            cell.alignment = Alignment(horizontal="left", vertical="center")

    # Автоматическая подгонка ширины столбцов под содержимое
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # ограничиваем ширину 50 символами
        sheet.column_dimensions[column_letter].width = adjusted_width

    # Создаём папку exports, если её ещё нет
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)

    # Сохраняем файл
    filepath = os.path.join(exports_dir, filename)
    workbook.save(filepath)
    logger.info(f"Excel файл создан: {filepath}")

    return filepath


async def export_keywords_internal(message: Message, user_id: int, state: FSMContext):
    """Экспортирует список ключевых слов пользователя в Excel-файл"""
    await state.clear()
    user = User.get(User.user_id == user_id)
    user_lang = user.language if user.language != "unset" else "ru"

    logger.info(f"Пользователь {user_id} запросил экспорт ключевых слов")

    keywords_model = create_keywords_model(user_id=user_id)

    if not keywords_model.table_exists():
        keywords_model.create_table()
        await message.answer(t("no_keywords_found", lang=user_lang))
        return

    keywords = list(keywords_model.select())

    if not keywords:
        await message.answer(t("no_keywords_found", lang=user_lang))
        return

    data = []
    for idx, keyword in enumerate(keywords, start=1):
        data.append((idx, keyword.user_keyword))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"keywords_{user_id}_{timestamp}.xlsx"
    headers = [t('excel_header_number', lang=user_lang), t('excel_header_keyword', lang=user_lang)]

    try:
        filepath = create_excel_file(
            data=data,
            headers=headers,
            filename=filename,
            sheet_name="Keywords"
        )

        document = FSInputFile(filepath)
        await message.answer_document(
            document=document,
            caption=t("keywords_export_caption", lang=user_lang, count=len(data))
        )

        os.remove(filepath)
        logger.info(f"Файл ключевых слов отправлен и удалён: {filepath}")

    except Exception as e:
        logger.exception(f"Ошибка при создании Excel-файла с ключевыми словами: {e}")
        await message.answer(t("export_error", lang=user_lang))


@router.message((F.text == t('keywords_list_button', 'ru')) | (F.text == t('keywords_list_button', 'en')))
async def get_keywords_list(message: Message, state: FSMContext):
    """
    Обработчик команды "🔍 Список ключевых слов" (текст).
    """
    await export_keywords_internal(message, message.from_user.id, state)


@router.callback_query(F.data == "settings_keywords_list")
async def get_keywords_list_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🔍 Список ключевых слов".
    """
    await callback.answer()
    await export_keywords_internal(callback.message, callback.from_user.id, state)


async def export_tracking_links_internal(message: Message, user_id: int, state: FSMContext):
    """Экспортирует список отслеживаемых ссылок пользователя в Excel-файл"""
    await state.clear()
    user = User.get(User.user_id == user_id)
    user_lang = user.language if user.language != "unset" else "ru"

    logger.info(f"Пользователь {user_id} запросил экспорт ссылок для отслеживания")

    usernames_list, total_count = get_user_channel_usernames(user_id)

    if not usernames_list:
        await message.answer(t("no_tracking_links_found", lang=user_lang))
        return

    data = []
    for idx, username in enumerate(usernames_list, start=1):
        data.append((idx, username))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tracking_links_{user_id}_{timestamp}.xlsx"
    headers = [t('excel_header_number', lang=user_lang), t('excel_header_username', lang=user_lang)]

    try:
        filepath = create_excel_file(
            data=data,
            headers=headers,
            filename=filename,
            sheet_name="Tracking Links"
        )

        document = FSInputFile(filepath)
        await message.answer_document(
            document=document,
            caption=t("tracking_links_export_caption", lang=user_lang, count=total_count)
        )

        os.remove(filepath)
        logger.info(f"Файл ссылок отправлен и удалён: {filepath}")

    except Exception as e:
        logger.exception(f"Ошибка при создании Excel-файла со ссылками: {e}")
        await message.answer(t("export_error", lang=user_lang))


@router.message((F.text == t('tracking_links_button', 'ru')) | (F.text == t('tracking_links_button', 'en')))
async def get_tracking_links_list(message: Message, state: FSMContext):
    """
    Обработчик команды "🌐 Ссылки для отслеживания" (текст).
    """
    await export_tracking_links_internal(message, message.from_user.id, state)


@router.callback_query(F.data == "settings_tracking_links")
async def get_tracking_links_list_cb(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🌐 Ссылки для отслеживания".
    """
    await callback.answer()
    await export_tracking_links_internal(callback.message, callback.from_user.id, state)
