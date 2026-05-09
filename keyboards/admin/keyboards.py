from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from locales.locales import t

'''
🔴 danger — красная кнопка (идеально для «Удалить», «Отмена», «Бан»).
🟢 success — зелёная кнопка («Подтвердить», «Оплатить», «Принять»).
🔵 primary — синяя кнопка (для основных целевых действий).
⚪️ Стандартный — привычный прозрачно-серый цвет.
'''


def menu_user_admin_keyboard(lang: str = 'ru'):
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
    return [
        [
            KeyboardButton(text=t("launch_tracking_button", lang=lang), style="success")
        ],
        [
            KeyboardButton(text=t("check_group_for_keywords_button", lang=lang), style="primary")
        ],
        [
            KeyboardButton(text=t("ai_search_button", lang=lang), style="primary"),
            KeyboardButton(text=t("get_database_button", lang=lang), style="primary")
        ],
        [
            KeyboardButton(text=t("instruction_button", lang=lang), style="primary")
        ],
        [
            KeyboardButton(text=t("settings_button", lang=lang), style="primary")
        ]
    ]


def main_admin_keyboard(lang: str = 'ru'):
    """
    Клавиатура администратора
    :return: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            *menu_user_admin_keyboard(lang),
            [
                KeyboardButton(text=t("admin_panel_button", lang=lang), style='success')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def admin_keyboard(lang: str = 'ru'):
    """
    Клавиатура панели администратора
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с кнопками и эмодзи.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("get_log_file_button", lang=lang), style='primary'),
                KeyboardButton(text=t("update_database_button", lang=lang), style='primary')
            ],
            [
                KeyboardButton(text=t("export_questions_button", lang=lang), style='primary'),
                KeyboardButton(text=t("assign_category_button", lang=lang), style='primary'
                               ),
                KeyboardButton(text=t("check_accounts_button", lang=lang), style='success')
            ],
            [
                KeyboardButton(text=t("assign_language_button", lang=lang), style='primary'),
                KeyboardButton(text=t("connect_account_button", lang=lang), style='primary')
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style='danger')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False  # Отправлять сообщение только один раз
    )


def category_method_keyboard(lang: str = 'ru'):
    """
    Клавиатура для выбора метода присвоения категорий
    :return: (ReplyKeyboardMarkup) Объект клавиатуры с выбором метода
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t("fast_method_button", lang=lang), style='primary')
            ],
            [
                KeyboardButton(text=t("powerful_method_openrouter_button", lang=lang), style='success')
            ],
            [
                KeyboardButton(text=t("powerful_method_groq_button", lang=lang), style='success')
            ],
            [
                KeyboardButton(text=t("back_button", lang=lang), style='danger')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
