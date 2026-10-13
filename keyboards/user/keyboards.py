from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.admin.keyboards import menu_user_admin_keyboard
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


def search_group_ai(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру для меню «Получить базу».
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("all_database_button", lang=lang), callback_data="db_export_all")
            ],
            [
                InlineKeyboardButton(text=t("channels_database_button", lang=lang), callback_data="db_export_channels"),
                InlineKeyboardButton(text=t("groups_database_button", lang=lang), callback_data="db_export_groups")
            ],
            [
                InlineKeyboardButton(text=t("select_category_button", lang=lang), callback_data="db_export_category_menu")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
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
                InlineKeyboardButton(text=t("finance_and_personal_budget_button", lang=lang), callback_data="cat_sel:finance")
            ],
            [
                InlineKeyboardButton(text=t("crypto_and_blockchain_button", lang=lang), callback_data="cat_sel:crypto"),
                InlineKeyboardButton(text=t("business_and_entrepreneurship_button", lang=lang), callback_data="cat_sel:business")
            ],
            [
                InlineKeyboardButton(text=t("marketing_and_promotion_button", lang=lang), callback_data="cat_sel:marketing")
            ],
            [
                InlineKeyboardButton(text=t("tech_and_it_button", lang=lang), callback_data="cat_sel:tech")
            ],
            [
                InlineKeyboardButton(text=t("education_and_self_development_button", lang=lang), callback_data="cat_sel:education")
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
                InlineKeyboardButton(text=t("shopping_and_discounts_button", lang=lang), callback_data="cat_sel:shopping")
            ],
            [
                InlineKeyboardButton(text=t("entertainment_and_leisure_button", lang=lang), callback_data="cat_sel:entertainment")
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
                InlineKeyboardButton(text=t("hobbies_and_creativity_button", lang=lang), callback_data="cat_sel:hobbies")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="cat_sel:back")
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


def ai_search_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура для поиска новых групп / каналов с помощью AI.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("global_ai_search_button", lang=lang), callback_data="ai_search_global")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
            ],
        ]
    )


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
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
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
                InlineKeyboardButton(text=t("delete_group_from_tracking_button", lang=lang), callback_data="settings_delete_group")
            ],
            [
                InlineKeyboardButton(text=t("keywords_list_button", lang=lang), callback_data="settings_keywords_list"),
                InlineKeyboardButton(text=t("tracking_links_button", lang=lang), callback_data="settings_tracking_links")
            ],
            [
                InlineKeyboardButton(text=t("connect_account_button", lang=lang), callback_data="settings_connect_account"),
                InlineKeyboardButton(text=t("connect_group_for_messages_button", lang=lang), callback_data="settings_connect_group")
            ],
            [
                InlineKeyboardButton(text=t("change_language_button", lang=lang), callback_data="settings_change_language"),
                InlineKeyboardButton(text=t("topup_stars_button", lang=lang), callback_data="settings_topup_stars")
            ],
            [
                InlineKeyboardButton(text="🔄 Передать настройки пользователю", callback_data="settings_transfer_rights")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
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
                InlineKeyboardButton(text=t("connect_free_account_button", lang=lang), callback_data="account_connect_free")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
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
                InlineKeyboardButton(text=t("connect_group_for_messages_button", lang=lang), callback_data="group_connect")
            ],
            [
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="menu_main")
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
                InlineKeyboardButton(text=t("back_button", lang=lang), callback_data=callback_data)
            ]
        ]
    )


def get_stars_topup_inline_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
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
            InlineKeyboardButton(text=t("back_button", lang=lang), callback_data="buy_stars_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
