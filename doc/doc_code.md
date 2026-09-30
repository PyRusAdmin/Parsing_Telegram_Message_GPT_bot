# 📚 Документация по коду AutoParseAlertBot

Данный документ содержит полное описание архитектуры проекта, его структуры, каждого модуля, а также списки классов и
функций с их назначением.

---

## 📑 Содержание

1. [📊 Общая архитектура проекта](#-общая-архитектура-проекта)
2. [🚀 Точки входа и конфигурация](#-точки-входа-и-конфигурация)
3. [💾 База данных (`../database`)](#-база-данных-database)
4. [🔑 Менеджер аккаунтов и Парсинг (`../account_manager`)](#-менеджер-аккаунтов-и-парсинг-account_manager)
5. [🤖 Модуль ИИ (`../ai`)](#-модуль-ии-ai)
6. [📱 Обработчики Telegram-бота (`../handlers`)](#-обработчики-telegram-бота-handlers)
    - [Пользовательские обработчики (`../handlers/user`)](#пользовательские-обработчики-handlersuser)
    - [Административные обработчики (`../handlers/admin`)](#административные-обработчики-handlersadmin)
7. [🌐 Веб-сервер и API (`../web`)](#-веб-сервер-и-api-web)
8. [⌨️ Клавиатуры, Состояния и Локализация](#️-клавиатуры-состояния-и-локализация)

---

## 📊 Общая архитектура проекта

Бот построен на базе асинхронного фреймворка **Aiogram 3** для Telegram-бота, клиентской библиотеки **Telethon** для
парсинга каналов через пользовательские сессии, **FastAPI** для Web App и REST API, а также ORM **Peewee** (SQLite) для
хранения данных.

```
[ Telegram User / Web UI ]
       │
       ├──► FastAPI Server (web/server.py) ──► REST API / Web App
       │
       └──► Aiogram 3 Bot (bot.py) ──────────► Telegram Bot Handlers
                                                    │
                                                    ▼
                                          Account Manager (Telethon)
                                                    │
                                                    ▼
                                          Parsing & Keyword Alert
                                                    │
                                                    ▼
                                          Database (SQLite / Peewee)
```

---

## 🚀 Точки входа и конфигурация

### `../main.py`

- **Описание**: Главный скрипт запуска всей системы.
- **Назначение**:
    - Запускает туннелирование **Tuna** (при необходимости) для обеспечения внешнего URL у FastAPI.
    - Параллельно запускает процессы `../bot.py` (Telegram-бот) и `web/server.py` (FastAPI Web API).
    - Управляет завершением процессов при получении сигнала прерывания (`SIGINT`).

### `../bot.py`

- **Описание**: Основной файл инициализации Telegram-бота на Aiogram 3.
- **Функции**:
    - `main()`: Инициализирует базу данных, подготавливает диспетчер, подключает все роутеры handlers (`user` и
      `admin`), устанавливает меню команд и запускает `start_polling()`.

### `../core/config.py`

- **Описание**: Загрузка конфигураций и переменных окружения (`../.env`).
- **Содержит**:
    - Ключи API (`BOT_TOKEN`, `GROQ_API_KEY`, `OPENROUTER_API_KEY` и др.).
    - Идентификаторы администраторов (`ADMIN_USER_ID`).
    - Настройки путей к сессиям и базам данных.

### `../core/constants.py`

- **Описание**: Константы проекта (системные тексты, лимиты, категории).

### `../core/proxy.py`

- **Описание**: Настройка прокси-серверов для Telethon-клиентов.
- **Функции**:
    - `setup_proxy()`: Настраивает соединения через SOCKS5/HTTP прокси.

---

## 💾 База данных (`../database/database.py`)

Модуль работы с SQLite через ORM Peewee. Поддерживает динамическое создание таблиц под ключевые слова и каналы каждого
пользователя.

### Таблицы (Модели):

- `User`: Пользователи бота (ID, язык, баланс звёзд Stars, дата подписки, лимиты).
- `Groups`: Отслеживаемые пользователем группы и каналы.
- `Account`: Сессии Telethon платная/системные.
- `AccountFree`: Бесплатные/общедоступные сессии Telethon.
- `UserAccountsTable`: Привязка аккаунтов пользователей к их Telegram ID.
- `TelegramGroup`: База данных Telegram-каналов и чатов (для поиска по категории и ИИ).
- `Question`: Логи вопросов к Базе Знаний / Поддержке.

### Основные функции `database.py`:

| Функция                                                              | Описание                                                                    |
|:---------------------------------------------------------------------|:----------------------------------------------------------------------------|
| `init_database()`                                                    | Инициализирует таблицы базы данных SQLite.                                  |
| `create_keywords_model(user_id)`                                     | Создает динамическую модель/таблицу ключевых слов для указанного `user_id`. |
| `create_group_model(user_id)`                                        | Создает динамическую модель/таблицу каналов для указанного `user_id`.       |
| `dell_group(user_id, username)`                                      | Удаляет отслеживаемый канал у пользователя.                                 |
| `get_tracked_channels_count(user_id)`                                | Возвращает количество отслеживаемых каналов пользователя.                   |
| `get_user_channel_usernames(user_id)`                                | Возвращает список usernames отслеживаемых каналов пользователя.             |
| `write_account_to_user_table(user_id, session_string, phone_number)` | Привязывает Telethon-сессию к пользователю.                                 |
| `get_user_accounts(user_id)`                                         | Возвращает список сессий пользователя.                                      |
| `write_account_to_db(session_string, phone_number)`                  | Добавляет новую сессию в общую базу аккаунтов.                              |
| `getting_free_account()` / `getting_account()`                       | Получает доступную сессию из базы для парсинга.                             |
| `delete_account_from_db(session_string)`                             | Удаляет невалидную или забаненную сессию.                                   |
| `get_all_data_telegram_groups()`                                     | Получает список всех каналов из общей базы `TelegramGroup`.                 |
| `clean_telegram_id_duplicates()`                                     | Очищает дубликаты каналов по `telegram_id`.                                 |
| `get_groups_without_category()`                                      | Возвращает каналы без присвоенной категории ИИ.                             |
| `migrate_categories_to_lowercase()`                                  | Приводит категории в базе к нижнему регистру.                               |
| `add_question(user_id, question, answer)`                            | Сохраняет вопрос и ответ в историю вопросов.                                |
| `get_all_questions()`                                                | Выгружает все вопросы пользователей (для админа).                           |

---

## 🔑 Менеджер аккаунтов и Парсинг (`../account_manager`)

Модуль отвечает за управление сессиями Telethon, подписку на каналы и реальный парсинг сообщений по ключевым словам.

### `../account_manager/auth.py`

- **`CheckingAccountsValidity`**: Класс валидации аккаунтов.
    - `verify_account(session_name)`: Проверяет работоспособность сессии Telethon.
    - `write_csv(data)`: Записывает результаты проверки сессий в CSV.
    - `read_invalid_sessions()`: Считывает недействительные сессии для удаления.
- `get_account_info(client)`: Возвращает данные профиля Telegram (ID, username, phone).

### `../account_manager/parser.py`

- `filter_messages(message, user_id, user)`: **Ключевая функция парсинга.** Запускает клиент Telethon, подключается к
  каналам пользователя, прослушивает входящие сообщения, проверяет совпадения по ключевым словам и пересылает найденные
  посты в целевую группу/чат пользователя.
- `join_target_group(client, user_id, message)`: Вступает аккаунтом в целевую группу пользователя для отправки алертов.
- `join_required_channels(client, user_id, message, already_subscribed)`: Вступает аккаунтом во все отслеживаемые
  пользователем каналы.
- `process_message(client, message, chat_id, user_id, target_group_id)`: Обрабатывает конкретное полученное сообщение из
  канала, фильтрует по ключевым словам.
- `determine_telegram_chat_type(entity)`: Определяет тип чата (Channel, Supergroup, Chat).
- `get_full_info_group(client, entity)`: Собирает подробную информацию о канале (подписчики, описания, типы).
- `update_group_channels_data_base(data, entity, group)`: Обновляет/сохраняет распарсенные данные группы в таблицу
  `TelegramGroup`.
- `stop_tracking(user_id, message)`: Останавливает парсинг для пользователя и отключает Telethon-клиенты.

### `../account_manager/session.py`

- `find_session_file(user_id, user, message)`: Находит или создает действующую сессию для пользователя.
- `_is_session_valid(session_string)`: Быстрая проверка валидности строки сессии Telethon.

### `../account_manager/subscription.py`

- `subscription_telegram(client, target_username)`: Подписывает клиент Telethon на указанный канал или группу.

### `../account_manager/unsubscribe.py`

- `unsubscribe(client, username_to_search)`: Отписывает клиент от указанного канала.

### `../account_manager/utilit.py`

- `normalize_telegram_link(input_link)`: Приводит ссылки Telegram (t.me/..., @...) к единому формату username.
- `read_json(file_name)`: Вспомогательное чтение JSON файлов.
- `choosing_random_ai_model()`: Выбирает случайную модель LLM для равномерной нагрузки API.

---

## 🤖 Модуль ИИ (`../ai/ai.py`)

Модуль для интеграции с нейросетевыми провайдерами (Groq, G4F, OpenAI, OpenRouter).

- `category_assignment(group_data, client, model)`: Классифицирует Telegram-канал по тематике/категории с помощью ИИ.
- `get_groq_response(user_input)`: Отправляет запрос к Groq API и возвращает сгенерированный ответ.
- `search_groups_in_telegram(client, group_names)`: Парсит или ищет подходящие каналы/группы в Telegram на основе
  поискового запроса пользователя.

---

## 📱 Обработчики Telegram-бота (`../handlers`)

### Пользовательские обработчики (`../handlers/user`)

| Файл                             | Назначение                                 | Основные функции                                                                                                                |
|:---------------------------------|:-------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------|
| `handlers.py`                    | Главное меню и основные команды            | `handle_start_command`, `handle_back_to_main_menu`, `handle_language_selection`, `handle_settings_menu`, `handle_stars_balance` |
| `connect_account.py`             | Подключение Telegram аккаунтов             | `handle_connect_account`, `handle_account_file`, `sanitization_file_name`                                                       |
| `connect_group.py`               | Добавление каналов для отслеживания        | `handle_connect_message_group`, `handle_group_username_submission`                                                              |
| `entering_keyword.py`            | Ввод ключевых слов для парсинга            | `handle_enter_keyword_menu`, `handle_keywords_submission`                                                                       |
| `checking_group_for_keywords.py` | Экспресс-проверка группы на ключевые слова | `checking_group_for_keywords`, `parse_group_for_keywords`                                                                       |
| `stop_tracking.py`               | Остановка отслеживания                     | `handle_stop_tracking`                                                                                                          |
| `delete_group_from_database.py`  | Удаление каналов из списка пользователя    | `delete_group_from_database`, `del_user_in_db`                                                                                  |
| `get_dada.py`                    | Экспорт списков в Excel                    | `get_keywords_list`, `get_tracking_links_list`, `create_excel_file`                                                             |
| `pars_ai.py`                     | ИИ-поиск каналов и выгрузка баз за Stars   | `parse_search_input`, `export_all_groups`, `export_channels`, `process_successful_payment`                                      |
| `post_doc.py`                    | База знаний и поддержка                    | `load_knowledge_base`, `send_instruction`, `handle_instruction_question`                                                        |
| `transfer_rights.py`             | Передача настроек/прав                     | `transfer_settings`                                                                                                             |

### Административные обработчики (`../handlers/admin`)

| Файл                       | Назначение                                 | Основные функции                                   |
|:---------------------------|:-------------------------------------------|:---------------------------------------------------|
| `admin.py`                 | Панель администратора                      | `admin_panel`, `export_questions`                  |
| `checking_accounts.py`     | Проверка валидности всех аккаунтов         | `checking_accounts_handler`                        |
| `checking_group_for_ai.py` | Автоматическая категоризация ИИ            | `checking_group_for_ai_db`, `assign_categories`    |
| `connecting_account.py`    | Массовая загрузка `.session` файлов        | `admin_connecting_account`, `receive_session_file` |
| `language_detection.py`    | Определение языка каналов через Lingua/LLM | `ai_llama`, `batch_update_languages`               |
| `post_log.py`              | Выгрузка системных логов                   | `log`                                              |

---

## 🌐 Веб-сервер и API (`../web/server.py`)

Приложение **FastAPI**, предоставляющее REST API для работы Web App (Telegram Mini App) и административной панели.

### Ключевые эндпоинты:

#### 👤 API Пользователя:

- `GET /api/status` — Текущий статус пользователя, каналов, слов и сессий.
- `POST /api/user/language` — Смена языка интерфейса.
- `POST /api/tracking/start` — Запуск парсинга сообщений (фоновая задача).
- `POST /api/tracking/stop` — Остановка парсинга сообщений.
- `GET /api/keywords` / `POST /api/keywords/add` / `DELETE /api/keywords/{kw_id}` — Управление ключевыми словами.
- `GET /api/channels` / `POST /api/channels/add` / `DELETE /api/channels/{ch_id}` — Управление каналами.
- `POST /api/channels/upload` — Загрузка файла со списком каналов.
- `POST /api/target-group/set` — Настройка целевой группы для алертов.
- `POST /api/accounts/upload` — Загрузка сессии `.session`.
- `POST /api/ai/search` — Поиск каналов через ИИ.
- `GET /api/database/download` — Выгрузка базы каналов в Excel.
- `POST /api/stars/topup` — Создание инвойса оплаты Telegram Stars.

#### 🛡️ API Администратора:

- `GET /api/admin/status` — Общая статистика системы (количество пользователей, каналов, аккаунтов).
- `POST /api/admin/check-accounts` — Запуск проверки валидности сессий.
- `POST /api/admin/actualize-db` — Запуск актуализации данных Telegram-каналов.
- `POST /api/admin/categorize-db` — Запуск ИИ-категоризации каналов.
- `POST /api/admin/detect-language` — Запуск определения языка каналов.
- `GET /api/admin/download-logs` — Скачивание логов сервера.

---

## ⌨️ Клавиатуры, Состояния и Локализация

### `../states/states.py`

Содержит классы состояний **FSM (Finite State Machine)** Aiogram:

- `MyStates`: Шаги пользователя (ввод ключевых слов, каналов, загрузка сессии, вопросы поддержки).
- `MyStatesParsing`: Шаги эксперсс-парсинга по ключевым словам.
- `ExportStates`: Шаги экспорта ИИ-баз каналов.
- `CategoryMethod`: Выбор метода категоризации администратором.

### `../keyboards`

- `../keyboards/user/keyboards.py`: Генерация пользовательских клавиатур (главное меню, настройки, баланс Stars, выбор
  категорий).
- `../keyboards/admin/keyboards.py`: Генерация клавиатур панели администратора.

### `../locales/locales.py`

- `get_l10n(lang)` / `t(key, lang)`: Система локализации (поддержка русского, английского и др. языков).

---
*Документация сгенерирована автоматически для проекта AutoParseAlertBot.*
