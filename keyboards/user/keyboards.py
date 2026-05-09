from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.admin.keyboards import menu_user_admin_keyboard


def search_group_ai():
    """
    Генерирует клавиатуру для меню «Получить базу».

    Предоставляет пользователю доступ к основным функциям поиска:
    - 📥 Получение всей базы данных групп и каналов
    - 🤖 AI-поиск по ключевому слову
    - 🔙 Возврат в предыдущее меню

    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📥 Вся база", style="primary")
            ],
            [
                KeyboardButton(text="📥 База каналов", style="primary"),
                KeyboardButton(text="📥 База групп", style="primary")
            ],
            [
                KeyboardButton(text="📂 Выбрать категорию", style="primary")
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def get_categories_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="инвестиции", style="primary")
            ],
            [
                KeyboardButton(text="финансы и личный бюджет", style="primary")
            ],
            [
                KeyboardButton(text="криптовалюты и блокчейн", style="primary"),
                KeyboardButton(text="бизнес и предпринимательство", style="primary")
            ],
            [
                KeyboardButton(text="маркетинг и продвижение", style="primary")
            ],
            [
                KeyboardButton(text="технологии и it", style="primary")
            ],
            [
                KeyboardButton(text="образование и саморазвитие", style="primary")
            ],
            [
                KeyboardButton(text="работа и карьера", style="primary")
            ],
            [
                KeyboardButton(text="недвижимость", style="primary")
            ],
            [
                KeyboardButton(text="здоровье и медицина", style="primary")
            ],
            [
                KeyboardButton(text="путешествия", style="primary")
            ],
            [
                KeyboardButton(text="авто и транспорт", style="primary")
            ],
            [
                KeyboardButton(text="шоппинг и скидки", style="primary")
            ],
            [
                KeyboardButton(text="развлечения и досуг", style="primary")
            ],
            [
                KeyboardButton(text="политика и общество", style="primary")
            ],
            [
                KeyboardButton(text="наука и исследования", style="primary")
            ],
            [
                KeyboardButton(text="спорт и фитнес", style="primary")
            ],
            [
                KeyboardButton(text="кулинария и еда", style="primary")
            ],
            [
                KeyboardButton(text="мода и красота", style="primary")
            ],
            [
                KeyboardButton(text="хобби и творчество", style="primary")
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def get_lang_keyboard():
    """
    Создаёт клавиатуру для выбора языка интерфейса.

    Содержит две кнопки: "🇷🇺 Русский" и "🇬🇧 English".
    Используется при первом запуске бота (/start), когда язык пользователя установлен в "unset".

    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками выбора языка.

    Notes:
        - Клавиатура подстраивается по размеру (resize_keyboard=True).
        - Не исчезает после первого использования (one_time_keyboard=False).
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇷🇺 Русский", style="primary"),
                KeyboardButton(text="🇬🇧 English", style="primary")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def main_menu_keyboard():
    """
    Создаёт клавиатуру главного меню бота.

    Предоставляет пользователю доступ к основным функциям:
        - Запуск и остановка отслеживания
        - Просмотр и управление ключевыми словами и ссылками
        - Поиск новых групп через ИИ
        - Настройки
        - Инструкция по использованию

    - Клавиатура подстраивается по размеру и остаётся видимой после использования.

    Layout:
        [Запуск отслеживания]
        [🔍 Список ключевых слов] [🌐 Ссылки для отслеживания]
        [Получить базу]
        [Инструкция по использованию]
        [Настройки]

    :return: (ReplyKeyboardMarkup) Объект клавиатуры с основными командами.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            *menu_user_admin_keyboard(),
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def ai_search_keyboard():
    """
    Клавиатура для поиска новых групп / каналов с помощью AI.
    :return:
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [

                KeyboardButton(text="🤖 AI поиск", style="primary"),
            ],
            [
                KeyboardButton(text="🌐 Глобальный AI поиск", style='primary')
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def menu_launch_tracking_keyboard():
    """
    Создаёт клавиатуру во время активного отслеживания.

    Позволяет пользователю остановить процесс парсинга или вернуться в главное меню.
    Появляется после нажатия кнопки "🚀 Запуск отслеживания".

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками управления отслеживанием.

    Layout:
        [🛑 Остановить отслеживание]
        [⬅️ Назад]

    Notes:
        - Отображает текущее состояние (отслеживание активно).
        - Клавиатура подстраивается по размеру и остаётся видимой.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛑 Остановить отслеживание", style="danger")
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def settings_keyboard():
    """
    Создаёт клавиатуру меню настроек.

    Предоставляет доступ к настройкам пользователя:
        - Обновление списка отслеживаемых групп
        - Ввод и редактирование ключевых слов
        - Подключение аккаунта и технической группы
        - Смена языка интерфейса
        - Возврат в главное меню

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с настройками.

    Layout:
        [🔁 Обновить список] [🔍 Ввод ключевого слова]
        [🗑️ Удалить группу из отслеживания]
        [🔍 Список ключевых слов] [🌐 Ссылки для отслеживания]
        [🔐 Подключить аккаунт] [📤 Подключить группу для сообщений]
        [🌐 Сменить язык]
        [⬅️ Назад]

    Notes:
        - Клавиатура подстраивается по размеру и остаётся видимой после использования.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔁 Обновить список", style="primary"),
                KeyboardButton(text="🔍 Ввод ключевого слова", style="primary")
            ],
            [
                KeyboardButton(text="🗑️ Удалить группу из отслеживания", style="danger")
            ],
            [
                KeyboardButton(text="🔍 Список ключевых слов", style="primary"),
                KeyboardButton(text="🌐 Ссылки для отслеживания", style="primary")
            ],
            [
                KeyboardButton(text="🔐 Подключить аккаунт", style="success"),
                KeyboardButton(text="📤 Подключить группу для сообщений", style="success")
            ],
            [
                KeyboardButton(text="🌐 Сменить язык", style="primary")
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def connect_keyboard_account():
    """Если у пользователя не подключен аккаунт, то высылаем ему наддую клавиатуру"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🔐 Подключить аккаунт", style="success")
            ],
            [
                KeyboardButton(text="🔐 Подключить свободный аккаунт", style="success")
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def connect_grup_keyboard_tech():
    """
    Подключает группу для сообщений, в которую будут отправляться уведомления о новых найденных группах.
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📤 Подключить группу для сообщений", style="success")
            ],
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def back_keyboard():
    """
    Создаёт простую клавиатуру с одной кнопкой Назад.

    Используется в подменю для возврата в предыдущее меню (например, настройки, ввод данных).
    Упрощает навигацию по интерфейсу бота.

    - Клавиатура подстраивается по размеру и остаётся видимой.
    - Является универсальной для всех подменю.

    :return ReplyKeyboardMarkup: Объект клавиатуры с кнопкой возврата. [⬅️ Назад]
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⬅️ Назад", style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )
