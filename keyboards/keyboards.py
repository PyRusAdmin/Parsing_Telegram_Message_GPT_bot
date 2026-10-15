from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.config import ADMIN_USER_ID
from locales.locales import t

# Словарь сопоставления ключей категорий с каноническими названиями в БД
CATEGORY_MAP = {
    "investments": "инвестиции",
    "finance": "финансы и личный бюджет",
    "crypto": "криптовалюты и блокчейн",
    "business": "бизнес и предпринимательство",
    "marketing": "маркетинг и продвижение",
    "tech": "технологии и it",
    "education": "образование и саморазвитие",
    "work": "работа и карьера",
    "real_estate": "недвижимость",
    "health": "здоровье и медицина",
    "travel": "путешествия",
    "auto": "авто и транспорт",
    "shopping": "шоппинг и скидки",
    "entertainment": "развлечения и досуг",
    "politics": "политика и общество",
    "science": "наука и исследования",
    "sports": "спорт и фитнес",
    "cooking": "кулинария и еда",
    "fashion": "мода и красота",
    "hobbies": "хобби и творчество",
}


def back_button(lang):
    """
    Кнопка ⬅️ Назад

    :param lang: Язык пользователя
    :return InlineKeyboardButton: Кнопка возврата
    """
    return InlineKeyboardButton(
        text=t("back_button", lang=lang),  # ⬅️ Назад
        callback_data="menu_main",
        style="danger"
    )


def search_group_ai(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру для меню «Получить базу».
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("all_database_button", lang=lang),  # 📥 Вся база
                    callback_data="db_export_all"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("channels_database_button", lang=lang),  # 📥 База каналов
                    callback_data="db_export_channels"
                ),
                InlineKeyboardButton(
                    text=t("groups_database_button", lang=lang),  # 📥 База групп
                    callback_data="db_export_groups"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("select_category_button", lang=lang),  # 📂 Выбрать категорию
                    callback_data="db_export_category_menu"
                )
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ],
        ]
    )


def get_categories_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру со списком категорий.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("investments_button", lang=lang), callback_data="cat_sel:investments")
            ],
            [
                InlineKeyboardButton(text=t("finance_and_personal_budget_button", lang=lang),
                                     callback_data="cat_sel:finance")
            ],
            [
                InlineKeyboardButton(text=t("crypto_and_blockchain_button", lang=lang), callback_data="cat_sel:crypto"),
                InlineKeyboardButton(text=t("business_and_entrepreneurship_button", lang=lang),
                                     callback_data="cat_sel:business")
            ],
            [
                InlineKeyboardButton(text=t("marketing_and_promotion_button", lang=lang),
                                     callback_data="cat_sel:marketing")
            ],
            [
                InlineKeyboardButton(text=t("tech_and_it_button", lang=lang), callback_data="cat_sel:tech")
            ],
            [
                InlineKeyboardButton(text=t("education_and_self_development_button", lang=lang),
                                     callback_data="cat_sel:education")
            ],
            [
                InlineKeyboardButton(text=t("work_and_career_button", lang=lang), callback_data="cat_sel:work")
            ],
            [
                InlineKeyboardButton(text=t("real_estate_button", lang=lang), callback_data="cat_sel:real_estate")
            ],
            [
                InlineKeyboardButton(text=t("health_and_medicine_button", lang=lang), callback_data="cat_sel:health")
            ],
            [
                InlineKeyboardButton(text=t("travel_button", lang=lang), callback_data="cat_sel:travel")
            ],
            [
                InlineKeyboardButton(text=t("auto_and_transport_button", lang=lang), callback_data="cat_sel:auto")
            ],
            [
                InlineKeyboardButton(text=t("shopping_and_discounts_button", lang=lang),
                                     callback_data="cat_sel:shopping")
            ],
            [
                InlineKeyboardButton(text=t("entertainment_and_leisure_button", lang=lang),
                                     callback_data="cat_sel:entertainment")
            ],
            [
                InlineKeyboardButton(text=t("politics_and_society_button", lang=lang), callback_data="cat_sel:politics")
            ],
            [
                InlineKeyboardButton(text=t("science_and_research_button", lang=lang), callback_data="cat_sel:science")
            ],
            [
                InlineKeyboardButton(text=t("sports_and_fitness_button", lang=lang), callback_data="cat_sel:sports")
            ],
            [
                InlineKeyboardButton(text=t("cooking_and_food_button", lang=lang), callback_data="cat_sel:cooking")
            ],
            [
                InlineKeyboardButton(text=t("fashion_and_beauty_button", lang=lang), callback_data="cat_sel:fashion")
            ],
            [
                InlineKeyboardButton(text=t("hobbies_and_creativity_button", lang=lang),
                                     callback_data="cat_sel:hobbies")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ],
        ]
    )


def get_lang_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру для выбора языка интерфейса.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("russian_language_button", lang=lang), callback_data="lang_ru"),
                InlineKeyboardButton(text=t("english_language_button", lang=lang), callback_data="lang_en")
            ]
        ]
    )


def main_menu_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру главного меню бота.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            *menu_user_admin_keyboard(lang),
        ]
    )


# def ai_search_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
#     """
#     Инлайн-клавиатура для поиска новых групп / каналов с помощью AI.
#     """
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text=t("global_ai_search_button", lang=lang), callback_data="ai_search_global")
#             ],
#             [
#                 back_button(lang)  # Кнопка ⬅️ Назад
#             ],
#         ]
#     )


def menu_launch_tracking_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру во время активного отслеживания.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("stop_tracking_button", lang=lang), callback_data="tracking_stop")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ],
        ]
    )


def settings_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру меню настроек.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("update_list_button", lang=lang), callback_data="settings_update_list"),
                InlineKeyboardButton(text=t("enter_keyword_button", lang=lang), callback_data="settings_enter_keyword")
            ],
            [
                InlineKeyboardButton(text=t("delete_group_from_tracking_button", lang=lang),
                                     callback_data="settings_delete_group")
            ],
            [
                InlineKeyboardButton(text=t("keywords_list_button", lang=lang), callback_data="settings_keywords_list"),
                InlineKeyboardButton(text=t("tracking_links_button", lang=lang),
                                     callback_data="settings_tracking_links")
            ],
            [
                InlineKeyboardButton(text=t("connect_account_button", lang=lang),
                                     callback_data="settings_connect_account"),
                InlineKeyboardButton(text=t("connect_group_for_messages_button", lang=lang),
                                     callback_data="settings_connect_group")
            ],
            [
                InlineKeyboardButton(text=t("change_language_button", lang=lang),
                                     callback_data="settings_change_language"),
                InlineKeyboardButton(text=t("topup_stars_button", lang=lang), callback_data="settings_topup_stars")
            ],
            [
                InlineKeyboardButton(text="🔄 Передать настройки пользователю", callback_data="settings_transfer_rights")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ],
        ]
    )


def connect_keyboard_account(lang: str = 'ru') -> InlineKeyboardMarkup:
    """Инлайн-клавиатура предложения подключить аккаунт"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("connect_account_button", lang=lang), callback_data="account_connect")
            ],
            [
                InlineKeyboardButton(text=t("connect_free_account_button", lang=lang),
                                     callback_data="account_connect_free")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def connect_grup_keyboard_tech(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура для подключения группы сообщений
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("connect_group_for_messages_button", lang=lang),
                                     callback_data="group_connect")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def back_keyboard(lang: str = 'ru', callback_data: str = "menu_main") -> InlineKeyboardMarkup:
    """
    Создаёт простую инлайн-клавиатуру с одной кнопкой Назад.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("back_button", lang=lang),
                    callback_data=callback_data,
                    style="danger"
                )
            ]
        ]
    )


def get_stars_topup_inline_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Генерирует инлайн-клавиатуру для выбора количества звезд при пополнении баланса"""
    buttons = [
        [
            InlineKeyboardButton(text="⭐ 5 Stars", callback_data="buy_stars_5"),
            InlineKeyboardButton(text="⭐ 15 Stars", callback_data="buy_stars_15")
        ],
        [
            InlineKeyboardButton(text="⭐ 50 Stars", callback_data="buy_stars_50"),
            InlineKeyboardButton(text="⭐ 100 Stars", callback_data="buy_stars_100")
        ],
        [
            back_button(lang)  # Кнопка ⬅️ Назад
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


"""Клавиатура Администратора"""


def menu_user_admin_keyboard(lang: str = 'ru', user_id: int | None = None):
    """
    Создаёт кнопки главного меню бота в виде инлайн-кнопок.

    :return: list[list[InlineKeyboardButton]] Список строк с кнопками.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=t("launch_tracking_button", lang=lang),  # 🚀 Запуск отслеживания
                callback_data="menu_launch_tracking"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎯 Персональное отслеживание",  # 🎯 Персональное отслеживание
                callback_data="menu_personal_tracking"
            )
        ],
        [
            InlineKeyboardButton(
                text=t("check_group_for_keywords_button", lang=lang),  # 🔍 Проверка группы на наличие ключевых слов
                callback_data="menu_check_group"
            )
        ],
        [
            InlineKeyboardButton(
                text=t("get_database_button", lang=lang),  # 📥 Получить базу
                callback_data="menu_get_database"
            ),
            InlineKeyboardButton(
                text=t("settings_button", lang=lang),  # ⚙️ Настройки
                callback_data="menu_settings"
            )
        ],
        [
            InlineKeyboardButton(
                text=t("instruction_button", lang=lang),  # 📖 Инструкция по использованию
                callback_data="menu_instruction"
            )
        ],
    ]

    # Добавляем кнопку статистики только для админов
    if user_id in ADMIN_USER_ID:
        buttons.append(
            [InlineKeyboardButton(text=t("admin_panel_button", lang=lang), callback_data="menu_admin_panel")])

    # return buttons
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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
                InlineKeyboardButton(text=t("export_questions_button", lang=lang),
                                     callback_data="admin_export_questions"),
                InlineKeyboardButton(text=t("assign_category_button", lang=lang),
                                     callback_data="admin_assign_category"),
                InlineKeyboardButton(text=t("check_accounts_button", lang=lang), callback_data="admin_check_accounts")
            ],
            [
                InlineKeyboardButton(text=t("connect_account_button", lang=lang), callback_data="admin_connect_account")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
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
                InlineKeyboardButton(text=t("powerful_method_openrouter_button", lang=lang),
                                     callback_data="cat_method_openrouter")
            ],
            [
                InlineKeyboardButton(text=t("powerful_method_groq_button", lang=lang), callback_data="cat_method_groq")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def personal_tracking_menu_kb(user_id: int, lang) -> InlineKeyboardMarkup:
    """
    Клавиатура меню 🎯 Персональное отслеживание ключевых слов
    :param user_id:
    :return InlineKeyboardMarkup:
    """
    buttons = [
        [
            InlineKeyboardButton(text="➕ Добавить отслеживание группы", callback_data="pt_add_tracking")
        ],
        [
            InlineKeyboardButton(text="📱 Подключить свой аккаунт (по телефону)", callback_data="pt_auth_phone")
        ],
        [
            InlineKeyboardButton(text="⭐ Докупить +1 слот (2 Stars)", callback_data="pt_buy_slot")
        ],
        [
            InlineKeyboardButton(text="📋 Мои отслеживаемые группы", callback_data="pt_list_tracking")
        ]
    ]

    # Добавляем кнопку статистики только для админов
    if user_id in ADMIN_USER_ID:
        buttons.append([InlineKeyboardButton(text="📊 Статистика", callback_data="pt_stats")])

    buttons.append(
        [
            back_button(lang)  # Кнопка ⬅️ Назад
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== КЛАВИАТУРЫ ====================

def emoji_code_keypad_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура с цифрами-эмодзи для безопасного выбора цифр кода авторизации (предотвращает спам-блокировку от Telegram).
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="1️⃣", callback_data="pt_digit_1"),
                InlineKeyboardButton(text="2️⃣", callback_data="pt_digit_2"),
                InlineKeyboardButton(text="3️⃣", callback_data="pt_digit_3"),
            ],
            [
                InlineKeyboardButton(text="4️⃣", callback_data="pt_digit_4"),
                InlineKeyboardButton(text="5️⃣", callback_data="pt_digit_5"),
                InlineKeyboardButton(text="6️⃣", callback_data="pt_digit_6"),
            ],
            [
                InlineKeyboardButton(text="7️⃣", callback_data="pt_digit_7"),
                InlineKeyboardButton(text="8️⃣", callback_data="pt_digit_8"),
                InlineKeyboardButton(text="9️⃣", callback_data="pt_digit_9"),
            ],
            [
                InlineKeyboardButton(text="❌ Стереть", callback_data="pt_digit_clear"),
                InlineKeyboardButton(text="0️⃣", callback_data="pt_digit_0"),
                InlineKeyboardButton(text="✅ Отправить", callback_data="pt_digit_submit"),
            ],
            [
                InlineKeyboardButton(text="🚫 Отмена", callback_data="pt_cancel_auth"),
            ]
        ]
    )


"""Клавиатура статистики"""


def tracking_list_keyboard(records):
    """Клавиатура для списка персональных отслеживаний"""

    buttons = []

    for idx, record in enumerate(records, start=1):
        title = str(record.target_link or "Без ссылки")

        # Обрезаем длинное название для кнопки
        if len(title) > 15:
            title = title[:15] + "..."

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"⚙️ Изменить #{idx} ({title})",
                    callback_data=f"pt_edit_{record.id}"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_inline_keyboard(stars: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура покупки звезд
    :param stars:
    :param lang:
    :return:
    """
    buttons = []
    if stars >= 5:
        buttons.append([
            InlineKeyboardButton(
                text=t("pay_from_balance_btn", lang=lang),
                callback_data="pay_db_balance"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text=t("pay_direct_btn", lang=lang),
            callback_data="pay_db_direct"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text=t("cancel_btn", lang=lang),
            callback_data="pay_db_cancel"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
