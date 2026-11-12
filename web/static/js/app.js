// Инициализация веб-приложения Telegram
const tg = window.Telegram?.WebApp;
let authToken = "";
let userLanguage = "ru"; // резерв по умолчанию
let isAdmin = false;
let isTrackingActive = false;
let statusInterval = null;
let currentSearchResults = [];

if (tg && tg.initData) {
    authToken = tg.initData;
    tg.expand(); // Развернуть мини-приложение до максимальной высоты
    tg.ready();
    console.log("Telegram WebApp loaded successfully.");
} else {
    // Резервный вариант для локальных разработчиков (используйте первый идентификатор администратора: 535185511)
    authToken = "mock_535185511";
    console.warn("Using mock developer credentials.");
}

// Словарь переводов
const translations = {
    ru: {
        title: "AutoParse Alert Monitor",
        hero_title: "AutoParse Alert Monitor",
        hero_desc: "Отслеживание ключевых слов в режиме реального времени в группах и каналах Telegram",
        tracking_active: "Отслеживание активно",
        tracking_inactive: "Отслеживание неактивно",
        start_tracking: "Начать отслеживание",
        stop_tracking: "Остановить отслеживание",
        monitored_channels: "Контролируемые каналы",
        active_keywords: "Активные ключевые слова",
        connected_sessions: "Связанные сеансы",
        groups_db: "Общая база AI",
        target_group_title: "Настройки переадресации",
        target_channel_subtitle: "Целевой канал оповещения",
        target_channel_desc: "Сообщения с ключевыми словами будут пересылаться сюда",
        placeholder_target_group: "@your_channel",
        save: "Сохранить",
        balance_title: "Баланс и утилиты",
        balance_desc: "Покупайте Stars, чтобы обойти 24-часовое ограничение на экспорт баз данных.",
        buy_stars: "Купить Stars",
        add_channels_title: "Добавить каналы для отслеживания",
        placeholder_channel: "@channel_username",
        add: "Добавить",
        drag_drop_txt: "Перетащите <strong>.txt</strong> файл со списком или <span class=\"browse-link\">выберите</span>",
        placeholder_search_channels: "Поиск каналов...",
        no_channels: "Пока не добавлены каналы.",
        loading_channels: "Загрузка каналов...",
        add_keyword_title: "Добавить ключевое слово",
        placeholder_keyword: "например, фриланс, python, разработка",
        add_keyword_btn: "Добавить ключевое слово",
        active_keywords_title: "Активные ключевые слова",
        no_keywords: "Ключевые слова не определены.",
        loading_keywords: "Загрузка ключевых слов...",
        connect_account_title: "Подключить аккаунт Telegram",
        connect_account_desc: "Загрузите файл сессии <strong>.session</strong> (Telethon / Pyrogram) рабочего аккаунта Telegram для автопоиска и мониторинга.",
        drag_drop_session: "Перетащите <strong>.session</strong> файл сюда или <span class=\"browse-link\">выберите на устройстве</span>",
        active_sessions_title: "Активные сессии",
        no_accounts: "Нет подключенных аккаунтов.",
        loading_sessions: "Загрузка сессий...",
        ai_search_title: "Поиск целевой группы с помощью искусственного интеллекта",
        ai_search_desc: "Используйте искусственный интеллект (Groq Llama 3) для генерации поисковых запросов, а затем найдите активные группы Telegram по вашей теме.",
        placeholder_ai_search: "например, Python Developer Jobs, Crypto Trades",
        find_groups: "Найти группы",
        ai_mass_search_title: "Массовый поиск целевых групп с помощью искусственного интеллекта",
        ai_mass_search_desc: "Массовый поиск групп и каналов на основе искусственного интеллекта. Используйте искусственный интеллект (Groq Llama 3) для генерации поисковых запросов, а затем найдите активные группы Telegram по вашей теме.",
        export_db_title: "База данных экспортных групп",
        export_db_desc: "Загрузите отфильтрованную таблицу Excel со всеми обнаруженными группами и каналами Telegram.",
        export_format_label: "Формат экспорта:",
        opt_all_records: "Все записи",
        opt_channels_only: "Только каналы",
        opt_groups_only: "Только для групп",
        filter_category_label: "Категория фильтров:",
        cat_all: "Все категории",
        cat_investments: "Инвестиции",
        cat_finance: "Финансы и личный бюджет",
        cat_crypto: "Криптовалюты и блокчейн",
        cat_business: "Бизнес и предпринимательство",
        cat_marketing: "Маркетинг и продвижение",
        cat_tech: "Технологии и IT",
        cat_education: "Образование и саморазвитие",
        cat_jobs: "Работа и карьера",
        cat_realestate: "Недвижимость",
        cat_health: "Здоровье и медицина",
        cat_travel: "Путешествия",
        cat_auto: "Авто и транспорт",
        cat_shopping: "Шоппинг и скидки",
        cat_entertainment: "Развлечения и досуг",
        cat_politics: "Политика и общество",
        cat_science: "Наука и исследования",
        cat_sport: "Спорт и фитнес",
        cat_cooking: "Кулинария и еда",
        cat_beauty: "Мода и красота",
        cat_hobby: "Хобби и творчество",
        export_limit_warning: "Достигнут лимит бесплатного скачивания (1/24 часа). Следующая загрузка вычитает 5 звёзд.",
        export_excel: "Экспорт в Excel",
        search_results: "Результаты поиска",
        download_results_excel: "Скачать в Excel",
        th_name: "Название",
        th_username: "Юзернейм",
        th_type: "Тип",
        th_members: "Участники",
        th_activity: "Активность",
        admin_panel_title: "Панель управления администратора",
        admin_panel_desc: "Выполняйте операции технического обслуживания, обновляйте сведения о группах, запускайте классификацию с помощью искусственного интеллекта и извлекайте системные журналы.",
        admin_task_running: "Запущенный фоновый процесс",
        admin_task_updating: "Обновление...",
        admin_task_processing: "Обработка данных...",
        admin_check_accounts_title: "Проверка подключенных аккаунтов",
        admin_check_accounts_desc: "Проверка действительности активных сеансов Telegram",
        admin_actualize_db_title: "Актуализировать базу данных",
        admin_actualize_db_desc: "Получение последних идентификаторов и названий Telegram",
        admin_system_files: "Системные файлы",
        admin_feedback_title: "Вопросы и отзывы пользователей",
        admin_feedback_desc: "Загрузка запросов пользователей из базы данных (CSV)",
        admin_logs_title: "Журналы приложений",
        admin_logs_desc: "Просмотр сырого файла журналирования следов бота (logs/log.log)",
        admin_nightly_title: "Ночная проверка базы данных (01:00)",
        admin_nightly_desc: "Автоматическое заполнение категорий и языков для необработанных групп каждые сутки в 01:00 с отчётом администратору в Telegram.",
        admin_nightly_toggle_title: "Статус автозапуска",
        run_now: "Запустить сейчас",
        download: "Загрузка",
        nav_home: "Домой",
        nav_channels: "Каналы",
        nav_keywords: "Слова",
        nav_accounts: "Аккаунты",
        nav_ai_search: "AI поиск",
        nav_admin: "Админ",
        modal_buy_stars_title: "Купить Telegram Stars",
        modal_buy_stars_desc: "Выберите количество звездочек, которые вы хотите приобрести для своего баланса:",
        stars_10: "10 звезд",
        stars_25: "25 звезд",
        stars_50: "50 звезд",
        stars_100: "100 звезд",
        modal_categorize_title: "Выберите метод классификации",
        modal_categorize_desc: "Выберите поставщика искусственного интеллекта и модель для выполнения категоризации чата:",
        cat_method_fast_title: "Быстрый метод (без G4F)",
        cat_method_fast_desc: "Последовательно использует бесплатные модели (gpt-4o-mini, llama-3)",
        cat_method_openrouter_title: "Мощный метод (OpenRouter DeepSeek)",
        cat_method_openrouter_desc: "Использует deepseek-v4-flash через OpenRouter API",
        cat_method_groq_title: "Мощный метод (Groq Llama)",
        cat_method_groq_desc: "Использует llama-3.1-8b через Groq API",
        confirm_delete_channel: "Вы уверены, что хотите прекратить отслеживание этого канала?",
        confirm_delete_keyword: "Удалить это ключевое слово?",
        confirm_delete_account: "Вы уверены, что хотите отключить эту учетную запись Telegram?",
        confirm_admin_action: "Вы уверены, что хотите вызвать действие администратора '{action}'?",
        channel_added: "Канал успешно добавлен!",
        keyword_added: "Ключевое слово добавлено!",
        account_connected: "Аккаунт {phone} успешно подключен!",
        channel_removed: "Канал удален.",
        keyword_removed: "Ключевое слово удалено.",
        account_disconnected: "Аккаунт отключен.",
        tracking_stop_sent: "Команда остановки отслеживания отправлена.",
        tracking_start_sent: "Отслеживание запускается в фоновом режиме...",
        file_sent_to_chat: "Файл отправлен в ваш чат с ботом и скачивается!",
        download_started: "Скачивание началось!",
        export_preparing: "Формирование экспорта базы данных...",
        excel_preparing: "Формирование Excel файла...",
        ai_searching: "AI Group Finder выполняет поиск в Telegram. Пожалуйста, подождите...",
        no_results_found: "В Telegram не найдено ни одной подходящей активной группы.",
        no_results_to_export: "Нет результатов поиска для экспорта",
        no_ids_to_export: "Не найдено ID результатов для экспорта",
        search_failed: "Ошибка поиска.",
        invoice_link_generating: "Создание ссылки на оплату...",
        stars_topup_success: "Баланс успешно пополнен! Добавлено {amount} звезд.",
        payment_cancelled: "Оплата отменена или не удалась.",
        invoice_opened_tab: "Счет открыт в новой вкладке. Пожалуйста, завершите оплату.",
        failed_stars_invoice: "Не удалось создать счет на оплату звезд.",
        admin_bg_started: "Начата фоновая операция: {endpoint}",
        admin_op_failed: "Ошибка операции администратора.",
        file_downloading: "Загрузка файла...",
        file_download_failed: "Ошибка скачивания файла",
        failed_load_dashboard: "Ошибка загрузки данных панели.",
        failed_update_lang: "Не удалось обновить язык.",
        only_txt_supported: "Поддерживаются только списки .txt.",
        uploading_channels: "Загрузка списка каналов...",
        channels_imported: "Импортировано: добавлено {added}, пропущено {skipped}.",
        only_session_supported: "Поддерживаются только файлы Telethon .session.",
        verifying_session: "Проверка и загрузка файла сессии...",
        network_error: "Сетевая ошибка",
        operation_failed: "Операция не удалась.",
        added_on: "Добавлен:",
        connected_on: "Подключен:",
        private_channel: "Приватный",
        limit_warning_text: "Достигнут 24-часовой лимит экспорта (Следующий бесплатно: {hours} ч. {minutes} мин.). Следующая загрузка будет стоить 5 звезд. (Ваш баланс: {balance}).",
        toggle_theme: "Переключить тему",
        switch_language: "Переключить язык",
        loading: "Загрузка...",
        success_saved: "Настройки успешно сохранены!",
        failed_save: "Ошибка сохранения настроек.",
        error_load: "Ошибка загрузки данных.",
        invalid_file: "Неверный формат файла.",
        starting: "Запуск...",
        stopping: "Остановка...",
        status_active: "Активен",
        status_inactive: "Неактивен",
        status_unknown: "Неизвестно"
    },
    en: {
        title: "AutoParse Alert Monitor",
        hero_title: "AutoParse Alert Monitor",
        hero_desc: "Real-time keyword monitoring in Telegram groups and channels",
        tracking_active: "Tracking Active",
        tracking_inactive: "Tracking Inactive",
        start_tracking: "Start Tracking",
        stop_tracking: "Stop Tracking",
        monitored_channels: "Monitored Channels",
        active_keywords: "Active Keywords",
        connected_sessions: "Connected Sessions",
        groups_db: "Global AI Database",
        target_group_title: "Forwarding Settings",
        target_channel_subtitle: "Target Alert Channel",
        target_channel_desc: "Keyword messages will be forwarded here",
        placeholder_target_group: "@your_channel",
        save: "Save",
        balance_title: "Balance & Utilities",
        balance_desc: "Buy Stars to bypass the 24-hour database export limit.",
        buy_stars: "Buy Stars",
        add_channels_title: "Add Channels to Track",
        placeholder_channel: "@channel_username",
        add: "Add",
        drag_drop_txt: "Drag & Drop <strong>.txt</strong> file with channels or <span class=\"browse-link\">browse</span>",
        placeholder_search_channels: "Search channels...",
        no_channels: "No tracked channels yet.",
        loading_channels: "Loading channels...",
        add_keyword_title: "Add Alert Keyword",
        placeholder_keyword: "e.g. freelance, python, developer",
        add_keyword_btn: "Add Keyword",
        active_keywords_title: "Active Keywords",
        no_keywords: "No keywords defined.",
        loading_keywords: "Loading keywords...",
        connect_account_title: "Connect Telegram Account",
        connect_account_desc: "Upload a <strong>.session</strong> file (Telethon / Pyrogram) of a working Telegram account for automated search and monitoring.",
        drag_drop_session: "Drag & drop <strong>.session</strong> file here or <span class=\"browse-link\">browse</span>",
        active_sessions_title: "Active Sessions",
        no_accounts: "No accounts connected.",
        loading_sessions: "Loading sessions...",
        ai_search_title: "AI Target Group Search",
        ai_search_desc: "Use AI (Groq Llama 3) to generate search queries and find active Telegram groups on your topic.",
        placeholder_ai_search: "e.g. Python Developer Jobs, Crypto Trades",
        find_groups: "Find Groups",
        ai_mass_search_title: "Mass AI Target Group Search",
        ai_mass_search_desc: "Mass search of groups and channels powered by AI. Use AI (Groq Llama 3) to generate queries and find active Telegram groups.",
        export_db_title: "Export Groups Database",
        export_db_desc: "Download a filtered Excel spreadsheet with all discovered Telegram groups and channels.",
        export_format_label: "Export format:",
        opt_all_records: "All records",
        opt_channels_only: "Channels only",
        opt_groups_only: "Groups only",
        filter_category_label: "Filter category:",
        cat_all: "All categories",
        cat_investments: "Investments",
        cat_finance: "Finance & Personal Budget",
        cat_crypto: "Cryptocurrency & Blockchain",
        cat_business: "Business & Entrepreneurship",
        cat_marketing: "Marketing & Promotion",
        cat_tech: "Technology & IT",
        cat_education: "Education & Self-development",
        cat_jobs: "Jobs & Career",
        cat_realestate: "Real Estate",
        cat_health: "Health & Medicine",
        cat_travel: "Travel",
        cat_auto: "Auto & Transport",
        cat_shopping: "Shopping & Discounts",
        cat_entertainment: "Entertainment & Leisure",
        cat_politics: "Politics & Society",
        cat_science: "Science & Research",
        cat_sport: "Sports & Fitness",
        cat_cooking: "Cooking & Food",
        cat_beauty: "Fashion & Beauty",
        cat_hobby: "Hobbies & Creativity",
        export_limit_warning: "Free download limit reached (1/24 hours). Next export costs 5 stars.",
        export_excel: "Export to Excel",
        search_results: "Search Results",
        download_results_excel: "Export to Excel",
        th_name: "Name",
        th_username: "Username",
        th_type: "Type",
        th_members: "Members",
        th_activity: "Activity",
        admin_panel_title: "Admin Control Panel",
        admin_panel_desc: "Perform maintenance operations, refresh group info, trigger AI classification, and retrieve system logs.",
        admin_task_running: "Running Background Process",
        admin_task_updating: "Updating...",
        admin_task_processing: "Processing data...",
        admin_check_accounts_title: "Check Connected Accounts",
        admin_check_accounts_desc: "Check validity of active Telegram sessions",
        admin_actualize_db_title: "Actualize Database",
        admin_actualize_db_desc: "Fetch latest Telegram IDs and titles",
        admin_system_files: "System Files",
        admin_feedback_title: "User Questions & Feedback",
        admin_feedback_desc: "Download user queries from database (CSV)",
        admin_logs_title: "Application Logs",
        admin_logs_desc: "View raw bot tracing log file (logs/log.log)",
        admin_nightly_title: "Nightly Database Check (01:00)",
        admin_nightly_desc: "Automatic category and language completion for unclassified groups every night at 01:00 with Telegram report.",
        admin_nightly_toggle_title: "Auto-run Status",
        run_now: "Run Now",
        download: "Download",
        nav_home: "Home",
        nav_channels: "Channels",
        nav_keywords: "Keywords",
        nav_accounts: "Accounts",
        nav_ai_search: "AI Search",
        nav_admin: "Admin",
        modal_buy_stars_title: "Buy Telegram Stars",
        modal_buy_stars_desc: "Select the number of stars you want to purchase for your balance:",
        stars_10: "10 Stars",
        stars_25: "25 Stars",
        stars_50: "50 Stars",
        stars_100: "100 Stars",
        modal_categorize_title: "Select Categorization Method",
        modal_categorize_desc: "Select an AI provider and model to perform chat categorization:",
        cat_method_fast_title: "Fast Method (No G4F)",
        cat_method_fast_desc: "Sequentially uses free models (gpt-4o-mini, llama-3)",
        cat_method_openrouter_title: "Powerful Method (OpenRouter DeepSeek)",
        cat_method_openrouter_desc: "Uses deepseek-v4-flash via OpenRouter API",
        cat_method_groq_title: "Powerful Method (Groq Llama)",
        cat_method_groq_desc: "Uses llama-3.1-8b via Groq API",
        confirm_delete_channel: "Are you sure you want to stop tracking this channel?",
        confirm_delete_keyword: "Delete this keyword?",
        confirm_delete_account: "Are you sure you want to disconnect this Telegram account?",
        confirm_admin_action: "Are you sure you want to trigger admin action '{action}'?",
        channel_added: "Channel added successfully!",
        keyword_added: "Keyword added successfully!",
        account_connected: "Account {phone} connected successfully!",
        channel_removed: "Channel removed.",
        keyword_removed: "Keyword deleted.",
        account_disconnected: "Account disconnected.",
        tracking_stop_sent: "Tracking stop command sent.",
        tracking_start_sent: "Tracking starting in background...",
        file_sent_to_chat: "File sent to your bot chat and downloading!",
        download_started: "Download started!",
        export_preparing: "Generating database export...",
        excel_preparing: "Generating Excel file...",
        ai_searching: "AI Group Finder is searching Telegram. Please wait...",
        no_results_found: "No matching active groups found in Telegram.",
        no_results_to_export: "No search results to export",
        no_ids_to_export: "No result IDs found for export",
        search_failed: "Search failed.",
        invoice_link_generating: "Generating invoice link...",
        stars_topup_success: "Stars top up success! Added {amount} stars.",
        payment_cancelled: "Payment cancelled or failed.",
        invoice_opened_tab: "Invoice opened in new tab. Please complete payment.",
        failed_stars_invoice: "Failed to create stars invoice.",
        admin_bg_started: "Started background operation: {endpoint}",
        admin_op_failed: "Admin operation failed.",
        file_downloading: "Downloading file...",
        file_download_failed: "File download failed",
        failed_load_dashboard: "Failed to load dashboard data.",
        failed_update_lang: "Failed to update language.",
        only_txt_supported: "Only .txt lists are supported.",
        uploading_channels: "Uploading channel list...",
        channels_imported: "Imported: {added} added, {skipped} skipped.",
        only_session_supported: "Only Telethon .session files are supported.",
        verifying_session: "Verifying & uploading session file...",
        network_error: "Network error",
        operation_failed: "Operation failed.",
        added_on: "Added:",
        connected_on: "Connected:",
        private_channel: "Private",
        limit_warning_text: "24-hour export limit reached (Next free: {hours}h {minutes}m). Next download will cost 5 stars. (Your balance: {balance}).",
        toggle_theme: "Toggle theme",
        switch_language: "Switch language",
        loading: "Loading...",
        success_saved: "Settings saved successfully!",
        failed_save: "Failed to save settings.",
        error_load: "Error loading data.",
        invalid_file: "Invalid file format.",
        starting: "Starting...",
        stopping: "Stopping...",
        status_active: "Active",
        status_inactive: "Inactive",
        status_unknown: "Unknown"
    }
};

// Функция перевода
function i18n(key, params = {}) {
    const langDict = translations[userLanguage] || translations.ru || {};
    let text = langDict[key] || translations.ru[key] || key;
    for (const [k, v] of Object.entries(params)) {
        text = text.replace(new RegExp(`\\{${k}\\}`, "g"), v);
    }
    return text;
}

// Помощник по выборке API с заголовком аутентификации
async function apiRequest(endpoint, options = {}) {
    options.headers = options.headers || {};
    options.headers["Authorization"] = `Bearer ${authToken}`;

    try {
        const response = await fetch(endpoint, options);
        if (response.status === 401) {
            showNotification(
                "Unauthorized. Please relaunch the app in Telegram.",
                "danger",
            );
            throw new Error("Unauthorized");
        }
        return response;
    } catch (e) {
        console.error("API error:", e);
        throw e;
    }
}

// Вспомогательная функция для скачивания Blob (Excel файлов)
function downloadBlob(blob, response, fallbackFilename = "export.xlsx") {
    const disposition =
        response && response.headers
            ? response.headers.get("content-disposition")
            : null;
    let filename = fallbackFilename;
    if (disposition && disposition.indexOf("filename=") !== -1) {
        filename = disposition.split("filename=")[1].replace(/"/g, "");
    }

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    setTimeout(() => {
        a.remove();
        window.URL.revokeObjectURL(url);
    }, 2000);
}

// Инициализация приложения
document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Определить язык
        if (tg && tg.initDataUnsafe?.user?.language_code) {
            const lang = tg.initDataUnsafe.user.language_code.toLowerCase();
            userLanguage =
                lang === "ru" || lang === "be" || lang === "uk" ? "ru" : "en";
        }

        // Инициализировать тему (Светлая / Тёмная)
        initTheme();

        // Проверьте локальное хранилище на предмет языковых предпочтений.
        const savedLang = localStorage.getItem("lang_pref");
        if (savedLang) {
            userLanguage = savedLang;
        }

        try {
            applyTranslations();
        } catch (e) {
            console.error("applyTranslations failed:", e);
        }

        try {
            await loadDashboardData();
        } catch (e) {
            console.error("loadDashboardData failed:", e);
        }

        try {
            setupEventListeners();
        } catch (e) {
            console.error("setupEventListeners failed:", e);
        }

        try {
            setupDragAndDrop();
        } catch (e) {
            console.error("setupDragAndDrop failed:", e);
        }
    } catch (e) {
        console.error("Initialization failed:", e);
    } finally {
        // Всегда скрывать экран загрузки
        const container = document.getElementById("app-container");
        if (container) {
            container.classList.remove("loading");
        }
    }

    // Настройка интервала автоматического обновления статуса (каждые 5 секунд)
    statusInterval = setInterval(refreshStatusAndTasks, 5000);
});

// Обновить текстовые значения пользовательского интерфейса в зависимости от активного языка.
function applyTranslations() {
    // 1. Текстовые элементы по data-i18n
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        const val = i18n(key);
        if (val) {
            el.innerHTML = val;
        }
    });

    // 2. Плейсхолдеры по data-i18n-placeholder
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
        const key = el.getAttribute("data-i18n-placeholder");
        const val = i18n(key);
        if (val) {
            el.placeholder = val;
        }
    });

    // 3. Подсказки title по data-i18n-title
    document.querySelectorAll("[data-i18n-title]").forEach((el) => {
        const key = el.getAttribute("data-i18n-title");
        const val = i18n(key);
        if (val) {
            el.title = val;
        }
    });

    // 4. Обновить статус отслеживания
    setTrackingStatusUI();

    // 5. Обновить атрибут lang страницы
    document.documentElement.lang = userLanguage;

    // 6. Обновить результаты поиска если открыты
    if (currentSearchResults && currentSearchResults.length > 0) {
        renderSearchResults(currentSearchResults, false);
    }
}

// Переключение активных вкладок навигации
function switchTab(tabId) {
    // Скрыть все вкладки
    document
        .querySelectorAll(".tab-content")
        .forEach((el) => el.classList.remove("active"));
    document
        .querySelectorAll(".nav-item")
        .forEach((el) => el.classList.remove("active"));

    // Показать вкладку выбора
    const targetTab = document.getElementById(`tab-${tabId}`);
    if (targetTab) {
        targetTab.classList.add("active");
    }

    // Выделить кнопку меню
    const navButtons = document.querySelectorAll(".nav-item");
    navButtons.forEach((btn) => {
        const onclickAttr = btn.getAttribute("onclick") || "";
        if (onclickAttr.includes(`'${tabId}'`)) {
            btn.classList.add("active");
        }
    });

    // Загрузить данные для конкретной вкладки
    if (tabId === "channels") {
        loadChannelsList();
    } else if (tabId === "keywords") {
        loadKeywordsList();
    } else if (tabId === "accounts") {
        loadAccountsList();
    } else if (tabId === "admin") {
        refreshStatusAndTasks();
        loadNightlyCheckStatus();
    }
}

// Статистика статуса загрузки и ограничения пользователей
async function loadDashboardData() {
    try {
        const res = await apiRequest("/api/status");
        if (res.ok) {
            const data = await res.json();

            // Установить профиль пользователя
            const initials = data.first_name
                ? data.first_name.charAt(0)
                : data.username
                    ? data.username.charAt(0)
                    : "T";
            document.getElementById("user-avatar").innerText = initials.toUpperCase();
            document.getElementById("user-fullname").innerText =
                data.first_name || data.username || "User";
            document.getElementById("user-tag").innerText = data.username
                ? `@${data.username}`
                : `ID: ${data.user_id}`;
            document.getElementById("stars-count").innerText = data.stars;

            // Статистика
            document.getElementById("stat-channels").innerText =
                data.stats.tracked_channels;
            document.getElementById("stat-keywords").innerText = data.stats.keywords;
            document.getElementById("stat-accounts").innerText =
                data.stats.connected_accounts;
            document.getElementById("stat-db-groups").innerText =
                data.stats.db_total_groups;

            // Целевая группа
            if (data.stats.target_group_username) {
                document.getElementById("target-group-input").value =
                    data.stats.target_group_username;
            }

            // Интерфейс отслеживания статуса
            setTrackingStatusUI(data.tracking_active);

            // Показывать кнопку вкладки администратора, если пользователь является администратором
            isAdmin = data.is_admin;
            if (isAdmin) {
                document.getElementById("nav-admin").classList.remove("hidden");
            } else {
                document.getElementById("nav-admin").classList.add("hidden");
            }

            // Обновить предпочтительную конфигурацию языка
            if (
                data.language &&
                data.language !== "unset" &&
                data.language !== userLanguage
            ) {
                userLanguage = data.language;
                localStorage.setItem("lang_pref", userLanguage);
                applyTranslations();
            }

            // Проверьте предупреждение об экспорте
            checkExportLimits();
        }
    } catch (e) {
        showNotification(i18n("failed_load_dashboard"), "danger");
    }
}

// Обновить активный пульс отслеживания и активные операции администратора.
async function refreshStatusAndTasks() {
    try {
        const res = await apiRequest("/api/status");
        if (res.ok) {
            const data = await res.json();
            setTrackingStatusUI(data.tracking_active);
            document.getElementById("stars-count").innerText = data.stars;

            // Update stats
            document.getElementById("stat-channels").innerText =
                data.stats.tracked_channels;
            document.getElementById("stat-keywords").innerText = data.stats.keywords;
            document.getElementById("stat-accounts").innerText =
                data.stats.connected_accounts;
            document.getElementById("stat-db-groups").innerText =
                data.stats.db_total_groups;
        }

        // If admin, check admin task progress
        if (isAdmin) {
            const adminRes = await apiRequest("/api/admin/status");
            if (adminRes.ok) {
                const adminData = await adminRes.json();
                const task = adminData.task;

                const taskCard = document.getElementById("admin-task-card");
                if (task.status === "running") {
                    taskCard.classList.remove("hidden");

                    document.getElementById("admin-task-name").innerText =
                        `Action: ${task.action.toUpperCase()}`;
                    document.getElementById("admin-task-message").innerText =
                        task.message;

                    const progress = task.progress || 0;
                    const total = task.total || 0;
                    document.getElementById("admin-progress-text").innerText =
                        `${progress} / ${total}`;

                    const pct = total > 0 ? (progress / total) * 100 : 0;
                    document.getElementById("admin-progress-fill").style.width =
                        `${pct}%`;
                } else {
                    taskCard.classList.add("hidden");
                }
            }
        }
    } catch (e) {
        console.error("Auto-refresh status check failed:", e);
    }
}

// Помощник для переключения импульса состояния отслеживания
function setTrackingStatusUI(isActive) {
    if (typeof isActive === "boolean") {
        isTrackingActive = isActive;
    }
    const pulse = document.getElementById("status-pulse");
    const label = document.getElementById("status-text");
    const toggleBtn = document.getElementById("btn-toggle-tracking");

    if (isTrackingActive) {
        if (pulse) pulse.className = "status-pulse active";
        if (label) label.innerText = i18n("tracking_active");
        if (toggleBtn) {
            toggleBtn.className = "btn-danger glow-effect";
            const icon = toggleBtn.querySelector("i");
            if (icon) icon.className = "fa-solid fa-stop";
            const span = toggleBtn.querySelector("span");
            if (span) span.innerText = i18n("stop_tracking");
        }
    } else {
        if (pulse) pulse.className = "status-pulse inactive";
        if (label) label.innerText = i18n("tracking_inactive");
        if (toggleBtn) {
            toggleBtn.className = "btn-primary glow-effect";
            const icon = toggleBtn.querySelector("i");
            if (icon) icon.className = "fa-solid fa-play";
            const span = toggleBtn.querySelector("span");
            if (span) span.innerText = i18n("start_tracking");
        }
    }
}

function initTheme() {
    const savedTheme = localStorage.getItem("theme_pref") || "light";
    setTheme(savedTheme);
}

function setTheme(theme) {
    document.body.setAttribute("data-theme", theme);
    localStorage.setItem("theme_pref", theme);
    const icon = document.getElementById("theme-toggle-icon");
    if (icon) {
        if (theme === "dark") {
            icon.className = "fa-solid fa-sun";
        } else {
            icon.className = "fa-solid fa-moon";
        }
    }
}

// Рендеринг таблицы результатов поиска
function renderSearchResults(groups, shouldScroll = true) {
    currentSearchResults = groups || [];
    const resultsCard = document.getElementById("search-results-card");
    const list = document.getElementById("search-results-list");

    list.innerHTML = "";
    document.getElementById("results-count").innerText = currentSearchResults.length;

    if (currentSearchResults.length > 0) {
        resultsCard.classList.remove("hidden");
        currentSearchResults.forEach((g) => {
            const tr = document.createElement("tr");
            const statusClass =
                g.availability === "active"
                    ? "status-active"
                    : g.availability === "inactive"
                        ? "status-inactive"
                        : "status-unknown";
            const statusLabel =
                g.availability === "active"
                    ? i18n("status_active")
                    : g.availability === "inactive"
                        ? i18n("status_inactive")
                        : i18n("status_unknown");

            tr.innerHTML = `
                <td><strong>${g.name || ""}</strong></td>
                <td><a href="${g.link || "#"}" target="_blank">${g.username || i18n("private_channel")}</a></td>
                <td>${g.group_type || ""}</td>
                <td>${(g.participants || 0).toLocaleString()}</td>
                <td><span class="label-status ${statusClass}">${statusLabel}</span></td>
            `;
            list.appendChild(tr);
        });
        if (shouldScroll) {
            resultsCard.scrollIntoView({behavior: "smooth"});
        }
    } else {
        resultsCard.classList.add("hidden");
        showNotification(i18n("no_results_found"), "warning");
    }
}

// Кнопки настройки и события ввода
function setupEventListeners() {
    // Кнопка переключения темы
    const themeBtn = document.getElementById("theme-toggle-btn");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            const currentTheme = document.body.getAttribute("data-theme") || "light";
            const nextTheme = currentTheme === "light" ? "dark" : "light";
            setTheme(nextTheme);
        });
    }

    // Кнопка переключения языка
    const langBtn = document.getElementById("lang-toggle-btn");
    if (langBtn) {
        langBtn.addEventListener("click", async () => {
            const nextLang = userLanguage === "ru" ? "en" : "ru";
            try {
                const res = await apiRequest(
                    `/api/settings/language?lang=${nextLang}`,
                    {method: "POST"},
                );
                if (res.ok) {
                    userLanguage = nextLang;
                    localStorage.setItem("lang_pref", userLanguage);
                    applyTranslations();
                    loadDashboardData();
                    showNotification(i18n("success_saved"), "success");
                }
            } catch (e) {
                showNotification(i18n("failed_update_lang"), "danger");
            }
        });
    }

    // Переключение начала/остановки отслеживания
    const toggleTrackingBtn = document.getElementById("btn-toggle-tracking");
    if (toggleTrackingBtn) {
        toggleTrackingBtn.addEventListener("click", async () => {
            const currentActive = toggleTrackingBtn.className.includes("btn-danger");
            toggleTrackingBtn.disabled = true;

            try {
                if (currentActive) {
                    const res = await apiRequest("/api/tracking/stop", {
                        method: "POST",
                    });
                    if (res.ok) {
                        showNotification(i18n("tracking_stop_sent"), "success");
                    }
                } else {
                    const res = await apiRequest("/api/tracking/start", {
                        method: "POST",
                    });
                    if (res.ok) {
                        showNotification(i18n("tracking_start_sent"), "success");
                    }
                }
                setTimeout(loadDashboardData, 1000);
            } catch (e) {
                showNotification(i18n("operation_failed"), "danger");
            } finally {
                toggleTrackingBtn.disabled = false;
            }
        });
    }

    // Сохранить целевую/группу пересылки
    const saveTargetBtn = document.getElementById("btn-save-target-group");
    if (saveTargetBtn) {
        saveTargetBtn.addEventListener("click", async () => {
            const input = document.getElementById("target-group-input");
            const username = input.value.trim();
            if (!username) return;

            const formData = new FormData();
            formData.append("username", username);

            try {
                const res = await apiRequest("/api/target-group", {
                    method: "POST",
                    body: formData,
                });
                if (res.ok) {
                    showNotification(i18n("success_saved"), "success");
                    loadDashboardData();
                } else {
                    showNotification(i18n("failed_save"), "danger");
                }
            } catch (e) {
                showNotification(i18n("network_error"), "danger");
            }
        });
    }

    // Добавить канал, отслеживаемый вручную
    const addChannelBtn = document.getElementById("btn-add-channel");
    if (addChannelBtn) {
        addChannelBtn.addEventListener("click", async () => {
            const input = document.getElementById("channel-username-input");
            const val = input.value.trim();
            if (!val) return;

            const fd = new FormData();
            fd.append("username", val);

            try {
                const res = await apiRequest("/api/channels", {
                    method: "POST",
                    body: fd,
                });
                if (res.ok) {
                    input.value = "";
                    loadChannelsList();
                    showNotification(i18n("channel_added"), "success");
                } else {
                    const error = await res.json();
                    showNotification(error.detail || i18n("operation_failed"), "danger");
                }
            } catch (e) {
                showNotification(i18n("network_error"), "danger");
            }
        });
    }

    // Добавить ключевое слово
    const addKeywordBtn = document.getElementById("btn-add-keyword");
    if (addKeywordBtn) {
        addKeywordBtn.addEventListener("click", async () => {
            const input = document.getElementById("keyword-input");
            const val = input.value.trim();
            if (!val) return;

            const fd = new FormData();
            fd.append("keyword", val);

            try {
                const res = await apiRequest("/api/keywords", {
                    method: "POST",
                    body: fd,
                });
                if (res.ok) {
                    input.value = "";
                    loadKeywordsList();
                    showNotification(i18n("keyword_added"), "success");
                } else {
                    const err = await res.json();
                    showNotification(err.detail || i18n("operation_failed"), "danger");
                }
            } catch (e) {
                showNotification(i18n("network_error"), "danger");
            }
        });
    }

    // Пополнение звезд вызывает модальное окно
    const topupModalBtn = document.getElementById("btn-topup-modal");
    if (topupModalBtn) {
        topupModalBtn.addEventListener("click", () => {
            document.getElementById("topup-modal").classList.remove("hidden");
        });
    }

    // Экспорт таблицы БД
    const exportDbBtn = document.getElementById("btn-export-db");
    if (exportDbBtn) {
        exportDbBtn.addEventListener("click", async () => {
            const expType = document.getElementById("export-type").value;
            const category = document.getElementById("export-category").value;

            const fd = new FormData();
            fd.append("export_type", expType);
            fd.append("category", category);

            showNotification(i18n("export_preparing"), "success");

            try {
                const res = await apiRequest("/api/export/download", {
                    method: "POST",
                    body: fd,
                });

                if (res.ok) {
                    const blob = await res.blob();
                    downloadBlob(blob, res, "db_export.xlsx");

                    if (window.Telegram?.WebApp) {
                        showNotification(i18n("file_sent_to_chat"), "success");
                    } else {
                        showNotification(i18n("download_started"), "success");
                    }
                    loadDashboardData();
                } else {
                    const err = await res.json();
                    showNotification(err.detail || i18n("operation_failed"), "danger");
                }
            } catch (e) {
                console.error("Export DB error:", e);
                showNotification(i18n("network_error"), "danger");
            }
        });
    }

    // Фильтр поиска по списку отслеживаемых каналов
    const filterInput = document.getElementById("search-channels-filter");
    if (filterInput) {
        filterInput.addEventListener("input", (e) => {
            const filterText = e.target.value.toLowerCase();
            const items = document.querySelectorAll("#channels-list .list-item");
            items.forEach((item) => {
                const titleEl = item.querySelector(".item-title");
                const username = titleEl ? titleEl.innerText.toLowerCase() : "";
                if (username.includes(filterText)) {
                    item.style.display = "flex";
                } else {
                    item.style.display = "none";
                }
            });
        });
    }

    // Запустить поиск AI
    const triggerAiSearchBtn = document.getElementById("btn-trigger-ai-search");
    if (triggerAiSearchBtn) {
        triggerAiSearchBtn.addEventListener("click", async () => {
            const input = document.getElementById("ai-search-query");
            const query = input.value.trim();
            if (!query) return;

            const fd = new FormData();
            fd.append("query", query);

            const spinner = document.getElementById("search-spinner");
            triggerAiSearchBtn.disabled = true;
            if (spinner) spinner.classList.remove("hidden");

            showNotification(i18n("ai_searching"), "success");

            try {
                const res = await apiRequest("/api/search/ai", {
                    method: "POST",
                    body: fd,
                });

                if (res.ok) {
                    const data = await res.json();
                    renderSearchResults(data.groups || []);
                } else {
                    const err = await res.json();
                    showNotification(err.detail || i18n("search_failed"), "danger");
                }
            } catch (e) {
                showNotification(i18n("search_failed"), "danger");
            } finally {
                triggerAiSearchBtn.disabled = false;
                if (spinner) spinner.classList.add("hidden");
            }
        });
    }

    // Запустить массовый поиск AI
    const triggerAiSearchsBtn = document.getElementById("btn-trigger-ai-searchs");
    if (triggerAiSearchsBtn) {
        triggerAiSearchsBtn.addEventListener("click", async () => {
            const input = document.getElementById("ai-search-querys");
            const query = input.value.trim();
            if (!query) return;

            const fd = new FormData();
            fd.append("query", query);

            const spinner = document.getElementById("search-spinners");
            triggerAiSearchsBtn.disabled = true;
            if (spinner) spinner.classList.remove("hidden");

            showNotification(i18n("ai_searching"), "success");

            try {
                const res = await apiRequest("/api/searchs/ai", {
                    method: "POST",
                    body: fd,
                });

                if (res.ok) {
                    const data = await res.json();
                    renderSearchResults(data.groups || []);
                } else {
                    const err = await res.json();
                    showNotification(err.detail || i18n("search_failed"), "danger");
                }
            } catch (e) {
                showNotification(i18n("search_failed"), "danger");
            } finally {
                triggerAiSearchsBtn.disabled = false;
                if (spinner) spinner.classList.add("hidden");
            }
        });
    }

    // Экспорт результатов поиска в Excel
    const btnExportSearch = document.getElementById("btn-export-search-results");
    if (btnExportSearch) {
        btnExportSearch.addEventListener("click", async () => {
            if (!currentSearchResults || currentSearchResults.length === 0) {
                showNotification(i18n("no_results_to_export"), "warning");
                return;
            }
            const ids = currentSearchResults
                .map((g) => g.telegram_id || g.id)
                .filter(Boolean);
            if (ids.length === 0) {
                showNotification(i18n("no_ids_to_export"), "warning");
                return;
            }

            const fd = new FormData();
            fd.append("telegram_ids", ids.join(","));

            showNotification(i18n("excel_preparing"), "success");

            try {
                const res = await apiRequest("/api/search/export_excel", {
                    method: "POST",
                    body: fd,
                });

                if (res.ok) {
                    const blob = await res.blob();
                    downloadBlob(blob, res, "search_results.xlsx");

                    if (window.Telegram?.WebApp) {
                        showNotification(i18n("file_sent_to_chat"), "success");
                    } else {
                        showNotification(i18n("download_started"), "success");
                    }
                } else {
                    const err = await res.json();
                    showNotification(err.detail || i18n("operation_failed"), "danger");
                }
            } catch (e) {
                console.error("Export search excel error:", e);
                showNotification(i18n("network_error"), "danger");
            }
        });
    }
}

// Перетащите вспомогательные привязки
function setupDragAndDrop() {
    // Каналы TXT Перетаскивание
    const chZone = document.getElementById("channel-drop-zone");
    const chFileInput = document.getElementById("channel-file-input");

    if (chZone && chFileInput) {
        chZone.addEventListener("click", () => chFileInput.click());
        chFileInput.addEventListener("change", (e) =>
            handleChannelFileUpload(e.target.files[0]),
        );
        bindDragEvents(chZone, handleChannelFileUpload);
    }

    // Перетаскивание сеанса учетных записей
    const accZone = document.getElementById("session-drop-zone");
    const accFileInput = document.getElementById("session-file-input");

    if (accZone && accFileInput) {
        accZone.addEventListener("click", () => accFileInput.click());
        accFileInput.addEventListener("change", (e) =>
            handleSessionFileUpload(e.target.files[0]),
        );
        bindDragEvents(accZone, handleSessionFileUpload);
    }
}

function bindDragEvents(zone, uploadCallback) {
    ["dragenter", "dragover"].forEach((eventName) => {
        zone.addEventListener(
            eventName,
            (e) => {
                e.preventDefault();
                zone.classList.add("dragover");
            },
            false,
        );
    });

    ["dragleave", "drop"].forEach((eventName) => {
        zone.addEventListener(
            eventName,
            (e) => {
                e.preventDefault();
                zone.classList.remove("dragover");
            },
            false,
        );
    });

    zone.addEventListener(
        "drop",
        (e) => {
            const dt = e.dataTransfer;
            const file = dt.files[0];
            if (file) {
                uploadCallback(file);
            }
        },
        false,
    );
}

// Реализации загрузки файлов
async function handleChannelFileUpload(file) {
    if (!file || !file.name.endsWith(".txt")) {
        showNotification(i18n("only_txt_supported"), "danger");
        return;
    }

    const fd = new FormData();
    fd.append("file", file);

    showNotification(i18n("uploading_channels"), "success");

    try {
        const res = await apiRequest("/api/channels/upload", {
            method: "POST",
            body: fd,
        });
        if (res.ok) {
            const data = await res.json();
            showNotification(
                i18n("channels_imported", {added: data.added, skipped: data.skipped}),
                "success",
            );
            loadChannelsList();
        } else {
            showNotification(i18n("operation_failed"), "danger");
        }
    } catch (e) {
        showNotification(i18n("network_error"), "danger");
    }
}

async function handleSessionFileUpload(file) {
    if (!file || !file.name.endsWith(".session")) {
        showNotification(i18n("only_session_supported"), "danger");
        return;
    }

    const fd = new FormData();
    fd.append("file", file);

    showNotification(i18n("verifying_session"), "success");

    try {
        const res = await apiRequest("/api/accounts/upload", {
            method: "POST",
            body: fd,
        });
        if (res.ok) {
            const data = await res.json();
            showNotification(
                i18n("account_connected", {phone: data.phone}),
                "success",
            );
            loadAccountsList();
            loadDashboardData();
        } else {
            const err = await res.json();
            showNotification(err.detail || i18n("operation_failed"), "danger");
        }
    } catch (e) {
        showNotification(i18n("network_error"), "danger");
    }
}

// Загрузчики данных
async function loadChannelsList() {
    const list = document.getElementById("channels-list");
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin"></i> ${i18n("loading_channels")}</div>`;

    try {
        const res = await apiRequest("/api/channels");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("channels-count").innerText = data.length;
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = `<div class="empty-state">${i18n("no_channels")}</div>`;
                return;
            }

            data.forEach((item) => {
                const el = document.createElement("div");
                el.className = "list-item";
                el.innerHTML = `
                    <div class="item-main">
                        <span class="item-title">${item.username}</span>
                        <span class="item-desc">${i18n("added_on")} ${item.date_added}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteChannel(${item.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
                list.appendChild(el);
            });
        }
    } catch (e) {
        list.innerHTML = `<div class="empty-state text-danger">${i18n("error_load")}</div>`;
    }
}

async function deleteChannel(id) {
    if (!confirm(i18n("confirm_delete_channel")))
        return;
    try {
        const res = await apiRequest(`/api/channels/${id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            showNotification(i18n("channel_removed"), "success");
            loadChannelsList();
            loadDashboardData();
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

async function loadKeywordsList() {
    const list = document.getElementById("keywords-list");
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin"></i> ${i18n("loading_keywords")}</div>`;

    try {
        const res = await apiRequest("/api/keywords");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("keywords-count").innerText = data.length;
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = `<div class="empty-state">${i18n("no_keywords")}</div>`;
                return;
            }

            data.forEach((item) => {
                const el = document.createElement("div");
                el.className = "list-item";
                el.innerHTML = `
                    <div class="item-main">
                        <span class="item-title">\`${item.keyword}\`</span>
                    </div>
                    <button class="delete-btn" onclick="deleteKeyword(${item.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
                list.appendChild(el);
            });
        }
    } catch (e) {
        list.innerHTML = `<div class="empty-state text-danger">${i18n("error_load")}</div>`;
    }
}

async function deleteKeyword(id) {
    if (!confirm(i18n("confirm_delete_keyword")))
        return;
    try {
        const res = await apiRequest(`/api/keywords/${id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            showNotification(i18n("keyword_removed"), "success");
            loadKeywordsList();
            loadDashboardData();
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

async function loadAccountsList() {
    const list = document.getElementById("accounts-list");
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin"></i> ${i18n("loading_sessions")}</div>`;

    try {
        const res = await apiRequest("/api/accounts");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("accounts-count").innerText = data.length;
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = `<div class="empty-state">${i18n("no_accounts")}</div>`;
                return;
            }

            data.forEach((item) => {
                const el = document.createElement("div");
                el.className = "list-item";
                const isRunning = item.is_active;
                const statusBadge = isRunning
                    ? `<span style="color: #10b981; font-weight: bold; font-size: 12px;"><i class="fa-solid fa-circle"></i> ${userLanguage === 'ru' ? 'Активен' : 'Active'}</span>`
                    : `<span style="color: #ef4444; font-size: 12px;"><i class="fa-regular fa-circle"></i> ${userLanguage === 'ru' ? 'Остановлен' : 'Stopped'}</span>`;
                const allChatsChecked = item.track_all_chats ? "checked" : "";

                el.innerHTML = `
                    <div class="item-main" style="width: 100%;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="item-title" style="font-size: 15px;">
                                <i class="fa-solid fa-user-tag icon-inline"></i> <b>${item.account_title || item.phone_number}</b>
                                <button class="btn-sm" style="background: none; border: none; cursor: pointer; color: #888; margin-left: 6px;" onclick="editAccountTitle(${item.id}, '${item.account_title || ''}')" title="Сменить название">
                                    <i class="fa-solid fa-pen"></i>
                                </button>
                            </span>
                            ${statusBadge}
                        </div>
                        <div style="font-size: 12px; color: #aaa; margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 10px;">
                            <span><i class="fa-solid fa-phone"></i> ${item.phone_number}</span>
                            <span><i class="fa-solid fa-tower-broadcast"></i> ${userLanguage === 'ru' ? 'Каналов' : 'Channels'}: <b>${item.channels_count || 0}</b></span>
                            <span><i class="fa-solid fa-tag"></i> ${userLanguage === 'ru' ? 'Слов' : 'Keywords'}: <b>${item.keywords_count || 0}</b></span>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 6px;">
                            <button class="btn btn-sm ${isRunning ? 'btn-danger' : 'btn-primary'}" onclick="toggleAccountTracking(${item.id}, ${isRunning})" style="padding: 4px 10px; font-size: 12px;">
                                <i class="fa-solid ${isRunning ? 'fa-stop' : 'fa-play'}"></i> ${isRunning ? (userLanguage === 'ru' ? 'Остановить' : 'Stop') : (userLanguage === 'ru' ? 'Запустить' : 'Start')}
                            </button>
                            <button class="btn btn-sm btn-secondary" onclick="syncAccountDialogs(${item.id})" style="padding: 4px 10px; font-size: 12px;" title="Синхронизировать закрытые и открытые чаты из tdata/Telegram">
                                <i class="fa-solid fa-rotate"></i> ${userLanguage === 'ru' ? 'Импорт чатов' : 'Import chats'}
                            </button>
                            <label style="font-size: 12px; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; margin-left: auto;">
                                <input type="checkbox" ${allChatsChecked} onchange="toggleAccountAllChats(${item.id}, this.checked)">
                                <span>${userLanguage === 'ru' ? 'Все чаты' : 'All chats'}</span>
                            </label>
                            <button class="delete-btn" style="margin-left: 6px;" onclick="deleteAccount('${item.id}')" title="Отключить">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
                list.appendChild(el);
            });
        }
    } catch (e) {
        list.innerHTML = `<div class="empty-state text-danger">${i18n("error_load")}</div>`;
    }
}

async function toggleAccountTracking(id, isRunning) {
    try {
        const endpoint = isRunning ? `/api/tracking/stop?account_id=${id}` : `/api/tracking/start?account_id=${id}`;
        const res = await apiRequest(endpoint, { method: "POST" });
        if (res.ok) {
            showNotification(isRunning ? (userLanguage === 'ru' ? 'Мониторинг остановлен' : 'Monitoring stopped') : (userLanguage === 'ru' ? 'Мониторинг запущен' : 'Monitoring started'), "success");
            loadAccountsList();
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

async function editAccountTitle(id, currentTitle) {
    const newTitle = prompt(userLanguage === 'ru' ? "Введите новое название/тему кампании (например, Диваны):" : "Enter new campaign title (e.g., Sofas):", currentTitle);
    if (newTitle === null) return;
    try {
        const formData = new FormData();
        formData.append("account_title", newTitle.trim());
        const res = await apiRequest(`/api/accounts/${id}/settings`, {
            method: "POST",
            body: formData
        });
        if (res.ok) {
            showNotification(userLanguage === 'ru' ? "Название обновлено" : "Title updated", "success");
            loadAccountsList();
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

async function toggleAccountAllChats(id, checked) {
    try {
        const formData = new FormData();
        formData.append("track_all_chats", checked);
        const res = await apiRequest(`/api/accounts/${id}/settings`, {
            method: "POST",
            body: formData
        });
        if (res.ok) {
            showNotification(userLanguage === 'ru' ? `Режим «Все чаты»: ${checked ? 'ВКЛ' : 'ВЫКЛ'}` : `All chats mode: ${checked ? 'ON' : 'OFF'}`, "success");
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

async function syncAccountDialogs(id) {
    showNotification(userLanguage === 'ru' ? "Сканирование закрытых и открытых чатов..." : "Scanning closed and open chats...", "info");
    try {
        const res = await apiRequest(`/api/accounts/${id}/sync-dialogs`, { method: "POST" });
        if (res.ok) {
            const data = await res.json();
            showNotification(userLanguage === 'ru' ? `Синхронизировано чатов: ${data.count}` : `Chats synced: ${data.count}`, "success");
            loadChannelsList();
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

async function deleteAccount(phone) {
    if (!confirm(i18n("confirm_delete_account")))
        return;
    try {
        const res = await apiRequest(`/api/accounts/${phone}`, {
            method: "DELETE",
        });
        if (res.ok) {
            showNotification(i18n("account_disconnected"), "success");
            loadAccountsList();
            loadDashboardData();
        }
    } catch (e) {
        showNotification(i18n("operation_failed"), "danger");
    }
}

// Триггер вариантов оплаты Star
async function buyStars(amount) {
    closeModal("topup");
    showNotification(i18n("invoice_link_generating"), "success");

    try {
        const res = await apiRequest(`/api/payment/stars-topup?amount=${amount}`, {
            method: "POST",
        });
        if (res.ok) {
            const data = await res.json();
            const link = data.invoice_link;

            // Проверьте, доступен ли TG WebApp SDK и открыт ли он в исходном виде.
            if (tg && tg.openInvoice) {
                tg.openInvoice(link, (status) => {
                    if (status === "paid") {
                        showNotification(
                            i18n("stars_topup_success", {amount}),
                            "success",
                        );
                        setTimeout(loadDashboardData, 1000);
                    } else {
                        showNotification(i18n("payment_cancelled"), "warning");
                    }
                });
            } else {
                // Обычный резервный браузер, открыть URL-адрес в новом окне
                window.open(link, "_blank");
                showNotification(
                    i18n("invoice_opened_tab"),
                    "warning",
                );
            }
        }
    } catch (e) {
        showNotification(i18n("failed_stars_invoice"), "danger");
    }
}

async function checkExportLimits() {
    try {
        const res = await apiRequest("/api/export/check");
        if (res.ok) {
            const data = await res.json();
            const warning = document.getElementById("export-limit-warning");
            if (!data.is_free) {
                warning.classList.remove("hidden");
                const hours = Math.floor(data.remaining_seconds / 3600);
                const minutes = Math.floor((data.remaining_seconds % 3600) / 60);
                warning.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${i18n("limit_warning_text", {
                    hours,
                    minutes,
                    balance: data.stars_balance
                })}`;
            } else {
                warning.classList.add("hidden");
            }
        }
    } catch (e) {
        console.error("Export limits check failed:", e);
    }
}

// Задачи администратора
async function triggerAdminAction(endpoint) {
    if (!confirm(i18n("confirm_admin_action", {action: endpoint})))
        return;
    try {
        const res = await apiRequest(`/api/admin/${endpoint}`, {
            method: "POST",
        });
        if (res.ok) {
            showNotification(i18n("admin_bg_started", {endpoint}), "success");
            refreshStatusAndTasks();
        } else {
            showNotification(i18n("admin_op_failed"), "danger");
        }
    } catch (e) {
        showNotification(i18n("admin_op_failed"), "danger");
    }
}

function openCategorizeModal() {
    document.getElementById("categorize-modal").classList.remove("hidden");
}

async function triggerCategorize(method) {
    closeModal("categorize");
    try {
        const res = await apiRequest(`/api/admin/categorize?method=${method}`, {
            method: "POST",
        });
        if (res.ok) {
            showNotification(
                i18n("admin_bg_started", {endpoint: method}),
                "success",
            );
            refreshStatusAndTasks();
        }
    } catch (e) {
        showNotification(i18n("admin_op_failed"), "danger");
    }
}

async function downloadAdminFile(endpoint) {
    showNotification(i18n("file_downloading"), "success");
    try {
        const res = await apiRequest(`/api/admin/${endpoint}`);
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;

            let filename =
                endpoint === "logs" ? "bot_logs.txt" : "questions_export.csv";
            const disposition = res.headers.get("content-disposition");
            if (disposition && disposition.indexOf("filename=") !== -1) {
                filename = disposition.split("filename=")[1].replace(/"/g, "");
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            showNotification(i18n("file_download_failed"), "danger");
        }
    } catch (e) {
        showNotification(i18n("file_download_failed"), "danger");
    }
}

// Помощники модального закрытия
function closeModal(modalId) {
    document.getElementById(`${modalId}-modal`).classList.add("hidden");
}

// Баннер настраиваемых уведомлений о предупреждениях
let bannerTimeout = null;

function showNotification(msg, type = "success") {
    const banner = document.getElementById("notification-banner");
    const bannerText = document.getElementById("notification-message");

    if (!banner || !bannerText) return;

    if (type === "success") {
        banner.style.background = "rgba(16, 185, 129, 0.2)";
        banner.style.borderLeftColor = "var(--color-success)";
    } else if (type === "danger") {
        banner.style.background = "rgba(239, 68, 68, 0.2)";
        banner.style.borderLeftColor = "var(--color-danger)";
    } else if (type === "warning") {
        banner.style.background = "rgba(245, 158, 11, 0.2)";
        banner.style.borderLeftColor = "var(--color-warning)";
    }

    bannerText.innerText = msg;
    banner.classList.remove("hidden");

    if (bannerTimeout) clearTimeout(bannerTimeout);
    bannerTimeout = setTimeout(() => {
        banner.classList.add("hidden");
    }, 4500);
}

const notifCloseBtn = document.getElementById("notification-close-btn");
if (notifCloseBtn) {
    notifCloseBtn.addEventListener("click", () => {
        const banner = document.getElementById("notification-banner");
        if (banner) banner.classList.add("hidden");
    });
}

// ==================== НОЧНАЯ ПРОВЕРКА БАЗЫ ДАННЫХ ====================

async function loadNightlyCheckStatus() {
    try {
        const res = await apiRequest("/api/admin/nightly-check");
        if (res.ok) {
            const data = await res.json();
            const settings = data.settings || {};
            const isEnabled = !!settings.nightly_check_enabled;

            const btn = document.getElementById("btn-toggle-nightly-check");
            const icon = document.getElementById("nightly-toggle-icon");
            const label = document.getElementById("nightly-toggle-label");
            const statusDesc = document.getElementById("nightly-status-desc");
            const remainingCount = document.getElementById("nightly-remaining-count");
            const lastRunInfo = document.getElementById("nightly-last-run-info");

            if (btn && label && icon) {
                if (isEnabled) {
                    btn.className = "btn-success";
                    icon.className = "fa-solid fa-bell";
                    label.innerText = userLanguage === "ru" ? "ВКЛ" : "ON";
                    if (statusDesc) {
                        statusDesc.innerText = userLanguage === "ru" ? "Каждую ночь в 01:00 (Активно)" : "Every night at 01:00 (Active)";
                    }
                } else {
                    btn.className = "btn-secondary";
                    icon.className = "fa-solid fa-bell-slash";
                    label.innerText = userLanguage === "ru" ? "ВЫКЛ" : "OFF";
                    if (statusDesc) {
                        statusDesc.innerText = userLanguage === "ru" ? "Автозапуск отключён" : "Auto-run disabled";
                    }
                }
            }

            if (remainingCount) {
                remainingCount.innerText = `${data.remaining_no_cat || 0} / ${data.remaining_no_lang || 0}`;
            }

            if (lastRunInfo && settings.last_run_date) {
                lastRunInfo.innerText = `${userLanguage === "ru" ? "Последний запуск:" : "Last run:"} ${settings.last_run_date}`;
            }
        }
    } catch (e) {
        console.error("Failed to load nightly check status:", e);
    }
}

async function toggleNightlyCheck() {
    try {
        const res = await apiRequest("/api/admin/nightly-check/toggle", { method: "POST" });
        if (res.ok) {
            const data = await res.json();
            const isEnabled = data.enabled;
            showNotification(
                isEnabled
                    ? (userLanguage === "ru" ? "🔔 Ночная проверка базы данных в 01:00 ВКЛЮЧЕНА" : "🔔 Nightly check at 01:00 ENABLED")
                    : (userLanguage === "ru" ? "🔕 Ночная проверка базы данных ВЫКЛЮЧЕНА" : "🔕 Nightly check DISABLED"),
                "success"
            );
            loadNightlyCheckStatus();
        } else {
            showNotification(i18n("admin_op_failed"), "danger");
        }
    } catch (e) {
        showNotification(i18n("admin_op_failed"), "danger");
    }
}

async function runNightlyCheckNow() {
    try {
        showNotification(userLanguage === "ru" ? "🚀 Запуск проверки базы данных в фоне..." : "🚀 Starting database check in background...", "success");
        const res = await apiRequest("/api/admin/nightly-check/run", { method: "POST" });
        if (res.ok) {
            setTimeout(loadNightlyCheckStatus, 3000);
        }
    } catch (e) {
        showNotification(i18n("admin_op_failed"), "danger");
    }
}