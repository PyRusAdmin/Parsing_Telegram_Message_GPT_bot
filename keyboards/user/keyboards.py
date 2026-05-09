from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from keyboards.admin.keyboards import menu_user_admin_keyboard
from locales.locales import t


def search_group_ai(lang: str = 'ru'):
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
                KeyboardButton(text=t("all_database_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("channels_database_button", lang=lang), style="primary"),
                KeyboardButton(text=t("groups_database_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("select_category_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def get_categories_keyboard(lang: str = 'ru'):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("investments_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("finance_and_personal_budget_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("crypto_and_blockchain_button", lang=lang), style="primary"),
                KeyboardButton(text=t("business_and_entrepreneurship_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("marketing_and_promotion_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("tech_and_it_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("education_and_self_development_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("work_and_career_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("real_estate_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("health_and_medicine_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("travel_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("auto_and_transport_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("shopping_and_discounts_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("entertainment_and_leisure_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("politics_and_society_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("science_and_research_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("sports_and_fitness_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("cooking_and_food_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("fashion_and_beauty_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("hobbies_and_creativity_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def get_lang_keyboard(lang: str = 'ru'):
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
                KeyboardButton(text=t("russian_language_button", lang=lang), style="primary"),
                KeyboardButton(text=t("english_language_button", lang=lang), style="primary")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def main_menu_keyboard(lang: str = 'ru'):
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
            *menu_user_admin_keyboard(lang),
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def ai_search_keyboard(lang: str = 'ru'):
    """
    Клавиатура для поиска новых групп / каналов с помощью AI.
    :return:
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [

                KeyboardButton(text=t("ai_search_button", lang=lang), style="primary"),
            ],
            [
                KeyboardButton(text=t("global_ai_search_button", lang=lang), style='primary')
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def menu_launch_tracking_keyboard(lang: str = 'ru'):
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
                KeyboardButton(text=t("stop_tracking_button", lang=lang), style="danger")
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def settings_keyboard(lang: str = 'ru'):
    """
    Создаёт клавиатуру меню настроек.

    Предоставляет доступ к настройкам пользователя:
        - Обновление списка отслеживаемых групп
        - Ввод и редактирование ключевых слов
        - Подключение аккаунта и технической группы
        - Смена языка интерфейса
        - Возврат в главное меню

    - Клавиатура подстраивается по размеру и остаётся видимой после использования.

    Layout:
        [🔁 Обновить список] [🔍 Ввод ключевого слова]
        [🗑️ Удалить группу из отслеживания]
        [🔍 Список ключевых слов] [🌐 Ссылки для отслеживания]
        [🔐 Подключить аккаунт] [📤 Подключить группу для сообщений]
        [🌐 Сменить язык]
        [⬅️ Назад]

    :return ReplyKeyboardMarkup: Объект клавиатуры с настройками.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("update_list_button", lang=lang), style="primary"),
                KeyboardButton(text=t("enter_keyword_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("delete_group_from_tracking_button", lang=lang), style="danger")
            ],
            [
                KeyboardButton(text=t("keywords_list_button", lang=lang), style="primary"),
                KeyboardButton(text=t("tracking_links_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("connect_account_button", lang=lang), style="success"),
                KeyboardButton(text=t("connect_group_for_messages_button", lang=lang), style="success")
            ],
            [
                KeyboardButton(text=t("change_language_button", lang=lang), style="primary")
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def connect_keyboard_account(lang: str = 'ru'):
    """Если у пользователя не подключен аккаунт, то высылаем ему наддую клавиатуру"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("connect_account_button", lang=lang), style="success")
            ],
            [
                KeyboardButton(text=t("connect_free_account_button", lang=lang), style="success")
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def connect_grup_keyboard_tech(lang: str = 'ru'):
    """
    Подключает группу для сообщений, в которую будут отправляться уведомления о новых найденных группах.
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("connect_group_for_messages_button", lang=lang), style="success")
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def back_keyboard(lang: str = 'ru'):
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
                KeyboardButton(text=t("back_button", lang=lang), style="danger")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )
