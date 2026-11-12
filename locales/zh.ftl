# ZH localization

welcome_ask_language =
    🌍 Hi! 请选择您的界面语言：

welcome_message_template =
    🤖 欢迎使用 Telegram Bot，用于跟踪 🔍 组和频道，以及 AI 社区搜索！

    📋 <b>版本：</b> { $version }
    📅 <b>发布日期：</b> 2026 年 9 月 4 日
    👨‍💻 <b>开发者：</b> <a href="https://t.me/PyAdminRU">@PyAdminRU</a>
    📢 <b>主频道：</b> <a href="https://t.me/master_tg_d">@master_tg_d</a>

    📊 <b>用户发现的组/频道：</b> { $groups_count }

    📱 <b>已连接的账号：</b> { $count }
    📤 <b>技术组（用于转发）：</b> { $group_count }
    🔍 <b>正在跟踪的关键词：</b> { $keywords_count }
    📡 <b>正在监控的频道：</b> { $get_groups }

    🎉 <b>主要功能：</b>

    • 🌐 <b>Web 面板中的 AI 搜索：</b> 现在可以在 Web 应用界面中使用 AI 驱动的搜索
    • 📥 <b>获取数据库：</b> 下载已发现的频道和组的当前数据库
    • 📚 <b>说明：</b> 使用 bot 的详细指南
    • ⚙️ <b>设置：</b> 配置账号连接、关键词和过滤器

    💡 <b>提示：</b> 为了获取最新功能和更新，请使用 /start 命令重启 bot

lang_selected =
    ✅ 好！现在界面将以您选择的语言显示。

settings_message =
    ⚙️ 在此菜单中，您可以：
    • 🔗 连接 Telegram 账号
    • 🌐 更改界面语言
    • 📢 添加组和频道进行跟踪
    • 🧩 配置关键词和过滤器

    请选择以下选项 👇

connect_account =
    📱 为了连接您的 Telegram 账号，请发送会话文件：

    `+79599999999.session`

    一旦上传，bot 将使用该账号进行跟踪。

launching_tracking =
    🚀 启动跟踪消息...

    停止跟踪仅在订阅组/频道后才可进行

tracking_launch_error =
    ⚠️ 列表中的频道为空。

    请在设置菜单中添加至少一个组或频道 🔍

update_list =
    📥 请发送 .txt 文件，包含要跟踪的组和频道：

    ✅ 每个用户名必须以 <b>@username</b> 格式
    ✅ 每个链接必须在 <b>单独行</b> 中
    ✅ 文件必须有 <b>.txt</b> 扩展名

    📌 示例文件内容：
    @group1
    @channel1
    @my_community

    文件格式很重要 — bot 将仅正确处理具有适当结构的文本文件。

account_missing =
    ⚠️ 您没有连接的 Telegram 账号。

account_missing_2 =
    ⚠️ 您的 Telegram 账号会话文件无效 — 请重新登录。发送有效的会话文件。

enter_keyword =
    🔍 输入要跟踪的关键词/短语

ai_search_welcome =
    🤖 <b>欢迎使用 AI 搜索菜单！</b>

    以下是您可以找到新主题组和频道的 AI 功能：

    🚀 <b>可用模式：</b>
    • 🤖 <b>AI 搜索：</b> 基于您的数据库和关键词的快速搜索
    • 🌐 <b>全球 AI 搜索：</b> 在 Telegram 空间中进行高级搜索以找到新社区

    请在键盘上选择所需的模式或输入请求！ 👇

enter_group =
    🔍 输入组的链接，格式为 @username，用于将消息转发到该组时检测关键词

admin_panel_message =
    👋 <b>欢迎使用管理员面板！</b>

    以下是您可以进行的操作：

    📁 <b>获取日志文件：</b> 查看 bot 的错误和事件日志，用于诊断

    🔄 <b>数据库更新：</b> 更新组和频道的信息：检查其当前类型（组/频道）并获取实际 ID

    🏷️ <b>分配类别：</b> 使用 AI 分类组和频道

    ✅ <b>检查账号：</b> 检查已连接的账号和会话

    🌐 <b>分配语言：</b> 检测组和频道的内容语言

    🔐 <b>连接账号：</b> 使用会话文件连接 Telegram 账号

tracking_stopped =
    ✅ 跟踪已停止。

instruction_caption =
    📘 <b>使用说明：</b>

    附带的说明文件包含 bot 功能的详细指南。

    🔗 <b>在线文档：</b>
    • <a href="{ $gitverse_link }">GitVerse</a>
    • <a href="{ $github_link }">GitHub</a>

    我们建议您浏览它以充分利用所有 bot 功能。

instruction_file_not_found =
    ⚠️ 服务器上未找到说明文件。

instruction_send_error =
    ❌ 发送文件时发生错误。

database_empty =
    📭 数据库为空。

export_all_caption =
    📦 Telegram 组和频道的完整数据库。

    📊 总记录数： { $total_records }
    🧹 删除重复记录前： { $deleted_duplicates }

export_channels_caption =
    📦 Telegram 频道数据库。

    📊 总记录数： { $total_records }

export_groups_caption =
    📦 Telegram 组数据库。

    📊 总记录数： { $total_records }

export_error_generic =
    ❌ 创建文件时发生错误。

get_database_menu =
    👋 欢迎使用数据库导出模式！

    以下是您可以进行的操作：

    🔹 <b>获取完整数据库：</b> 获取 Excel 格式的所有保存的组和频道列表
    🔹 <b>获取频道数据库：</b> 获取 Excel 格式的所有保存的频道列表
    🔹 <b>获取组数据库（超级组）：</b> 获取 Excel 格式的所有保存的超级组列表
    🔹 <b>获取旧式组数据库（旧式组）：</b> 获取 Excel 格式的所有保存的旧式组列表
    🔹 选择导出类别

    🔸 请按 <b>返回</b> 返回到主菜单。

select_category_prompt =
    📌 选择您要获取组/频道列表的类别：

action_cancelled =
    ❌ 取消。

invalid_category =
    ⚠️ 无效的类别。 请从列表中选择。

category_empty =
    📭 "{ $category }" 类别中尚无组。

category_export_caption =
    ✅ 已导出 { $group_count } 个组/频道的分类：
    "{ $category }"

searching_groups =
    🔍 寻找组和频道...

search_summary =
    ✅ <b>搜索完成!</b>

    📊 找到了并保存了：<b>{ $groups_count }</b> 个组/频道
    📁 结果已发送到 Excel 文件

    📍 <b>活动指标：</b>
    🟢 <b>active</b> — 组是活跃的（最后消息 ≤ 30 天）
    🔴 <b>inactive</b> — 组是不活跃的（消息 > 30 天或无消息）
    ⚪ <b>unknown</b> — 不能确定（Telegram 限制）

search_results_caption =
    📄 搜索结果：<b>{ $query }</b>

search_no_results =
    ❌ 对于您的查询，找不到任何内容。请尝试其他关键词。

search_error =
    ❌ 搜索过程中发生错误。请再试一次。

global_search_no_terms =
    ❌ 请至少输入一个搜索关键词。

global_search_processing =
    🔍 处理 { $total } 个查询...

global_search_skipped =
    ⚠️ 跳过：'{ $term }'（无可用账户）

global_search_progress =
    🔍 处理 { $current }/{ $total }: { $successful } 个成功

global_search_results_caption =
    📄 找到了 { $total } 个组，从 { $successful }/{ $total_queries } 个查询中

global_search_no_results =
    ❌ 没有找到任何内容。请尝试其他关键词。

group_added =
    ✅ 已为消息转发添加组 { $group }。

group_already_added =
    ⚠️ 这个组已经添加过了。

group_add_error =
    ⚠️ 添加组时发生错误。

delete_group_prompt =
    请输入组/频道的用户名（@username 格式）以从跟踪列表中删除：

group_deleted =
    ✅ 已成功从跟踪列表中删除组 { $group }。

group_not_found =
    ❌ 组 @{ $group } 在您的跟踪列表中找不到。

no_accounts =
    ❌ 您没有连接的账户。

    请发送`.session`文件或在菜单中单击“连接账户”。

no_keywords_entered =
    ⚠️ 未输入任何关键词。

keywords_added_count =
    添加关键词： { $count }

keywords_already_added =
    已经添加（ { $count }）

keywords_add_errors =
    添加关键词时发生错误。

keywords_and_more =
    和 { $count } 个更多

keywords_and_more_errors =
    和 { $count } 个更多错误

keywords_summary =
    总结

keywords_added =
    已添加

keywords_skipped =
    跳过（重复项）

keywords_errors =
    错误

check_group_ask_url =
    📤 请输入群组链接以检查：

check_group_ask_keyword =
    🔍 请输入要搜索的关键字：

check_group_started =
    🔍 开始群组检查...

check_group_new_message_with_link =
    📨 有新消息包含关键字！

    📌 <b>{ $title }</b>
    📅 日期： { $msg_date }
    🔗 <a href="{ $message_link }">查看消息</a>

check_group_new_message_no_link =
    📨 有新消息包含关键字！

    📌 <b>{ $title }</b>
    📅 日期： { $msg_date }

check_group_summary =
    ✅ 检查完成！

    找到消息： { $count }
    关键字： { $keyword }
    匹配： { $matched_count }

check_group_parse_error =
    ❌ 解析群组出错，请检查链接和聊天访问。

target_group_not_found =
    ❌ 用户未找到目标群组。请连接一个群组以便我可以转发用户的关键字找到的消息。

no_channels_to_track =
    📭 您没有添加的通道来追踪。

too_many_channels =
    ⚠️ 找到 { $total } 个通道。订阅将只对第一个 { $limit } 个通道。

channel_subscribed =
    ✅ 订阅 { $channel }
    ⏳ 下次尝试在 { $delay } 秒。

target_group_join_error =
    ❌ 账户无法加入目标群组，请检查已连接的群组。

target_group_not_configured =
    ❌ 用户未找到目标群组。请连接一个群组。

target_group_fetch_error =
    ❌ 无法获取目标群组，请检查连接。

bot_listening =
    👂 机器人正在监听新消息...

tracking_not_active =
    ⚠️ 跟踪未启动或已停止。

tracking_stop_requested =
    🛑 已发送停止命令。跟踪将在几秒钟内停止。

search_client_error =
    ❌ 连接到账户出错，请稍后再试。

search_no_available_accounts =
    ⚠️ 无可用账户用于搜索。

session_invalid =
    ⚠️ 账户 `{ $phone }` 已无效。
    请重新连接账户。

account_fetch_error =
    ⚠️ 获取账户时发生错误，请稍后再试。

checking_accounts_start =
    检查账户： { $count }

checking_accounts_complete =
    ✅ 账户检查完成

ai_category_select_method =
    🤖 <b>选择分类分配方法：</b>

    ⚡️ <b>快速（g4f.free）</b>
    • 免费，无需API密钥
    • 串行处理（较慢）
    • 适合小规模
    • 可能返回不准确的结果

    🚀 <b>强大（Groq API）</b>
    • 需要Groq API密钥
    • 并行处理10线程（更快）
    • 适合大规模
    • 更准确的结果

    选择方法：

ai_category_back =
    ↩️ 返回到管理面板

ai_category_checking_models =
    🔍 检查可用模型...

ai_category_model_selected =
    ✅ 选择模型： { $model }

ai_category_select_from_keyboard =
    请从下面的键盘中选择一个方法：

ai_category_all_have_categories =
    ✅ 所有组都已经有分类了！

ai_category_processing =
    🔄 正在处理 { $total } 个组...

ai_category_done =
    ✅ <b>完成!</b>

ai_category_error =
    ❌ 错误： { $error }

ai_category_stats_title =
    📊 <b>分类统计:</b>

ai_category_no_category_count =
    🗃️ 没有分类的组： { $count }

ai_category_run_ai =
    按‘🏷️ 分类’键开始 AI

connect_account_ask_session =
    📤 请发送 Telethon 会话文件（必须以 `.session` 结尾）

    你可以一次发送多个文件 — 机器人会按照顺序处理它们。
    当处理完成时 — 点击“返回”按钮或发送 `/start`

connect_account_invalid_file =
    ❌ 这不是一个会话文件！请发送一个以 `.session` 结尾的文件

connect_account_limit_reached =
    ⚠️ 达到限制： { $max } 个文件一次。
    处理当前文件并稍后再发送其他文件。

connect_account_file_queued =
    📥 文件已接受： `{ $filename }`
    📊 队列中： { $total } 个文件。处理中...

connect_account_success =
    ✅ <b>{ $filename }</b> — 成功！
    📱 { $phone } | 👤 { $name }

connect_free_account_success =
    ✅ <b>{ $filename }</b> — 已添加到免费账户池！
    📱 { $phone } | 👤 { $name } | 🆔 <code>{ $account_id }</code>

connect_account_failed =
    ❌ <b>{ $filename }</b> — 验证失败

connect_account_error =
    ⚠️ <b>{ $filename }</b> — 处理错误

connect_account_processing_done =
    📊 <b>处理完成!</b>

lang_detect_no_groups =
    ❌ 没有组需要处理

lang_detect_starting =
    🚀 开始处理 { $total } 个组...

lang_detect_error =
    ❌ 错误： { $error }

lang_detect_saving =
    💾 保存 { $count } 个结果到数据库...

lang_detect_complete =
    ✅ 处理完成！

    📊 统计：
    • 总计： { $total }
    • AI 检测： { $ai_success }
    • 保存到数据库： { $db_success }
    • AI 错误： { $ai_fail }
    • 数据库错误： { $db_fail }
    • 总错误： { $total_fail }

lang_detect_stats_title = 统计

lang_detect_stats_total = 总计

lang_detect_stats_ai_success = AI 检测

lang_detect_stats_db_success = 保存到数据库

lang_detect_stats_ai_fail = AI 错误

lang_detect_stats_db_fail = 数据库错误

lang_detect_stats_total_fail = 总错误数

log_file_caption =
    📄 错误日志

account_connect_personal =
    🔐 <b>Telegram 账户管理</b>

    📱 <b>当前账户:</b> ✅ <i>个人账户</i>
    📊 <b>模式:</b> 无限制频道（在您的槽位内）

    您可以使用另一种方法重新连接或断开连接。

account_connect_shared =
    🔐 <b>Telegram 账户管理</b>

    🎁 <b>当前账户:</b> <i>管理员免费账户</i>
    ⚠️ <b>限制:</b> 只允许在 <b>1 个群组</b> 中进行关键字跟踪。

    🔄 <i>如果当前账户出现问题，请点击下面的“重新连接免费账户”。</i>
    💡 <i>要同时跟踪多个群组，请连接您的个人账户。</i>

free_account_connected_success =
    🎉 <b>免费管理员账户连接成功!</b>

    📱 <b>账户:</b> { $phone }
    👤 <b>名称:</b> { $name }
    ⚠️ <b>注意:</b> 该免费账户仅限 <b>1 个群组</b>。

    💡 <i>如果您需要跟踪更多频道，请随时连接您的个人账户。</i>

free_account_reconnected_success =
    🎉 <b>免费账户重新连接成功!</b>

    📱 <b>新账户:</b> { $phone }
    👤 <b>名称:</b> { $name }
    ✅ <b>状态:</b> 活跃并准备进行跟踪。

    ⚠️ <b>注意:</b> 该免费账户仅限 <b>1 个群组</b>。

account_connect_none =
    🔐 <b>Telegram 账户管理</b>

    ⚠️ <b>当前账户:</b> <i>未连接</i>

    为了监视消息和关键字，请选择连接方法：
    • <b>个人账户</b> — 无频道限制。
    • <b>管理员免费账户</b> — 免费访问，仅限 <b>1 个群组</b>。

account_connected_free =
    ✅ 账户成功连接

no_free_accounts =
    ❌ 没有可用的免费账户。请稍后再试或联系管理员。

no_free_accounts_detailed =
    ⚠️ <b>没有可用的免费账户</b>

    目前，管理员没有提供免费账户。请连接您的个人账户（通过电话或会话文件）。

invalid_session_file =
    ❌ 这不是会话文件！请发送带有 `.session` 扩展名的文件

session_file_received =
    📥 接收的文件： `{ $filename }`

    🔍 检查账户...

session_connected_success =
    ✅ <b>{ $filename }</b> — 成功！
    📱 { $phone } | 👤 { $name }
    💾 保存到您的个人数据库。

session_validation_failed =
    ❌ <b>{ $filename }</b> — 验证失败。
    请检查会话文件是否是最新且未被其他地方使用。

session_check_error =
    ⚠️ 检查账户时发生错误。请稍后再试。

only_txt_files_supported =
    ⚠️ 只支持 .txt 文件。

empty_file_no_usernames =
    ⚠️ 文件为空或无用户名。

groups_upload_summary =
    ✅ 添加： { $added }
    ⚠️ 已存在： { $skipped }
    ❌ 错误： { $errors }

admin_found_accounts =
    🔍 找到了 { $count } 个账户

admin_db_actualization_start =
    🔄 开始 { $total } 个群组的实际化...

admin_using_account =
    📱 使用账户： { $account }

admin_account_error =
    ❌ 账户错误 { $account }： { $error }

admin_critical_error =
    ❌ 严重错误： { $error }

no_questions_in_db =
    📭 数据库中没有问题。

questions_export_caption =
    📦 问题和答案的导出

export_error =
    ❌ 导出时发生错误： { $error }

launch_tracking_button = 🚀 开始跟踪

check_group_for_keywords_button = 🔍 检查群组关键字

ai_search_button = ✨ AI 搜索

get_database_button = 📥 获取数据库

instruction_button = 📖 指导

settings_button = ⚙️ 设置

admin_panel_button = 🛡️ 管理面板

get_log_file_button = 📄 获取日志文件

export_questions_button = Export 问题

assign_category_button = 🏷️ 分类

check_accounts_button = ✅ 检查账户

connect_account_button = 🔐 连接账户

back_button = ⬅️ 返回

fast_method_button = ⚡️ 快速方法 (g4f.free)

powerful_method_openrouter_button = 🚀 强大方法 (Openrouter API)

powerful_method_groq_button = 🚀 强大方法 (GROQ API)

all_database_button = 📥 所有数据库

channels_database_button = 📥 频道数据库

groups_database_button = 📥 组数据库

select_category_button = 📂 选择分类

investments_button = 投资

finance_and_personal_budget_button = 财务和个人预算

crypto_and_blockchain_button = 加密和区块链

business_and_entrepreneurship_button = 商业和创业

marketing_and_promotion_button = 市场推广

tech_and_it_button = 技术和IT

education_and_self_development_button = 教育和自我发展

work_and_career_button = 工作和职业

real_estate_button = 房地产

health_and_medicine_button = 健康和医学

travel_button = 旅行

auto_and_transport_button = 自动和交通

shopping_and_discounts_button = 购物和折扣

entertainment_and_leisure_button = 娱乐和休闲

politics_and_society_button = 政治和社会

science_and_research_button = 科学和研究

sports_and_fitness_button = 运动和健康

cooking_and_food_button = 烹饪和美食

fashion_and_beauty_button = 时尚和美容

hobbies_and_creativity_button = 休闲和创造

russian_language_button = 🇷🇺 俄语

english_language_button = 🇬🇧 英文

stop_tracking_button = 🛑 停止跟踪

update_list_button = 🔁 更新列表

enter_keyword_button = 🔍 输入关键词

delete_group_from_tracking_button = 🗑️ 删除组从跟踪

keywords_list_button = 🔍 关键词列表

tracking_links_button = 🌐 跟踪链接

connect_group_for_messages_button = 📤 连接组为消息

change_language_button = 🌐 更改语言

connect_free_account_button = 🔐 连接免费账户

keywords_export_caption = 📋 关键词导出。总记录数：{ $count }

no_keywords_found = 📭 没有找到关键词。

tracking_links_export_caption = 🔗 跟踪链接导出。总记录数：{ $count }

no_tracking_links_found = 📭 没有找到跟踪链接。

excel_header_number =

excel_header_keyword = 关键词

excel_header_username = 通道/组用户名

Here is the translated content in Simplified Chinese (zh):

ai_search_button_user = 🤖 AI 搜索

excel_filename_all_db = 全数据库.xlsx

excel_filename_channels_db = 频道数据库.xlsx

excel_filename_groups_db = 组数据库.xlsx

excel_sheet_name_search_results = 搜索结果

excel_header_id = ID (Hash)

excel_header_name = 名称

excel_header_description = 描述

excel_header_participants = 参与者

excel_header_category = 类别

excel_header_type = 类型

excel_header_language = 语言

excel_header_activity = 活动

excel_header_link = 链接

excel_header_date_added = 添加日期

excel_sheet_name_groups = 组

excel_filename_groups_by_category = 组_{ $category }.xlsx

excel_header_group_name = 名称

excel_header_group_description = 描述

excel_header_group_type = 类型

excel_header_group_participants = 参与者

excel_header_group_link = 链接

excel_filename_telegram_groups = telegram_groups_{ $timestamp }.xlsx

instruction_question_prompt = 🤖 <b>您可以向我提任何关于使用机器人的问题，我会回答您!</b>

ai_support_assistant_system_prompt = 您是AutoParseAlertBot Telegram机器人支持助手。您的任务是根据提供的知识库回答用户问题。如果答案不在知识库中，请礼貌地告诉用户您不知道这个信息，并建议他们联系支持。以用户语言回答，使用可读性良好的文本，不使用任何标记（不使用Markdown字符）

lang_detect_summary = ✅ 处理完成！

    📊 统计信息：
    • 总数：{ $total }
    • AI检测：{ $ai_success }
    • 保存到DB：{ $db_success }
    • AI错误：{ $ai_fail }
    • DB错误：{ $db_fail }
    • 总错误：{ $total_fail }

name_prompt = 名称

description_prompt = 描述

no_data_prompt = 无数据

ai_lang_detect_prompt =
    确定文本或社区描述的主要语言。
    只需回复一个单词 — ISO 639-1 格式的语言代码（两位代码）。
    正确的回复例子： ru, en, es, zh, ar, hi, ja, ko, fr, de, pt, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn。
    如果无法确定语言或文本中有多种语言但没有明显的主流语言 — 回复： unknown。
    分析文本：
    { $user_input }

get_groups_without_category_message = 📊 <b>分类统计：</b>

    🗃️ 无分类的组： { $count }

    点击 '🏷️ 分类' 开始 AI

download_free_success = 📥 正在导出数据库（每天 1 次免费下载）。开始下载...

download_cooldown_message =
    ⚠️ 您已经在过去的 24 小时内下载了数据库。
    下一次免费下载将在 <b>{ $time }</b> 后可用。
    
    您可以现在下载数据库，花费 5 ⭐。
    机器人中的星球余额： <b>{ $stars }</b> ⭐

pay_from_balance_btn = 🪙 从余额中扣除 5 ⭐

pay_direct_btn = ⭐ 直接支付 5 ⭐

cancel_btn = ❌ 取消

download_paid_success = ✅ 支付/扣除 5 ⭐ 成功。开始数据库下载...

download_insufficient_stars = ❌ 余额中没有足够的星球。

stars_topup_success = 🎉 余额成功补充了 { $amount } ⭐！当前余额： { $balance } ⭐。

stars_added_admin = ⭐ 管理员为您补充了 { $amount } ⭐。当前余额： { $balance } ⭐。

topup_stars_button = 💳 补充星球

stars_balance_msg = 👤 <b>星球资料：</b>\n\n余额： <b>{ $stars }</b> ⭐\n\n您可以在这里补充 Telegram 星球余额，用于付费数据库下载。

stars_invoice_title = 补充星球余额

stars_invoice_desc = 购买 { $amount } Telegram 星球用于机器人

stars_invoice_dl_title = 数据库下载

stars_invoice_dl_desc = 一次性数据库下载，绕过每日限制

excel_filename_category_db = 分类数据库.xlsx

export_category_caption = 📂 分类 "{ $category }" 的数据库。总记录数： { $total_records }。

generating_database_wait = ⏳ 生成数据库文件，可能需要一些时间。请等待...

btn_add_channels_tracking = ➕ 添加监控的频道（文本或 .txt）

btn_channels_list = 📋 频道列表

btn_export_excel = 📥 导出到 Excel

btn_clear_all_channels = 🧹 清空所有频道

btn_tracking_channels = 🌐 监控的频道

btn_keywords = 🔍 关键字

btn_notification_group = 📢 通知组

btn_transfer_settings = 🔄 用户设置转移

btn_personal_tracking = 🎯 跟踪

btn_connect_account_session = 📄 通过会话连接账户 (.session)

btn_connect_account_phone = 📱 通过电话连接个人账户

btn_connect_free_account = 🎁 管理员的免费账户 (1 组)

btn_reconnect_free_account = 🔄 重连免费账户

btn_disconnect_account = ❌ 断开当前账户

btn_to_tracking_menu = 🎯 跟踪菜单

btn_to_settings_menu = ⚙️ 到设置

btn_main_menu = 🏠 主菜单

btn_add_keywords = ➕ 添加关键字

btn_keywords_list = 📋 关键字列表

btn_export_keywords = 📥 导出关键字

btn_goto_notification_group = 🔗 打开通知组

btn_notification_group_not_created = 🔗 组未创建

btn_recreate_notification_group = 🔄 重建组

btn_nav_prev = ◀️ 返回

btn_nav_next = 下一个 ▶️

btn_confirm_clear = ✅ 是，清除

btn_cancel = ❌ 取消

btn_broadcast_users = 📢 广播给用户

btn_broadcast_send = 🚀 发送广播

btn_broadcast_cancel = ❌ 取消广播

btn_pt_add_tracking = ➕ 添加组跟踪

btn_pt_buy_slot = ⭐ 购买+1 个槽 (2 颗星)

btn_pt_my_groups = 📋 我的监控组

btn_pt_stats = 📊 统计

btn_keypad_submit = 📦 提交

btn_keypad_cancel = 🚫 取消

btn_pt_edit_record = ⚙️ 编辑

btn_pt_buy_stars_slots = ⭐ 购买插槽（Telegram Stars）

btn_pt_connect_personal = 📱 连接个人账户

btn_pt_create_notification_group = 📢 创建通知组

settings_channels_title = 🌐 <b>监视的频道</b>\n\n📊 总频道数: <b>{ $total }</b>\n\n选择操作：

settings_channels_empty = 📭 频道列表为空。

settings_channels_list_title = 📋 <b>频道列表</b> (页面 { $page }/{ $total_pages }) · 总数: { $total }\n

settings_channels_list_hint = \n<i>点击 ❌ 删除一个频道。</i>

settings_channel_deleted = ✅ 删除频道: { $channel }

settings_channel_not_found = ⚠️ 未找到频道。

settings_channels_clear_confirm = 🧹 <b>清空整个频道列表?</b>\n\n将删除 <b>{ $total }</b> 个频道。这操作不可逆。

settings_channels_cleared = ✅ <b>频道列表已清空。</b>\n\n删除的频道: <b>{ $count }</b>

settings_keywords_title = 🔍 <b>关键词</b>\n\n📊 总关键词数: <b>{ $total }</b>\n\n选择操作：

settings_keywords_empty = 📭 关键词列表为空。

settings_keywords_list_title = 🔍 <b>关键词</b> (页面 { $page }/{ $total_pages }) · 总数: { $total }\n

settings_keywords_list_hint = \n<i>点击 ❌ 删除一个关键词。</i>

settings_keyword_deleted = ✅ 删除: { $keyword }

settings_keyword_not_found = ⚠️ 未找到关键词。

settings_notification_created = 📢 <b>通知组</b>\n\n✅ 组已创建。\n🔗 <a href='{ $link }'>前往组</a>

settings_notification_not_created = 📢 <b>通知组</b>\n\n❌ 组未创建。\n\n<i>请前往 «🎯 个人追踪» 创建组。</i>

settings_notification_alert_no_group = ❌ 组未创建。前往 «🎯 个人追踪» 创建组。

settings_notification_recreate_text = 🔄 <b>重新创建通知组</b>\n\n要重新创建组，请前往 «🎯 个人追踪» → «➕ 添加追踪组»。\n\n<i>重新创建组将自动创建新的组。</i>

connect_group_prompt = 🔗 <b>发送组或频道的链接或用户名</b>\n\n例如:\n<code>https://t.me/python_jobs</code>\nor <code>@python_jobs</code>\n\n可以发送多个链接，一个一行。

connect_group_no_links = ⚠️ 请发送至少一个链接或用户名。

connect_group_invalid_links = ⚠️ 请检查链接是否有效。

connect_group_saved = ✅ 组已保存到数据库。

Here is the translated content in Simplified Chinese (zh):

```
connect_group_text_required = ⚠️ 请发送一个链接或用户名的短信。

connect_group_file_invalid_links = ⚠️ 请检查文件中的链接是否有效。

connect_group_file_required = ⚠️ 请发送一个包含链接或用户名的TXT文件。

transfer_rights_prompt = 🔄 <b>将设置转移给另一个用户</b>\n\n发送你想复制你的频道和关键词的用户的Telegram ID。\n\n<i>例如：<code>1234567890</code></i>

transfer_rights_invalid_id = ⚠️ 无效的ID。ID必须只包含数字。\n\n请再试一次。

transfer_rights_self = ⚠️ 你不能将设置转移给自己。

transfer_rights_not_found = ⚠️ 用户ID<code>{ $target_user_id }</code>尚未启动这个机器人。

transfer_rights_success = ✅ <b>设置成功转移给用户 { $target_user_id }!</b>\n\n📋 添加的频道：<b>{ $groups }</b>\n🔑 添加的关键词：<b>{ $keywords }</b>

delete_group_invalid_format = ⚠️ <b>无法识别链接格式。</b>\n\n支持的格式:\n• <code>@channel_name</code>\n• <code>https://t.me/channel_name</code>\n• <code>https://t.me/+PrivateHash</code>\n• <code>https://t.me/joinchat/Hash</code>

keywords_added_success = ✅ 添加的关键词。\n\n📊 总共关键词：<b>{ $count }</b>

pt_no_slots_alert = ⚠️ 所有槽位都已使用！购买额外的槽位。

pt_ask_link = 🔗 <b>请输入群组或频道的链接</b>\n\n<i>例如：<code>https://t.me/python_jobs</code> 或 <code>@python_jobs</code></i>

pt_invalid_link = ⚠️ 请输入有效的链接（https://t.me/...）或@用户名。

pt_checking_group = 🔄 <i>正在检查群组并获取信息...</i>

pt_ask_keywords = 🔑 请输入要追踪的关键词，分隔符是逗号：

pt_saved_success = ✅ <b>追踪设置已保存!</b>

pt_step2_created =
    ✅ <b>群组创建成功!</b>

    1. 请加入创建的群组：<a href='{ $link }'>{ $link }</a>
    <i>(机器人 { $bot_name } 已经是群组的管理员)</i>

    <b>步骤 2：</b> 请输入要追踪的关键词（分隔符是逗号）：
    <i>例如：python，job，remote</i>

pt_configured_success =
    🎉 <b>个人追踪设置成功!</b>

    📌 <b>监控目标：</b> { $target }
    🔑 <b>关键词：</b> { $keywords }
    🔗 <b>结果群组：</b> <a href='{ $link }'>进入群组</a>

    <i>匹配的警报将直接发送到你创建的群组!</i>

pt_alert_message =
    🎯 <b>关键词匹配：</b> <code>{ $keyword }</code>

    💬 <b>消息文本：</b>
    { $text }

    🔗 <a href='{ $link }'>进入消息</a>

pt_no_active_trackings = ℹ️ 你尚未激活任何个人追踪。

pt_record_not_found = 错误：记录未找到

pt_edit_prompt = ⚙️ <b>编辑追踪</b>\n\n🔗 当前链接： { $link }\n🔑 关键词： { $keywords }\n\n请输入新的群组或频道链接：

pt_updating_group = 🔄 <i>正在更新订阅和群组...</i>

pt_updated_success = ✅ <b>追踪设置成功更新!</b>

pt_stats_msg = 📊 <b>个人追踪统计</b>\n\n👥 总共用户：<b>{ $users }</b>\n🎯 总共追踪：<b>{ $trackings }</b>

pt_code_prompt = 🔢 请输入5位验证码：

pt_invalid_code_alert = ❌ 无效的验证码！请再试一次。

pt_code_expired_alert = ❌ 验证码已过期！请重新申请验证码。
```

pt_login_error_alert = ❌ 登录错误： { $error }

pt_checking_2fa = 🔄 <i>正在验证 2FA 密码...</i>

pt_auth_success =
    🎉 <b>账户成功授权并连接!</b>

    👤 <b>名称：</b> { $name }
    📱 <b>电话：</b> +{ $phone }
    🆔 <b>Telegram ID：</b> <code>{ $tg_id }</code>

    ✅ 会话保存在数据库中，准备进行跟踪。

pt_auth_2fa_success =
    🎉 <b>账户成功授权使用 2FA 密码!</b>

    👤 <b>名称：</b> { $name }
    📱 <b>电话：</b> +{ $phone }
    🆔 <b>Telegram ID：</b> <code>{ $tg_id }</code>

    ✅ 会话成功保存在数据库中。

pt_auth_code_invalid_screen =
    📩 <b>已向您的 Telegram 发送验证码!</b>

    📱 <b>号码：</b> <code>{ $phone }</code>
    🔢 <b>输入的代码：</b> <code>_ _ _ _ _</code>

    ❌ <b>错误：无效代码。请再次尝试输入数字：</b>

pt_auth_2fa_prompt =
    🔐 <b>您的账户已启用双步验证（2FA）!</b>

    请在回复中输入云密码：

pt_auth_2fa_invalid =
    ❌ <b>无效的 2FA 密码!</b>

    请在回复中输入正确的云密码：

pt_auth_error = ❌ 授权错误： { $error }

pt_auth_cancelled = 🚫 授权已取消。

pt_phone_prompt = 📱 <b>连接 Telegram 账户</b>\n\n请输入国际格式的电话号码（例如，<code>+79991234567</code>）：

pt_phone_invalid = ❌ 输入的电话号码无效。请再试一次。

pt_phone_flood = ⏳ 超过尝试次数。请等待 { $seconds } 秒。

pt_code_request_error = ❌ 请求验证码错误： { $error }

pt_code_need_5_digits = ⚠️ 请输入 5 位验证码！

pt_sending_code_status = ⏳ 正在向 { $phone } 发送验证码...

pt_enter_code_keypad = 📱 <b>已向 Telegram 发送验证码</b>\n\n请输入以下键盘上的数字：

    已输入：<b>{ $code }</b>

pt_enter_2fa_prompt = 🔐 <b>双步验证（2FA）需要</b>\n\n请输入 2FA 云密码：

pt_no_account_connected = ⚠️ 未连接账户。请连接账户。

pt_record_error = 记录错误。

admin_access_denied = ⛔ 访问被拒绝。仅限管理员。

admin_broadcast_prompt = 📢 <b>向所有用户广播</b>\n\n请输入您想向所有用户广播的消息。\n\n• 支持 <b>HTML</b> 格式化（加粗，斜体，超链接）。\n• 您可以附加图片，视频，动画或文档。\n\n<i>要取消，请在下面点击“后退”</i>

admin_broadcast_preview_title = 👁️ <b>广播消息预览：</b>

admin_broadcast_preview_params = 📊 <b>广播参数：</b>\n\n👥 数据库中总受众人数：<b>{ $total }</b>\n\n确认发送或取消：

admin_broadcast_cancelled = ❌ <b>广播已取消。</b>

admin_broadcast_not_found = ⚠️ 错误：找不到广播消息。

admin_broadcast_started = 🚀 <b>广播已启动... 请稍等。</b>

admin_broadcast_progress = 🚀 <b>正在广播...</b>\n\n进度：<b>{ $current }/{ $total }</b>\n✅ 已发送：<b>{ $sent }</b>\n🚫 被用户阻止：<b>{ $blocked }</b>\n⚠️ 其他错误：<b>{ $errors }</b>

admin_broadcast_report = 🏁 <b>广播已完成!</b>\n\n📊 <b>最终报告：</b>\n• 总受众人数：<b>{ $total }</b>\n• ✅ 已成功传递：<b>{ $sent }</b>\n• 🚫 由于用户阻止：<b>{ $blocked }</b>\n• ⚠️ 其他错误：<b>{ $errors }</b>

Here is the translated content in Simplified Chinese (zh):

parser_notification_group_missing = ⚠️ <b>通知组未找到!</b>\n\n开始跟踪之前，请创建一个接收警报的目标组。\n点击下面的按钮进行设置：

parser_free_account_limit = ⚠️ <b>跟踪限制已达到!</b>\n\n您正在使用一个共享免费账户，允许跟踪仅 <b>1 个频道</b>。\n\n要跟踪更多频道:\n• 连接您的个人Telegram账户（无限制）\n• 或购买Telegram星球的额外槽位。

welcome_choose_lang = 👋 请您选择您的语言/ 选择您的语言：

no_connected_account = 未连接的账户。请连接一个账户。

excel_export_caption = 📊 Excel中组搜索结果

db_export_caption = 📊 数据库导出到Excel

found_groups_caption = 📊 找到了 <b>{ $count }</b> 个组/频道

nightly_check_btn = 每晚检查（01:00）

nightly_check_on = 开启

nightly_check_off = 关闭

nightly_check_toggled_on = 🔔 每晚自动数据库检查（01:00）已启用。

nightly_check_toggled_off = 🔕 每晚自动数据库检查已关闭。

btn_pt_accounts = 👥 我的活动/账户

btn_pt_rename_acc = ✏️ 更改标题/话题

btn_pt_tech_group = 📣 技术组

btn_pt_sync_dialogs = 📥 导入账户对话

btn_pt_toggle_all_chats = 🌐 所有账户对话： <b>{ $status }</b>

btn_pt_acc_keywords = 🔑 主题关键词

btn_pt_acc_groups = 👥 主题组

btn_pt_start_acc = ▶️ 开始这个账户

btn_pt_stop_acc = ⏹️ 停止这个账户

btn_pt_start_all = 🚀 开始所有账户

btn_pt_stop_all = 🛑 停止所有账户

pt_acc_card =
    📱 <b>活动:</b> «<b>{ $title }</b>»（<b>{ $phone }</b>）
    📡 <b>状态:</b> <b>{ $status }</b>
    📣 <b>技术组:</b> <b>{ $tech_group }</b>
    🔑 <b>关键词:</b> <b>{ $keywords_count }</b> 个。
    👥 <b>目标对话:</b> <b>{ $groups_count }</b> 个。
    🌐 <b>所有账户对话模式:</b> <b>{ $all_chats_mode }</b>

    💡 <i>在“所有账户对话”模式下，机器人跟踪所有通过tdata或手动加入的开放和关闭组。</i>

pt_ask_rename_acc = 请输入新的标题或话题（例如：<b>沙发</b>或<b>冰箱</b>）：

pt_acc_renamed = ✅ 活动标题成功更新到：<b><b>{ $title }</b></b>

pt_ask_acc_keywords =
    请输入活动“<b>{ $title }</b>”的关键词，分隔符为逗号或换行：
    <i>(例如：沙发，沙发，家具)</i>

pt_acc_keywords_saved = ✅ 活动“<b>{ $title }</b>”的关键词保存！添加了：<b>{ $count }</b> 个。

Here is the translated content in Simplified Chinese (zh):

pt_dialogs_syncing = ⏳ 通过 Telethon 扫描账号对话...

pt_dialogs_synced = ✅ 同步完成！找到并链接群组/频道： <b>{ $count }</b> 个。

pt_toggle_all_chats_done = «所有账号聊天» 模式为活动 «{ $title }»： <b>{ $status }</b>

pt_closed_group_hint =
    💡 <b>关闭群组支持：</b>
    • 发送邀请链接： <code>https://t.me/+hash</code>
    • 发送关闭聊天的数字 ID： <code>-100...</code>
    • 发送准确的关闭聊天的标题（账号已经是群组成员）
    • 或点击 <b>«📥 从 tdata 导入账号聊天»</b> 立即加载所有聊天！
