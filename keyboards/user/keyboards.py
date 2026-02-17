# -*- coding: utf-8 -*-
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def search_group_ai():
    """
    Генерирует клавиатуру для меню «📥 Получить базу».

    Предоставляет пользователю доступ к основным функциям поиска:
    - 📥 Получение всей базы данных групп и каналов
    - 🤖 AI-поиск по ключевому слову
    - 🔙 Возврат в предыдущее меню

    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📥 Вся база")],
            [KeyboardButton(text="📥 База каналов"), KeyboardButton(text="📥 База групп")],
            [KeyboardButton(text="Выбрать категорию")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def get_categories_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Инвестиции")],
            [KeyboardButton(text="Финансы и личный бюджет")],
            [KeyboardButton(text="Криптовалюты и блокчейн"), KeyboardButton(text="Бизнес и предпринимательство")],
            [KeyboardButton(text="Маркетинг и продвижение")],
            [KeyboardButton(text="Технологии и IT")],
            [KeyboardButton(text="Образование и саморазвитие")],
            [KeyboardButton(text="Работа и карьера")],
            [KeyboardButton(text="Недвижимость")],
            [KeyboardButton(text="Здоровье и медицина")],
            [KeyboardButton(text="Путешествия")],
            [KeyboardButton(text="Авто и транспорт")],
            [KeyboardButton(text="Шоппинг и скидки")],
            [KeyboardButton(text="Развлечения и досуг")],
            [KeyboardButton(text="Политика и общество")],
            [KeyboardButton(text="Наука и исследования")],
            [KeyboardButton(text="Спорт и фитнес")],
            [KeyboardButton(text="Кулинария и еда")],
            [KeyboardButton(text="Мода и красота")],
            [KeyboardButton(text="Хобби и творчество")],
            [KeyboardButton(text="🔙 Назад")],
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
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")]
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
        - ⚙ Настройки
        - 📘 Инструкция по использованию

    :return: (ReplyKeyboardMarkup) Объект клавиатуры с основными командами.

    Layout:
        [Запуск отслеживания]
        [🔍 Список ключевых слов] [🌐 Ссылки для отслеживания]
        [📥 Получить базу]
        [📘 Инструкция по использованию]
        [⚙ Настройки]

    Notes:
        - Клавиатура подстраивается по размеру и остаётся видимой после использования.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Запуск отслеживания")],
            [KeyboardButton(text="🔍 Проверка группы на наличие ключевых слов")],
            [KeyboardButton(text="🤖 AI поиск"), KeyboardButton(text="📥 Получить базу")],
            [KeyboardButton(text="📘 Инструкция по использованию")],
            [KeyboardButton(text="⚙ Настройки")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def menu_launch_tracking_keyboard():
    """
    Создаёт клавиатуру во время активного отслеживания.

    Позволяет пользователю остановить процесс парсинга или вернуться в главное меню.
    Появляется после нажатия кнопки "Запуск отслеживания".

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопками управления отслеживанием.

    Layout:
        [🛑 Остановить отслеживание]
        [🔙 Назад]

    Notes:
        - Отображает текущее состояние (отслеживание активно).
        - Клавиатура подстраивается по размеру и остаётся видимой.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛑 Остановить отслеживание")],
            [KeyboardButton(text="🔙 Назад")],
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
        [🔐 Подключить аккаунт] [📤 Подключить группу для сообщений]
        [🌐 Сменить язык]
        [🔙 Назад]

    Notes:
        - Клавиатура подстраивается по размеру и остаётся видимой после использования.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔁 Обновить список"), KeyboardButton(text="🔍 Ввод ключевого слова")],
            [KeyboardButton(text="Удалить группу из отслеживания")],
            [KeyboardButton(text="🔍 Список ключевых слов"), KeyboardButton(text="🌐 Ссылки для отслеживания")],
            [KeyboardButton(text="🔐 Подключить аккаунт"), KeyboardButton(text="📤 Подключить группу для сообщений")],
            [KeyboardButton(text="🌐 Сменить язык")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def connect_keyboard_account():
    """Если у пользователя не подключен аккаунт, то высылаем ему наддую клавиатуру"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Подключить аккаунт")],
            [KeyboardButton(text="🔐 Подключить свободный аккаунт")],
            [KeyboardButton(text="🔙 Назад")]
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
            [KeyboardButton(text="📤 Подключить группу для сообщений")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def back_keyboard():
    """
    Создаёт простую клавиатуру с одной кнопкой 🔙 Назад.

    Используется в подменю для возврата в предыдущее меню (например, настройки, ввод данных).
    Упрощает навигацию по интерфейсу бота.

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры с кнопкой возврата.

    Layout:
        [🔙 Назад]

    Notes:
        - Клавиатура подстраивается по размеру и остаётся видимой.
        - Является универсальной для всех подменю.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )
