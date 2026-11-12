01.01.2026

**Русский язык**

* Версия: 0.0.5
* Дата выхода: 1 января 2026 года
* Рефакторинг кода.
* Добавлен ИИ для 🔎 Поиска групп / каналов с выдачей пользователю.

Протестировать можете по ссылке https://t.me/AutoParseAlertBot

**English version**

* Version: 0.0.5
* Release date: January 1, 2026
* Code refactoring completed.
* Added AI functionality for 🔎 searching Telegram groups/channels and delivering results to users.

You can test it via the link: https://t.me/AutoParseAlertBot

02.01.2026

- Добавлена выдача общей базы групп/каналов пользователю бота.

11.01.2026

**Русский язык**

* Версия: 0.0.6
* Дата выхода: 11 января 2026 года
* Добавлены режимы выдачи базы данных по типам чатов: все группы/каналы, только каналы, только супергруппы, только
  обычные чаты.
* Улучшен нейминг функций в pars_ai.py для лучшей читаемости и поддержки.
* Обновлены языковые строки в locales.py с актуальной датой релиза.
* Добавлена административная панель с функцией актуализации базы данных (обновление ID и типа групп/каналов).
* Реализована возможность пересылки сообщений с ключевыми словами в указанную техническую группу.

**English version**

* Version: 0.0.6
* Release date: January 11, 2026
* Added database export modes by chat type: all groups/channels, channels only, supergroups only, basic groups only.
* Improved function naming in pars_ai.py for better code readability and maintainability.
* Updated locale strings in locales.py with current release date.
* Added admin panel with database update functionality (refreshing group/channel IDs and types).
* Implemented message forwarding feature for keyword-triggered messages to a designated technical group.

You can test the latest features via the link: https://t.me/AutoParseAlertBot

31.01.2026

**Русский язык**

* Версия: 0.0.9
* Дата выхода: 31 января 2026 года

- Добавлена миграция с CSV на XLSX
- Добавлен выбор категории для получения базы данных
- В панели администратора добавлена актуализация базы групп и каналов
- Улучшено логирование проекта

**English version**

* Version: 0.0.9
* Release date: January 31, 2026
* Added migration from CSV to XLSX format.
* Added category selection for database exports.
* Added database actualization feature in admin panel.
* Improved project logging.

04.09.2026

**Русский язык**

* Версия: 0.1.0
* Дата выхода: 4 сентября 2026 года

- Перенос AI поиска групп и каналов в Telegram Web App интерфейс
- Разделение AI поиска на одиночный и массовый поиск по всему пулу подключенных аккаунтов
- Интеграция выгрузки результатов поиска прямо в чат Telegram и веб-панель
- Интеграция баланса Telegram Stars для монетизации и снятия ограничений на экспорт базы данных

**English version**

* Version: 0.1.0
* Release date: September 04, 2026
* Moved AI search for Telegram groups and channels exclusively to the Telegram Web App interface.
* Introduced single and mass AI search modes powered by account session pools.
* Direct Excel export delivered via Web UI and Telegram chat.
* Integrated Telegram Stars payment for database export cooldown bypass.

You can test the latest features via the link: https://t.me/AutoParseAlertBot

12.11.2026

**Русский язык**

* Версия: 0.2.0
* Дата выхода: 12 ноября 2026 года

- **Поддержка закрытых и приватных групп:**
  - Реализован пересыл сообщений из закрытых групп, в которые аккаунт вступил вручную (через tdata / Telegram Desktop).
  - Внедрён режим «Все чаты аккаунта» (`track_all_chats`): моментальное включение прослушивания всех открытых и закрытых чатов аккаунта в 1 клик.
  - Добавлена функция «📥 Импортировать чаты аккаунта» для автоматического сканирования диалогов аккаунта и добавления их в базу с реальными ID и названиями.
  - Поддержка закрытых групп по инвайт-ссылкам (`+hash`, `joinchat/hash`), числовым ID (`-100...`) и точным названиям.
- **Мульти-аккаунты и независимые кампании:**
  - Реализована изоляция потоков мониторинга под разные ниши: например, акк №1 по «диванам» шлёт лиды в тех-группу по мебели, акк №2 по «холодильникам» — в тех-группу по технике.
  - Для каждого аккаунта задаются свои индивидуальные ключевые слова, свои целевые группы и персональная техническая группа.
  - Одновременный параллельный запуск независимых клиентов Telethon для одного пользователя.
- **Отказоустойчивость и фоновые службы:**
  - Планировщик ночной проверки базы данных в 01:00 (`nightly_check`) с управлением тумблером в боте и Web UI.
  - Автоматическое восстановление мониторинга всех активных аккаунтов при старте бота (`restore_all_user_trackings`).
  - Устранена критическая ошибка удаления профиля пользователя при невалидности сессии (теперь сессия безопасно сбрасывается без потери данных и баланса).
  - Защита административных маршрутов Web API с обязательной авторизацией администратора.

**English version**

* Version: 0.2.0
* Release date: November 12, 2026

- **Closed & Private Groups Support:**
  - Implemented message forwarding from private/closed groups joined manually (via tdata / Telegram Desktop).
  - Added «All Account Chats» mode (`track_all_chats`): 1-click toggle to monitor all open and closed groups the account participates in.
  - Added «📥 Import Account Chats» to scan account dialogs via Telethon and register them in the database with IDs and titles.
  - Added support for closed groups via invite links (`+hash`, `joinchat/hash`), numeric IDs (`-100...`), and exact titles.
- **Multi-Accounts & Independent Campaigns:**
  - Independent monitoring streams by niche (e.g. Account 1 for "Sofas" sends leads to Furniture Tech Group; Account 2 for "Refrigerators" sends leads to Appliances Tech Group).
  - Each account can have its own isolated keywords, target groups, and destination technical notification group.
  - Concurrent background execution of multiple Telethon sessions per user.
- **Reliability & System Services:**
  - Nightly database integrity check at 01:00 (`nightly_check`) manageable via Telegram bot and Web UI.
  - Automatic tracking restoration for all active accounts on bot restart (`restore_all_user_trackings`).
  - Fixed critical user profile deletion bug on session failure (session is now cleared safely without losing profile or stars balance).
  - Web API admin routes secured with strict administrator authorization.

You can test the latest features via the link: https://t.me/AutoParseAlertBot