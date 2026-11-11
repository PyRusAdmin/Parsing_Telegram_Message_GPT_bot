# Russian localization
welcome_ask_language =
    🌍 Привет! Пожалуйста, выберите язык интерфейса:
welcome_message_template =
    🤖 Добро пожаловать в Telegram-бота для отслеживания 🔍 ключевых слов в группах и каналах, а также AI-поиска сообществ!

    📋 <b>Версия:</b> { $version }
    📅 <b>Дата обновления:</b> 04.09.2026 года
    👨‍💻 <b>Разработчик:</b> <a href="https://t.me/PyAdminRU">@PyAdminRU</a>
    📢 <b>Основной канал:</b> <a href="https://t.me/master_tg_d">@master_tg_d</a>

    📊 <b>Найдено групп / каналов пользователями:</b> { $groups_count }

    🎉 <b>Основные функции бота:</b>
    • 🌐 <b>AI-поиск в Web-панели:</b> подбор и поиск групп/каналов с помощью ИИ теперь доступен в удобной Web-панели
    • 📥 <b>Получить базу:</b> скачайте актуальную базу найденных каналов и групп
    • 📚 <b>Инструкция:</b> подробное руководство по использованию бота
    • ⚙️ <b>Настройки:</b> настройте подключение аккаунтов, ключевые слова и фильтры

    💡 <b>Совет:</b> для получения актуальных обновлений и нового функционала рекомендуется перезапускать бота командой /start

lang_selected =
    ✅ Отлично! Интерфейс теперь будет отображаться на выбранном языке.
settings_message =
    ⚙️ В этом меню вы можете:
    • 🔗 🔐 Подключить аккаунт Telegram
    • 🌐 Изменить язык интерфейса
    • 📢 Добавить группы и каналы для отслеживания
    • 🧩 Настроить ключевые слова и фильтры

    Выберите нужный пункт ниже 👇
connect_account =
    📱 Для подключения аккаунта Telegram отправьте файл сессии в формате:
    `+79599999999.session`

    После загрузки бот начнёт использовать этот аккаунт для отслеживания сообщений.
launching_tracking =
    🚀 Запуск отслеживания сообщений...

    Остановка отслеживания возможна только после подписки на группы / каналы
tracking_launch_error =
    ⚠️ Список каналов пуст.

    Добавьте хотя бы одну группу или канал для отслеживания 🔍
    через меню настроек ⚙️
update_list =
    📥 Пришлите .txt файл со списком групп и каналов для отслеживания:

    ✅ Каждый username должен быть в формате <b>@username</b>
    ✅ Каждая ссылка должна находиться в <b>столбик</b> (на отдельной строке)
    ✅ Файл должен иметь расширение <b>.txt</b>

    📌 Пример содержимого файла:
    @group1
    @channel1
    @my_community

    Формат файла важен — бот корректно обработает только текстовые файлы с правильной структурой.
account_missing =
    ⚠️ У вас нет подключенного аккаунта Telegram.

account_missing_2 =
    ⚠️ Сессия аккаунта недействительна (session файл не валидный) — требуется повторный вход. Отправьте валидный файл сессии
enter_keyword =
    🔍 Введите ключевое слово / словосочетание для отслеживания
ai_search_welcome =
    🤖 <b>Добро пожаловать в меню AI-поиска!</b>

    Здесь вы можете находить новые тематические группы и каналы, используя возможности искусственного интеллекта.

    🚀 <b>Доступные режимы:</b>
    • 🤖 <b>AI поиск:</b> Быстрый поиск групп по вашей базе и ключевым словам.
    • 🌐 <b>Глобальный AI поиск:</b> Расширенный поиск по всему пространству Telegram для нахождения новых площадок.

    Просто выберите нужный режим на клавиатуре или введите запрос! 👇
enter_group =
    🔍 Введите ссылку на группу в формате @username, в которую будет пересылаться сообщение, обнаруженное по ключевому слову
admin_panel_message =
    👋 <b>Добро пожаловать в Панель администратора!</b>

    Вот что вы можете сделать:

    📁 <b>Получить лог-файл</b> — просмотреть журнал ошибок и событий бота за последнее время. Полезно для диагностики.

    🔄 <b>Актуализация базы данных</b> — обновить информацию о группах и каналах: проверить их текущий тип (группа/канал) и получить актуальные ID.

    🏷️ <b>Присвоить категорию</b> — автоматически классифицировать группы и каналы по темам с помощью AI.

    ✅ <b>Проверка аккаунтов</b> — проверить статус подключённых аккаунтов и их сессий.

    🌐 <b>Присвоить язык</b> — определить язык содержимого в группах и каналах.

    🔐 <b>Подключение аккаунта</b> — подключить Telegram-аккаунт через файл сессии для использования в боте.

tracking_stopped =
    ✅ Отслеживание остановлено.

instruction_caption =
    📘 <b>Инструкция по использованию</b>

    Прикреплён подробный руководство по функционалу бота.

    🔗 <b>Онлайн-документация:</b>
    • <a href="{ $gitverse_link }">GitVerse</a>
    • <a href="{ $github_link }">GitHub</a>

    Рекомендуем ознакомиться для эффективного использования всех возможностей бота.

instruction_file_not_found =
    ⚠️ Файл инструкции не найден на сервере.

instruction_send_error =
    ❌ Произошла ошибка при отправке файла.

# === Экспорт базы данных ===
database_empty =
    📭 База данных пуста.

export_all_caption =
    📦 Вся база данных Telegram-групп и каналов.

    📊 Всего записей: { $total_records }
    🧹 Дубликатов удалено перед экспортом: { $deleted_duplicates }

export_channels_caption =
    📦 База данных Telegram-каналов.

    📊 Всего записей: { $total_records }

export_groups_caption =
    📦 База данных Telegram-групп.

    📊 Всего записей: { $total_records }

export_error_generic =
    ❌ Произошла ошибка при создании файла.

get_database_menu =
    👋 Добро пожаловать в режим получения базы данных!

    Вот что вы можете сделать:

    🔹 <b>📥 Получить всю базу</b> — получите полный список всех сохранённых групп и каналов в формате Excel.
    🔹 <b>Получить базу Каналов</b> — получите список всех сохранённых каналов в формате Excel.
    🔹 <b>Получить базу Групп (супергрупп)</b> — получите список всех сохранённых супергрупп в формате Excel.
    🔹 <b>Получить базу Обычных чатов (группы старого типа)</b> — получите список всех сохранённых обычных чатов (групп старого типа) в формате Excel.
    🔹 Выбрать категорию для получения базы

    🔸 Нажмите <b>Назад</b>, чтобы вернуться в главное меню.

select_category_prompt =
    📌 Выберите категорию, по которой хотите получить список групп/каналов:

action_cancelled =
    ❌ Отменено.

invalid_category =
    ⚠️ Неверная категория. Пожалуйста, выберите из списка.

category_empty =
    📭 В категории «{ $category }» пока нет ни одной группы.

category_export_caption =
    ✅ Экспортировано { $group_count } групп/каналов по категории:
    «{ $category }»

# === AI Поиск ===
searching_groups =
    🔍 Ищу группы и каналы...

search_summary =
    ✅ <b>Поиск завершён!</b>

    📊 Найдено и сохранено: <b>{ $groups_count }</b> групп/каналов
    📁 Результаты отправлены в Excel-файле

    📍 <b>Обозначение активности:</b>
    🟢 <b>active</b> — группа активна (последнее сообщение ≤ 30 дней)
    🔴 <b>inactive</b> — группа неактивна (сообщений > 30 дней или нет вообще)
    ⚪ <b>unknown</b> — не удалось определить (ограничения Telegram)

search_results_caption =
    📄 Результаты поиска по запросу: <b>{ $query }</b>

search_no_results =
    ❌ К сожалению, по вашему запросу ничего не найдено. Попробуйте другие ключевые слова.

search_error =
    ❌ Произошла ошибка при поиске. Попробуйте ещё раз.

# === Глобальный AI поиск ===
global_search_no_terms =
    ❌ Введите хотя бы один поисковый запрос.

global_search_processing =
    🔍 Обрабатываю { $total } запросов...

global_search_skipped =
    ⚠️ Пропущено: '{ $term }' (нет доступных аккаунтов)

global_search_progress =
    🔍 Обработано { $current }/{ $total }: { $successful } успешно

global_search_results_caption =
    📄 Найдено { $total } групп по { $successful }/{ $total_queries } запросам

global_search_no_results =
    ❌ К сожалению, ничего не найдено. Попробуйте другие ключевые слова.

# === Подключение группы ===
group_added =
    ✅ Группа { $group } добавлена для отправки сообщений.

group_already_added =
    ⚠️ Эта группа уже добавлена.

group_add_error =
    ⚠️ Ошибка при добавлении группы.

# === Удаление группы ===
delete_group_prompt =
    Введите username группы / канала в формате @username для удаления из отслеживания:

group_deleted =
    ✅ Группа { $group } успешно удалена из отслеживания.

group_not_found =
    ❌ Группа @{ $group } не найдена в вашем списке отслеживаемых.

no_accounts =
    ❌ У вас нет подключённых аккаунтов.

    Отправьте файл сессии `.session` или нажмите «Подключение аккаунта» в меню.

# === Ключевые слова ===
no_keywords_entered =
    ⚠️ Вы не указали ни одного ключевого слова.

keywords_added_count =
    Добавлено ключевых слов: { $count }

keywords_already_added =
    Уже были добавлены ({ $count })

keywords_add_errors =
    Ошибки при добавлении

keywords_and_more =
    и ещё { $count }

keywords_and_more_errors =
    и ещё { $count } ошибок

keywords_summary =
    Итого

keywords_added =
    Добавлено

keywords_skipped =
    Пропущено (дубликаты)

keywords_errors =
    Ошибки

# === Проверка группы для关键词 ===
check_group_ask_url =
    📤 Введите ссылку на группу для проверки:

check_group_ask_keyword =
    🔍 Введите ключевое слово для поиска:

check_group_started =
    🔍 Начинаю проверку группы...

check_group_new_message_with_link =
    📨 Новое сообщение с ключевым словом!

    📌 <b>{ $title }</b>
    📅 Дата: { $msg_date }
    🔗 <a href="{ $message_link }">Перейти к сообщению</a>

check_group_new_message_no_link =
    📨 Новое сообщение с ключевым словом!

    📌 <b>{ $title }</b>
    📅 Дата: { $msg_date }

check_group_summary =
    ✅ Проверка завершена!

    Найдено сообщений: { $count }
    Ключевое слово: { $keyword }
    Совпадений: { $matched_count }

check_group_parse_error =
    ❌ Произошла ошибка при парсинге группы. Проверьте ссылку и доступ к чату.

# === Parser ===
target_group_not_found =
    ❌ Не найдена целевая группа для пользователя. Подключите группу, для того, что бы я мог пересылать туда сообщения, найденные по вашим ключевым словам.

no_channels_to_track =
    📭 У вас нет добавленных каналов для отслеживания.

too_many_channels =
    ⚠️ Найдено { $total } каналов. Подписка будет выполнена только на первые { $limit }.

channel_subscribed =
    ✅ Подписка на { $channel } выполнена
    ⏳ Следующая попытка через { $delay } сек.

target_group_join_error =
    ❌ Аккаунту не удалось присоединиться к целевой группе, проверьте подключенную группу

target_group_not_configured =
    ❌ Не найдена целевая группа для пользователя. Подключите группу.

target_group_fetch_error =
    ❌ Не удалось получить целевую группу. Проверьте подключение.

bot_listening =
    👂 Бот слушает новые сообщения...

tracking_not_active =
    ⚠️ Отслеживание не запущено или уже остановлено.

tracking_stop_requested =
    🛑 Команда остановки отправлена. Отслеживание будет остановлено в течение нескольких секунд.

search_client_error =
    ❌ Ошибка при подключении к аккаунту. Попробуйте позже.

search_no_available_accounts =
    ⚠️ Нет доступных аккаунтов для поиска.

# === Сессия ===
session_invalid =
    ⚠️ Аккаунт `{ $phone }` больше не действителен.
    Пожалуйста, подключите аккаунт заново.

account_fetch_error =
    ⚠️ Произошла ошибка при получении аккаунта. Попробуйте позже.

# === Проверка аккаунтов ===
checking_accounts_start =
    Аккаунтов для проверки: { $count }
checking_accounts_complete =
    ✅ Проверка аккаунтов завершена

# === Проверка группы для AI ===
ai_category_select_method =
    🤖 <b>Выберите метод присвоения категорий:</b>

    ⚡️ <b>Быстро (g4f.free)</b>
    • Бесплатно, без API ключей
    • Последовательная обработка (медленнее)
    • Подходит для небольших объёмов
    • Может возвращать неточные результаты

    🚀 <b>Мощно (Groq API)</b>
    • Требует API ключ Groq
    • Параллельная обработка в 10 потоков (быстрее)
    • Подходит для больших объёмов
    • Более точные результаты

    Выберите метод:
ai_category_back =
    ↩️ Возврат в панель администратора
ai_category_checking_models =
    🔍 Проверка доступных моделей...
ai_category_model_selected =
    ✅ Выбрана модель: { $model }
ai_category_select_from_keyboard =
    Пожалуйста, выберите метод из клавиатуры ниже:
ai_category_all_have_categories =
    ✅ Все группы уже имеют категории!
ai_category_processing =
    🔄 Обрабатываю { $total } групп...
ai_category_done =
    ✅ <b>Готово!</b>
ai_category_error =
    ❌ Ошибка: { $error }
ai_category_stats_title =
    📊 <b>Статистика категорий:</b>
ai_category_no_category_count =
    🗃️ Групп без категории: { $count }
ai_category_run_ai =
    Нажмите '🏷️ Присвоить категорию' для запуска AI

# === Подключение аккаунта ===
connect_account_ask_session =
    📤 Отправьте мне файл(ы) сессии Telethon (должны заканчиваться на `.session`)

    Можно отправить сразу несколько файлов — бот обработает их по очереди.
    Когда закончите — нажмите кнопку «Назад» или отправьте /start
connect_account_invalid_file =
    ❌ Это не файл сессии! Отправьте файл с расширением `.session`
connect_account_limit_reached =
    ⚠️ Достигнут лимит: { $max } файлов за раз.
    Обработайте текущие и отправьте остальные позже.
connect_account_file_queued =
    📥 Файл принят: `{ $filename }`
    📊 В очереди: { $total } файл(ов). Обрабатываю...
connect_account_success =
    ✅ <b>{ $filename }</b> — успешно!
    📱 { $phone } | 👤 { $name }
connect_account_failed =
    ❌ <b>{ $filename }</b> — не прошёл проверку
connect_account_error =
    ⚠️ <b>{ $filename }</b> — ошибка обработки
connect_account_processing_done =
    📊 <b>Обработка завершена!</b>

# === Определение языка ===
lang_detect_no_groups =
    ❌ Нет групп для обработки
lang_detect_starting =
    🚀 Запуск обработки { $total } групп...
lang_detect_error =
    ❌ Ошибка: { $error }
lang_detect_saving =
    💾 Сохранение { $count } результатов в БД...
lang_detect_complete =
    ✅ Обработка завершена!

    📊 Статистика:
    • Всего: { $total }
    • AI определил: { $ai_success }
    • Сохранено в БД: { $db_success }
    • Ошибок AI: { $ai_fail }
    • Ошибок БД: { $db_fail }
    • Всего ошибок: { $total_fail }

lang_detect_stats_title = Статистика
lang_detect_stats_total = Всего
lang_detect_stats_ai_success = AI определил
lang_detect_stats_db_success = Сохранено в БД
lang_detect_stats_ai_fail = Ошибок AI
lang_detect_stats_db_fail = Ошибок БД
lang_detect_stats_total_fail = Всего ошибок

# === Лог файл ===
log_file_caption =
    📄 Лог файл с ошибками.

# === connect_account.py ===
account_connect_personal =
    🔐 <b>Управление Telegram-аккаунтом</b>

    📱 <b>Текущий аккаунт:</b> ✅ <i>Личный аккаунт</i>
    📊 <b>Режим:</b> Без ограничений на количество каналов (в рамках ваших слотов)

    Вы можете переподключить аккаунт другим способом или отключить его.

account_connect_shared =
    🔐 <b>Управление Telegram-аккаунтом</b>

    🎁 <b>Текущий аккаунт:</b> <i>Бесплатный аккаунт от администратора</i>
    ⚠️ <b>Ограничение:</b> Отслеживание сигналов разрешено только в <b>1 группе</b>.

    💡 <i>Для отслеживания в нескольких группах одновременно подключите свой личный аккаунт.</i>

account_connect_none =
    🔐 <b>Управление Telegram-аккаунтом</b>

    ⚠️ <b>Текущий аккаунт:</b> <i>Не подключен</i>

    Для мониторинга сообщений и сигналов по ключевым словам выберите способ подключения:
    • <b>Личный аккаунт</b> — без ограничений по количеству каналов.
    • <b>Свободный аккаунт от админа</b> — бесплатный доступ, отслеживание ограничено 1 группой.

account_connected_free =
    ✅ Аккаунт успешно подключен

no_free_accounts =
    ❌ Нет доступных свободных аккаунтов. Пожалуйста, попробуйте позже или обратитесь к администратору.

no_free_accounts_detailed =
    ⚠️ <b>Нет свободных аккаунтов от администратора</b>

    В данный момент в пуле нет доступных свободных аккаунтов.
    Пожалуйста, подключите свой личный аккаунт (по телефону или через сессию).

invalid_session_file =
    ❌ Это не файл сессии! Отправьте файл с расширением `.session`

session_file_received =
    📥 Файл получен: `{ $filename }`

    🔍 Проверяю аккаунт...

session_connected_success =
    ✅ <b>{ $filename }</b> — успешно!
    📱 { $phone } | 👤 { $name }
    💾 Сохранено в вашу персональную базу.

session_validation_failed =
    ❌ <b>{ $filename }</b> — не прошёл проверку.
    Проверьте, что файл сессии актуален и не используется в другом месте.

session_check_error =
    ⚠️ Произошла ошибка при проверке аккаунта. Попробуйте позже.

# === handlers.py (группы) ===
only_txt_files_supported =
    ⚠️ Поддерживаются только .txt файлы.

empty_file_no_usernames =
    ⚠️ Файл пуст или не содержит username-ов.

groups_upload_summary =
    ✅ Добавлено: { $added }
    ⚠️ Уже есть: { $skipped }
    ❌ Ошибок: { $errors }

# === admin.py ===
admin_found_accounts =
    🔍 Найдено аккаунтов: { $count }

admin_db_actualization_start =
    🔄 Начинаю актуализацию { $total } групп...

admin_using_account =
    📱 Используется аккаунт: { $account }

admin_account_error =
    ❌ Ошибка аккаунта { $account }: { $error }

admin_critical_error =
    ❌ Критическая ошибка: { $error }

# === Экспорт вопросов ===
no_questions_in_db =
    📭 В базе данных нет вопросов.

questions_export_caption =
    📦 Экспорт вопросов и ответов.

export_error =
    ❌ Произошла ошибка при экспорте: { $error }

# === Кнопки ===
launch_tracking_button = 🚀 Запуск отслеживания
check_group_for_keywords_button = 🔍 Проверка группы на наличие ключевых слов
ai_search_button = ✨ Поиск через AI
get_database_button = 📥 Получить базу
instruction_button = 📖 Инструкция по использованию
settings_button = ⚙️ Настройки
admin_panel_button = 🛡️ Панель администратора
get_log_file_button = 📄 Получить лог файл
export_questions_button = Выгрузить вопросы
assign_category_button = 🏷️ Присвоить категорию
check_accounts_button = ✅ Проверка аккаунтов
connect_account_button = 🔐 Подключение аккаунта
back_button = ⬅️ Назад
fast_method_button = ⚡️ Быстро (g4f.free)
powerful_method_openrouter_button = 🚀 Мощно (Openrouter API)
powerful_method_groq_button = 🚀 Мощно (GROQ API)
all_database_button = 📥 Вся база
channels_database_button = 📥 База каналов
groups_database_button = 📥 База групп
select_category_button = 📂 Выбрать категорию
investments_button = инвестиции
finance_and_personal_budget_button = финансы и личный бюджет
crypto_and_blockchain_button = криптовалюты и блокчейн
business_and_entrepreneurship_button = бизнес и предпринимательство
marketing_and_promotion_button = маркетинг и продвижение
tech_and_it_button = технологии и it
education_and_self_development_button = образование и саморазвитие
work_and_career_button = работа и карьера
real_estate_button = недвижимость
health_and_medicine_button = здоровье и медицина
travel_button = путешествия
auto_and_transport_button = авто и транспорт
shopping_and_discounts_button = шоппинг и скидки
entertainment_and_leisure_button = развлечения и досуг
politics_and_society_button = политика и общество
science_and_research_button = наука и исследования
sports_and_fitness_button = спорт и фитнес
cooking_and_food_button = кулинария и еда
fashion_and_beauty_button = мода и красота
hobbies_and_creativity_button = хобби и творчество
russian_language_button = 🇷🇺 Русский
english_language_button = 🇬🇧 English
stop_tracking_button = 🛑 Остановить отслеживание
update_list_button = 🔁 Обновить список
enter_keyword_button = 🔍 Ввод ключевого слова
delete_group_from_tracking_button = 🗑️ Удалить группу из отслеживания
keywords_list_button = 🔍 Список ключевых слов
tracking_links_button = 🌐 Ссылки для отслеживания
connect_group_for_messages_button = 📤 Подключить группу для сообщений
change_language_button = 🌐 Сменить язык
connect_free_account_button = 🔐 Подключить свободный аккаунт

# post_doc.py
instruction_question_prompt = 🤖 <b>Вы можете задать мне любой вопрос по использованию бота, и я отвечу вам!</b>
ai_support_assistant_system_prompt = Вы — квалифицированный помощник службы поддержки Telegram-бота AutoParseAlertBot. Ваша задача — отвечать на вопросы пользователей, основываясь СТРОГО на предоставленной базе знаний. Если ответа нет в базе знаний, вежливо сообщите, что вы не обладаете данной информацией и посоветуйте обратиться в поддержку. Отвечайте на языке пользователя простым читаемым текстом БЕЗ использования символов разметки (не используйте Markdown символы ###, **, *, `, _ и HTML-теги).

excel_filename_telegram_groups = telegram_groups_{ $timestamp }.xlsx
excel_header_group_link = Ссылка
excel_header_group_participants = Участники
excel_header_group_type = Тип
excel_header_group_description = Описание
excel_header_group_name = Название
excel_filename_groups_by_category = groups_{ $category }.xlsx
excel_sheet_name_groups = Группы
excel_header_date_added = Дата добавления
excel_header_link = Ссылка
excel_header_activity = Активность
excel_header_language = Язык
excel_header_type = Тип
excel_header_category = Категория
excel_header_participants = Участников
excel_header_description = Описание
excel_header_name = Название
excel_header_id = ID (Hash)
excel_sheet_name_search_results = Результаты поиска
excel_filename_groups_db = База_групп.xlsx
excel_filename_channels_db = База_каналов.xlsx
excel_filename_all_db = Вся_база.xlsx
ai_search_button_user = 🤖 AI поиск
excel_header_username = Username канала/группы / Channel/Group Username
excel_header_keyword = Ключевое слово / Keyword
excel_header_number = №
no_tracking_links_found = 📭 У вас нет ссылок для отслеживания.
tracking_links_export_caption = 🔗 Экспорт ссылок для отслеживания. Всего записей: { $count }
no_keywords_found = 📭 У вас нет сохраненных ключевых слов.
keywords_export_caption = 📋 Экспорт ключевых слов. Всего записей: { $count }


# language_detection.py
lang_detect_summary = ✅ Обработка завершена!

    📊 Статистика:
    • Всего: { $total }
    • AI определил: { $ai_success }
    • Сохранено в БД: { $db_success }
    • Ошибок AI: { $ai_fail }
    • Ошибок БД: { $db_fail }
    • Всего ошибок: { $total_fail }
name_prompt = Название
description_prompt = Описание
no_data_prompt = Нет данных
ai_lang_detect_prompt =
    Определи основной язык текста или описания сообщества.
    Ответь СТРОГО одним словом — кодом языка в формате ISO 639-1 (двухбуквенный код).
    Примеры корректных ответов: ru, en, es, zh, ar, hi, ja, ko, fr, de, pt, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn.
    Если язык невозможно определить однозначно или текст содержит смесь языков без доминирующего — ответь: unknown.
    НЕ добавляй никаких пояснений, пунктуации, пробелов или дополнительного текста. Только код языка или 'unknown'.
    
    Текст для анализа:
    { $user_input }

# checking_group_for_ai.py
get_groups_without_category_message = 📊 <b>Статистика категорий:</b>

    🗃️ Групп без категории: { $count }

    Нажмите '🏷️ Присвоить категорию' для запуска AI


# === Лимиты скачивания и Звезды ===
download_free_success = 📥 Выгрузка базы (1 раз в сутки бесплатно). Начинаем скачивание...
download_cooldown_message =
    ⚠️ Вы уже скачивали базу за последние 24 часа.
    Следующее бесплатное скачивание будет доступно через <b>{ $time }</b>.
    
    Вы можете скачать базу прямо сейчас за 5 ⭐.
    Ваш баланс звезд в боте: <b>{ $stars }</b> ⭐
pay_from_balance_btn = 🪙 Списать 5 ⭐ с баланса
pay_direct_btn = ⭐ Оплатить 5 ⭐ напрямую
cancel_btn = ❌ Отмена
download_paid_success = ✅ Оплата/списание 5 ⭐ успешно произведено. Начинаем скачивание базы...
download_insufficient_stars = ❌ Недостаточно звезд на балансе.
stars_topup_success = 🎉 Баланс успешно пополнен на { $amount } ⭐! Ваш текущий баланс: { $balance } ⭐.
stars_added_admin = ⭐ Администратор начислил вам { $amount } ⭐. Текущий баланс: { $balance } ⭐.
topup_stars_button = 💳 Пополнение звезд
stars_balance_msg = 👤 <b>Ваш профиль звезд:</b>\n\nБаланс: <b>{ $stars }</b> ⭐\n\nЗдесь вы можете пополнить баланс Telegram Stars для платных скачиваний базы данных.
stars_invoice_title = Пополнение баланса звезд
stars_invoice_desc = Покупка { $amount } Telegram Stars для использования в боте
stars_invoice_dl_title = Скачивание базы данных
stars_invoice_dl_desc = Однократное скачивание базы данных в обход суточного лимита
excel_filename_category_db = category_database.xlsx
export_category_caption = 📂 База по категории "{ $category }". Всего записей: { $total_records }.
generating_database_wait = ⏳ Формируем файл базы данных, это может занять некоторое время. Пожалуйста, подождите...

# === Новые ключи локализации ===
# Клавиатуры и навигация
btn_add_channels_tracking = ➕ Добавить каналы (текстом или .txt)
btn_channels_list = 📋 Список каналов
btn_export_excel = 📥 Экспорт в Excel
btn_clear_all_channels = 🧹 Очистить весь список
btn_tracking_channels = 🌐 Каналы отслеживания
btn_keywords = 🔍 Ключевые слова
btn_notification_group = 📢 Группа уведомлений
btn_transfer_settings = 🔄 Передать настройки пользователю
btn_personal_tracking = 🎯 Отслеживание
btn_connect_account_session = 📄 Подключить аккаунт через сессию (.session)
btn_connect_account_phone = 📱 Подключить личный аккаунт (по телефону)
btn_connect_free_account = 🎁 Бесплатный аккаунт от админа (1 группа)
btn_disconnect_account = ❌ Отключить текущий аккаунт
btn_to_tracking_menu = 🎯 В меню отслеживания
btn_to_settings_menu = ⚙️ В настройки
btn_add_keywords = ➕ Добавить ключевые слова
btn_keywords_list = 📋 Список ключевых слов
btn_export_keywords = 📥 Экспорт ключевых слов
btn_goto_notification_group = 🔗 Перейти в группу уведомлений
btn_notification_group_not_created = 🔗 Группа ещё не создана
btn_recreate_notification_group = 🔄 Пересоздать группу
btn_nav_prev = ◀️ Назад
btn_nav_next = Вперёд ▶️
btn_confirm_clear = ✅ Да, очистить
btn_cancel = ❌ Отмена
btn_broadcast_users = 📢 Рассылка пользователям
btn_broadcast_send = 🚀 Запустить рассылку
btn_broadcast_cancel = ❌ Отменить рассылку
btn_pt_add_tracking = ➕ Добавить отслеживание группы
btn_pt_buy_slot = ⭐ Докупить +1 слот (2 Stars)
btn_pt_my_groups = 📋 Мои отслеживаемые группы
btn_pt_stats = 📊 Статистика
btn_keypad_clear = ❌ Стереть
btn_keypad_submit = ✅ Отправить
btn_keypad_cancel = 🚫 Отмена
btn_pt_edit_record = ⚙️ Изменить #{ $idx } ({ $title })
btn_pt_buy_stars_slots = ⭐ Докупить слоты (Telegram Stars)
btn_pt_connect_personal = 📱 Подключить личный аккаунт
btn_pt_create_notification_group = 📢 Создать группу уведомлений

# Настройки (settings.py)
settings_channels_title = 🌐 <b>Каналы отслеживания</b>\n\n📊 Всего каналов: <b>{ $total }</b>\n\nВыберите действие:
settings_channels_empty = 📭 Список каналов пуст.
settings_channels_list_title = 📋 <b>Список каналов</b> (стр. { $page }/{ $total_pages }) · всего: { $total }\n
settings_channels_list_hint = \n<i>Нажмите ❌ на канале, чтобы удалить его.</i>
settings_channel_deleted = ✅ Канал удалён: { $channel }
settings_channel_not_found = ⚠️ Канал не найден.
settings_channels_clear_confirm = 🧹 <b>Очистить весь список каналов?</b>\n\nБудет удалено <b>{ $total }</b> канал(ов). Это действие нельзя отменить.
settings_channels_cleared = ✅ <b>Список каналов очищен.</b>\n\nУдалено каналов: <b>{ $count }</b>
settings_keywords_title = 🔍 <b>Ключевые слова</b>\n\n📊 Всего слов: <b>{ $total }</b>\n\nВыберите действие:
settings_keywords_empty = 📭 Список ключевых слов пуст.
settings_keywords_list_title = 🔍 <b>Ключевые слова</b> (стр. { $page }/{ $total_pages }) · всего: { $total }\n
settings_keywords_list_hint = \n<i>Нажмите ❌ на слове, чтобы удалить его.</i>
settings_keyword_deleted = ✅ Удалено: { $keyword }
settings_keyword_not_found = ⚠️ Слово не найдено.
settings_notification_created = 📢 <b>Группа уведомлений</b>\n\n✅ Группа создана.\n🔗 <a href='{ $link }'>Перейти в группу</a>
settings_notification_not_created = 📢 <b>Группа уведомлений</b>\n\n❌ Группа ещё не создана.\n\n<i>Создайте группу через раздел «🎯 Персональное отслеживание».</i>
settings_notification_alert_no_group = ❌ Группа не создана. Перейдите в «🎯 Персональное отслеживание» для её создания.
settings_notification_recreate_text = 🔄 <b>Пересоздать группу уведомлений</b>\n\nДля пересоздания группы перейдите в раздел «🎯 Персональное отслеживание» → «➕ Добавить отслеживание группы».\n\n<i>Новая группа будет создана автоматически при добавлении нового отслеживания.</i>

# Добавление каналов (connect_group.py)
connect_group_prompt = 🔗 <b>Отправьте ссылку или username группы/канала для отслеживания</b>\n\nНапример:\n<code>https://t.me/python_jobs</code>\nили <code>@python_jobs</code>\n\nМожно отправить несколько ссылок, каждую с новой строки.
connect_group_no_links = ⚠️ Отправьте хотя бы одну ссылку или username.
connect_group_invalid_links = ⚠️ Проверьте правильность ссылок.
connect_group_saved = ✅ Группа / группы записаны в базу данных.
connect_group_text_required = ⚠️ Отправьте ссылку или username группы/канала текстовым сообщением.
connect_group_file_invalid_links = ⚠️ Проверьте правильность ссылок в файле.
connect_group_file_required = ⚠️ Отправьте TXT-файл со ссылками или username групп и каналов.

# Передача прав (transfer_rights.py)
transfer_rights_prompt = 🔄 <b>Передача настроек другому пользователю</b>\n\nОтправьте Telegram ID пользователя, которому хотите скопировать свои каналы и ключевые слова.\n\n<i>Пример: <code>1234567890</code></i>
transfer_rights_invalid_id = ⚠️ Некорректный ID. ID должен содержать только цифры.\n\nПопробуйте снова через меню настроек.
transfer_rights_self = ⚠️ Нельзя передать настройки самому себе.
transfer_rights_not_found = ⚠️ Пользователь с ID <code>{ $target_user_id }</code> ещё не запускал этого бота.
transfer_rights_success = ✅ <b>Настройки успешно переданы пользователю { $target_user_id }!</b>\n\n📋 Добавлено каналов: <b>{ $groups }</b>\n🔑 Добавлено ключевых слов: <b>{ $keywords }</b>

# Удаление и ввод ключевых слов
delete_group_invalid_format = ⚠️ <b>Не удалось распознать ссылку.</b>\n\nДопустимые форматы:\n• <code>@channel_name</code>\n• <code>https://t.me/channel_name</code>\n• <code>https://t.me/+PrivateHash</code>\n• <code>https://t.me/joinchat/Hash</code>
keywords_added_success = ✅ Ключевые слова добавлены.\n\n📊 Всего ключевых слов: <b>{ $count }</b>

# Персональное отслеживание (personal_tracking.py)
pt_no_slots_alert = ⚠️ Все слоты задействованы! Докупите дополнительный слот.
pt_ask_link = 🔗 <b>Введите ссылку на целевую группу или канал</b>\n\n<i>Например: <code>https://t.me/python_jobs</code> или <code>@python_jobs</code></i>
pt_invalid_link = ⚠️ Пожалуйста, введите корректную ссылку (https://t.me/...) или @username группы/канала.
pt_checking_group = 🔄 <i>Проверяем группу и получаем информацию...</i>
pt_ask_keywords = 🔑 Введите ключевые слова для отслеживания через запятую:
pt_saved_success = ✅ <b>Настройки отслеживания сохранены!</b>
pt_step2_created =
    ✅ <b>Группа создана!</b>

    1. Перейдите по ссылке и вступите в созданную группу: <a href='{ $link }'>{ $link }</a>
    <i>(Бот { $bot_name } уже назначен администратором группы)</i>

    <b>Шаг 2:</b> Введите ключевые слова для отслеживания в этой группе (через запятую):
    <i>Пример: python, вакансия, удаленка</i>
pt_configured_success =
    🎉 <b>Персональное отслеживание успешно настроено!</b>

    📌 <b>Отслеживаемый объект:</b> { $target }
    🔑 <b>Ключевые слова:</b> { $keywords }
    🔗 <b>Группа для результатов:</b> <a href='{ $link }'>Перейти в группу</a>

    <i>Уведомления о найденных совпадениях будут приходить прямо в Вашу созданную группу!</i>
pt_alert_message =
    🎯 <b>Найдено ключевое слово:</b> <code>{ $keyword }</code>

    💬 <b>Текст сообщения:</b>
    { $text }

    🔗 <a href='{ $link }'>Перейти к сообщению</a>
pt_no_active_trackings = ℹ️ У Вас пока нет активных персональных отслеживаний.
pt_record_not_found = Ошибка: Запись не найдена
pt_edit_prompt = ⚙️ <b>Редактирование отслеживания</b>\n\n🔗 Текущая ссылка: { $link }\n🔑 Ключевые слова: { $keywords }\n\nОтправьте новую ссылку на группу/канал:
pt_updating_group = 🔄 <i>Обновляем подписку и группу...</i>
pt_updated_success = ✅ <b>Настройки отслеживания успешно обновлены!</b>
pt_stats_msg = 📊 <b>Статистика персональных отслеживаний</b>\n\n👥 Всего пользователей: <b>{ $users }</b>\n🎯 Всего отслеживаний: <b>{ $trackings }</b>
pt_code_prompt = 🔢 Введите 5-значный код подтверждения:
pt_invalid_code_alert = ❌ Неверный код подтверждения! Попробуйте еще раз.
pt_code_expired_alert = ❌ Срок действия кода истек! Запросите код заново.
pt_login_error_alert = ❌ Ошибка входа: { $error }
pt_checking_2fa = 🔄 <i>Проверяем 2FA пароль...</i>
pt_auth_success =
    🎉 <b>Аккаунт успешно авторизован и подключен!</b>

    👤 <b>Имя:</b> { $name }
    📱 <b>Телефон:</b> +{ $phone }
    🆔 <b>Telegram ID:</b> <code>{ $tg_id }</code>

    ✅ Сессия сохранена в базе и готова к отслеживанию.
pt_auth_2fa_success =
    🎉 <b>Аккаунт успешно авторизован с 2FA паролем!</b>

    👤 <b>Имя:</b> { $name }
    📱 <b>Телефон:</b> +{ $phone }
    🆔 <b>Telegram ID:</b> <code>{ $tg_id }</code>

    ✅ Сессия успешно сохранена в базе данных.
pt_auth_code_invalid_screen =
    📩 <b>Код подтверждения отправлен в Ваш Telegram!</b>

    📱 <b>Номер:</b> <code>{ $phone }</code>
    🔢 <b>Введенный код:</b> <code>_ _ _ _ _</code>

    ❌ <b>Ошибка: Неверный код. Попробуйте выбрать цифры заново:</b>
pt_auth_2fa_prompt =
    🔐 <b>На Вашем аккаунте включена двухэтапная аутентификация (2FA)!</b>

    Пожалуйста, введите Ваш облачный пароль текстом в ответном сообщении:
pt_auth_2fa_invalid =
    ❌ <b>Неверный 2FA пароль!</b>

    Пожалуйста, введите корректный облачный пароль текстом:
pt_auth_error = ❌ Ошибка авторизации: { $error }
pt_auth_cancelled = 🚫 Авторизация отменена.
pt_phone_prompt = 📱 <b>Подключение Telegram-аккаунта</b>\n\nВведите ваш номер телефона в международном формате (например, <code>+79991234567</code>):
pt_phone_invalid = ❌ Введен недействительный номер телефона. Попробуйте еще раз.
pt_phone_flood = ⏳ Слишком много попыток. Пожалуйста, подождите { $seconds } секунд.
pt_code_request_error = ❌ Ошибка при запросе кода: { $error }
pt_code_need_5_digits = ⚠️ Введите все 5 цифр кода подтверждения!
pt_sending_code_status = ⏳ Отправляем код подтверждения на номер { $phone }...
pt_enter_code_keypad = 📱 <b>Код подтверждения отправлен в Telegram</b>\n\nНажмите цифры кода на клавиатуре ниже:\n\nВведено: <b>{ $code }</b>
pt_enter_2fa_prompt = 🔐 <b>Требуется облачный пароль (2FA)</b>\n\nВведите пароль двухфакторной аутентификации:
pt_no_account_connected = ⚠️ Нет подключенного аккаунта. Подключите аккаунт.
pt_record_error = Ошибка записи.

# Администратор и рассылка (admin.py)
admin_access_denied = ⛔ Доступ только для администраторов
admin_broadcast_prompt = 📢 <b>Рассылка сообщений пользователям</b>\n\nОтправьте сообщение, которое хотите разослать всем пользователям бота.\n\n• Поддерживается форматирование <b>HTML</b> (жирный, курсив, ссылки).\n• Можно прикрепить фото, видео, анимацию или документ с подписью.\n\n<i>Для отмены нажмите кнопку «Назад» ниже.</i>
admin_broadcast_preview_title = 👁️ <b>Предпросмотр сообщения для рассылки:</b>
admin_broadcast_preview_params = 📊 <b>Параметры рассылки:</b>\n\n👥 Всего получателей в базе данных: <b>{ $total }</b>\n\nПодтвердите отправку или отмените действие:
admin_broadcast_cancelled = ❌ <b>Рассылка отменена.</b>
admin_broadcast_not_found = ⚠️ Ошибка: сообщение для рассылки не найдено.
admin_broadcast_started = 🚀 <b>Рассылка запущена... Пожалуйста, подождите.</b>
admin_broadcast_progress = 🚀 <b>Выполняется рассылка...</b>\n\nПрогресс: <b>{ $current }/{ $total }</b>\n✅ Отправлено: { $sent }\n🚫 Заблокировали бота: { $blocked }\n⚠️ Ошибок: { $errors }
admin_broadcast_report = 🏁 <b>Рассылка завершена!</b>\n\n📊 <b>Итоговый отчёт:</b>\n• Всего получателей: <b>{ $total }</b>\n• ✅ Успешно доставлено: <b>{ $sent }</b>\n• 🚫 Бот заблокирован пользователем: <b>{ $blocked }</b>\n• ⚠️ Другие ошибки: <b>{ $errors }</b>

# Парсер и лимиты (parser.py)
parser_notification_group_missing = ⚠️ <b>Группа уведомлений не найдена!</b>\n\nПеред запуском отслеживания необходимо создать целевую группу для получения уведомлений.\nНажмите кнопку ниже, чтобы настроить её:
parser_free_account_limit = ⚠️ <b>Превышен лимит отслеживания!</b>\n\nВы используете <b>общий бесплатный аккаунт</b>, на котором разрешено отслеживать только <b>1 канал</b>.\n\nДля отслеживания большего количества каналов:\n• Подключите собственный личный Telegram-аккаунт (без ограничений)\n• Или оплатите дополнительные слоты через Telegram Stars.

# Общие сообщения
welcome_choose_lang = 👋 Привет! Пожалуйста, выберите язык / Please choose your language:
no_connected_account = Нет подключенного аккаунта. Подключите аккаунт.
excel_export_caption = 📊 Результаты поиска групп в Excel
db_export_caption = 📊 Экспорт базы данных в Excel
found_groups_caption = 📊 Найдено { $count } групп/каналов

# Ночная проверка базы данных
nightly_check_btn = Ночная проверка (01:00)
nightly_check_on = ВКЛ
nightly_check_off = ВЫКЛ
nightly_check_toggled_on = 🔔 Автоматическая ночная проверка базы данных в 01:00 ВКЛЮЧЕНА.
nightly_check_toggled_off = 🔕 Автоматическая ночная проверка базы данных ВЫКЛЮЧЕНА.




