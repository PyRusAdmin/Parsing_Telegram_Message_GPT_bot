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


def back_button(lang: str = 'ru', callback_data: str = "menu_main"):
    """
    Создает инлайн-кнопку "Назад".

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param callback_data: (str) Данные callback_data для кнопки (по умолчанию 'menu_main').
    :return: (InlineKeyboardButton) Объект инлайн-кнопки возврата.
    """
    return InlineKeyboardButton(
        text=t("back_button", lang=lang),  # ⬅️ Назад
        callback_data=callback_data,
        style="danger"  # Стиль кнопки
    )


def search_group_ai(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру для меню "Получить базу".

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
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
    Генерирует инлайн-клавиатуру со списком всех доступных категорий.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры с категориями.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("investments_button", lang=lang),  # инвестиции
                    callback_data="cat_sel:investments"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("finance_and_personal_budget_button", lang=lang),  # финансы и личный бюджет
                    callback_data="cat_sel:finance"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("crypto_and_blockchain_button", lang=lang),  # криптовалюты и блокчейн
                    callback_data="cat_sel:crypto"
                ),
                InlineKeyboardButton(
                    text=t("business_and_entrepreneurship_button", lang=lang),  # бизнес и предпринимательство
                    callback_data="cat_sel:business"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("marketing_and_promotion_button", lang=lang),  # маркетинг и продвижение
                    callback_data="cat_sel:marketing"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("tech_and_it_button", lang=lang),  # технологии и it
                    callback_data="cat_sel:tech"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("education_and_self_development_button", lang=lang),
                    # образование и саморазвитие
                    callback_data="cat_sel:education"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("work_and_career_button", lang=lang),  # работа и карьера
                    callback_data="cat_sel:work"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("real_estate_button", lang=lang),  # недвижимость
                    callback_data="cat_sel:real_estate"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("health_and_medicine_button", lang=lang),  # здоровье и медицина
                    callback_data="cat_sel:health"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("travel_button", lang=lang),  # путешествия
                    callback_data="cat_sel:travel"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("auto_and_transport_button", lang=lang),  # авто и транспорт
                    callback_data="cat_sel:auto"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("shopping_and_discounts_button", lang=lang),  # шоппинг и скидки
                    callback_data="cat_sel:shopping"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("entertainment_and_leisure_button", lang=lang),  # развлечения и досуг
                    callback_data="cat_sel:entertainment"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("politics_and_society_button", lang=lang),  # олитика и общество
                    callback_data="cat_sel:politics"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("science_and_research_button", lang=lang),  # наука и исследования
                    callback_data="cat_sel:science"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("sports_and_fitness_button", lang=lang),  # спорт и фитнес
                    callback_data="cat_sel:sports"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("cooking_and_food_button", lang=lang),  # кулинария и еда
                    callback_data="cat_sel:cooking"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("fashion_and_beauty_button", lang=lang),  # мода и красота
                    callback_data="cat_sel:fashion"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("hobbies_and_creativity_button", lang=lang),  # хобби и творчество
                    callback_data="cat_sel:hobbies"
                )
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ],
        ]

    )


def get_lang_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру для выбора языка интерфейса.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры смены языка.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("russian_language_button", lang=lang), callback_data="lang_ru"),
                InlineKeyboardButton(text=t("english_language_button", lang=lang), callback_data="lang_en")
            ]
        ]
    )


def main_menu_keyboard(lang: str = 'ru', user_id: int | None = None) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру главного меню бота.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param user_id: (int | None) ID пользователя Telegram.
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры главного меню.
    """
    return menu_user_admin_keyboard(lang=lang, user_id=user_id)


def menu_launch_tracking_keyboard(lang: str = 'ru', user_id: int | None = None) -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру во время активного отслеживания.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param user_id: (int | None) ID пользователя для определения статуса отслеживания.
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    is_active = True
    if user_id is not None:
        try:
            from account_manager.parser import active_clients
            is_active = str(user_id) in active_clients
        except ImportError:
            is_active = True
    return personal_tracking_menu_kb(user_id=user_id or 0, is_active=is_active, lang=lang)


"""Клавиатура меню подключения аккаунтов"""


def connect_account_keyboard(lang: str = 'ru', has_account: bool = False,
                             is_shared: bool = False) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для единого меню подключения аккаунтов.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param has_account: (bool) Подключен ли аккаунт у пользователя.
    :param is_shared: (bool) Подключен ли свободный общий аккаунт.
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры выбора метода подключения.
    """
    free_account_btn_text = (
        t("btn_reconnect_free_account", lang=lang)
        if is_shared
        else t("btn_connect_free_account", lang=lang)
    )

    buttons = [
        [
            InlineKeyboardButton(
                text=t("btn_connect_account_phone", lang=lang),  # 📱 Подключить личный аккаунт (по телефону)
                callback_data="pt_auth_phone"
            )
        ],
        [
            InlineKeyboardButton(
                text=t("btn_connect_account_session", lang=lang),  # 📄 Подключить аккаунт через сессию (.session)
                callback_data="connect_account_session"
            )
        ],
        [
            InlineKeyboardButton(
                text=free_account_btn_text,  # 🎁 Использовать бесплатный аккаунт / 🔄 Переподключить
                callback_data="account_connect_free"
            )
        ],
    ]

    if has_account:
        buttons.append([
            InlineKeyboardButton(
                text=t("btn_disconnect_account", lang=lang),  # ❌ Отключить текущий аккаунт
                callback_data="account_disconnect"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text=t("btn_to_tracking_menu", lang=lang), callback_data="menu_personal_tracking"),
        InlineKeyboardButton(text=t("btn_to_settings_menu", lang=lang), callback_data="menu_settings")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


"""Клавиатура меню настроек"""


def settings_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру главного меню настроек.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры настроек.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_tracking_channels", lang=lang),
                    callback_data="settings_section_channels"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_keywords", lang=lang),
                    callback_data="settings_section_keywords"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_notification_group", lang=lang),
                    callback_data="settings_section_notification"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("connect_account_button", lang=lang),  # Кнопка 🔐 Подключение аккаунта
                    callback_data="account_connect_menu"
                ),
            ],
            # [
            #     InlineKeyboardButton(
            #         text=t("connect_account_button", lang=lang),  # Кнопка "Подключить аккаунт"
            #         callback_data="settings_connect_account"
            #     ),
            # ], account_connect_menu
            [
                InlineKeyboardButton(
                    text=t("change_language_button", lang=lang),
                    callback_data="settings_change_language"
                ),
                InlineKeyboardButton(
                    text=t("topup_stars_button", lang=lang),
                    callback_data="settings_topup_stars"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_transfer_settings", lang=lang),
                    callback_data="settings_transfer_rights"
                )
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ],
        ]
    )


def connect_keyboard_account(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура предложения подключить аккаунт.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("connect_account_button", lang=lang), callback_data="account_connect_menu")
            ],
            [
                InlineKeyboardButton(text=t("btn_connect_free_account", lang=lang),
                                     callback_data="account_connect_free")
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def back_keyboard(lang: str = 'ru', callback_data: str = "menu_main") -> InlineKeyboardMarkup:
    """
    Создаёт простую инлайн-клавиатуру с одной кнопкой "Назад".

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param callback_data: (str) Callback data для кнопки (по умолчанию 'menu_main').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
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
    """
    Генерирует инлайн-клавиатуру для выбора количества звезд при пополнении баланса.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры пополнения звёзд.
    """
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
    Создаёт инлайн-клавиатуру главного меню бота для пользователя или администратора.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param user_id: (int | None) ID пользователя Telegram для проверки прав администратора.
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=t("btn_personal_tracking", lang=lang),  # 🎯 Отслеживание (единый функционал)
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
    if user_id is not None and int(user_id) == int(ADMIN_USER_ID):
        buttons.append(
            [InlineKeyboardButton(text=t("admin_panel_button", lang=lang), callback_data="menu_admin_panel")])

    # return buttons
    return InlineKeyboardMarkup(inline_keyboard=buttons)


"""⚙️ Меню настроек"""


def settings_menu_tracking_channels(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура подраздела "Каналы отслеживания".

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_add_channels_tracking", lang=lang),
                    callback_data="settings_update_list"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_channels_list", lang=lang),
                    callback_data="settings_channels_list"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_export_excel", lang=lang),
                    callback_data="settings_tracking_links"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_clear_all_channels", lang=lang),
                    callback_data="settings_channels_clear_confirm"
                ),
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def settings_keywords_submenu_kb(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура подраздела "Ключевые слова".

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_add_keywords", lang=lang),
                    callback_data="settings_enter_keyword"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_keywords_list", lang=lang),
                    callback_data="settings_keywords_list_inline"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_export_keywords", lang=lang),
                    callback_data="settings_keywords_list"
                )
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def settings_notification_group_kb(lang: str = 'ru', group_link: str = '') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура подраздела "Группа уведомлений".

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :param group_link: (str) Ссылка на созданную группу уведомлений.
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    buttons = []
    if group_link:
        buttons.append([
            InlineKeyboardButton(
                text=t("btn_goto_notification_group", lang=lang),
                url=group_link
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text=t("btn_notification_group_not_created", lang=lang),
                callback_data="settings_notification_no_group"
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text=t("btn_recreate_notification_group", lang=lang),
            callback_data="settings_notification_recreate"
        )
    ])
    buttons.append([
        back_button(lang)  # Кнопка ⬅️ Назад
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def channels_list_keyboard(records: list, page: int, total_pages: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура списка каналов с пагинацией и кнопками удаления.

    :param records: (list) Список объектов каналов для текущей страницы.
    :param page: (int) Текущая страница (начиная с 0).
    :param total_pages: (int) Общее количество страниц.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    buttons = []
    for rec in records:
        name = str(rec.username_group)
        display = name if len(name) <= 30 else name[:27] + "..."
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ {display}",
                callback_data=f"ch_del:{name[:60]}"
            )
        ])
    # Навигация
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("btn_nav_prev", lang=lang), callback_data=f"ch_page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("btn_nav_next", lang=lang), callback_data=f"ch_page:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([
        back_button(lang, callback_data="settings_section_channels")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def keywords_list_inline_kb(records: list, page: int, total_pages: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура списка ключевых слов с пагинацией и кнопками удаления.

    :param records: (list) Список объектов ключевых слов для текущей страницы.
    :param page: (int) Текущая страница (начиная с 0).
    :param total_pages: (int) Общее количество страниц.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    buttons = []
    for rec in records:
        kw = str(rec.user_keyword)
        display = kw if len(kw) <= 30 else kw[:27] + "..."
        buttons.append([
            InlineKeyboardButton(
                text=f"❌ {display}",
                callback_data=f"kw_del:{rec.id}"
            )
        ])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text=t("btn_nav_prev", lang=lang), callback_data=f"kw_page:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text=t("btn_nav_next", lang=lang), callback_data=f"kw_page:{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([
        back_button(lang, callback_data="settings_section_keywords")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_clear_keyboard(confirm_cb: str, cancel_cb: str, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения очистки списка.

    :param confirm_cb: (str) Callback data для подтверждения действия.
    :param cancel_cb: (str) Callback data для отмены действия.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры подтверждения.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_confirm_clear", lang=lang), callback_data=confirm_cb),
                InlineKeyboardButton(text=t("btn_cancel", lang=lang), callback_data=cancel_cb)
            ]
        ]
    )


"""Клавиатура администратора"""


def admin_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура панели администратора.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры админ-панели.
    """
    from handlers.admin.nightly_check import get_nightly_check_settings
    settings = get_nightly_check_settings()
    is_on = settings.get("nightly_check_enabled", True)
    status_icon = "🔔" if is_on else "🔕"
    status_text = t("nightly_check_on", lang=lang) if is_on else t("nightly_check_off", lang=lang)
    nightly_btn_text = f"{status_icon} {t('nightly_check_btn', lang=lang)}: {status_text}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_broadcast_users", lang=lang), callback_data="admin_broadcast_start"),
            ],
            [
                InlineKeyboardButton(text=nightly_btn_text, callback_data="admin_toggle_nightly_check"),
            ],
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


def broadcast_preview_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура предпросмотра и подтверждения рассылки сообщений.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t("btn_broadcast_send", lang=lang), callback_data="admin_broadcast_send"),
            ],
            [
                InlineKeyboardButton(text=t("btn_broadcast_cancel", lang=lang), callback_data="admin_broadcast_cancel"),
            ]
        ]
    )


def category_method_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Инлайн-клавиатура для выбора метода присвоения категорий.

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("fast_method_button", lang=lang), callback_data="cat_method_fast"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("powerful_method_openrouter_button", lang=lang),
                    callback_data="cat_method_openrouter"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("powerful_method_groq_button", lang=lang), callback_data="cat_method_groq"
                )
            ],
            [
                back_button(lang)  # Кнопка ⬅️ Назад
            ]
        ]
    )


def personal_tracking_menu_kb(user_id: int, is_active: bool = False, lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура единого меню "Отслеживание ключевых слов".

    :param user_id: (int) ID пользователя Telegram.
    :param is_active: (bool) Флаг активности отслеживания для данного пользователя.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    toggle_tracking_btn = (
        InlineKeyboardButton(text=t("stop_tracking_button", lang=lang), callback_data="tracking_stop")
        if is_active
        else InlineKeyboardButton(text=t("launch_tracking_button", lang=lang), callback_data="menu_launch_tracking")
    )

    buttons = [
        [toggle_tracking_btn],
        [
            InlineKeyboardButton(text=t("btn_pt_add_tracking", lang=lang), callback_data="pt_add_tracking")
        ],
        [
            InlineKeyboardButton(text=t("btn_pt_my_groups", lang=lang), callback_data="pt_list_tracking"),
            InlineKeyboardButton(text=t("btn_pt_buy_slot", lang=lang), callback_data="pt_buy_slot")
        ],
        [
            InlineKeyboardButton(
                text=t("connect_account_button", lang=lang),  # 🔐 Подключение аккаунта
                callback_data="account_connect_menu"
            )
        ]
    ]

    # Добавляем кнопку статистики только для админов
    if user_id is not None and int(user_id) == int(ADMIN_USER_ID):
        buttons.append([InlineKeyboardButton(text=t("btn_pt_stats", lang=lang), callback_data="pt_stats")])

    buttons.append(
        [
            back_button(lang)  # Кнопка ⬅️ Назад (в главное меню)
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== КЛАВИАТУРЫ ====================

def emoji_code_keypad_kb(lang: str = 'ru') -> InlineKeyboardMarkup:
    """
    Клавиатура с цифрами-эмодзи для безопасного выбора цифр кода авторизации (предотвращает спам-блокировку от Telegram).

    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры ввода кода.
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
                InlineKeyboardButton(text=t("btn_keypad_clear", lang=lang), callback_data="pt_digit_clear"),
                InlineKeyboardButton(text="0️⃣", callback_data="pt_digit_0"),
                InlineKeyboardButton(text=t("btn_keypad_submit", lang=lang), callback_data="pt_digit_submit"),
            ],
            [
                InlineKeyboardButton(text=t("btn_keypad_cancel", lang=lang), callback_data="pt_cancel_auth"),
            ]
        ]
    )


"""Клавиатура статистики"""


def tracking_list_keyboard(records, lang: str = 'ru'):
    """
    Клавиатура для списка персональных отслеживаний пользователя.

    :param records: Список записей отслеживаний пользователя.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    buttons = []

    for idx, record in enumerate(records, start=1):
        title = str(getattr(record, 'username_group', None) or getattr(record, 'target_link', None) or "Без ссылки")

        # Обрезаем длинное название для кнопки
        if len(title) > 15:
            title = title[:15] + "..."

        buttons.append(
            [
                InlineKeyboardButton(
                    text=t("btn_pt_edit_record", lang=lang, idx=idx, title=title),
                    callback_data=f"pt_edit_{record.id}"
                )
            ]
        )

    buttons.append([back_button(lang, callback_data="menu_personal_tracking")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_inline_keyboard(stars: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """
    Клавиатура выбора способа оплаты выгрузки базы данных.

    :param stars: (int) Текущий баланс звёзд пользователя.
    :param lang: (str) Код языка пользователя ('ru', 'en').
    :return: (InlineKeyboardMarkup) Объект инлайн-клавиатуры.
    """
    buttons = []
    if stars >= 5:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t("pay_from_balance_btn", lang=lang),
                    callback_data="pay_db_balance"
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text=t("pay_direct_btn", lang=lang),
                callback_data="pay_db_direct"
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text=t("cancel_btn", lang=lang),
                callback_data="pay_db_cancel"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
