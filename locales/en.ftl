# English localization
welcome_ask_language =
    🌍 Hi! Please choose your interface language:
welcome_message_template =
    🤖 Welcome to the Telegram bot for tracking 🔍 keywords in groups and channels, as well as searching for groups and channels with AI!

    📋 <b>Version:</b> { $version }
    📅 <b>Release date:</b> March 06, 2026

    📊 <b>Groups/channels found by users:</b> { $groups_count }

    📱 <b>Connected accounts:</b> { $count }
    📤 <b>Technical groups (for forwarding):</b> { $group_count }
    🔍 <b>Keywords tracked:</b> { $keywords_count }
    📡 <b>Channels being monitored:</b> { $get_groups }

    🎉 <b>Main bot features:</b>

    • 🤖 <b>AI Search:</b> find groups and channels using artificial intelligence
    • 📥 <b>Get Database:</b> download the current database of found channels and groups
    • 📚 <b>Instructions:</b> detailed guide on using the bot
    • ⚙️ <b>Settings:</b> configure account connections, keywords, and filters

    💡 <b>Tip:</b> to get the latest features and updates, it is recommended to restart the bot with the /start command

lang_selected =
    ✅ Great! The interface will now be displayed in your selected language.
settings_message =
    ⚙️ In this menu you can:
    • 🔗 Connect a Telegram account
    • 🌐 Change the interface language
    • 📢 Add groups and channels to track
    • 🧩 Configure keywords and filters

    Choose an option below 👇
connect_account =
    📱 To connect your Telegram account, send a session file in the format:
    `+79599999999.session`

    Once uploaded, the bot will use this account to track messages.
launching_tracking =
    🚀 Launching message tracking...

    Stopping tracking is only possible after subscribing to groups / channels
tracking_launch_error =
    ⚠️ The list of channels is empty.

    Please add at least one group or channel to track 🔍
    via the settings menu ⚙️
update_list =
    📥 Send a .txt file with a list of groups and channels to track:

    ✅ Each username must be in the format <b>@username</b>
    ✅ Each link must be on a <b>separate line</b>
    ✅ The file must have a <b>.txt</b> extension

    📌 Example file content:
    @group1
    @channel1
    @my_community

    File format is important — the bot will only correctly process text files with the proper structure.
account_missing =
    ⚠️ You do not have a connected Telegram account.

account_missing_2 =
    ⚠️ The session file for your Telegram account is invalid — you need to log in again. Send a valid session file.
enter_keyword =
    🔍 Enter a keyword / phrase to track
ai_search_welcome =
    🤖 <b>Welcome to the AI Search menu!</b>

    Here you can find new thematic groups and channels using the power of artificial intelligence.

    🚀 <b>Available modes:</b>
    • 🤖 <b>AI Search:</b> Fast search for groups based on your database and keywords.
    • 🌐 <b>Global AI Search:</b> Advanced search across the entire Telegram space to find new communities.

    Just select the desired mode on the keyboard or enter a request! 👇
enter_group =
    🔍 Enter a link to the group in the format @username to which the message will be forwarded when a keyword is detected
admin_panel_message =
    👋 <b>Welcome to Admin Panel!</b>

    Here's what you can do:

    📁 <b>Get Log File</b> — view the error and event log of the bot for the recent period. Useful for diagnostics.

    🔄 <b>Database Actualization</b> — update information about groups and channels: check their current type (group/channel) and get actual IDs.

    🏷️ <b>Assign Category</b> — automatically classify groups and channels by topics using AI.

    ✅ <b>Check Accounts</b> — check the status of connected accounts and their sessions.

    🌐 <b>Assign Language</b> — detect the language of content in groups and channels.

    🔐 <b>Connect Account</b> — connect a Telegram account via session file for use in the bot.

tracking_stopped =
    ✅ Tracking has been stopped.

instruction_caption =
    📘 <b>Usage Instructions</b>

    Attached is a detailed guide on the bot's functionality.

    🔗 <b>Online Documentation:</b>
    • <a href="{ $gitverse_link }">GitVerse</a>
    • <a href="{ $github_link }">GitHub</a>

    We recommend reviewing it for effective use of all bot features.

instruction_file_not_found =
    ⚠️ Instruction file not found on server.

instruction_send_error =
    ❌ An error occurred while sending the file.

# === Database Export ===
database_empty =
    📭 Database is empty.

export_all_caption =
    📦 Complete database of Telegram groups and channels.

    📊 Total records: { $total_records }
    🧹 Duplicates removed before export: { $deleted_duplicates }

export_channels_caption =
    📦 Telegram channels database.

    📊 Total records: { $total_records }

export_groups_caption =
    📦 Telegram groups database.

    📊 Total records: { $total_records }

export_error_generic =
    ❌ An error occurred while creating the file.

get_database_menu =
    👋 Welcome to the database export mode!

    Here's what you can do:

    🔹 <b>📥 Get Full Database</b> — get a complete list of all saved groups and channels in Excel format.
    🔹 <b>Get Channels Database</b> — get a list of all saved channels in Excel format.
    🔹 <b>Get Groups Database (supergroups)</b> — get a list of all saved supergroups in Excel format.
    🔹 <b>Get Regular Chats Database (old-style groups)</b> — get a list of all saved regular chats (old-style groups) in Excel format.
    🔹 Choose a category for export

    🔸 Press <b>Back</b> to return to the main menu.

select_category_prompt =
    📌 Select a category for which you want to get a list of groups/channels:

action_cancelled =
    ❌ Cancelled.

invalid_category =
    ⚠️ Invalid category. Please select from the list.

category_empty =
    📭 No groups in the "{ $category }" category yet.

category_export_caption =
    ✅ Exported { $group_count } groups/channels for category:
    "{ $category }"

# === AI Search ===
searching_groups =
    🔍 Searching for groups and channels...

search_summary =
    ✅ <b>Search completed!</b>

    📊 Found and saved: <b>{ $groups_count }</b> groups/channels
    📁 Results sent in Excel file

    📍 <b>Activity indicators:</b>
    🟢 <b>active</b> — group is active (last message ≤ 30 days)
    🔴 <b>inactive</b> — group is inactive (messages > 30 days or none at all)
    ⚪ <b>unknown</b> — could not determine (Telegram limitations)

search_results_caption =
    📄 Search results for query: <b>{ $query }</b>

search_no_results =
    ❌ Unfortunately, nothing was found for your query. Try other keywords.

search_error =
    ❌ An error occurred during search. Please try again.

# === Global AI Search ===
global_search_no_terms =
    ❌ Enter at least one search term.

global_search_processing =
    🔍 Processing { $total } queries...

global_search_skipped =
    ⚠️ Skipped: '{ $term }' (no available accounts)

global_search_progress =
    🔍 Processed { $current }/{ $total }: { $successful } successful

global_search_results_caption =
    📄 Found { $total } groups from { $successful }/{ $total_queries } queries

global_search_no_results =
    ❌ Unfortunately, nothing was found. Try other keywords.

# === Group Connection ===
group_added =
    ✅ Group { $group } has been added for message forwarding.

group_already_added =
    ⚠️ This group has already been added.

group_add_error =
    ⚠️ Error adding group.

# === Group Deletion ===
delete_group_prompt =
    Enter the group/channel username in @username format to remove from tracking:

group_deleted =
    ✅ Group { $group } has been successfully removed from tracking.

group_not_found =
    ❌ Group @{ $group } not found in your tracking list.

no_accounts =
    ❌ You have no connected accounts.

    Send a `.session` file or click "Connect Account" in the menu.

# === Keywords ===
no_keywords_entered =
    ⚠️ You haven't entered any keywords.

keywords_added_count =
    Keywords added: { $count }

keywords_already_added =
    Already added ({ $count })

keywords_add_errors =
    Errors adding

keywords_and_more =
    and { $count } more

keywords_and_more_errors =
    and { $count } more errors

keywords_summary =
    Summary

keywords_added =
    Added

keywords_skipped =
    Skipped (duplicates)

keywords_errors =
    Errors

# === Group Check ===
check_group_ask_url =
    📤 Enter the group link to check:

check_group_ask_keyword =
    🔍 Enter the keyword to search:

check_group_started =
    🔍 Starting group check...

check_group_new_message_with_link =
    📨 New message with keyword!

    📌 <b>{ $title }</b>
    📅 Date: { $msg_date }
    🔗 <a href="{ $message_link }">Go to message</a>

check_group_new_message_no_link =
    📨 New message with keyword!

    📌 <b>{ $title }</b>
    📅 Date: { $msg_date }

check_group_summary =
    ✅ Check completed!

    Messages found: { $count }
    Keyword: { $keyword }
    Matches: { $matched_count }

check_group_parse_error =
    ❌ Error parsing group. Please check the link and chat access.

# === Parser ===
target_group_not_found =
    ❌ Target group not found for user. Connect a group so I can forward messages found by your keywords.

no_channels_to_track =
    📭 You have no added channels to track.

too_many_channels =
    ⚠️ Found { $total } channels. Subscription will only be done for the first { $limit }.

channel_subscribed =
    ✅ Subscribed to { $channel }
    ⏳ Next attempt in { $delay } sec.

target_group_join_error =
    ❌ Account could not join the target group, check the connected group

target_group_not_configured =
    ❌ Target group not found for user. Connect a group.

target_group_fetch_error =
    ❌ Could not fetch target group. Check connection.

bot_listening =
    👂 Bot is listening for new messages...

tracking_not_active =
    ⚠️ Tracking is not started or already stopped.

tracking_stop_requested =
    🛑 Stop command sent. Tracking will be stopped within a few seconds.

search_client_error =
    ❌ Error connecting to account. Please try again later.

search_no_available_accounts =
    ⚠️ No available accounts for search.

# === Session ===
session_invalid =
    ⚠️ Account `{ $phone }` is no longer valid.
    Please reconnect the account.

account_fetch_error =
    ⚠️ An error occurred while fetching the account. Please try again later.

# === Account Checking ===
checking_accounts_start =
    Accounts to check: { $count }
checking_accounts_complete =
    ✅ Account checking completed

# === Category Assignment for AI ===
ai_category_select_method =
    🤖 <b>Select category assignment method:</b>

    ⚡️ <b>Fast (g4f.free)</b>
    • Free, no API keys
    • Sequential processing (slower)
    • Suitable for small volumes
    • May return inaccurate results

    🚀 <b>Powerful (Groq API)</b>
    • Requires Groq API key
    • Parallel processing in 10 threads (faster)
    • Suitable for large volumes
    • More accurate results

    Select a method:
ai_category_back =
    ↩️ Back to admin panel
ai_category_checking_models =
    🔍 Checking available models...
ai_category_model_selected =
    ✅ Selected model: { $model }
ai_category_select_from_keyboard =
    Please select a method from the keyboard below:
ai_category_all_have_categories =
    ✅ All groups already have categories!
ai_category_processing =
    🔄 Processing { $total } groups...
ai_category_done =
    ✅ <b>Done!</b>
ai_category_error =
    ❌ Error: { $error }
ai_category_stats_title =
    📊 <b>Category Statistics:</b>
ai_category_no_category_count =
    🗃️ Groups without category: { $count }
ai_category_run_ai =
    Press '🏷️ Assign Category' to start AI

# === Connect Account ===
connect_account_ask_session =
    📤 Send me Telethon session file(s) (must end with `.session`)

    You can send multiple files at once — the bot will process them in order.
    When done — press the "Back" button or send /start
connect_account_invalid_file =
    ❌ This is not a session file! Send a file with `.session` extension
connect_account_limit_reached =
    ⚠️ Limit reached: { $max } files at once.
    Process current files and send the rest later.
connect_account_file_queued =
    📥 File accepted: `{ $filename }`
    📊 In queue: { $total } file(s). Processing...
connect_account_success =
    ✅ <b>{ $filename }</b> — success!
    📱 { $phone } | 👤 { $name }
connect_account_failed =
    ❌ <b>{ $filename }</b> — failed validation
connect_account_error =
    ⚠️ <b>{ $filename }</b> — processing error
connect_account_processing_done =
    📊 <b>Processing completed!</b>

# === Language Detection ===
lang_detect_no_groups =
    ❌ No groups to process
lang_detect_starting =
    🚀 Starting processing of { $total } groups...
lang_detect_error =
    ❌ Error: { $error }
lang_detect_saving =
    💾 Saving { $count } results to DB...
lang_detect_complete =
    ✅ Processing completed!

    📊 Statistics:
    • Total: { $total }
    • AI detected: { $ai_success }
    • Saved to DB: { $db_success }
    • AI errors: { $ai_fail }
    • DB errors: { $db_fail }
    • Total errors: { $total_fail }

lang_detect_stats_title = Statistics
lang_detect_stats_total = Total
lang_detect_stats_ai_success = AI detected
lang_detect_stats_db_success = Saved to DB
lang_detect_stats_ai_fail = AI errors
lang_detect_stats_db_fail = DB errors
lang_detect_stats_total_fail = Total errors

# === Log File ===
log_file_caption =
    📄 Log file with errors.

# === connect_account.py ===
account_connected_free =
    ✅ Account successfully connected

invalid_session_file =
    ❌ This is not a session file! Send a file with `.session` extension

session_file_received =
    📥 File received: `{ $filename }`

    🔍 Checking account...

session_connected_success =
    ✅ <b>{ $filename }</b> — successful!
    📱 { $phone } | 👤 { $name }
    💾 Saved to your personal database.

session_validation_failed =
    ❌ <b>{ $filename }</b> — validation failed.
    Please check that the session file is current and not used elsewhere.

session_check_error =
    ⚠️ An error occurred while checking the account. Please try again later.

# === handlers.py (groups) ===
only_txt_files_supported =
    ⚠️ Only .txt files are supported.

empty_file_no_usernames =
    ⚠️ File is empty or contains no usernames.

groups_upload_summary =
    ✅ Added: { $added }
    ⚠️ Already exists: { $skipped }
    ❌ Errors: { $errors }

# === admin.py ===
admin_found_accounts =
    🔍 Found accounts: { $count }

admin_db_actualization_start =
    🔄 Starting actualization of { $total } groups...

admin_using_account =
    📱 Using account: { $account }

admin_account_error =
    ❌ Account error { $account }: { $error }

admin_critical_error =
    ❌ Critical error: { $error }

# === Question Export ===
no_questions_in_db =
    📭 There are no questions in the database.

questions_export_caption =
    📦 Export of questions and answers.

export_error =
    ❌ An error occurred during export: { $error }

# === Buttons ===
launch_tracking_button = 🚀 Start Tracking
check_group_for_keywords_button = 🔍 Check Group for Keywords
ai_search_button = ✨ AI Search
get_database_button = 📥 Get Database
instruction_button = 📖 Instructions
settings_button = ⚙️ Settings
admin_panel_button = 🛡️ Admin Panel
get_log_file_button = 📄 Get Log File
update_database_button = 🔄 Update Database
export_questions_button = Export Questions
assign_category_button = 🏷️ Assign Category
check_accounts_button = ✅ Check Accounts
assign_language_button = 🌐 Assign Language
connect_account_button = 🔐 Connect Account
back_button = ⬅️ Back
fast_method_button = ⚡️ Fast (g4f.free)
powerful_method_openrouter_button = 🚀 Powerful (Openrouter API)
powerful_method_groq_button = 🚀 Powerful (GROQ API)
all_database_button = 📥 All Database
channels_database_button = 📥 Channels Database
groups_database_button = 📥 Groups Database
select_category_button = 📂 Select Category
investments_button = investments
finance_and_personal_budget_button = finance and personal budget
crypto_and_blockchain_button = crypto and blockchain
business_and_entrepreneurship_button = business and entrepreneurship
marketing_and_promotion_button = marketing and promotion
tech_and_it_button = technologies and it
education_and_self_development_button = education and self-development
work_and_career_button = work and career
real_estate_button = real estate
health_and_medicine_button = health and medicine
travel_button = travel
auto_and_transport_button = auto and transport
shopping_and_discounts_button = shopping and discounts
entertainment_and_leisure_button = entertainment and leisure
politics_and_society_button = politics and society
science_and_research_button = science and research
sports_and_fitness_button = sports and fitness
cooking_and_food_button = cooking and food
fashion_and_beauty_button = fashion and beauty
hobbies_and_creativity_button = hobbies and creativity
russian_language_button = 🇷🇺 Russian
english_language_button = 🇬🇧 English
global_ai_search_button = 🌐 Global AI Search
stop_tracking_button = 🛑 Stop Tracking
update_list_button = 🔁 Update List
enter_keyword_button = 🔍 Enter Keyword
delete_group_from_tracking_button = 🗑️ Delete Group from Tracking
keywords_list_button = 🔍 Keywords List
tracking_links_button = 🌐 Tracking Links
connect_group_for_messages_button = 📤 Connect Group for Messages
change_language_button = 🌐 Change Language
connect_free_account_button = 🔐 Connect Free Account

# get_dada.py
keywords_export_caption = 📋 Keywords export. Total records: { $count }
no_keywords_found = 📭 You have no saved keywords.
tracking_links_export_caption = 🔗 Tracking links export. Total records: { $count }
no_tracking_links_found = 📭 You have no tracking links.
excel_header_number = #
excel_header_keyword = Keyword
excel_header_username = Channel/Group Username

# pars_ai.py
ai_search_button_user = 🤖 AI Search
excel_filename_all_db = All_Database.xlsx
excel_filename_channels_db = Channels_Database.xlsx
excel_filename_groups_db = Groups_Database.xlsx
excel_sheet_name_search_results = Search Results
excel_header_id = ID (Hash)
excel_header_name = Name
excel_header_description = Description
excel_header_participants = Participants
excel_header_category = Category
excel_header_type = Type
excel_header_language = Language
excel_header_activity = Activity
excel_header_link = Link
excel_header_date_added = Date Added
excel_sheet_name_groups = Groups
excel_filename_groups_by_category = groups_{ $category }.xlsx
excel_header_group_name = Name
excel_header_group_description = Description
excel_header_group_type = Type
excel_header_group_participants = Participants
excel_header_group_link = Link
excel_filename_telegram_groups = telegram_groups_{ $timestamp }.xlsx

# post_doc.py
instruction_question_prompt = 🤖 <b>You can ask me any question about using the bot, and I will answer you!</b>
# post_doc.py
instruction_question_prompt = 🤖 <b>You can ask me any question about using the bot, and I will answer you!</b>
ai_support_assistant_system_prompt = You are a qualified support assistant for the AutoParseAlertBot Telegram bot. Your task is to answer user questions based STRICTLY on the provided knowledge base. If the answer is not in the knowledge base, politely inform the user that you do not have this information and advise them to contact support. Respond in the user's language. Use HTML markup for formatting the answer.
excel_filename_telegram_groups = telegram_groups_{ $timestamp }.xlsx
excel_header_group_link = Link
excel_header_group_participants = Participants
excel_header_group_type = Type
excel_header_group_description = Description
excel_header_group_name = Name
excel_filename_groups_by_category = groups_{ $category }.xlsx
excel_sheet_name_groups = Groups
excel_header_date_added = Date Added
excel_header_link = Link
excel_header_activity = Activity
excel_header_language = Language
excel_header_type = Type
excel_header_category = Category
excel_header_participants = Participants
excel_header_description = Description
excel_header_name = Name
excel_header_id = ID (Hash)
excel_sheet_name_search_results = Search Results
excel_filename_groups_db = Groups_Database.xlsx
excel_filename_channels_db = Channels_Database.xlsx
excel_filename_all_db = All_Database.xlsx
ai_search_button_user = 🤖 AI Search
excel_header_username = Channel/Group Username
excel_header_keyword = Keyword
excel_header_number = #
no_tracking_links_found = 📭 You have no tracking links.
tracking_links_export_caption = 🔗 Tracking links export. Total records: { $count }
no_keywords_found = 📭 You have no saved keywords.
keywords_export_caption = 📋 Keywords export. Total records: { $count }
connect_free_account_button = 🔐 Connect Free Account
change_language_button = 🌐 Change Language
connect_group_for_messages_button = 📤 Connect Group for Messages
tracking_links_button = 🌐 Tracking Links
keywords_list_button = 🔍 Keywords List
delete_group_from_tracking_button = 🗑️ Delete Group from Tracking
enter_keyword_button = 🔍 Enter Keyword
update_list_button = 🔁 Update List
stop_tracking_button = 🛑 Stop Tracking
global_ai_search_button = 🌐 Global AI Search
english_language_button = 🇬🇧 English
russian_language_button = 🇷🇺 Russian
hobbies_and_creativity_button = hobbies and creativity
fashion_and_beauty_button = fashion and beauty
cooking_and_food_button = cooking and food
sports_and_fitness_button = sports and fitness
science_and_research_button = science and research
politics_and_society_button = politics and society
entertainment_and_leisure_button = entertainment and leisure
shopping_and_discounts_button = shopping and discounts
auto_and_transport_button = auto and transport
travel_button = travel
health_and_medicine_button = health and medicine
real_estate_button = real estate
work_and_career_button = work and career
education_and_self_development_button = education and self-development
tech_and_it_button = technologies and it
marketing_and_promotion_button = marketing and promotion
business_and_entrepreneurship_button = business and entrepreneurship
crypto_and_blockchain_button = crypto and blockchain
finance_and_personal_budget_button = finance and personal budget
investments_button = investments
select_category_button = 📂 Select Category
groups_database_button = 📥 Groups Database
channels_database_button = 📥 Channels Database
all_database_button = 📥 All Database
powerful_method_groq_button = 🚀 Powerful (GROQ API)
powerful_method_openrouter_button = 🚀 Powerful (Openrouter API)
fast_method_button = ⚡️ Fast (g4f.free)
back_button = ⬅️ Back
connect_account_button = 🔐 Connect Account
assign_language_button = 🌐 Assign Language
check_accounts_button = ✅ Check Accounts
assign_category_button = 🏷️ Assign Category
export_questions_button = Export Questions
update_database_button = 🔄 Update Database
get_log_file_button = 📄 Get Log File
admin_panel_button = 🛡️ Admin Panel
settings_button = ⚙️ Settings
instruction_button = 📖 Instructions
get_database_button = 📥 Get Database
ai_search_button = ✨ AI Search
check_group_for_keywords_button = 🔍 Check Group for Keywords
launch_tracking_button = 🚀 Start Tracking

# language_detection.py
lang_detect_summary = ✅ Processing completed!

    📊 Statistics:
    • Total: { $total }
    • AI detected: { $ai_success }
    • Saved to DB: { $db_success }
    • AI errors: { $ai_fail }
    • DB errors: { $db_fail }
    • Total errors: { $total_fail }
name_prompt = Name
description_prompt = Description
no_data_prompt = No data
ai_lang_detect_prompt = Determine the main language of the text or community description.
Respond STRICTLY with a single word — the language code in ISO 639-1 format (two-letter code).
Examples of correct answers: ru, en, es, zh, ar, hi, ja, ko, fr, de, pt, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn.
If the language cannot be determined unambiguously or the text contains a mixture of languages without a dominant one — answer: unknown.
DO NOT add any explanations, punctuation, spaces, or additional text. Only the language code or 'unknown'.

Text for analysis:
{ $user_input }

# checking_group_for_ai.py
get_groups_without_category_message = 📊 <b>Category Statistics:</b>

    🗃️ Groups without category: { $count }

    Press '🏷️ Assign Category' to start AI


