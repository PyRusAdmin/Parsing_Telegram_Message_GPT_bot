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
