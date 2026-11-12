# Spanish localization (es)

Here is the translated content in Spanish (es):

CRITICAL REQUIREMENTS:
1. Keep ALL keys on the left side of '=' EXACTLY as they are. Never translate key names.
2. Keep ALL variables in braces like { $version }, { $count }, { $title }, etc. EXACTLY as they are.
3. Keep ALL HTML tags (<b>, </b>, <i>, </i>, <code>, </code>, <a href="...">, </a>) intact.
4. Keep the Fluent multiline indentation format (subsequent lines indented by 4 spaces).
5. Return ONLY the translated .ftl content. Do NOT include markdown code fences (no ``` or ```ftl), no explanations.

welcome_ask_language =
    🌍 ¡Hola! Por favor, elige el idioma de interfaz:

welcome_message_template =
    🤖 Bienvenido al bot de Telegram para el seguimiento 🔍 de palabras clave en grupos y canales, así como la búsqueda de la comunidad AI.

    📋 <b>Versión:</b> { $version }
    📅 <b>Fecha de lanzamiento:</b> 04 de septiembre de 2026
    👨‍💻 <b>Desarrollador:</b> <a href="https://t.me/PyAdminRU">@PyAdminRU</a>
    📢 <b>Canales principales:</b> <a href="https://t.me/master_tg_d">@master_tg_d</a>

    📊 <b>Grupos/canales encontrados por los usuarios:</b> { $groups_count }

    📱 <b>Cuentas conectadas:</b> { $count }
    📤 <b>Grupos técnicos (para reenviar):</b> { $group_count }
    🔍 <b>Palabras clave rastreadas:</b> { $keywords_count }
    📡 <b>Canales que se están monitoreando:</b> { $get_groups }

    🎉 <b>Características principales del bot:</b>

    • 🌐 <b>Búsqueda AI en el panel web:</b> La búsqueda AI dirigida para grupos y canales está disponible en la interfaz del panel web
    • 📥 <b>Obtener base de datos:</b> Descargar la base de datos actual de canales y grupos encontrados
    • 📚 <b>Instrucciones:</b> Guía detallada sobre el uso del bot
    • ⚙️ <b>Configuración:</b> Configurar conexiones de cuentas, palabras clave y filtros

    💡 <b>Consejo:</b> Para obtener las últimas características y actualizaciones, se recomienda reiniciar el bot con el comando /start

lang_selected =
    ✅ ¡Genial! La interfaz ahora se mostrará en el idioma seleccionado.

settings_message =
    ⚙️ En este menú puedes:
    • 🔗 Conectar una cuenta de Telegram
    • 🌐 Cambiar el idioma de interfaz
    • 📢 Agregar grupos y canales para rastrear
    • 🧩 Configurar palabras clave y filtros

    Elige una opción debajo 👇

connect_account =
    📱 Para conectar tu cuenta de Telegram, envía un archivo de sesión en formato:
    `+79599999999.session`

    Una vez cargado, el bot utilizará esta cuenta para rastrear mensajes.

launching_tracking =
    🚀 Lanzando el seguimiento de mensajes...

    La parada del seguimiento es posible solo después de suscribirse a grupos/canales

tracking_launch_error =
    ⚠️ La lista de canales está vacía.

    Por favor, agrega al menos un grupo o canal para rastrear 🔍
    a través del menú de configuración ⚙️

update_list =
    📥 Envía un archivo .txt con una lista de grupos y canales para rastrear:

    ✅ Cada usuario debe estar en el formato <b>@username</b>
    ✅ Cada enlace debe estar en una <b>línea separada</b>
    ✅ El archivo debe tener una <b>extensión .txt</b>

    📌 Ejemplo de contenido del archivo:
    @grupo1
    @canal1
    @mi_comunidad

    El formato del archivo es importante — el bot solo procesará archivos de texto con la estructura correcta.

account_missing =
    ⚠️ No tienes una cuenta de Telegram conectada.

account_missing_2 =
    ⚠️ El archivo de sesión para tu cuenta de Telegram es inválido — debes iniciar sesión de nuevo. Envía un archivo de sesión válido.

enter_keyword =
    🔍 Ingresa una palabra clave/frase para rastrear

ai_search_welcome =
    🤖 <b>Bienvenido al menú de búsqueda AI!</b>

    Aquí puedes encontrar nuevos grupos y canales utilizando el poder de la inteligencia artificial.

    🚀 <b>Modos disponibles:</b>
    • 🤖 <b>Búsqueda AI:</b> Búsqueda rápida de grupos basada en tu base de datos y palabras clave.
    • 🌐 <b>Búsqueda global AI:</b> Búsqueda avanzada en todo el espacio de Telegram para encontrar nuevas comunidades.

    Solo selecciona el modo deseado en el teclado o ingresa una solicitud! 👇

enter_group =
    🔍 Ingresa un enlace al grupo en el formato @username al que se enviará el mensaje cuando se detecte una palabra clave

admin_panel_message =
    👋 <b>Bienvenido al panel de administración!</b>

    Aquí puedes hacer lo siguiente:

    📁 <b>Obtener archivo de registro:</b> Ver el registro de errores y eventos del bot para el período reciente. Útil para el diagnóstico.

    🔄 <b>Actualización de base de datos:</b> Actualizar la información sobre grupos y canales: verificar su tipo actual (grupo/canal) y obtener IDs actuales.

    🏷️ <b>Asignar categoría:</b> Clasificar automáticamente grupos y canales por temas utilizando AI.

    ✅ <b>Verificar cuentas:</b> Verificar el estado de las cuentas conectadas y sus sesiones.

    🌐 <b>Asignar idioma:</b> Detectar el idioma del contenido en grupos y canales.

    🔐 <b>Conectar cuenta:</b> Conectar una cuenta de Telegram mediante archivo de sesión para su uso en el bot.

tracking_stopped =
    ✅ El seguimiento ha sido detenido.

instruction_caption =
    📘 <b>Instrucciones de uso:</b>

    Adjunto está una guía detallada sobre la funcionalidad del bot.

    🔗 <b>Documentación en línea:</b>
    • <a href="{ $gitverse_link }">GitVerse</a>
    • <a href="{ $github_link }">GitHub</a>

    Se recomienda revisarla para el uso efectivo de todas las características del bot.

instruction_file_not_found =
    ⚠️ El archivo de instrucciones no se encontró en el servidor.

instruction_send_error =
    ❌ Ocurrió un error al enviar el archivo.

database_empty =
    📭 La base de datos está vacía.

export_all_caption =
    📦 Base de datos completa de grupos y canales de Telegram.

    📊 Total de registros: { $total_records }
    🧹 Registros duplicados eliminados antes de la exportación: { $deleted_duplicates }

export_channels_caption =
    📦 Base de datos de canales de Telegram.

    📊 Total de registros: { $total_records }

export_groups_caption =
    📦 Base de datos de grupos de Telegram.

    📊 Total de registros: { $total_records }

export_error_generic =
    ❌ Ocurrió un error al crear el archivo.

get_database_menu =
    👋 Bienvenido al modo de exportación de base de datos!

    Aquí puedes hacer lo siguiente:

    🔹 <b>📥 Obtener base de datos completa:</b> Obtener una lista completa de todos los grupos y canales guardados en formato de Excel.
    🔹 <b>Obtener base de datos de canales:</b> Obtener una lista de todos los canales guardados en formato de Excel.
    🔹 <b>Obtener base de datos de grupos (supergrupos):</b> Obtener una lista de todos los supergrupos guardados en formato de Excel.
    🔹 <b>Obtener base de datos de chats regulares (grupos antiguos):</b> Obtener una lista de todos los chats regulares (grupos antiguos) guardados en formato de Excel.
    🔹 Elige una categoría para exportar

    🔸 Presiona <b>Atrás</b> para regresar al menú principal.

select_category_prompt =
    📌 Selecciona una categoría para la que deseas obtener una lista de grupos/canales:

action_cancelled =
    ❌ Cancelado.

invalid_category =
    ⚠️ Categoría inválida. Seleccione de la lista.

category_empty =
    📭 No grupos en la categoría "{ $category }" aún.

category_export_caption =
    ✅ Exportado { $group_count } grupos/canales para la categoría:
    "{ $category }"

searching_groups =
    🔍 Buscando grupos y canales...

search_summary =
    ✅ <b>Busqueda completada!</b>

    📊 Encontrados y guardados: <b>{ $groups_count }</b> grupos/canales
    📁 Resultados enviados en archivo de Excel

    📍 <b>Indicadores de actividad:</b>
    🟢 <b>activo</b> — grupo es activo (último mensaje ≤ 30 días)
    🔴 <b>inactivo</b> — grupo es inactivo (mensajes > 30 días o ninguno)
    ⚪ <b>desconocido</b> — no se pudo determinar (limitaciones de Telegram)

search_results_caption =
    📄 Resultados de búsqueda para la consulta: <b>{ $query }</b>

search_no_results =
    ❌ Desafortunadamente, no se encontró nada para su consulta. Pruebe con otros palabras clave.

search_error =
    ❌ Se produjo un error durante la búsqueda. Pruebe de nuevo.

global_search_no_terms =
    ❌ Ingrese al menos una palabra clave.

global_search_processing =
    🔍 Procesando { $total } consultas...

global_search_skipped =
    ⚠️ Saltado: '{ $term }' (no se encuentran cuentas disponibles)

global_search_progress =
    🔍 Procesados { $current }/{ $total }: { $successful } consultas exitosas

global_search_results_caption =
    📄 Encontrados { $total } grupos de { $successful }/{ $total_queries } consultas

global_search_no_results =
    ❌ Desafortunadamente, no se encontró nada. Pruebe con otras palabras clave.

group_added =
    ✅ Grupo { $group } agregado con éxito para la retransmisión de mensajes.

group_already_added =
    ⚠️ Este grupo ya ha sido agregado.

group_add_error =
    ⚠️ Error al agregar el grupo.

delete_group_prompt =
    Ingrese el nombre del grupo/canal en formato @username para eliminar de la lista de seguimiento:

group_deleted =
    ✅ Grupo { $group } eliminado con éxito de la lista de seguimiento.

group_not_found =
    ❌ Grupo @{ $group } no encontrado en la lista de seguimiento.

no_accounts =
    ❌ No tiene cuentas conectadas.

    Envíe un archivo `.session` o haga clic en "Conectar cuenta" en el menú.

no_keywords_entered =
    ⚠️ No ha ingresado ninguna palabra clave.

keywords_added_count =
    Palabras clave agregadas: { $count }

keywords_already_added =
    Ya agregadas ({ $count })

keywords_add_errors = 
    Errores al agregar

keywords_and_more = 
    y { $count } más

keywords_and_more_errors = 
    y { $count } errores más

keywords_summary = 
    Resumen

keywords_added = 
    Agregado

keywords_skipped = 
    Saltado (duplicados)

keywords_errors = 
    Errores

check_group_ask_url = 
    📤 Introduzca el enlace del grupo para verificar:

check_group_ask_keyword = 
    🔍 Introduzca la palabra clave para buscar:

check_group_started = 
    🔍 Comenzando verificación del grupo...

check_group_new_message_with_link = 
    📨 Nuevo mensaje con palabra clave!

    📌 <b>{ $title }</b>
    📅 Fecha: { $msg_date }
    🔗 <a href="{ $message_link }">Ir al mensaje</a>

check_group_new_message_no_link = 
    📨 Nuevo mensaje con palabra clave!

    📌 <b>{ $title }</b>
    📅 Fecha: { $msg_date }

check_group_summary = 
    ✅ Verificación completada!

    Mensajes encontrados: { $count }
    Palabra clave: { $keyword }
    Coincidencias: { $matched_count }

check_group_parse_error = 
    ❌ Error al procesar el grupo. Verifique el enlace y el acceso a la chat.

target_group_not_found = 
    ❌ Grupo de destino no encontrado para el usuario. Conecte un grupo para que pueda enviar mensajes encontrados por sus palabras clave.

no_channels_to_track = 
    📭 No tiene canales agregados para seguir.

too_many_channels = 
    ⚠️ Encontrados { $total } canales. La suscripción solo se hará para el primer { $limit }.

channel_subscribed = 
    ✅ Suscrito a { $channel }
    ⏳ Próximo intento en { $delay } seg.

target_group_join_error = 
    ❌ El cuenta no pudo unirse al grupo de destino, verifique el grupo conectado

target_group_not_configured = 
    ❌ Grupo de destino no encontrado para el usuario. Conecte un grupo.

target_group_fetch_error = 
    ❌ No se pudo recuperar el grupo de destino. Verifique la conexión.

bot_listening = 
    👂 El bot está escuchando nuevos mensajes...

tracking_not_active = 
    ⚠️ La pista no está activada o ya se ha detenido.

tracking_stop_requested = 
    🛑 Se envió la orden de parada. La pista se detendrá en unos segundos.

search_client_error = 
    ❌ Error al conectar con la cuenta. Inténtelo de nuevo más tarde.

search_no_available_accounts =
    ⚠️ No hay cuentas disponibles para la búsqueda.

session_invalid =
    ⚠️ La cuenta `{ $phone }` ya no es válida.
    Por favor, reconecta la cuenta.

account_fetch_error =
    ⚠️ Ocurrió un error al obtener la cuenta. Intenta de nuevo más tarde.

checking_accounts_start =
    Cuentas a verificar: { $count }

checking_accounts_complete =
    ✅ Verificación de cuentas completada

ai_category_select_method =
    🤖 <b>Selecciona el método de asignación de categoría:</b>

    ⚡️ <b>Rápido (g4f.free)</b>
    • Gratuito, sin claves de API
    • Procesamiento secuencial (lento)
    • Adecuado para volúmenes pequeños
    • Puede devolver resultados inexactos

    🚀 <b>Poderoso (Groq API)</b>
    • Requiere clave de API de Groq
    • Procesamiento paralelo en 10 hilos (rápido)
    • Adecuado para volúmenes grandes
    • Resultados más precisos

    Selecciona un método:

ai_category_back =
    ↩️ Volver al panel de administración

ai_category_checking_models =
    🔍 Verificando modelos disponibles...

ai_category_model_selected =
    ✅ Seleccionado modelo: { $model }

ai_category_select_from_keyboard =
    Por favor, selecciona un método desde el teclado a continuación:

ai_category_all_have_categories =
    ✅ Todos los grupos ya tienen categorías!

ai_category_processing =
    🔄 Procesando { $total } grupos...

ai_category_done =
    ✅ <b>Hecho!</b>

ai_category_error =
    ❌ Error: { $error }

ai_category_stats_title =
    📊 <b>Título de estadísticas de categoría:</b>

ai_category_no_category_count =
    🗃️ Grupos sin categoría: { $count }

ai_category_run_ai =
    Presiona '🏷️ Asignar Categoría' para iniciar el AI

connect_account_ask_session =
    📤 Envíame archivo de sesión Telethon (debe terminar con `.session`)

    Puedes enviar múltiples archivos a la vez — el bot los procesará en orden.
    Cuando estés listo — presiona el botón "Atrás" o envía /start

connect_account_invalid_file =
    ❌ Esto no es un archivo de sesión! Envía un archivo con extensión `.session`

connect_account_limit_reached =
    ⚠️ Límite alcanzado: { $max } archivos a la vez.
    Procesa los archivos actuales y envía el resto más tarde.

connect_account_file_queued =
    📥 Archivo aceptado: `{ $filename }`
    📊 En cola: { $total } archivo(s). Procesando...

connect_account_success =
    ✅ <b>{ $filename }</b> — éxito!
    📱 { $phone } | 👤 { $name }

connect_free_account_success =
    ✅ <b>{ $filename }</b> — agregado a la piscina de cuentas gratuitas!
    📱 { $phone } | 👤 { $name } | 🆔 <code>{ $account_id }</code>

connect_account_failed =
    ❌ <b>{ $filename }</b> — falló la validación

connect_account_error =
    ⚠️ <b>{ $filename }</b> — error de procesamiento

Here is the translated content:

connect_account_processing_done =
    📊 <b>Proceso completado!</b>

lang_detect_no_groups =
    ❌ No grupos para procesar

lang_detect_starting =
    🚀 Iniciando el proceso de { $total } grupos...

lang_detect_error =
    ❌ Error: { $error }

lang_detect_saving =
    💾 Almacenando { $count } resultados en la base de datos...

lang_detect_complete =
    ✅ Proceso completado!

    📊 Estadísticas:
    • Total: { $total }
    • AI detectado: { $ai_success }
    • Almacenado en la base de datos: { $db_success }
    • Errores de AI: { $ai_fail }
    • Errores de la base de datos: { $db_fail }
    • Errores totales: { $total_fail }

lang_detect_stats_title = Estadísticas

lang_detect_stats_total = Total

lang_detect_stats_ai_success = AI detectado

lang_detect_stats_db_success = Almacenado en la base de datos

lang_detect_stats_ai_fail = Errores de AI

lang_detect_stats_db_fail = Errores de la base de datos

lang_detect_stats_total_fail = Errores totales

log_file_caption =
    📄 Archivo de registro con errores.

account_connect_personal =
    🔐 <b>Administración de cuenta de Telegram</b>

    📱 <b>Cuenta actual:</b> ✅ <i>Cuenta personal</i>
    📊 <b>Modo:</b> Canales ilimitados (dentro de tus slots)

    Puedes reconectar utilizando otro método o desconectarla.

account_connect_shared =
    🔐 <b>Administración de cuenta de Telegram</b>

    🎁 <b>Cuenta actual:</b> <i>Cuenta gratuita del administrador</i>
    ⚠️ <b>Límite:</b> La rastreo de palabras solo está permitido en <b>1 grupo</b>.

    🔄 <i>Si hay problemas con la cuenta actual, haz clic en "Reconectar cuenta gratuita" a continuación.</i>
    💡 <i>Para rastrear múltiples grupos simultáneamente, conecta tu cuenta personal.</i>

free_account_connected_success =
    🎉 <b>Cuenta gratuita del administrador conectada con éxito!</b>

    📱 <b>Cuenta:</b> { $phone }
    👤 <b>Nombre:</b> { $name }
    ⚠️ <b>Nota:</b> Un límite de <b>1 grupo/canal</b> se aplica a esta cuenta gratuita.

    💡 <i>Si necesitas rastrear más canales, puedes conectar tu cuenta personal en cualquier momento.</i>

free_account_reconnected_success =
    🎉 <b>Cuenta gratuita reconectada con éxito!</b>

    📱 <b>Nueva cuenta:</b> { $phone }
    👤 <b>Nombre:</b> { $name }
    ✅ <b>Estado:</b> Activa y lista para el seguimiento.

    ⚠️ <b>Nota:</b> El límite de 1 grupo se aplica a esta cuenta gratuita.

account_connect_none =
    🔐 <b>Administración de cuenta de Telegram</b>

    ⚠️ <b>Cuenta actual:</b> <i>No conectada</i>

    Para monitorear mensajes y palabras clave, elige un método de conexión:
    • <b>Cuenta personal</b> — sin límite de canales.
    • <b>Cuenta gratuita del administrador</b> — acceso gratuito, limitado a 1 grupo.

account_connected_free =
    ✅ Cuenta conectada con éxito

no_free_accounts =
    ❌ No hay cuentas gratuitas disponibles. Intenta nuevamente más tarde o contacta al administrador.

no_free_accounts_detailed =
    ⚠️ <b>No hay cuentas gratuitas disponibles</b>

    Actualmente, no hay cuentas gratuitas disponibles del administrador.
    Conecta tu cuenta personal (por teléfono o mediante archivo de sesión).

invalid_session_file =
    ❌ Esto no es un archivo de sesión! Envía un archivo con extensión `.session`

session_file_received =
    📥 Archivo recibido: `{ $filename }`

    🔍 Verificando cuenta...

session_connected_success =
    ✅ <b>{ $filename }</b> — exitoso!
    📱 { $phone } | 👤 { $name }
    💾 Almacenado en tu base de datos personal.

Here is the translated content:

sesión_validación_fallida =
    ❌ <b>{ $filename }</b> — falló la validación.
    Por favor, verifica que el archivo de sesión es actualizado y no está siendo utilizado en otro lugar.

sesión_verificar_error =
    ⚠️ Ocurrió un error al verificar la cuenta. Intenta de nuevo más tarde.

solo_archivos_txt_son_apoyados =
    ⚠️ Solo se admiten archivos .txt.

archivo_vacio_sin_nombres_de_usuarios =
    ⚠️ El archivo está vacío o no contiene nombres de usuarios.

subir_grupo_resumen =
    ✅ Agregados: { $added }
    ⚠️ Ya existen: { $skipped }
    ❌ Errores: { $errors }

cuentas_encontradas =
    🔍 Encontradas cuentas: { $count }

actualización_de_base_de_datos_inicio =
    🔄 Iniciando actualización de { $total } grupos...

utilizando_cuenta =
    📱 Utilizando cuenta: { $account }

error_de_cuenta_admin =
    ❌ Error de cuenta { $account }: { $error }

error_critico_admin =
    ❌ Error crítico: { $error }

no_hay_preguntas_en_la_base_de_datos =
    📭 No hay preguntas en la base de datos.

captura_de_preguntas_y_respuestas =
    📦 Captura de preguntas y respuestas.

error_durante_exportación =
    ❌ Ocurrió un error durante la exportación: { $error }

botón_de_lanzamiento_de_seguimiento = 🚀 Iniciar seguimiento

botón_de_verificación_de_grupo_para_palabras_clave = 🔍 Verificar grupo para palabras clave

botón_de_busqueda_con_inteligencia_artificial = ✨ Buscar con inteligencia artificial

botón_de_obtener_base_de_datos = 📥 Obtener base de datos

botón_de_instrucciones = 📖 Instrucciones

botón_de_configuración = ⚙️ Configuración

botón_de_panel_administrativo = 🛡️ Panel administrativo

botón_de_obtener_archivo_de_log = 📄 Obtener archivo de log

botón_de_exportar_preguntas = Exportar preguntas

botón_de_asignar_categoria = 🏷️ Asignar categoría

botón_de_verificar_cuentas = ✅ Verificar cuentas

botón_de_conectar_cuenta = 🔐 Conectar cuenta

back_button = ⬅️ Atrás

fast_method_button = ⚡️ Rápido (g4f.free)

powerful_method_openrouter_button = 🚀 Poderoso (API de Openrouter)

powerful_method_groq_button = 🚀 Poderoso (API de GROQ)

all_database_button = 📥 Todo el Banco de Datos

channels_database_button = 📥 Banco de Datos de Canales

groups_database_button = 📥 Banco de Datos de Grupos

select_category_button = 📂 Seleccionar Categoría

investments_button = Inversiones

finance_and_personal_budget_button = Finanzas y presupuesto personal

crypto_and_blockchain_button = Cripto y blockchain

business_and_entrepreneurship_button = Negocios y emprendimiento

marketing_and_promotion_button = Marketing y promoción

tech_and_it_button = Tecnologías y TI

education_and_self_development_button = Educación y auto-desarrollo

work_and_career_button = Trabajo y carrera

real_estate_button = Bienes raíces

health_and_medicine_button = Salud y medicina

travel_button = Viajes

auto_and_transport_button = Automoción y transporte

shopping_and_discounts_button = Compras y descuentos

entertainment_and_leisure_button = Entretenimiento y ocio

politics_and_society_button = Política y sociedad

science_and_research_button = Ciencia y investigación

sports_and_fitness_button = Deportes y fitness

cooking_and_food_button = cocina y comida

fashion_and_beauty_button = moda y belleza

hobbies_and_creativity_button = pasatiempos y creatividad

russian_language_button = 🇷🇺 Ruso

english_language_button = 🇬🇧 Inglés

stop_tracking_button = 🛑 Detener la pista

update_list_button = 🔁 Actualizar lista

enter_keyword_button = 🔍 Introducir palabra clave

delete_group_from_tracking_button = 🗑️ Eliminar grupo de la pista

keywords_list_button = 🔍 Lista de palabras clave

tracking_links_button = 🌐 Enlaces de seguimiento

connect_group_for_messages_button = 📤 Conectar grupo para mensajes

change_language_button = 🌐 Cambiar idioma

connect_free_account_button = 🔐 Conectar cuenta gratuita

keywords_export_caption = 📋 Exportar palabras clave. Registros totales: { $count }

no_keywords_found = 📭 No se encontraron palabras clave guardadas.

tracking_links_export_caption = 🔗 Exportar enlaces de seguimiento. Registros totales: { $count }

no_tracking_links_found = 📭 No se encontraron enlaces de seguimiento.

excel_header_number =

excel_header_keyword = Palabra clave

excel_header_username = Nombre de usuario del canal/grupo

ai_search_button_user = 🤖 Búsqueda con IA

excel_filename_all_db = Todos_los_basureros.xlsx

excel_filename_channels_db = Base_de_datos_de_canal.xlsx

excel_filename_groups_db = Base_de_datos_de_grupo.xlsx

excel_sheet_name_search_results = Resultados de búsqueda

excel_header_id = ID (Hash)

excel_header_name = Nombre

excel_header_description = Descripción

excel_header_participants = Participantes

excel_header_category = Categoría

excel_header_type = Tipo

excel_header_language = Idioma

excel_header_activity = Actividad

excel_header_link = Enlace

excel_header_date_added = Fecha agregada

excel_sheet_name_groups = Grupos

excel_filename_groups_by_category = grupos_{ $category }.xlsx

excel_header_group_name = Nombre

excel_header_group_description = Descripción

excel_header_group_type = Tipo

excel_header_group_participants = Participantes

excel_header_group_link = Enlace

excel_filename_telegram_groups = grupos_telegram_{ $timestamp }.xlsx

instruction_question_prompt = 🤖 <b>Tú puedes hacerme cualquier pregunta sobre el uso del bot, y yo te responderé!</b>

ai_support_assistant_system_prompt = Eres un asistente de soporte calificado para el bot Telegram AutoParseAlertBot. Tu tarea es responder a las preguntas de los usuarios basándote estrictamente en la base de conocimientos proporcionada. Si la respuesta no está en la base de conocimientos, informa amablemente al usuario de que no tienes esta información y aconseja a los usuarios que contacten con el soporte. Responde en el idioma del usuario en texto legible sin formato de marcado (no utilices caracteres de Markdown

lang_detect_summary = ✅ Proceso completado!

    📊 Estadísticas:
    • Total: { $total }
    • AI detectó: { $ai_success }
    • Guardado en DB: { $db_success }
    • Errores de AI: { $ai_fail }
    • Errores de DB: { $db_fail }
    • Errores totales: { $total_fail }

name_prompt = Nombre

description_prompt = Descripción

no_data_prompt = Sin datos

Here is the translated content in Spanish (.ftl):

ai_lang_detect_prompt =
    Determina el idioma principal del texto o descripción de la comunidad.
    Responde EÍTRO EN UNA PALABRA — el código de idioma en formato ISO 639-1 (código de dos letras).
    Ejemplos de respuestas correctas: es, en, fr, zh, ar, hi, ja, ko, pt, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn.
    Si el idioma no puede determinarse de manera inequívoca o el texto contiene una mezcla de idiomas sin uno dominante — responde: desconocido.
    Texto para análisis:
    { $user_input }

get_groups_without_category_message = 📊 <b>Estadísticas de categoría:</b>

    🗃️ Grupos sin categoría: { $count }

    Presiona '🏷️ Asignar categoría' para empezar el AI

download_free_success = 📥 Exportando base de datos (1 descarga gratuita por día). Iniciando descarga...

download_cooldown_message =
    ⚠️ Ya has descargado la base de datos en las últimas 24 horas.
    La próxima descarga gratuita estará disponible en <b>{ $time }</b>.
    
    Puedes descargar la base de datos ahora por 5 ⭐.
    Tu saldo de estrellas en el bot: <b>{ $stars }</b> ⭐

pay_from_balance_btn = 🪙 Deductir 5 ⭐ del saldo

pay_direct_btn = ⭐ Pagar 5 ⭐ directamente

cancel_btn = ❌ Cancelar

download_paid_success = ✅ Pago/deducción de 5 ⭐ exitosa. Iniciando descarga de base de datos...

download_insufficient_stars = ❌ Insuficiente estrellas en tu saldo.

stars_topup_success = 🎉 Saldo de estrellas reabastecido con éxito por { $amount } ⭐! Tu saldo actual: { $balance } ⭐.

stars_added_admin = ⭐ Administrador creditó { $amount } ⭐ a ti. Saldo actual: { $balance } ⭐.

topup_stars_button = 💳 Reabastecer estrellas

stars_balance_msg = 👤 <b>Perfil de estrellas:</b>\n\nSaldo: <b>{ $stars }</b> ⭐\n\nAquí puedes reabastecer tu saldo de estrellas de Telegram para descargas de base de datos pagadas.

stars_invoice_title = Reabastecer saldo de estrellas

stars_invoice_desc = Compra de { $amount } estrellas de Telegram para uso en el bot

stars_invoice_dl_title = Descarga de base de datos

stars_invoice_dl_desc = Descarga de base de datos una vez, evitando el límite diario

excel_filename_category_db = base_de_datos_por_categoria.xlsx

export_category_caption = 📂 Base de datos por categoría "{ $category }". Registros totales: { $total_records }.

generating_database_wait = ⏳ Generando archivo de base de datos, esto puede llevar algún tiempo. Por favor, espera...

btn_add_channels_tracking = ➕ Agregar canales (texto o .txt)

btn_channels_list = 📋 Lista de canales

btn_export_excel = 📥 Exportar a Excel

btn_clear_all_channels = 🧹 Borrar todos los canales

btn_tracking_channels = 🌐 Canales monitoreados

btn_keywords = 🔍 Palabras clave

btn_notification_group = 📢 Grupo de notificación

btn_transfer_settings = 🔄 Configuración de transferencia a usuario

btn_personal_tracking = 🎯 Seguimiento personal

btn_connect_account_session = 📄 Conectar cuenta mediante sesión (.session)

btn_connect_account_phone = 📱 Conectar cuenta personal (por teléfono)

btn_connect_free_account = 🎁 Cuenta gratuita del administrador (1 grupo)

btn_reconnect_free_account = 🔄 Reconectar cuenta gratuita

btn_disconnect_account = ❌ Desconectar cuenta actual

btn_to_tracking_menu = 🎯 Al menú de seguimiento

btn_to_settings_menu = ⚙️ Al menú de configuración

btn_main_menu = 🏠 Menú principal

btn_add_keywords = ➕ Agregar palabras clave

btn_keywords_list = 📋 Lista de palabras clave

btn_export_keywords = 📥 Exportar palabras clave

btn_goto_notification_group = 🔗 Abrir grupo de notificación

btn_notification_group_not_created = 🔗 Grupo no creado todavía

btn_recreate_notification_group = 🔄 Recrear grupo

btn_nav_prev = ◀️ Atrás

btn_nav_next = Siguiente ▶️

btn_confirm_clear = ✅ Sí, borrar

btn_cancel = ❌ Cancelar

btn_broadcast_users = 📢 Emisión a usuarios

btn_broadcast_send = 🚀 Lanzar emisión

btn_broadcast_cancel = ❌ Cancelar emisión

btn_pt_add_tracking = ➕ Agregar seguimiento de grupo

btn_pt_buy_slot = ⭐ Comprar +1 slot (2 estrellas)

btn_pt_my_groups = 📋 Mis grupos monitoreados

btn_pt_stats = 📊 Estadísticas

btn_keypad_clear = ❌ Borrar

btn_keypad_submit = ✅ Enviar

btn_keypad_cancel = 🚫 Cancelar

btn_pt_edit_record = ⚙️ Editar

btn_pt_buy_stars_slots = ⭐ Comprar slots (Telegram estrellas)

btn_pt_connect_personal = 📱 Conectar cuenta personal

btn_pt_create_notification_group = 📢 Crear grupo de notificación

settings_channels_title = 🌐 <b>Canales monitoreados</b>\n\n📊 Total canales: <b>{ $total }</b>\n\nElige una acción:

settings_channels_empty = 📭 La lista de canales está vacía.

settings_channels_list_title = 📋 <b>Lista de canales</b> (página { $page }/{ $total_pages }) · total: { $total }\n

settings_channels_list_hint = \n<i>Haz clic en ❌ en un canal para eliminarlo.</i>

settings_channel_deleted = ✅ Canal eliminado: { $channel }

settings_channel_not_found = ⚠️ Canal no encontrado.

settings_channels_clear_confirm = 🧹 <b>¿Vaciar toda la lista de canales?</b>\n\n<b>{ $total }</b> canal(es) se eliminarán. Esta acción no se puede deshacer.

settings_channels_cleared = ✅ <b>Lista de canales vaciada.</b>\n\nEliminados canales: <b>{ $count }</b>

settings_keywords_title = 🔍 <b>Palabras clave</b>\n\n📊 Total palabras clave: <b>{ $total }</b>\n\nElige una acción:

settings_keywords_empty = 📭 La lista de palabras clave está vacía.

settings_keywords_list_title = 🔍 <b>Palabras clave</b> (página { $page }/{ $total_pages }) · total: { $total }\n

settings_keywords_list_hint = \n<i>Haz clic en ❌ en una palabra para eliminarla.</i>

settings_keyword_deleted = ✅ Eliminada: { $keyword }

settings_keyword_not_found = ⚠️ Palabra no encontrada.

settings_notification_created = 📢 <b>Grupo de notificación</b>\n\n✅ Grupo creado.\n🔗 <a href='{ $link }'>Ir al grupo</a>

settings_notification_not_created = 📢 <b>Grupo de notificación</b>\n\n❌ Grupo no creado todavía.\n\n<i>Crea un grupo mediante «🎯 Seguimiento personal».</i>

settings_notification_alert_no_group = ❌ El grupo no está creado. Ve a «🎯 Seguimiento personal» para crearlo.

settings_notification_recreate_text = 🔄 <b>Recrear Grupo de Notificación</b>\n\nPara recrear el grupo, ve a «🎯 Seguimiento personal» → «➕ Agregar seguimiento de grupo».\n\n<i>Un nuevo grupo se creará automáticamente cuando se agregue seguimiento.</i>

connect_group_prompt = 🔗 <b>Envía un enlace o nombre de usuario del grupo/canal para seguir</b>\n\nPor ejemplo:\n<code>https://t.me/python_jobs</code>\nor <code>@python_jobs</code>\n\nPuedes enviar múltiples enlaces, uno por línea.

connect_group_no_links = ⚠️ Por favor, envía al menos un enlace o nombre de usuario.

connect_group_invalid_links = ⚠️ Por favor, verifica si los enlaces son válidos.

connect_group_saved = ✅ Grupo(s) guardados en la base de datos.

connect_group_text_required = ⚠️ Por favor, envía un enlace o nombre de usuario como mensaje de texto.

connect_group_file_invalid_links = ⚠️ Por favor, verifica si los enlaces en el archivo son válidos.

connect_group_file_required = ⚠️ Por favor, envía un archivo de texto (TXT) que contenga enlaces o nombres de usuario.

transfer_rights_prompt = 🔄 <b>Transferir configuración a otro usuario</b>\n\nEnvía el ID de Telegram del usuario a quien deseas copiar tus canales y palabras clave.\n\n<i>Ejemplo: <code>1234567890</code></i>

transfer_rights_invalid_id = ⚠️ ID inválido. El ID debe contener solo dígitos.\n\nIntenta de nuevo desde el menú de configuración.

transfer_rights_self = ⚠️ No puedes transferir configuración a ti mismo.

transfer_rights_not_found = ⚠️ El usuario con ID <code>{ $target_user_id }</code> aún no ha iniciado este bot.

transfer_rights_success = ✅ <b>Configuración transferida con éxito al usuario { $target_user_id }!</b>\n\n📋 Canales agregados: <b>{ $groups }</b>\n🔑 Palabras clave agregadas: <b>{ $keywords }</b>

delete_group_invalid_format = ⚠️ <b>No se pudo reconocer el formato del enlace.</b>\n\nFormatos admitidos:\n• <code>@nombre_de_canal</code>\n• <code>https://t.me/nombre_de_canal</code>\n• <code>https://t.me/+Código_de_hash</code>\n• <code>https://t.me/joinchat/Código_de_hash</code>

keywords_added_success = ✅ Palabras clave agregadas.\n\n📊 Palabras clave totales: <b>{ $count }</b>

pt_no_slots_alert = ⚠️ Todos los slots están en uso! Compra un slot adicional.

pt_ask_link = 🔗 <b>Introduce enlace al grupo o canal para seguir</b>\n\n<i>Ejemplo: <code>https://t.me/python_jobs</code> o <code>@python_jobs</code></i>

pt_invalid_link = ⚠️ Por favor, introduce un enlace válido (https://t.me/...) o @nombre_de_usuario.

pt_checking_group = 🔄 <i>Verificando grupo y recuperando información...</i>

pt_ask_keywords = 🔑 Introduce palabras clave para seguir separadas por comas:

pt_saved_success = ✅ <b>Configuración de seguimiento guardada!</b>

pt_step2_created =
    ✅ <b>Grupo creado!</b>

    1. Sigue el enlace y únete al grupo creado: <a href='{ $link }'>{ $link }</a>
    <i>(El bot { $bot_name } ya es administrador del grupo)</i>

    <b>Paso 2:</b> Introduce palabras clave para seguir en este grupo (separadas por comas):
    <i>Ejemplo: python, trabajo, remoto</i>

Here is the translated content:

pt_configured_success =
    🎉 <b>Configuración de seguimiento personal configurada con éxito!</b>

    📌 <b>Objetivo de seguimiento:</b> { $target }
    🔑 <b>Palabras clave:</b> { $keywords }
    🔗 <b>Grupo para resultados:</b> <a href='{ $link }'>Ir al grupo</a>

    <i>Se enviarán alertas directamente a tu grupo creado!</i>

pt_alert_message =
    🎯 <b>Palabra clave coincidente:</b> <code>{ $keyword }</code>

    💬 <b>Texto del mensaje:</b>
    { $text }

    🔗 <a href='{ $link }'>Ir al mensaje</a>

pt_no_active_trackings = ℹ️ Aún no tienes seguimientos personales activos.

pt_record_not_found = Error: Registro no encontrado

pt_edit_prompt = ⚙️ <b>Editar seguimiento</b>\n\n🔗 Enlace actual: { $link }\n🔑 Palabras clave: { $keywords }\n\nEnvía un nuevo enlace de grupo/canal:

pt_updating_group = 🔄 <i>Actualizando la suscripción y el grupo...</i>

pt_updated_success = ✅ <b>Configuración de seguimiento actualizada con éxito!</b>

pt_stats_msg = 📊 <b>Estadísticas de seguimiento personal</b>\n\n👥 Usuarios totales: <b>{ $users }</b>\n🎯 Seguimientos totales: <b>{ $trackings }</b>

pt_code_prompt = 🔢 Ingrese el código de verificación de 5 dígitos:

pt_invalid_code_alert = ❌ Código de verificación inválido! Intentelo de nuevo.

pt_code_expired_alert = ❌ Código de verificación expirado! Pida el código de nuevo.

pt_login_error_alert = ❌ Error de inicio de sesión: { $error }

pt_checking_2fa = 🔄 <i>Verificando la contraseña de 2FA...</i>

pt_auth_success =
    🎉 <b>Cuenta autorizada y conectada con éxito!</b>

    👤 <b>Nombre:</b> { $name }
    📱 <b>Teléfono:</b> +{ $phone }
    🆔 <b>ID de Telegram:</b> <code>{ $tg_id }</code>

    ✅ Sesión guardada en la base de datos y lista para el seguimiento.

pt_auth_2fa_success =
    🎉 <b>Cuenta autorizada con contraseña de 2FA!</b>

    👤 <b>Nombre:</b> { $name }
    📱 <b>Teléfono:</b> +{ $phone }
    🆔 <b>ID de Telegram:</b> <code>{ $tg_id }</code>

    ✅ Sesión guardada con éxito en la base de datos.

pt_auth_code_invalid_screen =
    📩 <b>Código de verificación enviado a tu Telegram!</b>

    📱 <b>Número:</b> <code>{ $phone }</code>
    🔢 <b>Código ingresado:</b> <code>_ _ _ _ _</code>

    ❌ <b>Error: Código inválido. Intentelo de nuevo:</b>

pt_auth_2fa_prompt =
    🔐 <b>Verificación de dos pasos (2FA) habilitada en tu cuenta!</b>

    Por favor, ingresa tu contraseña de nube como texto en respuesta:

pt_auth_2fa_invalid =
    ❌ <b>Contraseña de 2FA inválida!</b>

    Por favor, ingresa la contraseña de nube correcta como texto:

pt_auth_error = ❌ Error de autorización: { $error }

pt_auth_cancelled = 🚫 Autorización cancelada.

pt_phone_prompt = 📱 <b>Conectar cuenta de Telegram</b>\n\nIngrese su número de teléfono en formato internacional (por ejemplo, <code>+79991234567</code>):

pt_phone_invalid = ❌ Número de teléfono inválido. Intentelo de nuevo.

pt_phone_flood = ⏳ Demasiados intentos. Espere { $seconds } segundos.

pt_code_request_error = ❌ Error al solicitar el código: { $error }

pt_code_need_5_digits = ⚠️ Ingrese todos los 5 dígitos del código de verificación!

pt_sending_code_status = ⏳ Estamos enviando el código de verificación a { $phone }...

pt_enter_code_keypad = 📱 <b>Código de verificación enviado en Telegram</b>\n\nIngrese los dígitos en el teclado inferior:\n\nIngresado: <b>{ $code }</b>

pt_enter_2fa_prompt = 🔐 <b>Verificación de dos pasos (2FA) requerida</b>\n\nIngrese su contraseña de 2FA en la nube:

pt_no_account_connected = ⚠️ No se ha conectado ningún cuenta. Por favor, conecte una cuenta.

pt_record_error = Error de registro.

admin_access_denied = ⛔ Acceso denegado. Solo para administradores.

admin_broadcast_prompt = 📢 <b>Emisión a los usuarios</b>\n\nEnvíe el mensaje que desea enviar a todos los usuarios del bot.\n\n• Soporta la formación en HTML (negrita, itálico, enlaces).\n• Puede adjuntar fotos, videos, animaciones o documentos.\n\n<i>Para cancelar, haga clic en «Atrás» debajo.</i>

admin_broadcast_preview_title = 👁️ <b>Previsualización del mensaje de emisión:</b>

admin_broadcast_preview_params = 📊 <b>Parámetros de emisión:</b>\n\n👥 Total de destinatarios en la base de datos: <b>{ $total }</b>\n\nConfirme la emisión o cancelar:

admin_broadcast_cancelled = ❌ <b>Emisión cancelada.</b>

admin_broadcast_not_found = ⚠️ Error: no se encontró el mensaje de emisión.

admin_broadcast_started = 🚀 <b>Emisión iniciada... Por favor, espere.</b>

admin_broadcast_progress = 🚀 <b>Emitiendo...</b>\n\nProgreso: <b>{ $current }/{ $total }</b>\n✅ Enviado: { $sent }\n🚫 Bloqueado: { $blocked }\n⚠️ Errores: { $errors }

admin_broadcast_report = 🏁 <b>Emisión finalizada!</b>\n\n📊 <b>Informe final:</b>\n• Total de destinatarios: <b>{ $total }</b>\n• ✅ Enviado con éxito: <b>{ $sent }</b>\n• 🚫 Bloqueado por el bot del usuario: <b>{ $blocked }</b>\n• ⚠️ Otros errores: <b>{ $errors }</b>

parser_notification_group_missing = ⚠️ <b>No se encontró el grupo de notificaciones!</b>\n\nAntes de iniciar la vigilancia, debe crear un grupo objetivo para recibir alertas.\nHaga clic en el botón debajo para configurarlo:

parser_free_account_limit = ⚠️ <b!Se ha superado el límite de vigilancia!</b>\n\nEstá utilizando una <b>cuenta compartida gratuita</b>, que permite la vigilancia de solo <b>1 canal</b>.\n\nPara vigilar más canales:\n• Conecte su cuenta personal de Telegram (sin límites)\n• O compre slots adicionales con Telegram Stars.

welcome_choose_lang = 👋 Hola! Por favor, elija su idioma / Привет! Пожалуйста, выберите язык:

no_connected_account = No se ha conectado ninguna cuenta. Por favor, conecte una cuenta.

excel_export_caption = 📊 Resultados de búsqueda de grupos en Excel

db_export_caption = 📊 Exportación de base de datos en Excel

found_groups_caption = 📊 Encontrados { $count } grupos/canales

nightly_check_btn = Verificación nocturna (01:00)

nightly_check_on = ENCENDIDO

nightly_check_off = APAGADO

nightly_check_toggled_on = 🔔 La verificación nocturna automática a las 01:00 está ACTIVADA.

nightly_check_toggled_off = 🔕 El chequeo nocturno de la base de datos está DESACTIVADO.

btn_pt_accounts = 👥 Mis Campañas / Cuentas

btn_pt_rename_acc = ✏️ Cambiar Título/Tema

btn_pt_tech_group = 📣 Grupo Técnico

btn_pt_sync_dialogs = 📥 Importar Conversaciones de Cuenta

btn_pt_toggle_all_chats = 🌐 Todas las Conversaciones de Cuenta: { $status }

btn_pt_acc_keywords = 🔑 Palabras Clave de la Cuenta

btn_pt_acc_groups = 👥 Grupos de la Cuenta

btn_pt_start_acc = ▶️ Iniciar esta Cuenta

btn_pt_stop_acc = ⏹️ Detener esta Cuenta

btn_pt_start_all = 🚀 Iniciar todas las Cuentas

btn_pt_stop_all = 🛑 Detener todas las Cuentas

pt_acc_card =
    📱 <b>Campaña:</b> «{ $title }» ({ $phone })
    📡 <b>Estado:</b> { $status }
    📣 <b>Grupo Técnico:</b> { $tech_group }
    🔑 <b>Palabras Clave:</b> { $keywords_count } pcs.
    👥 <b>Conversaciones de Objetivo:</b> { $groups_count } pcs.
    🌐 <b>Modo de Todas las Conversaciones de la Cuenta:</b> { $all_chats_mode }

    💡 <i>En «Modo de Todas las Conversaciones de la Cuenta» el bot sigue todas las grupos abiertos y cerrados que la cuenta se unió a través de tdata o manualmente.</i>

pt_ask_rename_acc = Ingrese un nuevo título o tema para esta campaña (por ejemplo: <b>Sofás</b> o <b>Refrigeradores</b>):

pt_acc_renamed = ✅ El título de la campaña se actualizó con éxito a: <b>{ $title }</b>

pt_ask_acc_keywords =
    Ingrese palabras clave para la campaña «{ $title }» separadas por comas o en nuevas líneas:
    <i>(Ejemplo: sofá, cama, muebles)</i>

pt_acc_keywords_saved = ✅ Palabras clave para la campaña «{ $title }» guardadas! Agregadas: <b>{ $count }</b> pcs.

pt_dialogs_syncing = ⏳ Escaneando conversaciones de la cuenta a través de Telethon...

pt_dialogs_synced = ✅ Sincronización finalizada! Encontrados y vinculados grupos/canales: <b>{ $count }</b> pcs.

pt_toggle_all_chats_done = «Modo de Todas las Conversaciones de la Cuenta» para la campaña «{ $title }»: <b>{ $status }</b>

pt_closed_group_hint =
    💡 <b>Soporte para Grupos Cerrados:</b>
    • Enviar enlace de invitación: <code>https://t.me/+hash</code>
    • Enviar ID numérico del chat cerrado: <code>-100...</code>
    • Enviar título exacto del chat cerrado (donde la cuenta ya es miembro)
    • O haga clic en <b>«📥 Importar Conversaciones de la Cuenta»</b> para cargar todas las conversaciones de tdata de manera instantánea!
