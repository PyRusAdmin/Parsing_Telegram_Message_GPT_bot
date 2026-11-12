# HI localization

welcome_ask_language = 
    🌍 हाय! कृपया अपनी इंटरफ़ेस भाषा चुनें:

welcome_message_template = 
    🤖 टेलीग्राम बॉट के लिए स्वागत है जो समूहों और चैनलों में कीवर्ड ट्रैक करने के लिए एआई समुदाय की खोज करता है!

    📋 <b>संस्करण:</b> { $version }
    📅 <b>रिलीज़ डेट:</b> 04 सितंबर 2026
    👨‍💻 <b>विकासक:</b> <a href="https://t.me/PyAdminRU">@PyAdminRU</a>
    📢 <b>मुख्य चैनल:</b> <a href="https://t.me/master_tg_d">@master_tg_d</a>

    📊 <b>उपयोगकर्ताओं द्वारा पाए गए समूहों/चैनलों की संख्या:</b> { $groups_count }

    📱 <b>कनेक्टेड अकाउंट्स:</b> { $count }
    📤 <b>तकनीकी समूह (फॉरवर्डिंग के लिए):</b> { $group_count }
    🔍 <b>ट्रैक किए गए कीवर्ड:</b> { $keywords_count }
    📡 <b>चैनलों की निगरानी के लिए जारी है:</b> { $get_groups }

    🎉 <b>मुख्य बॉट फीचर्स:</b>

    • 🌐 <b>वेब पैनल में एआई सर्च:</b> ग्रुप्स और चैनलों की एआई-ड्राइवन खोज अब वेब इंटरफ़ेस में उपलब्ध है
    • 📥 <b>डेटाबेस प्राप्त करें:</b> चैनलों और समूहों के वर्तमान डेटाबेस को डाउनलोड करें
    • 📚 <b>निर्देश:</b> बॉट का उपयोग करने के लिए विस्तृत मार्गदर्शिका
    • ⚙️ <b>सेटिंग्स:</b> खाता कनेक्शन, कीवर्ड, और फिल्टर कॉन्फ़िगर करें

    💡 <b>टिप:</b> नवीनतम फीचर्स और अपडेट प्राप्त करने के लिए, /start कमांड के साथ बॉट को फिर से शुरू करना सुझावित है

lang_selected = 
    ✅ अच्छा! अब आपकी चुनी हुई भाषा में इंटरफ़ेस दिखाई देगा।

settings_message = 
    ⚙️ इस मेनू में आप कर सकते हैं:
    • 🔗 टेलीग्राम खाता कनेक्ट करें
    • 🌐 इंटरफ़ेस भाषा बदलें
    • 📢 समूहों और चैनलों को ट्रैक करने के लिए जोड़ें
    • 🧩 कीवर्ड और फिल्टर कॉन्फ़िगर करें

    चुने गए विकल्प के नीचे 👇

connect_account = 
    📱 अपने टेलीग्राम खाता कनेक्ट करने के लिए, एक सेशन फ़ाइल को इस प्रारूप में भेजें:
    `+79599999999.session`

    एक बार फ़ाइल अपलोड होने के बाद, बॉट इस खाता का उपयोग करके मैसेज ट्रैक करेगा।

launching_tracking = 
    🚀 मैसेज ट्रैकिंग शुरू हो रही है...

    ट्रैकिंग रोकना सिर्फ़ ग्रुप्स/चैनलों के लिए सब्सक्राइब करने के बाद ही संभव है

tracking_launch_error = 
    ⚠️ चैनलों की सूची खाली है।

    कृपया कम से कम एक समूह या चैनल ट्रैक करने के लिए जोड़ें 🔍
    मेनू में सेटिंग्स ⚙️ के माध्यम से

update_list = 
    📥 एक .txt फ़ाइल भेजें जिसमें ट्रैक करने के लिए समूहों और चैनलों की सूची है:

    ✅ प्रत्येक उपयोगकर्ता का नाम को <b>@username</b> प्रारूप में होना चाहिए
    ✅ प्रत्येक लिंक को एक <b>अलग पंक्ति</b> पर होना चाहिए
    ✅ फ़ाइल को <b>.txt</b> विस्तार के साथ होना चाहिए

    📌 उदाहरण फ़ाइल का सामग्री:
    @group1
    @channel1
    @my_community

    फ़ाइल का प्रारूप महत्वपूर्ण है - बॉट केवल उन टेक्स्ट फ़ाइलों को सही ढंग से प्रोसेस करेगा जिनका सही संरचना है।

account_missing = 
    ⚠️ आपके पास कनेक्टेड टेलीग्राम खाता नहीं है।

account_missing_2 = 
    ⚠️ आपके टेलीग्राम खाता की सेशन फ़ाइल वैध नहीं है - कृपया फिर से लॉग इन करें। एक वैध सेशन फ़ाइल भेजें।

enter_keyword = 
    🔍 ट्रैक करने के लिए एक कीवर्ड/फ़्रेज़ दर्ज करें

ai_search_welcome = 
    🤖 <b>एआई सर्च मेनू में स्वागत है!</b>

    यहाँ आप एआई की शक्ति का उपयोग करके थीमेटिक समूहों और चैनलों की खोज कर सकते हैं।

    🚀 <b>उपलब्ध मोड्स:</b>
    • 🤖 <b>एआई सर्च:</b> अपने डेटाबेस और कीवर्ड के आधार पर ग्रुप्स की तेज़ खोज करें
    • 🌐 <b>ग्लोबल एआई सर्च:</b> पूरे टेलीग्राम स्पेस में नई समुदायों की खोज करें

    बस डेस्कटॉप पर चुने गए मोड को चुनें या एक अनुरोध दर्ज करें! 👇

enter_group = 
    🔍 एक लिंक दर्ज करें जो समूह के लिए है जिसे मैसेज को ट्रैक करने के लिए फॉरवर्ड किया जाएगा जब कीवर्ड डिटेक्ट होता है

admin_panel_message = 
    👋 <b>एडमिन पैनल में स्वागत है!</b>

    यहाँ आप कर सकते हैं:

    📁 <b>लॉग फ़ाइल प्राप्त करें:</b> बॉट के लिए हाल के कार्यों और त्रुटियों की लॉग देखें
    🔄 <b>डेटाबेस अपडेट करें:</b> समूहों और चैनलों के बारे में जानकारी को अद्यतन करें: उनके वर्तमान प्रकार (ग्रुप/चैनल) की जांच करें और वास्तविक आईडी प्राप्त करें
    🏷️ <b>श्रेणी आवंटित करें:</b> एआई का उपयोग करके समूहों और चैनलों को विषयों के अनुसार वर्गीकृत करें
    ✅ <b>खाता जांच करें:</b> कनेक्टेड खाताओं की स्थिति और उनकी सेशन की जांच करें
    🌐 <b>भाषा आवंटित करें:</b> समूहों और चैनलों के सामग्री की भाषा की जांच करें
    🔐 <b>खाता कनेक्ट करें:</b> एक सेशन फ़ाइल के माध्यम से टेलीग्राम खाता कनेक्ट करें

tracking_stopped = 
    ✅ ट्रैकिंग रोक दिया गया है।

instruction_caption = 
    📘 <b>उपयोग निर्देश:</b>

    एक विस्तृत मार्गदर्शिका जो बॉट की कार्यात्मकता के बारे में है जोड़ी गई है।

    🔗 <b>ऑनलाइन दस्तावेज़ीकरण:</b>
    • <a href="{ $gitverse_link }">गिटवर्स</a>
    • <a href="{ $github_link }">गिटहब</a>

    हमें नवीनतम फीचर्स और अपडेट प्राप्त करने के लिए बॉट के सभी फीचर्स का उपयोग करने के लिए इसका समीक्षा करना सुझावित है।

instruction_file_not_found = 
    ⚠️ सर्वर पर निर्देश फ़ाइल नहीं मिली।

instruction_send_error = 
    ❌ एक त्रुटि हुई जब फ़ाइल भेजने का प्रयास किया।

database_empty = 
    📭 डेटाबेस खाली है।

export_all_caption = 
    📦 टेलीग्राम समूहों और चैनलों का पूरा डेटाबेस।

    📊 कुल रिकॉर्ड्स: { $total_records }
    🧹 दोहराए गए रिकॉर्ड्स को हटाया गया: { $deleted_duplicates }

export_channels_caption = 
    📦 टेलीग्राम चैनलों का डेटाबेस।

    📊 कुल रिकॉर्ड्स: { $total_records }

export_groups_caption = 
    📦 टेलीग्राम समूहों का डेटाबेस।

    📊 कुल रिकॉर्ड्स: { $total_records }

export_error_generic = 
    ❌ एक त्रुटि हुई जब फ़ाइल बनाने का प्रयास किया।

get_database_menu = 
    👋 डेटाबेस निकासी मोड में स्वागत है!

    यहाँ आप कर सकते हैं:

    🔹 <b>📥 पूरा डेटाबेस प्राप्त करें:</b> एक्सेल फॉर्मेट में सभी सेवे किए गए समूहों और चैनलों की सूची प्राप्त करें
    🔹 <b>चैनलों का डेटाबेस प्राप्त करें:</b> एक्सेल फॉर्मेट में सभी सेवे किए गए चैनलों की सूची प्राप्त करें
    🔹 <b>ग्रुप्स का डेटाबेस प्राप्त करें (सुपरग्रुप्स):</b> एक्सेल फॉर्मेट में सभी सेवे किए गए सुपरग्रुप्स की सूची प्राप्त करें
    🔹 <b>नियमित चैट्स का डेटाबेस प्राप्त करें (पुराने शैली के समूह):</b> एक्सेल फॉर्मेट में सभी सेवे किए गए नियमित चैट्स (पुराने शैली के समूह) की सूची प्राप्त करें
    🔹 चुने गए श्रेणी के लिए एक सूची प्राप्त करें

    🔸 <b>पीछे</b> पर दबाएं तो मेनू में वापस जाएँ।

select_category_prompt = 
    📌 एक श्रेणी चुनें जिसके लिए आप एक सूची प्राप्त करना चाहते हैं:

action_cancelled = 
    ❌ रद्द किया।

invalid_category = 
    ⚠️ वैध श्रेणी नहीं है। कृपया सूची से चुनें।

category_empty = 
    📭 "{ $category }" श्रेणी में अभी तक कोई समूह नहीं है।

category_export_caption =
    ✅ { $group_count } { $group } { $category } के लिए group/channels का निर्यात किया गया है:

    "{ $category }"

searching_groups =
    🔍 group और channels की तलाश कर रहे हैं...

search_summary =
    ✅ <b>खोज पूरी हो गई!</b>

    📊 पाया और बचाया: <b>{ $groups_count }</b> group/channels
    📁 परिणाम Excel फ़ाइल में भेजे गए हैं

    📍 <b>कार्य सूचक:</b>
    🟢 <b>सक्रिय</b> — group सक्रिय है (अंतिम संदेश ≤ 30 दिन)
    🔴 <b>निष्क्रिय</b> — group निष्क्रिय है (संदेश > 30 दिन या कोई भी नहीं)
    ⚪ <b>अज्ञात</b> — टेलीग्राम सीमाओं के कारण निर्धारित नहीं किया जा सका

search_results_caption =
    📄 query के लिए खोज परिणाम: <b>{ $query }</b>

search_no_results =
    ❌ आपके query के लिए कुछ भी नहीं मिला। अन्य शब्दों की कोशिश करें।

search_error =
    ❌ खोज के दौरान एक त्रुटि हुई। फिर से प्रयास करें।

global_search_no_terms =
    ❌ कम से कम एक खोज शब्द दर्ज करें।

global_search_processing =
    🔍 { $total } queries को संसाधित कर रहे हैं...

global_search_skipped =
    ⚠️ छोड़ दिया गया: '{ $term }' (कोई उपलब्ध खाता नहीं)

global_search_progress =
    🔍 { $current }/{ $total }: { $successful } सकारात्मक परिणाम

global_search_results_caption =
    📄 { $total } group { $successful }/{ $total_queries } queries से पाया गया

global_search_no_results =
    ❌ कोई भी नहीं मिला। अन्य शब्दों की कोशिश करें।

group_added =
    ✅ group { $group } को संदेश प्रसारित करने के लिए जोड़ा गया है।

group_already_added =
    ⚠️ यह group पहले से ही जोड़ा गया है।

group_add_error =
    ⚠️ group जोड़ने में त्रुटि हुई।

delete_group_prompt =
    group/channel का उपयोगकर्ता नाम दर्ज करें @username फॉर्मेट में group को ट्रैकिंग से हटाने के लिए:

group_deleted =
    ✅ group { $group } को सफलतापूर्वक ट्रैकिंग से हटा दिया गया।

group_not_found =
    ❌ group @{ $group } आपके ट्रैकिंग सूची में नहीं पाया गया।

no_accounts =
    ❌ आपके पास कोई जुड़े खाता नहीं है।

    एक `.session` फ़ाइल भेजें या मेनू में "खाता जोड़ें" पर क्लिक करें।

no_keywords_entered =
    ⚠️ आपने कोई भी शब्द दर्ज नहीं किया।

keywords_added_count =
    शब्द जोड़े गए: { $count }

keywords_already_added =
    पहले से ही जोड़े गए ({ $count })

keywords_add_errors =
    जोड़ने में त्रुटि

keywords_and_more =
    और { $count } और

keywords_and_more_errors =
    और { $count } और त्रुटि

keywords_summary =
    सारांश

keywords_added =
    जोड़े गए

keywords_skipped =
    छोड़ दिया गया (दुहरावें)

keywords_errors = =
    त्रुटियाँ

check_group_ask_url =
    📤 समूह लिंक को प्रवेश करें जाँच के लिए:

check_group_ask_keyword =
    🔍 खोज शब्द को प्रवेश करें:

check_group_started =
    🔍 समूह जाँच शुरू हो रहा है...

check_group_new_message_with_link =
    📨 खोज शब्द के साथ नया संदेश!

    📌 <b>{ $title }</b>
    📅 तारीख: { $msg_date }
    🔗 <a href="{ $message_link }">संदेश पर जाएँ</a>

check_group_new_message_no_link =
    📨 खोज शब्द के साथ नया संदेश!

    📌 <b>{ $title }</b>
    📅 तारीख: { $msg_date }

check_group_summary =
    ✅ जाँच पूरी हो गई!

    पाया गया संदेश: { $count }
    खोज शब्द: { $keyword }
    मेल: { $matched_count }

check_group_parse_error =
    ❌ समूह को जाँच करें। कृपया लिंक और चैट एक्सेस की जाँच करें।

target_group_not_found =
    ❌ उपयोगकर्ता के लिए लक्ष्य समूह नहीं मिला।

connect_group_so_i_can_forward_messages_found_by_your_keywords =
    एक समूह जोड़ें ताकि मैं आपके खोज शब्द द्वारा पाए गए संदेश को अग्रेषित कर सकूँ।

no_channels_to_track =
    📭 आपके पास ट्रैक करने के लिए कोई चैनल नहीं है।

too_many_channels =
    ⚠️ पाया गया { $total } चैनल। सिर्फ पहले { $limit } के लिए सब्सक्राइब किया जाएगा।

channel_subscribed =
    ✅ { $channel } को सब्सक्राइब किया गया है।
    ⏳ अगली प्रयास में { $delay } सेकंड।

target_group_join_error =
    ❌ खाता लक्ष्य समूह में शामिल नहीं हो सका।

target_group_not_configured =
    ❌ उपयोगकर्ता के लिए लक्ष्य समूह नहीं मिला।

target_group_fetch_error =
    ❌ लक्ष्य समूह को प्राप्त नहीं कर सका। कृपया कनेक्शन की जाँच करें।

bot_listening =
    👂 बॉट नये संदेश के लिए सुन रहा है...

tracking_not_active =
    ⚠️ ट्रैकिंग शुरू नहीं हुआ या पहले से ही रोक दिया गया।

tracking_stop_requested =
    🛑 रोकने का आदेश दिया गया। ट्रैकिंग कुछ सेकंड में रोक दिया जाएगा।

search_client_error =
    ❌ खाता से कनेक्ट करने में त्रुटि हुई। कृपया बाद में प्रयास करें।

search_no_available_accounts =
    ⚠️ खोज के लिए कोई उपलब्ध खाता नहीं है।

session_invalid =
    ⚠️ खाता `{ $phone }` अब वैध नहीं है।
    कृपया खाता को फिर से जोड़ें।

account_fetch_error =
    ⚠️ खाता को प्राप्त करने में त्रुटि हुई। कृपया बाद में प्रयास करें।

checking_accounts_start =
    जाँच के लिए खाता की सूची: { $count }

checking_accounts_complete =
    ✅ खाता जाँच पूरी हो गई।

ai_category_select_method =
    🤖 <b>केटेगरी असाइनमेंट मेथड को चुनें:</b>

    ⚡️ <b>तेज (ग्रो क्यू एआईपी)</b>
    • मुफ्त, कोई एआईपी की आवश्यकता नहीं
    • सीक्वेंशियल प्रोसेसिंग (धीमा)
    • छोटे वॉल्यूम के लिए उपयुक्त
    • असही परिणाम दे सकता है

    🚀 <b>शक्तिशाली (ग्रो क्यू एआईपी)</b>
    • ग्रो क्यू एआईपी की आवश्यकता होगी
    • 10 थ्रेड्स में पैरेलल प्रोसेसिंग (तेज)
    • बड़े वॉल्यूम के लिए उपयुक्त
    • अधिक सटीक परिणाम

    एक मेथड को चुनें:

ai_category_back =
    ↩️ प्रबंधक पैनल में वापस जाएँ

ai_category_checking_models =
    🔍 उपलब्ध मॉडल की जाँच कर रहा है...

ai_category_model_selected =
    ✅ चुना गया मॉडल: { $model }

Here is the translated content in Hindi (hi):

ai_category_select_from_keyboard =
    कीबोर्ड के नीचे से एक तरीका चुनें:

ai_category_all_have_categories =
    ✅ सभी समूहों में श्रेणियां हैं!

ai_category_processing =
    🔄 { $total } समूहों को प्रोसेस कर रहे हैं...

ai_category_done =
    ✅ <b>कार्य पूरा!</b>

ai_category_error =
    ❌ त्रुटि: { $error }

ai_category_stats_title =
    📊 <b>श्रेणी सांख्यिकी:</b>

ai_category_no_category_count =
    🗃️ श्रेणी विहीन समूह: { $count }

ai_category_run_ai =
    '🏷️ श्रेणी आवंटित करें' पर क्लिक करें और AI शुरू करें

connect_account_ask_session =
    📤 मुझे टेलेथॉन सेशन फ़ाइल (जो `.session` से समाप्त हो) भेजें

    आप एक साथ कई फ़ाइलें भेज सकते हैं - बॉट उन्हें क्रम में प्रोसेस करेगा।
    जब कार्य पूरा हो जाए - पीछे की बटन पर क्लिक करें या /start भेजें

connect_account_invalid_file =
    ❌ यह एक सेशन फ़ाइल नहीं है! `.session` विस्तार वाली फ़ाइल भेजें

connect_account_limit_reached =
    ⚠️ सीमा प्राप्त हो गई: { $max } फ़ाइलें एक साथ।
    वर्तमान फ़ाइलों को प्रोसेस करें और बाकी को बाद में भेजें

connect_account_file_queued =
    📥 फ़ाइल स्वीकृत: `{ $filename }`
    📊 क्वॉइंग में: { $total } फ़ाइलें (s)। प्रोसेस कर रहे हैं...

connect_account_success =
    ✅ <b>{ $filename }</b> - सफल!
    📱 { $phone } | 👤 { $name }

connect_free_account_success =
    ✅ <b>{ $filename }</b> - मुफ्त खाता पूल में जोड़ा गया!
    📱 { $phone } | 👤 { $name } | 🆔 <code>{ $account_id }</code>

connect_account_failed =
    ❌ <b>{ $filename }</b> - सत्यापन में असफल

connect_account_error =
    ⚠️ <b>{ $filename }</b> - प्रोसेसिंग में त्रुटि

connect_account_processing_done =
    📊 <b>प्रोसेसिंग पूरा हो गया!</b>

lang_detect_no_groups =
    ❌ कोई समूह प्रोसेस करने के लिए नहीं हैं

lang_detect_starting =
    🚀 { $total } समूहों को प्रोसेस करने के लिए शुरू हो रहे हैं...

lang_detect_error =
    ❌ त्रुटि: { $error }

lang_detect_saving =
    💾 { $count } परिणामों को डीबी में सेव कर रहे हैं...

lang_detect_complete =
    ✅ प्रोसेसिंग पूरा हो गया!

    📊 सांख्यिकी:
    • कुल: { $total }
    • AI द्वारा पता लगाया गया: { $ai_success }
    • डीबी में सेव किया गया: { $db_success }
    • AI त्रुटियां: { $ai_fail }
    • डीबी त्रुटियां: { $db_fail }
    • कुल त्रुटियां: { $total_fail }

lang_detect_stats_title = सांख्यिकी

lang_detect_stats_total = कुल

lang_detect_stats_ai_success = AI द्वारा पता लगाया गया

lang_detect_stats_db_success = डीबी में सेव किया

lang_detect_stats_ai_fail = AI त्रुटियां

lang_detect_stats_db_fail = डीबी त्रुटियां

lang_detect_stats_total_fail = कुल त्रुटियाँ

log_file_caption =
    📄 त्रुटियों के साथ लॉग फ़ाइल।

account_connect_personal =
    🔐 <b>टेलीग्राम खाता प्रबंधन</b>

    📱 <b>वर्तमान खाता:</b> ✅ <i>व्यक्तिगत खाता</i>
    📊 <b>प्रारूप:</b> सीमित चैनल (अपने स्लॉट में)

    आप दूसरे तरीके से जुड़ने या इसे अलग करने के लिए क्लिक कर सकते हैं।

account_connect_shared =
    🔐 <b>टेलीग्राम खाता प्रबंधन</b>

    🎁 <b>वर्तमान खाता:</b> <i>प्रशासक का मुफ्त खाता</i>
    ⚠️ <b>प्रतिबंध:</b> केवल <b>1 ग्रुप</b> में कीवर्ड ट्रैकिंग की अनुमति है।

    🔄 <i>वर्तमान खाता में कोई समस्या होने पर नीचे "मुफ्त खाता" को रिकनेक्ट करें।</i>
    💡 <i>अधिक ग्रुप्स को एक साथ ट्रैक करने के लिए, अपने व्यक्तिगत खाता को जोड़ें।</i>

free_account_connected_success =
    🎉 <b>मुफ्त प्रशासक खाता सफलतापूर्वक जुड़ा है!</b>

    📱 <b>खाता:</b> { $phone }
    👤 <b>नाम:</b> { $name }
    ⚠️ <b>ध्यान दें:</b> इस मुफ्त खाता पर 1 ग्रुप/चैनल की सीमा लागू है।

    💡 <i>अगर आपको अधिक चैनलों की आवश्यकता है, तो आप अपने व्यक्तिगत खाता को कभी भी जोड़ सकते हैं।</i>

free_account_reconnected_success =
    🎉 <b>मुफ्त खाता सफलतापूर्वक फिर से जुड़ा है!</b>

    📱 <b>नया खाता:</b> { $phone }
    👤 <b>नाम:</b> { $name }
    ✅ <b>स्थिति:</b> सक्रिय और ट्रैकिंग के लिए तैयार।

    ⚠️ <b>ध्यान दें:</b> इस मुफ्त खाता पर 1 ग्रुप की सीमा लागू है।

account_connect_none =
    🔐 <b>टेलीग्राम खाता प्रबंधन</b>

    ⚠️ <b>वर्तमान खाता:</b> <i>नहीं जुड़ा</i>

    संदेशों और कीवर्ड को ट्रैक करने के लिए एक कनेक्शन विधि चुनें:
    • <b>व्यक्तिगत खाता</b> — कोई चैनल सीमा नहीं।
    • <b>प्रशासक का मुफ्त खाता</b> — मुफ्त पहुंच, केवल 1 ग्रुप तक सीमित।

account_connected_free =
    ✅ खाता सफलतापूर्वक जुड़ा

no_free_accounts =
    ❌ प्रशासक द्वारा कोई मुफ्त खाता उपलब्ध नहीं है। कृपया बाद में फिर से प्रयास करें या प्रशासक से संपर्क करें।

no_free_accounts_detailed =
    ⚠️ <b>कोई मुफ्त खाता उपलब्ध नहीं है</b>

    वर्तमान में प्रशासक से कोई मुफ्त खाता उपलब्ध नहीं है।
    कृपया अपने व्यक्तिगत खाता (फ़ोन या सेशन फ़ाइल के माध्यम से) जोड़ें।

invalid_session_file =
    ❌ यह एक सेशन फ़ाइल नहीं है! .session विस्तार के साथ एक फ़ाइल भेजें

session_file_received =
    📥 फ़ाइल प्राप्त: `{ $filename }`

    🔍 खाता की जांच कर रहे हैं...

session_connected_success =
    ✅ <b>{ $filename }</b> — सफलतापूर्वक!
    📱 { $phone } | 👤 { $name }
    💾 अपने व्यक्तिगत डेटाबेस में सेवा किया गया।

session_validation_failed =
    ❌ <b>{ $filename }</b> — सत्यापन विफल।
    कृपया यह सुनिश्चित करें कि सेशन फ़ाइल वर्तमान है और कहीं और उपयोग नहीं की जा रही है।

session_check_error =
    ⚠️ सत्यापन के दौरान एक त्रुटि हुई। कृपया बाद में फिर से प्रयास करें।

only_txt_files_supported =
    ⚠️ केवल .txt फ़ाइलें समर्थित हैं।

empty_file_no_usernames =
    ⚠️ फ़ाइल खाली है या कोई उपयोगकर्ता नाम नहीं है।

groups_upload_summary =
    ✅ जोड़ा गया: { $added }
    ⚠️ पहले से मौजूद: { $skipped }
    ❌ त्रुटियाँ: { $errors }

admin_found_accounts =
    🔍 खोजे गए खाता: { $count }

admin_db_actualization_start =
    🔄 { $total } ग्रुपों की वास्तविक कार्यशीलता शुरू करें...

admin_using_account =
    📱 खाता का उपयोग कर रहा हूँ: { $account }

admin_account_error =
    ❌ खाता त्रुटि { $account }: { $error }

admin_critical_error =
    ❌ महत्वपूर्ण त्रुटि: { $error }

no_questions_in_db =
    📭 डेटाबेस में कोई प्रश्न नहीं है।

questions_export_caption =
    📦 प्रश्नों और उत्तरों का निर्यात।

export_error =
    ❌ निर्यात के दौरान एक त्रुटि हुई: { $error }

launch_tracking_button = 🚀 ट्रैकिंग शुरू करें

check_group_for_keywords_button = 🔍 ग्रुप के लिए कीवर्ड जांच करें

ai_search_button = ✨ AI Search

get_database_button = 📥 डेटाबेस प्राप्त कर

instruction_button = 📖 निर्देश

settings_button = ⚙️ सेटिंग्स

admin_panel_button = 🛡️ प्रशासक पैनल

get_log_file_button = 📄 लॉग फ़ाइल प्राप्त कर

export_questions_button = प्रश्न निर्यात कर

assign_category_button = 🏷️ श्रेणी आवंटित कर

check_accounts_button = ✅ खातों की जांच कर

connect_account_button = 🔐 खाता जोड़

back_button = ⬅️ पीछे

fast_method_button = ⚡️ तेज़ (g4f.free)

powerful_method_openrouter_button = 🚀 शक्तिशाली (Openrouter API)

powerful_method_groq_button = 🚀 शक्तिशाली (GROQ API)

all_database_button = 📥 सभी डेटाबेस

channels_database_button = 📥 चैनल डेटाबेस

groups_database_button = 📥 समूह डेटाबेस

select_category_button = 📂 श्रेणी चुन

investments_button = निवेश

finance_and_personal_budget_button = वित्त और व्यक्तिगत बजट

crypto_and_blockchain_button = क्रिप्टो और ब्लॉकचेन

business_and_entrepreneurship_button = व्यवसाय और उद्यमिता

marketing_and_promotion_button = विज्ञापन और प्रचार

tech_and_it_button = प्रौद्योगिकी और आईटी

education_and_self_development_button = शिक्षा और आत्म-विकास

work_and_career_button = काम और करियर

real_estate_button = वास्तविक संपत्ति

health_and_medicine_button = स्वास्थ्य और चिकित्सा

travel_button = यात्रा

auto_and_transport_button = ऑटो और परिवहन

shopping_and_discounts_button = शॉपिंग और छूट

entertainment_and_leisure_button = मनोरंजन और स्वतंत्रता

politics_and_society_button = राजनीति और समाज

science_and_research_button = विज्ञान और अनुसंधान

sports_and_fitness_button = खेल और फिटनेस

cooking_and_food_button = पकाना और भोजन

fashion_and_beauty_button = फैशन और सौंदर्य

hobbies_and_creativity_button = शौक और रचनात्मकता

russian_language_button = 🇷🇺 रूसी भाषा

english_language_button = 🇬🇧 अंग्रेजी भाषा

stop_tracking_button = 🛑 ट्रैकिंग रोकना

update_list_button = 🔁 लिस्ट अपडेट

enter_keyword_button = 🔍 कुंजी दर्ज करें

delete_group_from_tracking_button = 🗑️ ट्रैकिंग से ग्रुप हटाएं

keywords_list_button = 🔍 कुंजी लिस्ट

tracking_links_button = 🌐 ट्रैकिंग लिंक्स

connect_group_for_messages_button = 📤 मैसेजेस के लिए ग्रुप जोड़ें

change_language_button = 🌐 भाषा बदलें

connect_free_account_button = 🔐 मुफ्त खाता जोड़ें

keywords_export_caption = 📋 कुंजी निर्यात. कुल रिकॉर्ड: { $count }

no_keywords_found = 📭 आपके पास कोई सेव की गई कुंजी नहीं है।

tracking_links_export_caption = 🔗 ट्रैकिंग लिंक्स निर्यात. कुल रिकॉर्ड: { $count }

no_tracking_links_found = 📭 आपके पास कोई ट्रैकिंग लिंक्स नहीं है।

excel_header_number =

excel_header_keyword = कुंजी

excel_header_username = चैनल/ग्रुप यूजरनेम

ai_search_button_user = 🤖 AI Search

excel_filename_all_db = सभी डेटाबेस .xlsx

excel_filename_channels_db = चैनल्स डेटाबेस .xlsx

excel_filename_groups_db = ग्रुप्स डेटाबेस .xlsx

excel_sheet_name_search_results = खोज परिणाम

excel_header_id = आईडी (हैश)

excel_header_name = नाम

excel_header_description = विवरण

excel_header_participants = भाग लेने वाले

excel_header_category = श्रेणी

excel_header_type = प्रकार

excel_header_language = भाषा

excel_header_activity = गतिविधि

excel_header_link = लिंक

excel_header_date_added = जोड़ा गया तिथि

excel_sheet_name_groups = ग्रुप्स

excel_filename_groups_by_category = ग्रुप्स_{ $category }.xlsx

excel_header_group_name = नाम

excel_header_group_description = विवरण

excel_header_group_type = प्रकार

excel_header_group_participants = भाग लेने वाले

excel_header_group_link = लिंक

excel_filename_telegram_groups = टेलीग्राम ग्रुप्स_{ $timestamp }.xlsx

instruction_question_prompt = 🤖 <b>आप मुझसे किसी भी बॉट का उपयोग करने के बारे में प्रश्न पूछ सकते हैं और मैं आपको जवाब दूंगा!</b>

ai_support_assistant_system_prompt = आप एक योग्य सहायता सहायक हैं AutoParseAlertBot टेलीग्राम बॉट के लिए। आपका कार्य उपयोगकर्ता प्रश्नों का उत्तर देना है जो सख्ती से प्रदान किए गए ज्ञान आधार पर है। यदि उत्तर ज्ञान आधार में नहीं है, तो उपयोगकर्ता को सूचित करें कि आप इस जानकारी के बारे में नहीं जानते हैं और उन्हें समर्थन से संपर्क करने की सलाह दें। उपयोगकर्ता की भाषा में स्पष्ट पढ़ने योग्य पाठ में उत्तर दें, कोई भी मार्कअप फ़ॉर्मेटिंग का उपयोग न करें (मार्कडाउन के कोई भी चिह्न ना)

lang_detect_summary = ✅ प्रोसेसिंग पूरा हुआ!

    📊 सांख्यिकी:
    • कुल: { $total }
    • AI द्वारा पता लगाया गया: { $ai_success }
    • DB में सेवा की गई: { $db_success }
    • AI के त्रुटियाँ: { $ai_fail }
    • DB के त्रुटियाँ: { $db_fail }
    • कुल त्रुटियाँ: { $total_fail }

name_prompt = नाम

description_prompt = विवरण

Here is the translated content in Hindi (hi):

CRITICAL REQUIREMENTS:
1. Keep ALL keys on the left side of '=' EXACTLY as they are. Never translate key names.
2. Keep ALL variables in braces like { $version }, { $count }, { $title }, etc. EXACTLY as they are.
3. Keep ALL HTML tags intact.
4. Keep the Fluent multiline indentation format.
5. Return ONLY the translated .ftl content. DO NOT include markdown code fences (no ``` or ```ftl), no explanations.

Content to translate:

no_data_prompt = कोई डेटा नहीं

ai_lang_detect_prompt =
    प्रमुख भाषा का निर्धारण करें या समुदाय विवरण का।
    एकल शब्द में जवाब दें - आईएसओ 639-1 फ़ॉर्मेट में भाषा कोड (दो-अक्षर कोड)।
    उदाहरण: रु, एएन, एस, जीएच, आर, एचआर, जीए, को, एफआर, डी, पीटी, आईटी, एनएल, एसवी, पीएल, टीआर, वीआई, थ, आईडी, एफए, ही, यूके, सीएस, एल, आरओ, ह्यू, फीआई, डीएन, एसके, बीजी, एचआर, एसआर, एसएल, एट, एलवी, एलटी, एमके, एसक्यू, एमटी, ईयू, जीएल, गीए, आईएस, एमएस, स्व, टीएल, उर, बीएन, टीए, टी, एमआर, गू, केएन, एमएल, सी, लो, माय, अम, ह्यू, का।

    यदि भाषा का निर्धारण अस्पष्ट हो या पाठ में एकाधिक भाषाओं का मिश्रण हो जिसमें एक प्रमुख भाषा न हो - अज्ञात।
    कोई व्याख्या, पूर्णता, स्थान, या अतिरिक्त पाठ नहीं।
    
    विश्लेषण के लिए पाठ:
    { $user_input }

get_groups_without_category_message = 📊 <b>श्रेणी की सांख्यिकी:</b>

    🗃️ श्रेणी के बिना समूह: { $count }

    '🏷️ श्रेणी आवंटित करें' पर क्लिक करें तो AI शुरू करें

download_free_success = 📥 डेटाबेस का निर्यात (प्रति दिन एक मुफ्त डाउनलोड)। डाउनलोड शुरू हो रहा है...

download_cooldown_message =
    ⚠️ आपने पिछले 24 घंटों में डेटाबेस डाउनलोड किया है।
    अगला मुफ्त डाउनलोड <b>{ $time }</b> में उपलब्ध होगा।
    
    आप डेटाबेस को अब 5 ⭐ के लिए डाउनलोड कर सकते हैं।
    बॉट में आपके स्टार्स की संख्या: <b>{ $stars }</b> ⭐

pay_from_balance_btn = 🪙 5 ⭐ से बैलेंस का उपयोग करें

pay_direct_btn = ⭐ सीधे 5 ⭐ का भुगतान करें

cancel_btn = ❌ रद्द करें

download_paid_success = ✅ भुगतान/शर्तों का भुगतान सफल हुआ। डेटाबेस डाउनलोड शुरू हो रहा है...

download_insufficient_stars = ❌ आपके बैलेंस में पर्याप्त स्टार्स नहीं हैं।

stars_topup_success = 🎉 आपके बैलेंस को सफलतापूर्वक { $amount } ⭐ से भरा गया है! वर्तमान बैलेंस: { $balance } ⭐।

stars_added_admin = ⭐ प्रशासक ने आपको { $amount } ⭐ दिया है। वर्तमान बैलेंस: { $balance } ⭐।

topup_stars_button = 💳 स्टार्स को भरें

stars_balance_msg = 👤 <b>स्टार प्रोफाइल:</b>\n\nबैलेंस: <b>{ $stars }</b> ⭐\n\nयहाँ आप अपने टेलीग्राम स्टार्स को भर सकते हैं जो भुगतान के लिए भुगतान किया जाता है।

stars_invoice_title = स्टार बैलेंस को भरने के लिए खर्च

stars_invoice_desc = { $amount } टेलीग्राम स्टार्स का खर्च जो बॉट में उपयोग किया जाता है

stars_invoice_dl_title = डेटाबेस डाउनलोड

stars_invoice_dl_desc = एक बार के लिए डेटाबेस डाउनलोड को निर्धारित करने के लिए दैनिक सीमा को पार करें

excel_filename_category_db = श्रेणी डेटाबेस.xlsx

export_category_caption = 📂 श्रेणी "{ $category }" का डेटाबेस। कुल रिकॉर्ड: { $total_records }।

generating_database_wait = ⏳ डेटाबेस फ़ाइल का निर्माण हो रहा है। कृपया इंतजार करें...

btn_add_channels_tracking = ➕ ट्रैकिंग के लिए चैनल जोड़

btn_channels_list = 📋 चैनलों की सूची

btn_export_excel = 📥 एक्सेल में निर्यात करें

btn_clear_all_channels = 🧹 सभी चैनलों को साफ करें

btn_tracking_channels = 🌐 ट्रैकिंग चैनल

btn_keywords = 🔍 कीवर्ड

btn_notification_group = 📢 सूचना समूह

btn_transfer_settings = 🔄 उपयोगकर्ता के लिए स्थिति स्थानांतरण

btn_personal_tracking = 🎯 ट्रैकिंग

btn_connect_account_session = 📄 सत्र (.session) के माध्यम से खाता जोड़

btn_connect_account_phone = 📱 फ़ोन द्वारा व्यक्तिगत खाता जोड़

btn_connect_free_account = 🎁 प्रशासक का मुफ्त खाता (1 समूह)

btn_reconnect_free_account = 🔄 मुफ्त खाता को पुनः संयोजित करें

btn_disconnect_account = ❌ वर्तमान खाता से विभाजित करें

btn_to_tracking_menu = 🎯 ट्रैकिंग मेनू में जाएँ

btn_to_settings_menu = ⚙️ सेटिंग्स मेनू में जाएँ

btn_main_menu = 🏠 मुख्य मेनू

btn_add_keywords = ➕ शब्दसूची जोड़

btn_keywords_list = 📋 शब्दसूची सूची

btn_export_keywords = 📥 शब्दसूची निर्यात करें

btn_goto_notification_group = 🔗 सूचना समूह खोलें

btn_notification_group_not_created = 🔗 समूह अभी तक बनाया नहीं गया

btn_recreate_notification_group = 🔄 समूह को पुनः स्थापित करें

btn_nav_prev = ◀️ पिछला

btn_nav_next = ▶️ अगला

btn_confirm_clear = ✅ हाँ, साफ़ करें

btn_cancel = ❌ रद्द करें

btn_broadcast_users = 📢 उपयोगकर्ताओं को प्रसारित करें

btn_broadcast_send = 🚀 प्रसारित करें

btn_broadcast_cancel = ❌ प्रसारित करना रद्द करें

btn_pt_add_tracking = ➕ ट्रैकिंग जोड़

btn_pt_buy_slot = ⭐ 2 सितारे के साथ +1 स्लॉट खरीदें

btn_pt_my_groups = 📋 मेरे ट्रैकिंग किए गए समूह

btn_pt_stats = 📊 आंकड़े

btn_keypad_clear = ❌ साफ़ करें

btn_keypad_submit = ✅ प्रस्तुत करें

btn_keypad_cancel = 🚫 रद्द करें

btn_pt_edit_record = ⚙️ रिकॉर्ड संपादित करें

btn_pt_buy_stars_slots = ⭐ स्टार्स स्लॉट खरीदें (टेलीग्राम स्टार्स)

btn_pt_connect_personal = 📱 व्यक्तिगत खाता जुड़ें

btn_pt_create_notification_group = 📢 सूचना समूह बनाएं

settings_channels_title = 🌐 <b>निगरनी किए गए चैनल</b>\n\n📊 कुल चैनल: <b>{ $total }</b>\n\nएक कार्य चुनें:

settings_channels_empty = 📭 चैनलों की सूची खाली है।

settings_channels_list_title = 📋 <b>चैनलों की सूची</b> (पृष्ठ { $page }/{ $total_pages }) · कुल: { $total }\n

settings_channels_list_hint = \n<i>एक चैनल को हटाने के लिए ❌ पर क्लिक करें।</i>

settings_channel_deleted = ✅ चैनल हटाया गया: { $channel }

settings_channel_not_found = ⚠️ चैनल नहीं मिला।

settings_channels_clear_confirm = 🧹 <b>पूरे चैनलों की सूची को साफ़ करें?</b>\n\n<ब>{ $total }</b> चैनल हटाए जाएंगे। यह कार्य पूर्ववत नहीं किया जा सकता है।

settings_channels_cleared = ✅ <b>चैनलों की सूची साफ़ की गई</b>\n\nहटाए गए चैनल: <b>{ $count }</b>

settings_keywords_title = 🔍 <b>कीवर्ड्स</b>\n\n📊 कुल कीवर्ड्स: <b>{ $total }</b>\n\nएक कार्य चुनें:

settings_keywords_empty = 📭 कीवर्ड्स की सूची खाली है।

settings_keywords_list_title = 🔍 <b>कीवर्ड्स</b> (पृष्ठ { $page }/{ $total_pages }) · कुल: { $total }\n

settings_keywords_list_hint = \n<i>एक शब्द को हटाने के लिए ❌ पर क्लिक करें।</i>

settings_keyword_deleted = ✅ हटाया गया: { $keyword }

settings_keyword_not_found = ⚠️ शब्द नहीं मिला।

settings_notification_created = 📢 <b>सूचना समूह</b>\n\n✅ समूह बनाया गया।\n\n🔗 <a href='{ $link }'>समूह पर जाएं</a>

settings_notification_not_created = 📢 <b>सूचना समूह</b>\n\n❌ समूह बनाया नहीं गया है।\n\n<i>«🎯 व्यक्तिगत ट्रैकिंग» से एक समूह बनाएं।</i>

settings_notification_alert_no_group = ❌ समूह बनाया नहीं गया है। «🎯 व्यक्तिगत ट्रैकिंग» में एक समूह बनाएं।

settings_notification_recreate_text = 🔄 <b>सूचना समूह को पुनः स्थापित करें</b>\n\nसमूह को पुनः स्थापित करने के लिए «🎯 व्यक्तिगत ट्रैकिंग» → «➕ समूह ट्रैकिंग जोड़ें» में जाएं।\n\n<i>एक नया समूह स्वचालित रूप से जोड़े जाएंगे जब ट्रैकिंग जोड़ेंगे।</i>

connect_group_prompt = 🔗 <b>एक लिंक या उपयोगकर्ता का नाम भेजें</b>\n\nउदाहरण के लिए:\n<code>https://t.me/python_jobs</code>\nया <code>@python_jobs</code>\n\nएक लिंक को एक पंक्ति में भेजें।

connect_group_no_links = ⚠️ कृपया कम से कम एक लिंक या उपयोगकर्ता का नाम भेजें।

connect_group_invalid_links = ⚠️ कृपया लिंकों की जांच करें कि वे सही हैं।

connect_group_saved = ✅ समूह को डेटाबेस में सुरक्षित किया गया है।

Here is the translated content in Hindi (hi):

connect_group_text_required = ⚠️ कृपया एक टेक्स्ट मैसेज के रूप में लिंक या यूजरनेम भेजें।

connect_group_file_invalid_links = ⚠️ कृपया फ़ाइल में दिए गए लिंक की जाँच करें।

connect_group_file_required = ⚠️ कृपया एक टेक्स्ट फ़ाइल भेजें जिसमें लिंक या यूजरनेम हों।

transfer_rights_prompt = 🔄 <b>अन्य उपयोगकर्ता को सेटिंग्स ट्रांसफर करें</b>\n\nकृपया जिस उपयोगकर्ता के टेलीग्राम आईडी को आप अपने चैनल और कीवर्ड्स को कॉपी करना चाहते हैं, उनका टेलीग्राम आईडी भेजें।\n\n<i>उदाहरण: <code>1234567890</code></i>

transfer_rights_invalid_id = ⚠️ अवैध आईडी। आईडी में केवल अंक ही होने चाहिए।\n\nपुनः सेटिंग्स मेनू से प्रयास करें।

transfer_rights_self = ⚠️ आप खुद को सेटिंग्स ट्रांसफर नहीं कर सकते।

transfer_rights_not_found = ⚠️ उपयोगकर्ता आईडी <code>{ $target_user_id }</code> ने अभी तक इस बॉट को शुरू नहीं किया है।

transfer_rights_success = ✅ <b>सेटिंग्स उपयोगकर्ता { $target_user_id } को सफलतापूर्वक ट्रांसफर किया गया!</b>\n\n📋 चैनल जोड़े गए: <b>{ $groups }</b>\n🔑 कीवर्ड जोड़े गए: <b>{ $keywords }</b>

delete_group_invalid_format = ⚠️ <b>लिंक फ़ॉर्मेट को पहचान नहीं सका।</b>\n\nसही फ़ॉर्मेट:\n• <code>@channel_name</code>\n• <code>https://t.me/channel_name</code>\n• <code>https://t.me/+PrivateHash</code>\n• <code>https://t.me/joinchat/Hash</code>

keywords_added_success = ✅ कीवर्ड जोड़े गए।\n\n📊 कुल कीवर्ड: <b>{ $count }</b>

pt_no_slots_alert = ⚠️ सभी स्लॉट का उपयोग किया जा रहा है! एक अतिरिक्त स्लॉट खरीदें।

pt_ask_link = 🔗 <b>ग्रुप या चैनल के लिंक को ट्रैक करने के लिए पूछें</b>\n\n<i>उदाहरण: <code>https://t.me/python_jobs</code> या <code>@python_jobs</code></i>

pt_invalid_link = ⚠️ कृपया एक वैध लिंक (https://t.me/...) या @यूजरनेम को प्रवेश करें।

pt_checking_group = 🔄 <i>ग्रुप की जाँच कर रहा हूँ और जानकारी प्राप्त कर रहा हूँ...</i>

pt_ask_keywords = 🔑 कृपया ट्रैक करने के लिए कीवर्ड दर्ज करें जो विभाजित हैं:

pt_saved_success = ✅ <b>ट्रैकिंग सेटिंग्स सफलतापूर्वक बचाए गए!</b>

pt_step2_created =
    ✅ <b>ग्रुप बनाया गया!</b>

    1. लिंक पर क्लिक करें और बनाए गए ग्रुप में शामिल हों: <a href='{ $link }'>{ $link }</a>
    <i>(बॉट { $bot_name } पहले से ही ग्रुप का प्रशासक है)</i>

    <b>चरण 2:</b> ट्रैक करने के लिए कीवर्ड दर्ज करें जो विभाजित हैं:
    <i>उदाहरण: python, job, remote</i>

pt_configured_success =
    🎉 <b>व्यक्तिगत ट्रैकिंग को सफलतापूर्वक निर्धारित किया गया!</b>

    📌 <b>निर्धारित लक्ष्य:</b> { $target }
    🔑 <b>कीवर्ड:</b> { $keywords }
    🔗 <b>परिणामों के लिए ग्रुप:</b> <a href='{ $link }'>ग्रुप में जाएँ</a>

    <i>संगति के बारे में मेल की सूचनाएँ सीधे आपके बनाए गए ग्रुप में भेजी जाएँगी!</i>

pt_alert_message =
    🎯 <b>कीवर्ड की संगति:</b> <code>{ $keyword }</code>

    💬 <b>संदेश का पाठ:</b>
    { $text }

    🔗 <a href='{ $link }'>ग्रुप में जाएँ</a>

pt_no_active_trackings = ℹ️ आप अभी तक कोई सक्रिय व्यक्तिगत ट्रैकिंग नहीं हैं।

pt_record_not_found = त्रुटि: रिकॉर्ड नहीं मिला।

pt_edit_prompt = ⚙️ <b>ट्रैकिंग को संपादित करें</b>\n\n🔗 वर्तमान लिंक: { $link }\n🔑 कीवर्ड: { $keywords }\n\nकृपया एक नया ग्रुप/चैनल लिंक भेजें:

pt_updating_group = 🔄 <i>सब्सक्रिप्शन और ग्रुप को अपडेट कर रहा हूँ...</i>

pt_updated_success = ✅ <b>ट्रैकिंग सेटिंग्स सफलतापूर्वक अपडेट किया गया!</b>

pt_stats_msg = 📊 <b>व्यक्तिगत ट्रैकिंग की सांख्यिकी</b>\n\n👥 कुल उपयोगकर्ता: <b>{ $users }</b>\n🎯 कुल ट्रैकिंग: <b>{ $trackings }</b>

pt_code_prompt = 🔢 5-डिजिट वेरिफिकेशन कोड दर्ज करें:

pt_invalid_code_alert = ❌ अवैध वेरिफिकेशन कोड! पुनः प्रयास करें।

pt_code_expired_alert = ❌ वेरिफिकेशन कोड समाप्त हो गया है! कोड को फिर से माँगें।

Here is the translated content in Hindi (hi):

pt_login_error_alert = ❌ लॉगिन त्रुटि: { $error }

pt_checking_2fa = 🔄 <i>2FA पासवर्ड की पुष्टि कर रहे हैं...</i>

pt_auth_success =
    🎉 <b>लेखा सफलतापूर्वक प्राधिकृत और जोड़ा गया है!</b>

    👤 <b>नाम:</b> { $name }
    📱 <b>फोन:</b> +{ $phone }
    🆔 <b>टेलीग्राम आईडी:</b> <code>{ $tg_id }</code>

    ✅ डेटाबेस में सेशन सहेजा गया और ट्रैकिंग के लिए तैयार है।

pt_auth_2fa_success =
    🎉 <b>लेखा सफलतापूर्वक प्राधिकृत 2FA पासवर्ड के साथ!</b>

    👤 <b>नाम:</b> { $name }
    📱 <b>फोन:</b> +{ $phone }
    🆔 <b>टेलीग्राम आईडी:</b> <code>{ $tg_id }</code>

    ✅ डेटाबेस में सेशन सफलतापूर्वक सहेजा गया।

pt_auth_code_invalid_screen =
    📩 <b>आपके टेलीग्राम में सत्यापन कोड भेजा गया है!</b>

    📱 <b>नंबर:</b> <code>{ $phone }</code>
    🔢 <b>प्रवेश कोड:</b> <code>_ _ _ _ _</code>

    ❌ <b>त्रुटि: अवैध कोड। फिर से डिजिट्स चुनने के लिए कृपया प्रयास करें:</b>

pt_auth_2fa_prompt =
    🔐 <b>आपके खाते पर दो-चरण सत्यापन (2FA) सक्रिय है!</b>

    कृपया अपने क्लाउड पासवर्ड को टेक्स्ट में प्रवेश करें:

pt_auth_2fa_invalid =
    ❌ <b>अवैध 2FA पासवर्ड!</b>

    कृपया सही क्लाउड पासवर्ड को टेक्स्ट में प्रवेश करें:

pt_auth_error = ❌ प्राधिकरण त्रुटि: { $error }

pt_auth_cancelled = 🚫 प्राधिकरण रद्द किया गया।

pt_phone_prompt = 📱 <b>टेलीग्राम खाता जोड़ें</b>\n\nअंतरराष्ट्रीय स्वरूप में अपना फोन नंबर दर्ज करें (उदाहरण के लिए, <code>+79991234567</code>):

pt_phone_invalid = ❌ अवैध फोन नंबर दर्ज किया गया। फिर से प्रयास करें।

pt_phone_flood = ⏳ बहुत सारे प्रयास। कृपया { $seconds } सेकंड के लिए इंतजार करें।

pt_code_request_error = ❌ कोड की मांग में त्रुटि: { $error }

pt_code_need_5_digits = ⚠️ सत्यापन कोड के सभी 5 डिजिट दर्ज करें!

pt_sending_code_status = ⏳ सत्यापन कोड { $phone } को भेज रहा है...

pt_enter_code_keypad = 📱 <b>सत्यापन कोड टेलीग्राम में भेजा गया है</b>\n\nकीपैड के नीचे डिजिट्स दर्ज करें:\n\nप्रवेश किया गया: <b>{ $code }</b>

pt_enter_2fa_prompt = 🔐 <b>दो-चरण सत्यापन (2FA) आवश्यक</b>\n\nकृपया अपने 2FA क्लाउड पासवर्ड को दर्ज करें:

pt_no_account_connected = ⚠️ कोई जुड़ा हुआ खाता नहीं है। कृपया एक खाता जोड़ें।

pt_record_error = रिकॉर्ड त्रुटि।

admin_access_denied = ⛔ प्रशासकों के लिए एक्सेस अस्वीकार किया गया।

admin_broadcast_prompt = 📢 <b>उपभोक्ताओं को प्रसारित करें</b>\n\nआप जो संदेश प्रसारित करना चाहते हैं उसे प्रसारित करें।\n\n• <b>HTML</b> स्वरूपण का समर्थन करता है (बोल्ड, इटैलिक, लिंक)।\n• आप फोटो, वीडियो, एनिमेशन, या दस्तावेज़ को जोड़ सकते हैं।\n\n<i>रद्द करने के लिए नीचे के «पीछे» पर क्लिक करें।</i>

admin_broadcast_preview_title = 👁️ <b>प्रसारित संदेश का पूर्वावलोकन:</b>

admin_broadcast_preview_params = 📊 <b>प्रसारित पैरामीटर:</b>\n\n👥 डेटाबेस में पूरे प्राप्तकर्ताओं की संख्या: <b>{ $total }</b>\n\nप्रसारित करने या रद्द करने के लिए पुष्टि करें:

admin_broadcast_cancelled = ❌ <b>प्रसारित रद्द किया गया है।</b>

admin_broadcast_not_found = ⚠️ त्रुटि: प्रसारित संदेश नहीं पाया।

admin_broadcast_started = 🚀 <b>प्रसारित शुरू किया गया... कृपया इंतजार करें।</b>

admin_broadcast_progress = 🚀 <b>प्रसारित कर रहा है...</b>\n\nप्रगति: <b>{ $current }/{ $total }</b>\n✅ भेजा गया: <b>{ $sent }</b>\n🚫 ब्लॉक किया गया: <b>{ $blocked }</b>\n⚠️ अन्य त्रुटियां: <b>{ $errors }</b>

admin_broadcast_report = 🏁 <b>प्रसारित समाप्त हुआ!</b>\n\n📊 <b>अंतिम रिपोर्ट:</b>\n• पूरे प्राप्तकर्ताओं की संख्या: <b>{ $total }</b>\n• ✅ सफलतापूर्वक भेजा गया: <b>{ $sent }</b>\n• 🚫 उपयोगकर्ता द्वारा ब्लॉक किया गया: <b>{ $blocked }</b>\n• ⚠️ अन्य त्रुटियां: <b>{ $errors }</b>

Here is the translated .ftl content from English to Hindi (hi):

CRITICAL REQUIREMENTS:
1. Keep ALL keys on the left side of '=' EXACTLY as they are. Never translate key names.
2. Keep ALL variables in braces like { $version }, { $count }, { $title }, etc. EXACTLY as they are.
3. Keep ALL HTML tags intact.
4. Keep the Fluent multiline indentation format.
5. Return ONLY the translated .ftl content. DO NOT include markdown code fences (no ``` or ```ftl), no explanations.

Content to translate:

parser_notification_group_missing = ⚠️ <b>नोटिफिकेशन ग्रुप नहीं मिला!</b>\n\nट्रैकिंग शुरू करने से पहले, आपको एक लक्ष्य ग्रुप बनाना होगा जो अलर्ट प्राप्त करे।\nनीचे दिए गए बटन पर क्लिक करें और इसे सेट अप करें:

parser_free_account_limit = ⚠️ <b>ट्रैकिंग सीमा पार हो गई!</b>\n\nआप एक <b>साझा मुफ़्त खाता</b> का उपयोग कर रहे हैं, जो केवल <b>1 चैनल</b> को ट्रैक करने की अनुमति देता है।\n\nअधिक चैनल ट्रैक करने के लिए:\n• अपने व्यक्तिगत टेलीग्राम खाते को जोड़ें (असीमित)\n• या टेलीग्राम स्टार्स के साथ अतिरिक्त स्लॉट खरीदें।

welcome_choose_lang = 👋 नमस्ते! कृपया अपनी भाषा चुनें / Привет! Пожалуйста, выберите язык:

no_connected_account = कोई जुड़ा हुआ खाता नहीं। कृपया एक खाता जुड़ें।

excel_export_caption = 📊 एक्सेल में ग्रुप खोज परिणाम

db_export_caption = 📊 एक्सेल में डेटाबेस निर्यात

found_groups_caption = 📊 पाया गया { $count } ग्रुप/चैनल

nightly_check_btn = रात्रि जांच (01:00)

nightly_check_on = चालू

nightly_check_off = बंद

nightly_check_toggled_on = 🔔 01:00 पर रात्रि जांच की स्वचालित जांच सक्षम है।

nightly_check_toggled_off = 🔕 रात्रि जांच की स्वचालित जांच बंद है।

btn_pt_accounts = 👥 मेरे अभियान / खाते

btn_pt_rename_acc = ✏️ शीर्षक / विषय बदलें

btn_pt_tech_group = 📣 तकनीकी ग्रुप

btn_pt_sync_dialogs = 📥 खाता चैट्स आयात करें

btn_pt_toggle_all_chats = 🌐 सभी खाता चैट्स: { $status }

btn_pt_acc_keywords = 🔑 विषय के शब्दकोष

btn_pt_acc_groups = 👥 विषय ग्रुप्स

btn_pt_start_acc = ▶️ इस खाता को शुरू करें

btn_pt_stop_acc = ⏹️ इस खाता को रोकें

btn_pt_start_all = 🚀 सभी खाता शुरू करें

btn_pt_stop_all = 🛑 सभी खाता रोकें

pt_acc_card =
    📱 <b>अभियान:</b> «{ $title }» ({ $phone })
    📡 <b>स्थिति:</b> { $status }
    📣 <b>तकनीकी ग्रुप:</b> { $tech_group }
    🔑 <b>शब्दकोष:</b> { $keywords_count } पीसी।
    👥 <b>लक्ष्य चैट्स:</b> { $groups_count } पीसी।
    🌐 <b>सभी खाता चैट्स मोड:</b> { $all_chats_mode }

    💡 <i>«सभी खाता चैट्स» मोड में, बॉट सभी खुले और बंद ग्रुप्स को ट्रैक करता है जो खाता टीडेटा या मैनुअली जुड़ा हुआ है।</i>

pt_ask_rename_acc = इस अभियान के लिए एक नया शीर्षक या विषय दर्ज करें (उदाहरण के लिए: <b>सोफे</b> या <b>रेफ्रिजरेटर</b>):

pt_acc_renamed = ✅ अभियान का शीर्षक सफलतापूर्वक अद्यतन किया गया है: <b>{ $title }</b>

pt_ask_acc_keywords =
    अभियान «{ $title }» के लिए शब्दकोष दर्ज करें जो कोमा या नई पंक्तियों के साथ अलग किया जा सकता है:
    <i>(उदाहरण के लिए: सोफा, कुशन, फर्नीचर)</i>

pt_acc_keywords_saved = ✅ अभियान «{ $title }» के लिए शब्दकोष सफलतापूर्वक सुरक्षित है! जोड़ा गया: <b>{ $count }</b> पीसी।

pt_dialogs_syncing = ⏳ खाते के डायलॉग्स को टेलेथॉन के माध्यम से स्कैनिंग...

pt_dialogs_synced = ✅ सिंक्रनाइजेशन पूरी हुई! पाए गए और लिंक किए गए ग्रुप/चैनल: <b>{ $count }</b> पीसी.

pt_toggle_all_chats_done = «सार्वजनिक खाता चैट» मोड के लिए अभियान «{ $title }»: <b>{ $status }</b>

pt_closed_group_hint =
    💡 <b>बंद ग्रुप सपोर्ट:</b>
    • निमंत्रण लिंक भेजें: <code>https://t.me/+हैश</code>
    • बंद चैट का संख्यात्मक आईडी भेजें: <code>-100...</code>
    • बंद चैट का सटीक शीर्षक भेजें (जहां खाता पहले से ही एक सदस्य है)
    • या <b>«📥 खाता चैट लोड करें»</b> पर क्लिक करें ताकि तीडेटा से सभी चैट को तुरंत लोड किया जा सके!
