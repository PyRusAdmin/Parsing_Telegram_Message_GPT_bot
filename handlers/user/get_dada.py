import os

from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from loguru import logger
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

from database.database import get_user_channel_usernames, get_keywords_count, get_user_keywords
from handlers.user_language import determines_user_language
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


@router.callback_query(F.data == "settings_keywords_list")
async def get_keywords_list_cb(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🔍 Список ключевых слов".
    """
    await callback.answer()
    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)
    logger.info(f"Пользователь {callback.from_user.id} запросил экспорт ключевых слов")

    # Получаем количество ключевых слов и если их равно 0, то выводим сообщение пользователю
    keywords_count = get_keywords_count(user_id=callback.from_user.id)  # Ключевые слова
    if keywords_count == 0:
        await callback.answer(t("no_keywords_found", lang=user_lang))
        return

    keywords = get_user_keywords(user_id=callback.from_user.id)

    data = []
    for idx, keyword in enumerate(keywords, start=1):
        data.append((idx, keyword))

    headers = [t('excel_header_number', lang=user_lang), t('excel_header_keyword', lang=user_lang)]

    try:
        filepath = create_excel_file(
            data=data,
            headers=headers,
            filename=f"keywords_{callback.from_user.id}.xlsx",
            sheet_name="Keywords"
        )

        document = types.FSInputFile(filepath)
        await callback.message.answer_document(
            document=document,
            caption=t("keywords_export_caption", lang=user_lang, count=len(data))
        )

        os.remove(filepath)
        logger.info(f"Файл ключевых слов отправлен и удалён: {filepath}")

    except Exception as e:
        logger.exception(f"Ошибка при создании Excel-файла с ключевыми словами: {e}")
        await callback.answer(t("export_error", lang=user_lang))


@router.callback_query(F.data == "settings_tracking_links")
async def get_tracking_links_list_cb(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик инлайн-кнопки "🌐 Ссылки для отслеживания".
    """
    # await callback.answer()

    await state.clear()
    user_lang = determines_user_language(message_or_callback=callback.from_user.id)

    logger.info(f"Пользователь {callback.from_user.id} запросил экспорт ссылок для отслеживания")

    usernames_list, total_count = get_user_channel_usernames(callback.from_user.id)

    if not usernames_list:
        await callback.answer(t("no_tracking_links_found", lang=user_lang))
        return

    data = []
    for idx, username in enumerate(usernames_list, start=1):
        data.append((idx, username))

    # filename = f"tracking_links_{callback.from_user.id}.xlsx"
    # headers = [t('excel_header_number', lang=user_lang), t('excel_header_username', lang=user_lang)]

    try:
        filepath = create_excel_file(
            data=data,
            headers=[t('excel_header_number', lang=user_lang), t('excel_header_username', lang=user_lang)],
            filename=f"tracking_links_{callback.from_user.id}.xlsx",
            sheet_name="Tracking Links"
        )

        document = types.FSInputFile(filepath)
        await callback.message.answer_document(
            document=document,
            caption=t("tracking_links_export_caption", lang=user_lang, count=total_count)
        )

        os.remove(filepath)
        logger.info(f"Файл ссылок отправлен и удалён: {filepath}")

    except Exception as e:
        logger.exception(f"Ошибка при создании Excel-файла со ссылками: {e}")
        await callback.answer(t("export_error", lang=user_lang))
