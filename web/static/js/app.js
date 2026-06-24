// Инициализация веб-приложения Telegram
const tg = window.Telegram?.WebApp;
let authToken = "";
let userLanguage = "ru"; // резерв по умолчанию
let isAdmin = false;
let statusInterval = null;

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
        title: "AutoParse Панель",
        tracking_active: "Отслеживание Активно",
        tracking_inactive: "Отслеживание Неактивно",
        start_tracking: "Запустить отслеживание",
        stop_tracking: "Остановить отслеживание",
        monitored_channels: "Каналы отслеживания",
        active_keywords: "Ключевые слова",
        connected_sessions: "Подключено аккаунтов",
        groups_db: "Групп в базе",
        target_group_title: "Группа для пересылки",
        save: "Сохранить",
        add: "Добавить",
        upload_txt:
            "Перетащите файл <strong>.txt</strong> со списком или <span>выберите</span>",
        upload_session:
            "Перетащите файл <strong>.session</strong> или <span>выберите</span>",
        search_results: "Результаты поиска",
        all_records: "Вся база",
        channels_only: "Только каналы",
        groups_only: "Только группы",
        all_categories: "Все категории",
        export_excel: "Скачать базу Excel",
        find_groups: "Найти группы",
        admin_panel: "Панель администратора",
        check_accounts: "Проверить сессии",
        actualize_db: "Актуализация БД",
        classify_ai: "AI Категоризация",
        detect_lang: "Определить языки",
        download: "Скачать",
        stars_invoice_desc: "Пополнение баланса на {amount} звезд",
        success_saved: "Настройки успешно сохранены!",
        failed_save: "Ошибка сохранения настроек.",
        error_load: "Ошибка загрузки данных.",
        invalid_file: "Неверный формат файла.",
        starting: "Запуск...",
        stopping: "Остановка...",
    },
    en: {
        title: "AutoParse Panel",
        tracking_active: "Tracking Active",
        tracking_inactive: "Tracking Inactive",
        start_tracking: "Start Tracking",
        stop_tracking: "Stop Tracking",
        monitored_channels: "Monitored Channels",
        active_keywords: "Active Keywords",
        connected_sessions: "Connected Sessions",
        groups_db: "Telegram Groups DB",
        target_group_title: "Forwarding Settings",
        save: "Save",
        add: "Add",
        upload_txt:
            "Drag & Drop <strong>.txt</strong> file with channels or <span>browse</span>",
        upload_session:
            "Drag & Drop <strong>.session</strong> file or <span>browse</span>",
        search_results: "Search Results",
        all_records: "All Records",
        channels_only: "Channels Only",
        groups_only: "Groups Only",
        all_categories: "All Categories",
        export_excel: "Export to Excel",
        find_groups: "Find Groups",
        admin_panel: "Admin Control Panel",
        check_accounts: "Check Sessions",
        actualize_db: "Actualize DB",
        classify_ai: "Classify AI",
        detect_lang: "Detect Languages",
        download: "Download",
        stars_invoice_desc: "Stars balance top up: {amount} stars",
        success_saved: "Settings saved successfully!",
        failed_save: "Failed to save settings.",
        error_load: "Error loading data.",
        invalid_file: "Invalid file format.",
        starting: "Starting...",
        stopping: "Stopping...",
    },
};

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

// Инициализация приложения
document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Определить язык
        if (tg && tg.initDataUnsafe?.user?.language_code) {
            const lang = tg.initDataUnsafe.user.language_code.toLowerCase();
            userLanguage =
                lang === "ru" || lang === "be" || lang === "uk" ? "ru" : "en";
        }

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
    const t = translations[userLanguage] || translations.en || {};

    // Элементы всей страницы
    document.querySelector(".hero-title").innerText = t.title || "Title";
    document.querySelector(".hero-desc").innerText =
        t.hero_desc || t.title || "";

    // Установить метки блоков статистики
    document.querySelector("[onclick=\"switchTab('channels')\"] p").innerText =
        t.monitored_channels || "Monitored Channels";
    document.querySelector("[onclick=\"switchTab('keywords')\"] p").innerText =
        t.active_keywords;
    document.querySelector("[onclick=\"switchTab('accounts')\"] p").innerText =
        t.connected_sessions;
    document.querySelector("[onclick=\"switchTab('admin')\"] span").innerText =
        "Admin";

    // Встроенные заголовки
    document.querySelector("#tab-dashboard .card h3").innerHTML =
        `<i class="fa-solid fa-gears icon-inline"></i> ${t.target_group_title}`;
    document.querySelector("#tab-channels .card h3").innerHTML =
        `<i class="fa-solid fa-square-plus icon-inline"></i> ${translations[userLanguage] === translations.ru ? "Добавить каналы" : "Add Channels to Track"}`;
    document.querySelector("#tab-keywords .card h3").innerHTML =
        `<i class="fa-solid fa-key icon-inline"></i> ${translations[userLanguage] === translations.ru ? "Добавить ключевое слово" : "Add Alert Keyword"}`;
    document.querySelector("#tab-accounts .card h3").innerHTML =
        `<i class="fa-solid fa-user-plus icon-inline"></i> ${translations[userLanguage] === translations.ru ? "Подключить аккаунт Telegram" : "Connect Telegram Account"}`;
    document.querySelector("#tab-search .card h3").innerHTML =
        `<i class="fa-solid fa-robot icon-inline"></i> ${t.classify_ai}`;
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
        if (btn.getAttribute("onclick").includes(`'${tabId}'`)) {
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
            document.getElementById("user-avatar").innerText =
                initials.toUpperCase();
            document.getElementById("user-fullname").innerText =
                data.first_name || data.username || "User";
            document.getElementById("user-tag").innerText = data.username
                ? `@${data.username}`
                : `ID: ${data.user_id}`;
            document.getElementById("stars-count").innerText = data.stars;

            // Статистика
            document.getElementById("stat-channels").innerText =
                data.stats.tracked_channels;
            document.getElementById("stat-keywords").innerText =
                data.stats.keywords;
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
        showNotification("Failed to load dashboard data.", "danger");
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
            document.getElementById("stat-keywords").innerText =
                data.stats.keywords;
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
    const t = translations[userLanguage];
    const pulse = document.getElementById("status-pulse");
    const label = document.getElementById("status-text");
    const toggleBtn = document.getElementById("btn-toggle-tracking");

    if (isActive) {
        pulse.className = "status-pulse active";
        label.innerText = t.tracking_active;
        toggleBtn.className = "btn-danger glow-effect";
        toggleBtn.querySelector("i").className = "fa-solid fa-stop";
        toggleBtn.querySelector("span").innerText = t.stop_tracking;
    } else {
        pulse.className = "status-pulse inactive";
        label.innerText = t.tracking_inactive;
        toggleBtn.className = "btn-primary glow-effect";
        toggleBtn.querySelector("i").className = "fa-solid fa-play";
        toggleBtn.querySelector("span").innerText = t.start_tracking;
    }
}

// Кнопки настройки и события ввода
function setupEventListeners() {
    // Кнопка переключения языка
    document
        .getElementById("lang-toggle-btn")
        .addEventListener("click", async () => {
            const nextLang = userLanguage === "ru" ? "en" : "ru";
            try {
                const res = await apiRequest(
                    `/api/settings/language?lang=${nextLang}`,
                    { method: "POST" },
                );
                if (res.ok) {
                    userLanguage = nextLang;
                    localStorage.setItem("lang_pref", userLanguage);
                    applyTranslations();
                    loadDashboardData();
                    showNotification(
                        translations[userLanguage].success_saved,
                        "success",
                    );
                }
            } catch (e) {
                showNotification("Failed to update language.", "danger");
            }
        });

    // Переключение начала/остановки отслеживания
    document
        .getElementById("btn-toggle-tracking")
        .addEventListener("click", async () => {
            const btn = document.getElementById("btn-toggle-tracking");
            const currentActive = btn.className.includes("btn-danger");

            btn.disabled = true;

            try {
                if (currentActive) {
                    const res = await apiRequest("/api/tracking/stop", {
                        method: "POST",
                    });
                    if (res.ok) {
                        showNotification(
                            "Tracking stop command sent.",
                            "success",
                        );
                    }
                } else {
                    const res = await apiRequest("/api/tracking/start", {
                        method: "POST",
                    });
                    if (res.ok) {
                        showNotification(
                            "Tracking starting in background...",
                            "success",
                        );
                    }
                }
                // Подождите 1 секунду, затем перезагрузите
                setTimeout(loadDashboardData, 1000);
            } catch (e) {
                showNotification("Operation failed.", "danger");
            } finally {
                btn.disabled = false;
            }
        });

    // Сохранить целевую/группу пересылки
    document
        .getElementById("btn-save-target-group")
        .addEventListener("click", async () => {
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
                    showNotification(
                        translations[userLanguage].success_saved,
                        "success",
                    );
                    loadDashboardData();
                } else {
                    showNotification(
                        translations[userLanguage].failed_save,
                        "danger",
                    );
                }
            } catch (e) {
                showNotification("Network error", "danger");
            }
        });

    // Добавить канал, отслеживаемый вручную
    document
        .getElementById("btn-add-channel")
        .addEventListener("click", async () => {
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
                    showNotification("Channel added successfully!", "success");
                } else {
                    const error = await res.json();
                    showNotification(
                        error.detail || "Error adding channel",
                        "danger",
                    );
                }
            } catch (e) {
                showNotification("Network error", "danger");
            }
        });

    // Добавить ключевое слово
    document
        .getElementById("btn-add-keyword")
        .addEventListener("click", async () => {
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
                    showNotification("Keyword added!", "success");
                } else {
                    const err = await res.json();
                    showNotification(
                        err.detail || "Error adding keyword",
                        "danger",
                    );
                }
            } catch (e) {
                showNotification("Network error", "danger");
            }
        });

    // Пополнение звезд вызывает модальное окно
    document.getElementById("btn-topup-modal").addEventListener("click", () => {
        document.getElementById("topup-modal").classList.remove("hidden");
    });

    // Экспорт таблицы БД
    document
        .getElementById("btn-export-db")
        .addEventListener("click", async () => {
            const expType = document.getElementById("export-type").value;
            const category = document.getElementById("export-category").value;

            const fd = new FormData();
            fd.append("export_type", expType);
            fd.append("category", category);

            showNotification("Generating database export...", "success");

            try {
                const res = await apiRequest("/api/export/download", {
                    method: "POST",
                    body: fd,
                });

                if (res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;

                    // Получить имя файла из заголовка
                    const disposition = res.headers.get("content-disposition");
                    let filename = "db_export.xlsx";
                    if (
                        disposition &&
                        disposition.indexOf("filename=") !== -1
                    ) {
                        filename = disposition
                            .split("filename=")[1]
                            .replace(/"/g, "");
                    }

                    a.download = filename;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);

                    showNotification("Download started!", "success");
                    loadDashboardData(); // Перезагрузите обновление звезд, если они были вычтены.
                } else {
                    const err = await res.json();
                    showNotification(
                        err.detail || "Failed to download export",
                        "danger",
                    );
                }
            } catch (e) {
                showNotification("Download failed", "danger");
            }
        });

    // Фильтр поиска по списку отслеживаемых каналов
    document
        .getElementById("search-channels-filter")
        .addEventListener("input", (e) => {
            const filterText = e.target.value.toLowerCase();
            const items = document.querySelectorAll(
                "#channels-list .list-item",
            );
            items.forEach((item) => {
                const username = item
                    .querySelector(".item-title")
                    .innerText.toLowerCase();
                if (username.includes(filterText)) {
                    item.style.display = "flex";
                } else {
                    item.style.display = "none";
                }
            });
        });

    // Запустить поиск AI
    document
        .getElementById("btn-trigger-ai-search")
        .addEventListener("click", async () => {
            const input = document.getElementById("ai-search-query");
            const query = input.value.trim();
            if (!query) return;

            const fd = new FormData();
            fd.append("query", query);

            const btn = document.getElementById("btn-trigger-ai-search");
            const spinner = document.getElementById("search-spinner");

            btn.disabled = true;
            spinner.classList.remove("hidden");

            showNotification(
                "AI Group Finder is running search in Telegram. Please wait...",
                "success",
            );

            try {
                const res = await apiRequest("/api/search/ai", {
                    method: "POST",
                    body: fd,
                });

                if (res.ok) {
                    const data = await res.json();

                    // Отобразить таблицу результатов
                    const resultsCard = document.getElementById(
                        "search-results-card",
                    );
                    const list = document.getElementById("search-results-list");

                    list.innerHTML = "";
                    document.getElementById("results-count").innerText =
                        data.groups.length;

                    if (data.groups.length > 0) {
                        resultsCard.classList.remove("hidden");
                        data.groups.forEach((g) => {
                            const tr = document.createElement("tr");
                            const statusClass =
                                g.availability === "active"
                                    ? "status-active"
                                    : g.availability === "inactive"
                                      ? "status-inactive"
                                      : "status-unknown";

                            tr.innerHTML = `
                            <td><strong>${g.name}</strong></td>
                            <td><a href="${g.link || "#"}" target="_blank">${g.username || "Private"}</a></td>
                            <td>${g.group_type}</td>
                            <td>${g.participants.toLocaleString()}</td>
                            <td><span class="label-status ${statusClass}">${g.availability}</span></td>
                        `;
                            list.appendChild(tr);
                        });
                    } else {
                        resultsCard.classList.add("hidden");
                        showNotification(
                            "No matching active groups found on Telegram.",
                            "warning",
                        );
                    }
                } else {
                    const err = await res.json();
                    showNotification(err.detail || "Search failed.", "danger");
                }
            } catch (e) {
                showNotification("Search failed.", "danger");
            } finally {
                btn.disabled = false;
                spinner.classList.add("hidden");
            }
        });
}

// Перетащите вспомогательные привязки
function setupDragAndDrop() {
    // Каналы TXT Перетаскивание
    const chZone = document.getElementById("channel-drop-zone");
    const chFileInput = document.getElementById("channel-file-input");

    chZone.addEventListener("click", () => chFileInput.click());
    chFileInput.addEventListener("change", (e) =>
        handleChannelFileUpload(e.target.files[0]),
    );

    bindDragEvents(chZone, handleChannelFileUpload);

    // Перетаскивание сеанса учетных записей
    const accZone = document.getElementById("session-drop-zone");
    const accFileInput = document.getElementById("session-file-input");

    accZone.addEventListener("click", () => accFileInput.click());
    accFileInput.addEventListener("change", (e) =>
        handleSessionFileUpload(e.target.files[0]),
    );

    bindDragEvents(accZone, handleSessionFileUpload);
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
        showNotification("Only .txt lists are supported.", "danger");
        return;
    }

    const fd = new FormData();
    fd.append("file", file);

    showNotification("Uploading channel list...", "success");

    try {
        const res = await apiRequest("/api/channels/upload", {
            method: "POST",
            body: fd,
        });
        if (res.ok) {
            const data = await res.json();
            showNotification(
                `Imported: ${data.added} added, ${data.skipped} skipped.`,
                "success",
            );
            loadChannelsList();
        } else {
            showNotification("File upload failed", "danger");
        }
    } catch (e) {
        showNotification("Network error during file upload", "danger");
    }
}

async function handleSessionFileUpload(file) {
    if (!file || !file.name.endsWith(".session")) {
        showNotification(
            "Only Telethon .session files are supported.",
            "danger",
        );
        return;
    }

    const fd = new FormData();
    fd.append("file", file);

    showNotification("Verifying & uploading session file...", "success");

    try {
        const res = await apiRequest("/api/accounts/upload", {
            method: "POST",
            body: fd,
        });
        if (res.ok) {
            const data = await res.json();
            showNotification(
                `Account ${data.phone} connected successfully!`,
                "success",
            );
            loadAccountsList();
            loadDashboardData();
        } else {
            const err = await res.json();
            showNotification(
                err.detail || "Session validation failed",
                "danger",
            );
        }
    } catch (e) {
        showNotification("Network error during session verification", "danger");
    }
}

// Загрузчики данных
async function loadChannelsList() {
    const list = document.getElementById("channels-list");
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading channels...</div>`;

    try {
        const res = await apiRequest("/api/channels");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("channels-count").innerText = data.length;
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = `<div class="empty-state">No tracked channels yet.</div>`;
                return;
            }

            data.forEach((item) => {
                const el = document.createElement("div");
                el.className = "list-item";
                el.innerHTML = `
                    <div class="item-main">
                        <span class="item-title">${item.username}</span>
                        <span class="item-desc">Added on ${item.date_added}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteChannel(${item.id})">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
                list.appendChild(el);
            });
        }
    } catch (e) {
        list.innerHTML = `<div class="empty-state text-danger">Failed to load channels.</div>`;
    }
}

async function deleteChannel(id) {
    if (!confirm("Are you sure you want to stop tracking this channel?"))
        return;
    try {
        const res = await apiRequest(`/api/channels/${id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            showNotification("Channel removed.", "success");
            loadChannelsList();
            loadDashboardData();
        }
    } catch (e) {
        showNotification("Delete failed.", "danger");
    }
}

async function loadKeywordsList() {
    const list = document.getElementById("keywords-list");
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading keywords...</div>`;

    try {
        const res = await apiRequest("/api/keywords");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("keywords-count").innerText = data.length;
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = `<div class="empty-state">No active keywords.</div>`;
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
        list.innerHTML = `<div class="empty-state text-danger">Failed to load keywords.</div>`;
    }
}

async function deleteKeyword(id) {
    try {
        const res = await apiRequest(`/api/keywords/${id}`, {
            method: "DELETE",
        });
        if (res.ok) {
            showNotification("Keyword deleted.", "success");
            loadKeywordsList();
            loadDashboardData();
        }
    } catch (e) {
        showNotification("Delete failed.", "danger");
    }
}

async function loadAccountsList() {
    const list = document.getElementById("accounts-list");
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading sessions...</div>`;

    try {
        const res = await apiRequest("/api/accounts");
        if (res.ok) {
            const data = await res.json();
            document.getElementById("accounts-count").innerText = data.length;
            list.innerHTML = "";

            if (data.length === 0) {
                list.innerHTML = `<div class="empty-state">No accounts connected.</div>`;
                return;
            }

            data.forEach((item) => {
                const el = document.createElement("div");
                el.className = "list-item";
                el.innerHTML = `
                    <div class="item-main">
                        <span class="item-title"><i class="fa-solid fa-phone icon-inline"></i> ${item.phone_number}</span>
                        <span class="item-desc">Connected: ${item.created_at}</span>
                    </div>
                    <button class="delete-btn" onclick="deleteAccount('${item.phone_number}')">
                        <i class="fa-solid fa-unlink"></i>
                    </button>
                `;
                list.appendChild(el);
            });
        }
    } catch (e) {
        list.innerHTML = `<div class="empty-state text-danger">Failed to load accounts.</div>`;
    }
}

async function deleteAccount(phone) {
    if (!confirm("Are you sure you want to disconnect this Telegram account?"))
        return;
    try {
        const res = await apiRequest(`/api/accounts/${phone}`, {
            method: "DELETE",
        });
        if (res.ok) {
            showNotification("Account disconnected.", "success");
            loadAccountsList();
            loadDashboardData();
        }
    } catch (e) {
        showNotification("Disconnect failed.", "danger");
    }
}

// Триггер вариантов оплаты Star
async function buyStars(amount) {
    closeModal("topup");
    showNotification("Generating invoice link...", "success");

    try {
        const res = await apiRequest(
            `/api/payment/stars-topup?amount=${amount}`,
            { method: "POST" },
        );
        if (res.ok) {
            const data = await res.json();
            const link = data.invoice_link;

            // Проверьте, доступен ли TG WebApp SDK и открыт ли он в исходном виде.
            if (tg && tg.openInvoice) {
                tg.openInvoice(link, (status) => {
                    if (status === "paid") {
                        showNotification(
                            `Stars top up success! Added ${amount} stars.`,
                            "success",
                        );
                        setTimeout(loadDashboardData, 1000);
                    } else {
                        showNotification(
                            "Payment cancelled or failed.",
                            "warning",
                        );
                    }
                });
            } else {
                // Обычный резервный браузер, открыть URL-адрес в новом окне
                window.open(link, "_blank");
                showNotification(
                    "Invoice opened in new tab. Please complete payment.",
                    "warning",
                );
            }
        }
    } catch (e) {
        showNotification("Failed to create stars invoice.", "danger");
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
                // Обновить текст предупреждения, добавив информацию об обратном отсчете или балансе
                const hours = Math.floor(data.remaining_seconds / 3600);
                const minutes = Math.floor(
                    (data.remaining_seconds % 3600) / 60,
                );
                warning.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Достигнут 24-часовой лимит экспорта (Следующий бесплатно: ${hours} часов ${minutes} минут). Следующая загрузка будет стоить 5 звезд. (Ваш баланс: ${data.stars_balance}).`;
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
    if (
        !confirm(
            `Вы уверены, что хотите вызвать действие администратора? '${endpoint}'?`,
        )
    )
        return;
    try {
        const res = await apiRequest(`/api/admin/${endpoint}`, {
            method: "POST",
        });
        if (res.ok) {
            showNotification(`Начал фоновую операцию: ${endpoint}`, "success");
            // Показывать панель состояния задачи и прогресс загрузки
            refreshStatusAndTasks();
        } else {
            showNotification("Operation busy or rejected.", "danger");
        }
    } catch (e) {
        showNotification("Admin operation failed.", "danger");
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
                `Started AI classification using method: ${method}`,
                "success",
            );
            refreshStatusAndTasks();
        }
    } catch (e) {
        showNotification("Failed to trigger classification.", "danger");
    }
}

async function downloadAdminFile(endpoint) {
    showNotification("Downloading file...", "success");
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
            showNotification("File download failed", "danger");
        }
    } catch (e) {
        showNotification("Download failed", "danger");
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

    // Выбор стиля
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

document
    .getElementById("notification-close-btn")
    .addEventListener("click", () => {
        document.getElementById("notification-banner").classList.add("hidden");
    });
