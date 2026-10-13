from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from locales.locales import t


def menu_user_admin_keyboard(lang: str = 'ru'):
    """
    Создаёт кнопки главного меню бота в виде инлайн-кнопок.

    :return: list[list[InlineKeyboardButton]] Список строк с кнопками.
    """
    return [
        [
            InlineKeyboardButton(text=t("launch_tracking_button", lang=lang), callback_data="menu_launch_tracking")
        ],
        [
            InlineKeyboardButton(text="🎯 Персональное отслеживание", callback_data="menu_personal_tracking")
        ],
        [
            InlineKeyboardButton(text=t("check_group_for_keywords_button", lang=lang), callback_data="menu_check_group")
        ],
        [
            InlineKeyboardButton(text=t("get_database_button", lang=lang), callback_data="menu_get_database")
        ],
        [
            InlineKeyboardButton(text=t("instruction_button", lang=lang), callback_data="menu_instruction")
        ],
        [
            InlineKeyboardButton(text=t("settings_button", lang=lang), callback_data="menu_settings")
        ],
    ]


def main_admin_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура администратора (главное меню)
    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *menu_user_admin_keyboard(lang),
            [
                InlineKeyboardButton(text=t("admin_panel_button", lang=lang), callback_data="menu_admin_panel")
            ]
        ]
    )


def admin_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура панели администратора
    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("get_log_file_button", lang=lang), callback_data="admin_get_log"),
            ],
            [
                InlineKeyboardButton(text=t("export_questions_button", lang=lang), callback_data="admin_export_questions"),
                InlineKeyboardButton(text=t("assign_category_button", lang=lang), callback_data="admin_assign_category"),
                InlineKeyboardButton(text=t("check_accounts_button", lang=lang), callback_data="admin_check_accounts")
            ],
            [
                InlineKeyboardButton(text=t("connect_account_button", lang=lang), callback_data="admin_connect_account")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
            ]
        ]
    )


def category_method_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура для выбора метода присвоения категорий
    :return: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("fast_method_button", lang=lang), callback_data="cat_method_fast")
            ],
            [
                InlineKeyboardButton(text=t("powerful_method_openrouter_button", lang=lang), callback_data="cat_method_openrouter")
            ],
            [
                InlineKeyboardButton(text=t("powerful_method_groq_button", lang=lang), callback_data="cat_method_groq")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_admin_panel")
            ]
        ]
    )
