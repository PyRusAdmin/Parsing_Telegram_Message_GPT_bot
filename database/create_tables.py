from loguru import logger  # https://github.com/Delgan/loguru

from database.database import database, AccountFree, TelegramGroups
# from database.database import User  # Таблица User объединена с users_personal_trackings
from database.users_accounts import UsersAccounts
from database.users_groups import UsersGroups
from database.users_keywords import Keywords
from database.users_personal_trackings import UsersPersonalTrackings, PersonalTracking
from database.users_questions import UsersQuestions

"""Создает таблицы для базы данных, если ранее не были созданы"""


def migrate_old_table_names():
    """
    Переименовывает старые имена таблиц и колонок в новую структуру:
    - keywords -> users_keywords
    - account -> users_accounts
    - user_groups -> users_groups
    - personal_tracking / users_personal_tracking -> users_personal_trackings
    - question -> users_questions
    - user объединяется с users_personal_trackings (за основу берется User с переносом данных)
    Удаляет устаревшую таблицу personal_tracking_stats.
    """
    cursor = database.execute_sql("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    # Удаляем устаревшую таблицу personal_tracking_stats, если она существует
    if "personal_tracking_stats" in existing_tables:
        logger.info("🗑️ Удаление устаревшей таблицы 'personal_tracking_stats'...")
        database.execute_sql("DROP TABLE IF EXISTS personal_tracking_stats;")
        logger.success("✅ Устаревшая таблица 'personal_tracking_stats' успешно удалена")
        existing_tables.remove("personal_tracking_stats")
    else:
        database.execute_sql("DROP TABLE IF EXISTS personal_tracking_stats;")

    table_renames = [
        ("keywords", "users_keywords"),
        ("account", "users_accounts"),
        ("users_account", "users_accounts"),
        ("user_groups", "users_groups"),
        ("personal_tracking", "users_personal_trackings"),
        ("users_personal_tracking", "users_personal_trackings"),
        ("question", "users_questions")
    ]

    for old_name, new_name in table_renames:
        if old_name in existing_tables and new_name not in existing_tables:
            logger.info(f"🔄 Миграция таблицы: {old_name} -> {new_name}")
            database.execute_sql(f"ALTER TABLE {old_name} RENAME TO {new_name};")
            logger.success(f"✅ Таблица '{old_name}' успешно переименована в '{new_name}'")
            existing_tables.remove(old_name)
            existing_tables.add(new_name)

    # Объединение таблицы User с таблицей users_personal_trackings (за основу берется User)
    if "user" in existing_tables:
        if "users_personal_trackings" in existing_tables:
            cursor_cnt = database.execute_sql("SELECT COUNT(*) FROM users_personal_trackings;")
            pt_count = cursor_cnt.fetchone()[0]
            if pt_count == 0:
                logger.info("🔄 Замена пустой таблицы 'users_personal_trackings' на основу из 'user'...")
                database.execute_sql("DROP TABLE users_personal_trackings;")
                database.execute_sql("ALTER TABLE user RENAME TO users_personal_trackings;")
                existing_tables.remove("user")
            else:
                logger.info("🔄 Перенос пользователей из 'user' в 'users_personal_trackings'...")
                database.execute_sql("""
                    INSERT OR IGNORE INTO users_personal_trackings (
                        user_id, language, stars, last_free_download_at, last_changed_at
                    )
                    SELECT user_id, language, stars, last_free_download_at, CURRENT_TIMESTAMP
                    FROM user;
                """)
        else:
            logger.info("🔄 Переименование базовой таблицы 'user' в 'users_personal_trackings'...")
            database.execute_sql("ALTER TABLE user RENAME TO users_personal_trackings;")
            existing_tables.remove("user")
            existing_tables.add("users_personal_trackings")

    # Проверяем колонки в users_personal_trackings
    cursor = database.execute_sql("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}

    if "users_personal_trackings" in existing_tables:
        cursor_pt_cols = database.execute_sql("PRAGMA table_info(users_personal_trackings);")
        existing_pt_cols = {row[1] for row in cursor_pt_cols.fetchall()}

        columns_to_add_pt = [
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("user_last_name", "VARCHAR(255)"),
            ("created_group_link", "VARCHAR(255)"),
            ("created_group_id", "INTEGER"),
            ("language", "VARCHAR(10) DEFAULT 'ru'"),
            ("stars", "INTEGER DEFAULT 0"),
            ("last_free_download_at", "DATETIME"),
            ("shared_account", "VARCHAR(255) DEFAULT ''"),
            ("personal_account", "VARCHAR(255) DEFAULT ''"),
            ("last_changed_at", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_pt:
            if col_name not in existing_pt_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_personal_trackings'...")
                database.execute_sql(f"ALTER TABLE users_personal_trackings ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_personal_trackings'")
                existing_pt_cols.add(col_name)

        # Копируем данные из старых колонок (username -> user_username, first_name -> user_firstname, last_name -> user_last_name)
        if "username" in existing_pt_cols:
            database.execute_sql("UPDATE users_personal_trackings SET user_username = username WHERE user_username IS NULL AND username IS NOT NULL;")
        if "first_name" in existing_pt_cols:
            database.execute_sql("UPDATE users_personal_trackings SET user_firstname = first_name WHERE user_firstname IS NULL AND first_name IS NOT NULL;")
        if "last_name" in existing_pt_cols:
            database.execute_sql("UPDATE users_personal_trackings SET user_last_name = last_name WHERE user_last_name IS NULL AND last_name IS NOT NULL;")

        database.execute_sql("UPDATE users_personal_trackings SET last_changed_at = CURRENT_TIMESTAMP WHERE last_changed_at IS NULL;")

    # Проверяем колонки в users_accounts
    if "users_accounts" in existing_tables:
        cursor_cols = database.execute_sql("PRAGMA table_info(users_accounts);")
        existing_cols = {row[1] for row in cursor_cols.fetchall()}

        if "session_string" in existing_cols and "user_session_string" not in existing_cols:
            logger.info(
                "🔄 Миграция: переименование колонки 'session_string' -> 'user_session_string' в 'users_accounts'...")
            database.execute_sql("ALTER TABLE users_accounts RENAME COLUMN session_string TO user_session_string;")
            existing_cols.remove("session_string")
            existing_cols.add("user_session_string")

        if "phone_number" in existing_cols and "phone_number_session_string" not in existing_cols:
            logger.info(
                "🔄 Миграция: переименование колонки 'phone_number' -> 'phone_number_session_string' в 'users_accounts'...")
            database.execute_sql(
                "ALTER TABLE users_accounts RENAME COLUMN phone_number TO phone_number_session_string;")
            existing_cols.remove("phone_number")
            existing_cols.add("phone_number_session_string")

        columns_to_add_accounts = [
            ("user_id", "INTEGER"),
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("phone_number_session_string", "VARCHAR(255)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_accounts:
            if col_name not in existing_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_accounts'...")
                database.execute_sql(f"ALTER TABLE users_accounts ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_accounts'")
                existing_cols.add(col_name)

    # Проверяем колонки в users_keywords
    if "users_keywords" in existing_tables:
        cursor_kw_cols = database.execute_sql("PRAGMA table_info(users_keywords);")
        existing_kw_cols = {row[1] for row in cursor_kw_cols.fetchall()}

        columns_to_add_kw = [
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("user_session_string", "VARCHAR(500)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_kw:
            if col_name not in existing_kw_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_keywords'...")
                database.execute_sql(f"ALTER TABLE users_keywords ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_keywords'")
                existing_kw_cols.add(col_name)

    # Проверяем колонки в users_groups
    if "users_groups" in existing_tables:
        cursor_gr_cols = database.execute_sql("PRAGMA table_info(users_groups);")
        existing_gr_cols = {row[1] for row in cursor_gr_cols.fetchall()}

        columns_to_add_gr = [
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("id_group", "INTEGER"),
            ("name_group", "VARCHAR(255)"),
            ("user_session_string", "VARCHAR(500)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_gr:
            if col_name not in existing_gr_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_groups'...")
                database.execute_sql(f"ALTER TABLE users_groups ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_groups'")
                existing_gr_cols.add(col_name)

    # Проверяем колонки в users_questions
    if "users_questions" in existing_tables:
        cursor_q_cols = database.execute_sql("PRAGMA table_info(users_questions);")
        existing_q_cols = {row[1] for row in cursor_q_cols.fetchall()}

        if "question" in existing_q_cols and "user_question" not in existing_q_cols:
            logger.info("🔄 Миграция: переименование колонки 'question' -> 'user_question' в 'users_questions'...")
            database.execute_sql("ALTER TABLE users_questions RENAME COLUMN question TO user_question;")
            existing_q_cols.remove("question")
            existing_q_cols.add("user_question")

        if "answer" in existing_q_cols and "answer_ai" not in existing_q_cols:
            logger.info("🔄 Миграция: переименование колонки 'answer' -> 'answer_ai' в 'users_questions'...")
            database.execute_sql("ALTER TABLE users_questions RENAME COLUMN answer TO answer_ai;")
            existing_q_cols.remove("answer")
            existing_q_cols.add("answer_ai")

        if "status" in existing_q_cols and "status_question" not in existing_q_cols:
            logger.info("🔄 Миграция: переименование колонки 'status' -> 'status_question' в 'users_questions'...")
            database.execute_sql("ALTER TABLE users_questions RENAME COLUMN status TO status_question;")
            existing_q_cols.remove("status")
            existing_q_cols.add("status_question")

        columns_to_add_questions = [
            ("question_number", "INTEGER"),
            ("user_username", "VARCHAR(255)"),
            ("user_firstname", "VARCHAR(255)"),
            ("answer_ai", "TEXT"),
            ("status_question", "VARCHAR(100)"),
            ("date_added", "DATETIME")
        ]
        for col_name, col_type in columns_to_add_questions:
            if col_name not in existing_q_cols:
                logger.info(f"🔄 Миграция: добавление колонки '{col_name}' в 'users_questions'...")
                database.execute_sql(f"ALTER TABLE users_questions ADD COLUMN {col_name} {col_type};")
                logger.success(f"✅ Колонка '{col_name}' успешно добавлена в 'users_questions'")
                existing_q_cols.add(col_name)

        # Заполняем question_number и status_question для существующих строк при необходимости
        database.execute_sql("UPDATE users_questions SET question_number = id WHERE question_number IS NULL;")
        database.execute_sql("UPDATE users_questions SET status_question = 'Не проверен' WHERE status_question IS NULL OR status_question = 'Новый';")


def init_database():
    """Инициализация БД и создание таблиц"""
    database.connect(reuse_if_open=True)

    migrate_old_table_names()

    database.create_tables(
        [
            UsersAccounts,  # Таблица аккаунтов пользователей (users_accounts)
            AccountFree,  # Таблица бесплатных аккаунтов от админа (выдаются пользователям для парсинга ключевых слов)
            TelegramGroups,  # Таблица общей базы Telegram-групп и каналов по категориям
            UsersQuestions,  # Таблица вопросов и ответов пользователей для расширения базы знаний (users_questions)
            # User,  # Таблица User объединена с users_personal_trackings (закомментирована, но не удалена)
            UsersPersonalTrackings,
            # Таблица данных о пользователе бота и настроек персонального отслеживания (users_personal_trackings)
            Keywords,  # Таблица ключевых слов пользователей (users_keywords)
            UsersGroups  # Таблица целевых каналов и групп пользователей для мониторинга (users_groups)
        ],
        safe=True
    )

    logger.info(
        "✅ База данных инициализирована. Проверены/созданы таблицы:\n"
        "  • Account (users_accounts) — аккаунты пользователей для поиска ключевых слов\n"
        "  • AccountFree — пул бесплатных аккаунтов от администратора\n"
        "  • TelegramGroup — общая база каналов и групп по категориям\n"
        "  • Question (users_questions) — вопросы пользователей для базы знаний\n"
        "  • UsersPersonalTrackings (users_personal_trackings) — профили пользователей бота и персональный трекинг\n"
        "  • Keywords (users_keywords) — ключевые слова пользователей для отслеживания\n"
        "  • Group (users_groups) — отслеживаемые пользователями каналы и группы"
    )

    database.close()
