# PT localization

welcome_ask_language =
    🌍 Olá! Por favor, escolha o seu idioma de interface:

welcome_message_template =
    🤖 Bem-vindo ao bot do Telegram para rastrear 🔍 palavras-chave em grupos e canais, bem como busca de comunidade AI!

    📋 <b>Versão:</b> { $version }
    📅 <b>Data de lançamento:</b> 04 de setembro de 2026
    👨‍💻 <b>Desenvolvedor:</b> <a href="https://t.me/PyAdminRU">@PyAdminRU</a>
    📢 <b>Canal principal:</b> <a href="https://t.me/master_tg_d">@master_tg_d</a>

    📊 <b>Grupos/canais encontrados pelos usuários:</b> { $groups_count }

    📱 <b>Contas conectadas:</b> { $count }
    📤 <b>Grupos técnicos (para encaminhar):</b> { $group_count }
    🔍 <b>Palavras-chave rastreadas:</b> { $keywords_count }
    📡 <b>Canais sendo monitorados:</b> { $get_groups }

    🎉 <b>Principais recursos do bot:</b>

    • 🌐 <b>Busca AI no Painel Web:</b> Busca AI-driven para grupos e canais agora está disponível no interface do Painel Web
    • 📥 <b>Obter Banco de Dados:</b> Baixe o banco de dados atual do canais e grupos encontrados
    • 📚 <b>Instruções:</b> Guia detalhado sobre o uso do bot
    • ⚙️ <b>Configurações:</b> Configure as conexões de conta, palavras-chave e filtros

    💡 <b>Dica:</b> Para obter as últimas funcionalidades e atualizações, é recomendável reiniciar o bot com o comando /start

lang_selected =
    ✅ Ótimo! A interface agora será exibida em seu idioma selecionado.

settings_message =
    ⚙️ Nesta tela você pode:
    • 🔗 Conectar uma conta do Telegram
    • 🌐 Mudar o idioma da interface
    • 📢 Adicionar grupos e canais para rastrear
    • 🧩 Configurar palavras-chave e filtros

    Escolha uma opção abaixo 👇

connect_account =
    📱 Para conectar sua conta do Telegram, envie um arquivo de sessão no formato:
    `+79599999999.session`

    Uma vez carregado, o bot usará essa conta para rastrear mensagens.

launching_tracking =
    🚀 Lançando rastreamento de mensagens...

    A parada de rastreamento é possível apenas após assinar grupos/canais

tracking_launch_error =
    ⚠️ A lista de canais está vazia.

    Por favor, adicione ao menos um grupo ou canal para rastrear 🔍
    via o menu de configurações ⚙️

update_list =
    📥 Envie um arquivo .txt com uma lista de grupos e canais para rastrear:

    ✅ Cada usuário deve estar no formato <b>@username</b>
    ✅ Cada link deve estar em uma <b>linha separada</b>
    ✅ O arquivo deve ter uma <b>extensão .txt</b>

    📌 Exemplo de conteúdo do arquivo:
    @grupo1
    @canal1
    @minha_comunidade

    O formato do arquivo é importante — o bot apenas processará arquivos de texto com a estrutura correta.

account_missing =
    ⚠️ Você não tem uma conta do Telegram conectada.

account_missing_2 =
    ⚠️ O arquivo de sessão para sua conta do Telegram é inválido — você precisa se conectar novamente. Envie um arquivo de sessão válido.

enter_keyword =
    🔍 Insira uma palavra-chave/frase para rastrear

ai_search_welcome =
    🤖 <b>Bem-vindo ao menu de busca AI!</b>

    Aqui você pode encontrar novos grupos e canais usando a força da inteligência artificial.

    🚀 <b>Modos disponíveis:</b>
    • 🤖 <b>Busca AI:</b> Busca rápida para grupos com base no seu banco de dados e palavras-chave.
    • 🌐 <b>Busca Global AI:</b> Busca avançada em todo o espaço do Telegram para encontrar novas comunidades.

    Basta selecionar o modo desejado no teclado ou insira uma solicitação! 👇

enter_group =
    🔍 Insira um link para o grupo no formato @username para o qual a mensagem será encaminhada quando uma palavra-chave for detectada

admin_panel_message =
    👋 <b>Bem-vindo ao Painel de Administração!</b>

    Aqui é o que você pode fazer:

    📁 <b>Obter Arquivo de Log:</b> — visualize o log de erros e eventos do bot para o período recente. Útil para diagnósticos.

    🔄 <b>Atualização do Banco de Dados:</b> — atualize informações sobre grupos e canais: verifique o seu tipo atual (grupo/canal) e obtenha IDs atuais.

    🏷️ <b>Atribuir Categoria:</b> — classifique automaticamente grupos e canais por tópicos usando AI.

    ✅ <b>Verificar Contas:</b> — verifique o status das contas conectadas e suas sessões.

    🌐 <b>Atribuir Idioma:</b> — detecte o idioma do conteúdo em grupos e canais.

    🔐 <b>Conectar Conta:</b> — conecte uma conta do Telegram via arquivo de sessão para uso no bot.

tracking_stopped =
    ✅ O rastreamento foi parado.

instruction_caption =
    📘 <b>Instruções de Uso:</b>

    Anexado está um guia detalhado sobre a funcionalidade do bot.

    🔗 <b>Documentação Online:</b>
    • <a href="{ $gitverse_link }">GitVerse</a>
    • <a href="{ $github_link }">GitHub</a>

    Recomendamos que o revise para o uso efetivo de todas as funcionalidades do bot.

instruction_file_not_found =
    ⚠️ O arquivo de instruções não foi encontrado no servidor.

instruction_send_error =
    ❌ Ocorreu um erro ao enviar o arquivo.

database_empty =
    📭 O banco de dados está vazio.

export_all_caption =
    📦 Banco de dados completo de grupos e canais do Telegram.

    📊 Total de registros: { $total_records }
    🧹 Registros duplicados removidos antes da exportação: { $deleted_duplicates }

export_channels_caption =
    📦 Banco de dados de canais do Telegram.

    📊 Total de registros: { $total_records }

export_groups_caption =
    📦 Banco de dados de grupos do Telegram.

    📊 Total de registros: { $total_records }

export_error_generic =
    ❌ Ocorreu um erro ao criar o arquivo.

get_database_menu =
    👋 Bem-vindo ao modo de exportação do banco de dados!

    Aqui é o que você pode fazer:

    🔹 <b>📥 Obter Banco de Dados Completo:</b> — obtenha uma lista completa de todos os grupos e canais salvos em Excel.
    🔹 <b>Obter Banco de Dados de Canais:</b> — obtenha uma lista de todos os canais salvos em Excel.
    🔹 <b>Obter Banco de Dados de Grupos (supergrupos):</b> — obtenha uma lista de todos os supergrupos salvos em Excel.
    🔹 <b>Obter Banco de Dados de Conversas Regulares (grupos antigos):</b> — obtenha uma lista de todas as conversas regulares (grupos antigos) em Excel.
    🔹 Escolha uma categoria para exportar

    🔸 Pressione <b>Back</b> para retornar ao menu principal.

select_category_prompt =
    📌 Selecione uma categoria para a qual você deseja obter uma lista de grupos/canais:

action_cancelled =
    ❌ Cancelado.

invalid_category =
    ⚠️ Categoria inválida. Por favor, selecione da lista.

category_empty =
    📭 Nenhum grupo na categoria "{ $category }" ainda.

category_export_caption =
    ✅ Exportado { $group_count } grupos/canais para categoria:
    "{ $category }"

searching_groups =
    🔍 Procurando grupos e canais...

search_summary =
    ✅ <b>Busca concluída!</b>

    📊 Encontrado e salvo: <b>{ $groups_count }</b> grupos/canais
    📁 Resultados enviados em arquivo Excel

    📍 <b>Indicadores de atividade:</b>
    🟢 <b>ativo</b> — grupo é ativo (última mensagem ≤ 30 dias)
    🔴 <b>inativo</b> — grupo é inativo (mensagens > 30 dias ou nenhuma)
    ⚪ <b>desconhecido</b> — não pôde determinar (limitações do Telegram)

search_results_caption =
    📄 Resultados da busca para consulta: <b>{ $query }</b>

search_no_results =
    ❌ Infelizmente, nada foi encontrado para sua consulta. Tente outros termos.

search_error =
    ❌ Ocorreu um erro durante a busca. Tente novamente.

global_search_no_terms =
    ❌ Insira pelo menos um termo de busca.

global_search_processing =
    🔍 Processando { $total } consultas...

global_search_skipped =
    ⚠️ Ignorado: '{ $term }' (sem contas disponíveis)

global_search_progress =
    🔍 Processado { $current }/{ $total }: { $successful } bem-sucedidos

global_search_results_caption =
    📄 Encontrados { $total } grupos de { $successful }/{ $total_queries } consultas

global_search_no_results =
    ❌ Infelizmente, nada foi encontrado. Tente outros termos.

group_added =
    ✅ Grupo { $group } foi adicionado para encaminhamento de mensagens.

group_already_added =
    ⚠️ Este grupo já foi adicionado.

group_add_error =
    ⚠️ Erro ao adicionar grupo.

delete_group_prompt =
    Insira o nome do grupo/canal no formato @username para remover do rastreamento:

group_deleted =
    ✅ Grupo { $group } foi removido com sucesso do rastreamento.

group_not_found =
    ❌ Grupo @{ $group } não encontrado na lista de rastreamento.

no_accounts =
    ❌ Você não tem contas conectadas.

    Envie um arquivo `.session` ou clique em "Conectar Conta" no menu.

no_keywords_entered =
    ⚠️ Você não entrou nenhum termo.

keywords_added_count =
    Palavras-chave adicionadas: { $count }

keywords_already_added =
    Já adicionadas ({ $count })

keywords_add_errors =
    Erros ao adicionar

keywords_and_more =
    e { $count } mais

keywords_and_more_errors =
    e { $count } mais erros

keywords_summary =
    Resumo

keywords_added =
    Adicionado

keywords_skipped =
    Ignorado (duplicatas)

Here is the translated .ftl content in Portuguese (pt):

CRÍTICAS REQUISITOS:
1. Mantenha TODOS os chaves na esquerda do '=' EXATAMENTE como estão. Nunca traduza nomes de chaves.
2. Mantenha TODAS as variáveis em chaves como { $versão }, { $contagem }, { $título }, etc. EXATAMENTE como estão.
3. Mantenha TODOS os tags HTML intactos.
4. Mantenha o formato de indentação de múltiplas linhas do Fluent.
5. Retorne APENAS o conteúdo de .ftl traduzido. NÃO inclua cintas de código (nenhuma ` ou `ftl), sem explicações.

Conteúdo para traduzir:
palavras-chave_erro =
    Erros

verificar_grupo_perguntar_url =
    📤 Insira o link do grupo para verificar:

verificar_grupo_perguntar_palavra_chave =
    🔍 Insira a palavra-chave para procurar:

verificar_grupo_iniciado =
    🔍 Iniciando verificação do grupo...

verificar_grupo_mensagem_nova_com_link =
    📨 Nova mensagem com palavra-chave!

    📌 <b>{ $título }</b>
    📅 Data: { $msg_data }
    🔗 <a href="{ $link_mensagem }">Ir para a mensagem</a>

verificar_grupo_mensagem_nova_sem_link =
    📨 Nova mensagem com palavra-chave!

    📌 <b>{ $título }</b>
    📅 Data: { $msg_data }

resumo_verificar_grupo =
    ✅ Verificação concluída!

    Mensagens encontradas: { $contagem }
    Palavra-chave: { $palavra_chave }
    Acertos: { $acertos_contagem }

erro_de_parse_grupo =
    ❌ Erro ao processar grupo. Verifique o link e o acesso ao chat.

grupo_alvo_não_encontrado =
    ❌ Grupo-alvo não encontrado para o usuário. Conecte um grupo para que eu possa enviar mensagens encontradas com as suas palavras-chave.

nenhuma_canal_para_seguir =
    📭 Você não adicionou nenhum canal para seguir.

muito_canais =
    ⚠️ Encontrados { $total } canais. A subscrição será feita apenas para os primeiros { $limite }.

canal_subscrito =
    ✅ Subscrito a { $canal }
    ⏳ Próxima tentativa em { $delay } seg.

erro_juntar_grupo_alvo =
    ❌ O conta não pôde se juntar ao grupo-alvo, verifique o grupo conectado

grupo_alvo_não_configurado =
    ❌ Grupo-alvo não encontrado para o usuário. Conecte um grupo.

erro_buscar_grupo_alvo =
    ❌ Não foi possível buscar o grupo-alvo. Verifique a conexão.

bot_está_ouvindo =
    👂 O bot está ouvindo mensagens novas...

monitoramento_não_ativado =
    ⚠️ O monitoramento não foi iniciado ou já foi parado.

parar_monitoramento_solicitado =
    🛑 Comando de parada enviado. O monitoramento será parado em alguns segundos.

erro_conectar_conta =
    ❌ Erro ao conectar à conta. Tente novamente mais tarde.

nenhuma_conta_disponível =
    ⚠️ Nenhuma conta disponível para busca.

sessão_inválida =
    ⚠️ A conta `{ $telefone }` não é mais válida.
    Por favor, conecte a conta novamente.

erro_buscar_conta =
    ⚠️ Ocorreu um erro ao buscar a conta. Por favor, tente novamente mais tarde.

iniciando_verificar_contas =
    Contas para verificar: { $contagem }

verificar_contas_concluída =
    ✅ Verificação de contas concluída

seleção_metodo_categoria_ai =
    🤖 <b>Selecione o método de atribuição de categoria:</b>

    ⚡️ <b>Rápido (g4f.free)</b>
    • Gratuito, sem chaves de API
    • Processamento sequencial (mais lento)
    • Apropriado para pequenos volumes
    • Pode retornar resultados imprecisos

    🚀 <b>Poderoso (Groq API)</b>
    • Requer chaves de API do Groq
    • Processamento em paralelo em 10 threads (mais rápido)
    • Apropriado para grandes volumes
    • Resultados mais precisos

    Selecione um método:

seleção_categoria_ai =
    ↩️ Voltar para o painel de administração

verificar_modelos_categoria_ai =
    🔍 Verificando modelos disponíveis...

modelo_categoria_ai_selecionado =
    ✅ Modelo selecionado: { $modelo }

Here is the translated Fluent (.ftl) localization content from English into Portuguese (pt):

CRITICAL REQUIREMENTS:
1. Keep ALL keys on the left side of '=' EXACTLY as they are. Never translate key names.
2. Keep ALL variables in braces like { $version }, { $count }, { $title }, etc. EXACTLY as they are.
3. Keep ALL HTML tags intact.
4. Keep the Fluent multiline indentation format.
5. Return ONLY the translated .ftl content. Do NOT include markdown code fences (no ``` or ```ftl), no explanations.

Content to translate:
categoria_ai_selecionar_do_teclado =
    Por favor, selecione um método do teclado abaixo:

categoria_todos_tem_categorias =
    ✅ Todos os grupos já têm categorias!

categoria_processando =
    🔄 Processando { $total } grupos...

categoria_feito =
    ✅ <b>Feito!</b>

categoria_erro =
    ❌ Erro: { $error }

categoria_estatisticas_titulo =
    📊 <b>Estatísticas da Categoria:</b>

categoria_sem_categoria_contagem =
    🗃️ Grupos sem categoria: { $count }

categoria_executar_ai =
    Pressione '🏷️ Atribuir Categoria' para iniciar o AI

conectar_conta_pega_sessao =
    📤 Envie o arquivo de sessão Telethon (deve terminar com `.session`)

    Você pode enviar vários arquivos ao mesmo tempo — o bot processará em ordem.
    Quando terminar — pressione o botão "Voltar" ou envie /start

conectar_conta_arquivo_invalido =
    ❌ Isso não é um arquivo de sessão! Envie um arquivo com extensão `.session`

conectar_conta_limite_reachado =
    ⚠️ Limite atingido: { $max } arquivos ao mesmo tempo.
    Processar arquivos atuais e enviar o resto mais tarde.

conectar_conta_arquivo_enfileirado =
    📥 Arquivo aceito: `{ $filename }`
    📊 Em fila: { $total } arquivo(s). Processando...

conectar_conta_sucesso =
    ✅ <b>{ $filename }</b> — sucesso!
    📱 { $phone } | 👤 { $name }

conectar_conta_gratuito_sucesso =
    ✅ <b>{ $filename }</b> — adicionado à pool de contas gratuitas!
    📱 { $phone } | 👤 { $name } | 🆔 <code>{ $account_id }</code>

conectar_conta_falha =
    ❌ <b>{ $filename }</b> — falha de validação

conectar_conta_erro =
    ⚠️ <b>{ $filename }</b> — erro de processamento

conectar_conta_processamento_feito =
    📊 <b>Processamento concluído!</b>

não_ha_grupos_detectar =
    ❌ Não há grupos para processar

iniciar_detectar =
    🚀 Iniciando processamento de { $total } grupos...

detectar_erro =
    ❌ Erro: { $error }

salvar_detectar =
    💾 Salvando { $count } resultados no DB...

detectar_concluído =
    ✅ Processamento concluído!

    📊 Estatísticas:
    • Total: { $total }
    • AI detectou: { $ai_success }
    • Salvo no DB: { $db_success }
    • Erros do AI: { $ai_fail }
    • Erros do DB: { $db_fail }
    • Erros totais: { $total_fail }

detectar_estatisticas_titulo = Estatísticas

detectar_estatisticas_total = Total

detectar_estatisticas_ai_sucesso = AI detectou

detectar_estatisticas_db_sucesso = Salvo no DB

detectar_estatisticas_ai_falha = Erros do AI

detectar_estatisticas_db_falha = Erros do DB

Aqui está o conteúdo localizado para o português (pt):

lang_detect_stats_total_fail = Total de erros

log_file_caption =
    📄 Arquivo de log com erros.

account_connect_personal =
    🔐 <b>Gerenciamento de Conta do Telegram</b>

    📱 <b>Conta atual:</b> ✅ <i>Conta pessoal</i>
    📊 <b>Modo:</b> Canais ilimitados (dentro dos seus slots)

    Você pode se conectar novamente usando outro método ou desconectar.

account_connect_shared =
    🔐 <b>Gerenciamento de Conta do Telegram</b>

    🎁 <b>Conta atual:</b> <i>Conta gratuita do administrador</i>
    ⚠️ <b>Limitação:</b> A rastreabilidade de palavras-chave é permitida apenas em <b>1 grupo</b>.

    🔄 <i>Se houver problemas com a conta atual, clique em "Reconectar conta gratuita" abaixo.</i>
    💡 <i>Para rastrear múltiplos grupos simultaneamente, conecte sua conta pessoal.</i>

free_account_connected_success =
    🎉 <b>Conta gratuita do administrador conectada com sucesso!</b>

    📱 <b>Conta:</b> { $phone }
    👤 <b>Nome:</b> { $name }
    ⚠️ <b>Aviso:</b> A limitação de <b>1 grupo/canal</b> se aplica a essa conta gratuita.

    💡 <i>Se você precisar rastrear mais canais, pode se conectar à sua conta pessoal a qualquer momento.</i>

free_account_reconnected_success =
    🎉 <b>Conta gratuita reconectada com sucesso!</b>

    📱 <b>Nova conta:</b> { $phone }
    👤 <b>Nome:</b> { $name }
    ✅ <b>Status:</b> Ativa e pronta para rastreamento.

    ⚠️ <b>Aviso:</b> A limitação de 1 grupo se aplica a essa conta gratuita.

account_connect_none =
    🔐 <b>Gerenciamento de Conta do Telegram</b>

    ⚠️ <b>Conta atual:</b> <i>Não conectada</i>

    Para monitorar mensagens e palavras-chave, escolha um método de conexão:
    • <b>Conta pessoal</b> — sem limite de canais.
    • <b>Conta gratuita do administrador</b> — acesso gratuito, limitado a 1 grupo.

account_connected_free =
    ✅ Conta conectada com sucesso

no_free_accounts =
    ❌ Sem contas gratuitas disponíveis. Tente novamente mais tarde ou entre em contato com o administrador.

no_free_accounts_detailed =
    ⚠️ <b>Sem contas gratuitas disponíveis</b>

    Atualmente, não há contas gratuitas disponíveis do administrador.
    Conecte sua conta pessoal (pelo telefone ou via arquivo de sessão).

invalid_session_file =
    ❌ Isso não é um arquivo de sessão! Envie um arquivo com extensão `.session`

session_file_received =
    📥 Arquivo recebido: `{ $filename }`

    🔍 Verificando conta...

session_connected_success =
    ✅ <b>{ $filename }</b> — bem-sucedido!
    📱 { $phone } | 👤 { $name }
    💾 Salvo na sua base de dados pessoal.

session_validation_failed =
    ❌ <b>{ $filename }</b> — falha de validação.
    Por favor, verifique que o arquivo de sessão é atual e não está sendo usado em outro lugar.

session_check_error =
    ⚠️ Ocorreu um erro ao verificar a conta. Tente novamente mais tarde.

only_txt_files_supported =
    ⚠️ Somente arquivos .txt são suportados.

empty_file_no_usernames =
    ⚠️ O arquivo está vazio ou não contém nomes de usuários.

groups_upload_summary =
    ✅ Adicionados: { $added }
    ⚠️ Já existem: { $skipped }
    ❌ Erros: { $errors }

admin_found_accounts =
    🔍 Encontradas contas: { $count }

admin_db_actualization_start =
    🔄 Iniciando a atualização de { $total } grupos...

admin_using_account =
    📱 Usando conta: { $account }

admin_account_error =
    ❌ Erro de conta { $account }: { $error }

admin_critical_error =
    ❌ Erro crítico: { $error }

no_questions_in_db =
    📭 Não há perguntas na base de dados.

questions_export_caption =
    📦 Exportação de perguntas e respostas.

export_error =
    ❌ Ocorreu um erro durante a exportação: { $error }

launch_tracking_button = 🚀 Iniciar rastreamento

check_group_for_keywords_button = 🔍 Verificar grupo para palavras-chave

ai_search_button = ✨ Pesquisa AI

get_database_button = 📥 Obter Banco de Dados

instruction_button = 📖 Instruções

settings_button = ⚙️ Configurações

admin_panel_button = 🛡️ Painel de Administração

get_log_file_button = 📄 Obter Arquivo de Log

export_questions_button = Exportar Perguntas

assign_category_button = 🏷️ Atribuir Categoria

check_accounts_button = ✅ Verificar Contas

connect_account_button = 🔐 Conectar Conta

back_button = ⬅️ Voltar

fast_method_button = ⚡️ Rápido (g4f.free)

powerful_method_openrouter_button = 🚀 Poderoso (API Openrouter)

powerful_method_groq_button = 🚀 Poderoso (API GROQ)

all_database_button = 📥 Banco de Dados Completo

channels_database_button = 📥 Banco de Dados de Canais

groups_database_button = 📥 Banco de Dados de Grupos

select_category_button = 📂 Selecionar Categoria

investments_button = Investimentos

finance_and_personal_budget_button = Orçamento Financeiro e Pessoal

crypto_and_blockchain_button = Cripto e Blockchain

business_and_entrepreneurship_button = Negócios e Empreendedorismo

marketing_and_promotion_button = Marketing e Promoção

tech_and_it_button = Tecnologia e IT

education_and_self_development_button = Educação e Desenvolvimento Pessoal

work_and_career_button = Trabalho e Carreira

real_estate_button = Imóveis

health_and_medicine_button = Saúde e Medicina

travel_button = viagem

auto_and_transport_button = automóvel e transporte

shopping_and_discounts_button = compras e descontos

entertainment_and_leisure_button = entretenimento e lazer

politics_and_society_button = política e sociedade

science_and_research_button = ciência e pesquisa

sports_and_fitness_button = esportes e condicionamento físico

cooking_and_food_button = culinária e comida

fashion_and_beauty_button = moda e beleza

hobbies_and_creativity_button = hobbies e criatividade

russian_language_button = 🇷🇺 Russo

english_language_button = 🇬🇧 Inglês

stop_tracking_button = 🛑 Parar de rastrear

update_list_button = 🔁 Atualizar lista

enter_keyword_button = 🔍 Digite palavra-chave

delete_group_from_tracking_button = 🗑️ Excluir grupo do rastreamento

keywords_list_button = 🔍 Lista de palavras-chave

tracking_links_button = 🌐 Links de rastreamento

connect_group_for_messages_button = 📤 Conectar grupo para mensagens

change_language_button = 🌐 Mudar idioma

connect_free_account_button = 🔐 Conectar conta gratuita

keywords_export_caption = 📋 Exportar palavras-chave. Registros totais: { $count }

no_keywords_found = 📭 Você não tem palavras-chave salvas.

tracking_links_export_caption = 🔗 Exportar links de rastreamento. Registros totais: { $count }

no_tracking_links_found = 📭 Você não tem links de rastreamento.

excel_header_number = Número

excel_header_keyword = Palavra-chave

excel_header_username = Nome do canal/grupo

ai_search_button_user = 🤖 Pesquisa AI

excel_filename_all_db = Todos_os_Bancos.xlsx

excel_filename_channels_db = Bancos_de_Canais.xlsx

excel_filename_groups_db = Bancos_de_Grupos.xlsx

excel_sheet_name_search_results = Resultados de Pesquisa

excel_header_id = ID (Hash)

excel_header_name = Nome

excel_header_description = Descrição

excel_header_participants = Participantes

excel_header_category = Categoria

excel_header_type = Tipo

excel_header_language = Linguagem

excel_header_activity = Atividade

excel_header_link = Link

excel_header_date_added = Adicionado em

excel_sheet_name_groups = Grupos

excel_filename_groups_by_category = grupos_{ $category }.xlsx

excel_header_group_name = Nome

excel_header_group_description = Descrição

excel_header_group_type = Tipo

excel_header_group_participants = Participantes

excel_header_group_link = Link

excel_filename_telegram_groups = grupos_telegram_{ $timestamp }.xlsx

instruction_question_prompt = 🤖 <b>Pode me fazer qualquer pergunta sobre o uso do bot, e eu vou responder!</b>

ai_support_assistant_system_prompt = Você é um assistente de suporte qualificado para o bot Telegram AutoParseAlert. Sua tarefa é responder às perguntas dos usuários com base no conhecimento base estritamente fornecido. Se a resposta não estiver no conhecimento base, informe o usuário educadamente que você não tem essa informação e aconselhe a entrar em contato com o suporte. Responda na linguagem do usuário em texto legível sem formatação de marcação (não use caracteres de formatação Markdown

lang_detect_summary = ✅ Processamento concluído!

    📊 Estatísticas:
    • Total: { $total }
    • AI detectou: { $ai_success }
    • Salvo no BD: { $db_success }
    • Erros de AI: { $ai_fail }
    • Erros de BD: { $db_fail }
    • Erros totais: { $total_fail }

name_prompt = Nome

description_prompt = Descrição

Here is the translated Fluent (.ftl) localization content from English into Portuguese (pt):

CRITICAL REQUIREMENTS:
1. Keep ALL keys on the left side of '=' EXACTLY as they are. Never translate key names.
2. Keep ALL variables in braces like { $version }, { $count }, { $title }, etc. EXACTLY as they are.
3. Keep ALL HTML tags intact.
4. Keep the Fluent multiline indentation format.
5. Return ONLY the translated .ftl content. DO NOT include markdown code fences (no ``` or ```ftl), no explanations.

Content to translate:

sem_dados_prompt = Sem dados

ai_lang_detect_prompt =
    Determinar a língua principal do texto ou descrição da comunidade.
    Responda EXATAMENTE com uma palavra — o código de língua em ISO 639-1 (código de duas letras).
    Exemplos de respostas corretas: pt, en, es, zh, ar, hi, ja, ko, fr, de, it, nl, sv, pl, tr, vi, th, id, fa, he, uk, cs, el, ro, hu, fi, da, no, sk, bg, hr, sr, sl, et, lv, lt, mk, sq, mt, cy, eu, gl, ga, is, ms, sw, tl, ur, bn, ta, te, mr, gu, kn, ml, si, km, lo, my, am, hy, ka, az, uz, kk, ky, tg, tk, mn, ps, ku, sd, ne, si, lo, km, my, dz, bo, ug, yi, ha, yo, ig, zu, xh, st, tn, ts, ve, nr, ss, ch, rw, rn, mg, ln, kg, sw, tn.
    Se a língua não puder ser determinada de forma inequívoca ou o texto contém uma mistura de línguas sem uma dominante — responda: desconhecido.
    
    Texto para análise:
    { $user_input }

get_groups_without_category_message = 📊 <b>Estatísticas de Categoria:</b>

    🗃️ Grupos sem categoria: { $count }

    Pressione '🏷️ Atribuir Categoria' para iniciar o AI

download_free_success = 📥 Exportando banco de dados (1 download gratuito por dia). Iniciando download...

download_cooldown_message =
    ⚠️ Você já baixou o banco de dados em 24 horas.
    Próximo download gratuito estará disponível em <b>{ $time }</b>.
    
    Você pode baixar o banco de dados agora por 5 ⭐.
    Seu saldo de estrelas no bot: <b>{ $stars }</b> ⭐

pay_from_balance_btn = 🪙 Deduzir 5 ⭐ do saldo

pay_direct_btn = ⭐ Pagar 5 ⭐ diretamente

cancel_btn = ❌ Cancelar

download_paid_success = ✅ Pagamento/dedução de 5 ⭐ bem-sucedida. Iniciando download do banco de dados...

download_insufficient_stars = ❌ Insuficiente estrelas no seu saldo.

stars_topup_success = 🎉 Saldo de estrelas atualizado com sucesso por { $amount } ⭐! Seu saldo atual: { $balance } ⭐.

stars_added_admin = ⭐ Administrador creditou { $amount } ⭐ para você. Saldo atual: { $balance } ⭐.

topup_stars_button = 💳 Recarregar Estrelas

stars_balance_msg = 👤 <b>Sua Conta de Estrelas:</b>\n\nSaldo: <b>{ $stars }</b> ⭐\n\nAqui você pode recarregar sua conta de estrelas do Telegram para baixar bancos de dados pagos.

stars_invoice_title = Recarregar Conta de Estrelas

stars_invoice_desc = Compra de { $amount } Estrelas do Telegram para uso no bot

stars_invoice_dl_title = Baixar Banco de Dados

stars_invoice_dl_desc = Baixar banco de dados uma vez, ignorando o limite diário

excel_filename_category_db = banco_de_dados_por_categoria.xlsx

export_category_caption = 📂 Banco de dados por categoria "{ $category }". Registros totais: { $total_records }.

generating_database_wait = ⏳ Gerando arquivo de banco de dados, isso pode levar algum tempo. Por favor, aguarde...

btn_add_channels_tracking = ➕ Adicionar Canais (texto ou .txt)

btn_channels_list = 📋 Lista de Canais

btn_export_excel = 📥 Exportar para Excel

btn_clear_all_channels = 🧹 Limpar Todos os Canais

btn_tracking_channels = 🌐 Canais Monitores

btn_keywords = 🔍 Palavras-chave

btn_notification_group = 📢 Grupo de Notificação

Here is the translated content in Portuguese (pt):

btn_transfer_settings = 🔄 Configuração de Transferência para Usuário

btn_personal_tracking = 🎯 Rastreamento

btn_connect_account_session = 📄 Conectar conta via sessão (.session)

btn_connect_account_phone = 📱 Conectar conta pessoal (por telefone)

btn_connect_free_account = 🎁 Conta gratuita do administrador (1 grupo)

btn_reconnect_free_account = 🔄 Reconectar conta gratuita

btn_disconnect_account = ❌ Desconectar conta atual

btn_to_tracking_menu = 🎯 Para menu de rastreamento

btn_to_settings_menu = ⚙️ Para menu de configuração

btn_main_menu = 🏠 Menu Principal

btn_add_keywords = ➕ Adicionar Palavras-chave

btn_keywords_list = 📋 Lista de Palavras-chave

btn_export_keywords = 📥 Exportar Palavras-chave

btn_goto_notification_group = 🔗 Abrir Grupo de Notificação

btn_notification_group_not_created = 🔗 Grupo ainda não criado

btn_recreate_notification_group = 🔄 Recrear Grupo

btn_nav_prev = ◀️ Voltar

btn_nav_next = Próximo ▶️

btn_confirm_clear = ✅ Sim, limpar

btn_cancel = ❌ Cancelar

btn_broadcast_users = 📢 Transmitir para usuários

btn_broadcast_send = 🚀 Lançar Transmissão

btn_broadcast_cancel = ❌ Cancelar Transmissão

btn_pt_add_tracking = ➕ Adicionar Grupo de Rastreamento

btn_pt_buy_slot = ⭐ Comprar +1 Slot (2 Estrelas)

btn_pt_my_groups = 📋 Meus Grupos Monitorados

btn_pt_stats = 📊 Estatísticas

btn_keypad_clear = ❌ Limpar

btn_keypad_submit = ✅ Enviar

btn_keypad_cancel = 🚫 Cancelar

btn_pt_edit_record = ⚙️ Editar

btn_pt_buy_stars_slots = ⭐ Comprar slots (Estrelas do Telegram)

btn_pt_connect_personal = 📱 Conectar conta pessoal

btn_pt_create_notification_group = 📢 Criar Grupo de Notificação

settings_channels_title = 🌐 <b>Canais Monitores</b>\n\n📊 Total de canais: <b>{ $total }</b>\n\nEscolha uma ação:

settings_channels_empty = 📭 A lista de canais está vazia.

settings_channels_list_title = 📋 <b>Lista de Canais</b> (página { $page }/{ $total_pages }) · total: { $total }\n

settings_channels_list_hint = \n<i>Clique ❌ em um canal para removê-lo.</i>

settings_channel_deleted = ✅ Canal removido: { $channel }

settings_channel_not_found = ⚠️ Canal não encontrado.

settings_channels_clear_confirm = 🧹 <b>Limpar lista de canais inteira?</b>\n\n<b>{ $total }</b> canal(s) será deletado. Essa ação não pode ser desfeita.

settings_channels_cleared = ✅ <b>Lista de canais limpa.</b>\n\nCanais deletados: <b>{ $count }</b>

settings_keywords_title = 🔍 <b>Palavras-chave</b>\n\n📊 Total de palavras-chave: <b>{ $total }</b>\n\nEscolha uma ação:

settings_keywords_empty = 📭 A lista de palavras-chave está vazia.

settings_keywords_list_title = 🔍 <b>Palavras-chave</b> (página { $page }/{ $total_pages }) · total: { $total }\n

settings_keywords_list_hint = \n<i>Clique ❌ em uma palavra para removê-la.</i>

settings_keyword_deleted = ✅ Removido: { $keyword }

settings_keyword_not_found = ⚠️ Palavra não encontrada.

settings_notification_created = 📢 <b>Grupo de Notificação</b>\n\n✅ Grupo criado.\n🔗 <a href='{ $link }'>Ir para o grupo</a>

settings_notification_not_created = 📢 <b>Grupo de Notificação</b>\n\n❌ Grupo não criado ainda.\n\n<i>Crie um grupo via «🎯 Monitoramento Pessoal».</i>

settings_notification_alert_no_group = ❌ O grupo não foi criado. Vá para «🎯 Monitoramento Pessoal» para criá-lo.

settings_notification_recreate_text = 🔄 <b>Recriar Grupo de Notificação</b>\n\nPara recriar o grupo, vá para «🎯 Monitoramento Pessoal» → «➕ Adicionar Monitoramento».\n\n<i>Um novo grupo será criado automaticamente ao adicionar o monitoramento.</i>

connect_group_prompt = 🔗 <b>Envie um link ou nome de usuário do grupo/canal para monitorar</b>\n\nExemplo:\n<code>https://t.me/python_jobs</code>\nor <code>@python_jobs</code>\n\nPode enviar vários links, um por linha.

connect_group_no_links = ⚠️ Por favor, envie ao menos um link ou nome de usuário.

connect_group_invalid_links = ⚠️ Por favor, verifique se os links são válidos.

connect_group_saved = ✅ Grupo(s) salvo no banco de dados.

Aqui está a tradução da localização em pt:

connect_group_text_required = ⚠️ Por favor, envie um link ou nome de usuário como mensagem de texto.

connect_group_file_invalid_links = ⚠️ Por favor, verifique se os links no arquivo são válidos.

connect_group_file_required = ⚠️ Por favor, envie um arquivo TXT contendo links ou nomes de usuários.

transfer_rights_prompt = 🔄 <b>Transferir configurações para outro usuário</b>\n\nEnvie o ID do Telegram do usuário que deseja copiar as suas canais e palavras-chave.\n\n<i>Exemplo: <code>1234567890</code></i>

transfer_rights_invalid_id = ⚠️ ID inválido. O ID deve conter apenas números.\n\nTente novamente do menu de configuração.

transfer_rights_self = ⚠️ Não é possível transferir configurações para si mesmo.

transfer_rights_not_found = ⚠️ O usuário com o ID <code>{ $target_user_id }</code> ainda não iniciou o bot.

transfer_rights_success = ✅ <b>Configurações transferidas com sucesso para o usuário { $target_user_id }!</b>\n\n📋 Canais adicionados: <b>{ $groups }</b>\n🔑 Palavras-chave adicionadas: <b>{ $keywords }</b>

delete_group_invalid_format = ⚠️ <b>Não foi possível reconhecer o formato do link.</b>\n\nFormatos suportados:\n• <code>@nome_do_canal</code>\n• <code>https://t.me/nome_do_canal</code>\n• <code>https://t.me/+Hash_privado</code>\n• <code>https://t.me/joinchat/Hash</code>

keywords_added_success = ✅ Palavras-chave adicionadas.\n\n📊 Total de palavras-chave: <b>{ $count }</b>

pt_no_slots_alert = ⚠️ Todos os slots estão em uso! Compre um slot adicional.

pt_ask_link = 🔗 <b>Insira o link para o grupo ou canal para rastrear</b>\n\n<i>Exemplo: <code>https://t.me/python_jobs</code> ou <code>@python_jobs</code></i>

pt_invalid_link = ⚠️ Por favor, insira um link válido (https://t.me/...) ou @nome_do_usuario.

pt_checking_group = 🔄 <i>Verificando o grupo e recuperando informações...</i>

pt_ask_keywords = 🔑 Insira as palavras-chave para rastrear separadas por vírgulas:

pt_saved_success = ✅ <b>Configurações de rastreamento salvas!</b>

pt_step2_created =
    ✅ <b>Grupo criado!</b>

    1. Siga o link e adira ao grupo criado: <a href='{ $link }'>{ $link }</a>
    <i>(O bot { $bot_name } já é administrador do grupo)</i>

    <b>Passo 2:</b> Insira as palavras-chave para rastrear no grupo (separadas por vírgulas):
    <i>Exemplo: python, job, remote</i>

pt_configured_success =
    🎉 <b>Configuração de rastreamento pessoal configurada com sucesso!</b>

    📌 <b>Alvo de rastreamento:</b> { $target }
    🔑 <b>Palavras-chave:</b> { $keywords }
    🔗 <b>Grupo para resultados:</b> <a href='{ $link }'>Acesse o grupo</a>

    <i>Alertas sobre correspondências serão enviados diretamente para o seu grupo criado!</i>

pt_alert_message =
    🎯 <b>Correspondência de palavra-chave:</b> <code>{ $keyword }</code>

    💬 <b>Texto da mensagem:</b>
    { $text }

    🔗 <a href='{ $link }'>Acesse a mensagem</a>

pt_no_active_trackings = ℹ️ Você não tem rastreamentos pessoais ativos ainda.

pt_record_not_found = Erro: Registro não encontrado

pt_edit_prompt = ⚙️ <b>Editar Rastreamento</b>\n\n🔗 Link atual: { $link }\n🔑 Palavras-chave: { $keywords }\n\nEnvie um novo link do grupo/canal:

pt_updating_group = 🔄 <i>Atualizando a subscrição e o grupo...</i>

pt_updated_success = ✅ <b>Configurações de rastreamento atualizadas com sucesso!</b>

pt_stats_msg = 📊 <b>Estatísticas de Rastreamento Pessoal</b>\n\n👥 Total de usuários: <b>{ $users }</b>\n🎯 Total de rastreamentos: <b>{ $trackings }</b>

pt_code_prompt = 🔢 Insira o código de verificação de 5 dígitos:

pt_invalid_code_alert = ❌ Código de verificação inválido! Tente novamente.

pt_code_expired_alert = ❌ Código de verificação expirou! Peça o código novamente.

Aqui está o conteúdo localizado para o português:

pt_login_error_alert = ❌ Erro de login: { $error }

pt_checking_2fa = 🔄 <i>Verificando senha de 2FA...</i>

pt_auth_success =
    🎉 <b>Autorização e conexão de conta realizadas com sucesso!</b>

    👤 <b>Nome:</b> { $name }
    📱 <b>Telefone:</b> +{ $phone }
    🆔 <b>ID do Telegram:</b> <code>{ $tg_id }</code>

    ✅ Sessão salva no banco de dados e pronta para rastreamento.

pt_auth_2fa_success =
    🎉 <b>Autorização de conta realizada com sucesso com senha de 2FA!</b>

    👤 <b>Nome:</b> { $name }
    📱 <b>Telefone:</b> +{ $phone }
    🆔 <b>ID do Telegram:</b> <code>{ $tg_id }</code>

    ✅ Sessão salva no banco de dados com sucesso.

pt_auth_code_invalid_screen =
    📩 <b>Código de verificação enviado para o seu Telegram!</b>

    📱 <b>Número:</b> <code>{ $phone }</code>
    🔢 <b>Código inserido:</b> <code>_ _ _ _ _</code>

    ❌ <b>Erro: Código inválido. Tente selecionar os dígitos novamente:</b>

pt_auth_2fa_prompt =
    🔐 <b>Autorização de 2FA habilitada na sua conta!</b>

    Por favor, insira sua senha de nuvem como texto em resposta:

pt_auth_2fa_invalid =
    ❌ <b>Senha de 2FA inválida!</b>

    Por favor, insira a senha de nuvem correta como texto:

pt_auth_error = ❌ Erro de autorização: { $error }

pt_auth_cancelled = 🚫 Autorização cancelada.

pt_phone_prompt = 📱 <b>Conectar conta do Telegram</b>\n\nInsira o seu número de telefone no formato internacional (por exemplo, <code>+79991234567</code>):

pt_phone_invalid = ❌ Número de telefone inválido inserido. Tente novamente.

pt_phone_flood = ⏳ Muitas tentativas. Aguarde { $seconds } segundos.

pt_code_request_error = ❌ Erro ao solicitar código: { $error }

pt_code_need_5_digits = ⚠️ Insira todos os 5 dígitos do código de verificação!

pt_sending_code_status = ⏳ Enviando código de verificação para { $phone }...

pt_enter_code_keypad = 📱 <b>Código de verificação enviado no Telegram</b>\n\nInsira os dígitos no teclado abaixo:\n\nInserido: <b>{ $code }</b>

pt_enter_2fa_prompt = 🔐 <b>Autorização de 2FA requerida</b>\n\nInsira sua senha de nuvem de 2FA:

pt_no_account_connected = ⚠️ Nenhuma conta conectada. Conecte uma conta.

pt_record_error = Erro de registro.

admin_access_denied = ⛔ Acesso negado. Apenas administradores.

admin_broadcast_prompt = 📢 <b>Enviar mensagem para os usuários</b>\n\nEnvie a mensagem que deseja enviar para todos os usuários do bot.\n\n• Suporta formatação <b>HTML</b> (negrito, itálico, links).\n• Você pode anexar fotos, vídeos, animações ou documentos.\n\n<i>Para cancelar, clique em «Voltar» abaixo.</i>

admin_broadcast_preview_title = 👁️ <b>Prévia da mensagem de broadcast:</b>

admin_broadcast_preview_params = 📊 <b>Parâmetros da mensagem de broadcast:</b>\n\n👥 Total de destinatários no banco de dados: <b>{ $total }</b>\n\nConfirme a envio ou cancele:

admin_broadcast_cancelled = ❌ <b>Mensagem de broadcast cancelada.</b>

admin_broadcast_not_found = ⚠️ Erro: mensagem de broadcast não encontrada.

admin_broadcast_started = 🚀 <b>Mensagem de broadcast iniciada... Aguarde.</b>

admin_broadcast_progress = 🚀 <b>Enviando mensagem de broadcast...</b>\n\nProgresso: <b>{ $current }/{ $total }</b>\n✅ Enviado: <b>{ $sent }</b>\n🚫 Bloqueado pelo usuário: <b>{ $blocked }</b>\n⚠️ Erros: <b>{ $errors }</b>

admin_broadcast_report = 🏁 <b>Mensagem de broadcast concluída!</b>\n\n📊 <b>Relatório final:</b>\n• Total de destinatários: <b>{ $total }</b>\n• ✅ Enviado com sucesso: <b>{ $sent }</b>\n• 🚫 Bloqueado pelo usuário: <b>{ $blocked }</b>\n• ⚠️ Outros erros: <b>{ $errors }</b>

Here is the translated Fluent (.ftl) localization content from English into Portuguese (pt):

CRITICAL REQUIREMENTS:
1. Keep ALL keys on the left side of '=' EXACTLY as they are. Never translate key names.
2. Keep ALL variables in braces like { $version }, { $count }, { $title }, etc. EXACTLY as they are.
3. Keep ALL HTML tags intact.
4. Keep the Fluent multiline indentation format.
5. Return ONLY the translated .ftl content. DO NOT include markdown code fences (no ``` or ```ftl), no explanations.

Content to translate:
parser_notification_group_missing = ⚠️ <b>Grupo de notificação não encontrado!</b>\n\nAntes de iniciar o rastreamento, você deve criar um grupo-alvo para receber alertas.\nClique no botão abaixo para configurá-lo:

parser_free_account_limit = ⚠️ <b>O limite de rastreamento foi excedido!</b>\n\nVocê está usando uma <b>conta compartilhada gratuita</b>, que permite rastrear apenas <b>1 canal</b>.\n\nPara rastrear mais canais:\n• Conecte sua conta do Telegram pessoal (ilimitado)\n• Ou compre slots adicionais com estrelas do Telegram.

welcome_choose_lang = 👋 Olá! Por favor, escolha sua língua / Привет! Пожалуйста, выберите язык:

no_connected_account = Sem conta conectada. Por favor, conecte uma conta.

excel_export_caption = 📊 Resultados de busca de grupos em Excel

db_export_caption = 📊 Exportação de banco de dados em Excel

found_groups_caption = 📊 Encontrados { $count } grupos/canais

nightly_check_btn = Verificação noturna (01:00)

nightly_check_on = LIGADO

nightly_check_off = DESLIGADO

nightly_check_toggled_on = 🔔 A verificação noturna do banco de dados às 01:00 está HABILITADA.

nightly_check_toggled_off = 🔕 A verificação noturna do banco de dados está DESABILITADA.

btn_pt_accounts = 👥 Meus Campanhas / Contas

btn_pt_rename_acc = ✏️ Alterar Título/Tema

btn_pt_tech_group = 📣 Grupo Técnico

btn_pt_sync_dialogs = 📥 Importar Chats de Conta

btn_pt_toggle_all_chats = 🌐 Todos os Chats de Conta: { $status }

btn_pt_acc_keywords = 🔑 Palavras-chave do Tópico

btn_pt_acc_groups = 👥 Grupos do Tópico

btn_pt_start_acc = ▶️ Iniciar Esta Conta

btn_pt_stop_acc = ⏹️ Parar Esta Conta

btn_pt_start_all = 🚀 Iniciar Todas as Contas

btn_pt_stop_all = 🛑 Parar Todas as Contas

pt_acc_card =
    📱 <b>Campanha:</b> «{ $title }» ({ $phone })
    📡 <b>Estado:</b> { $status }
    📣 <b>Grupo Técnico:</b> { $tech_group }
    🔑 <b>Palavras-chave:</b> { $keywords_count } pcs.
    👥 <b>Chats-alvo:</b> { $groups_count } pcs.
    🌐 <b>Todos os Chats de Conta:</b> { $all_chats_mode }

    💡 <i>No modo «Todos os Chats de Conta», o bot rastreia todos os grupos abertos e fechados que a conta se juntou via tdata ou manualmente.</i>

pt_ask_rename_acc = Insira um novo título ou tema para esta campanha (por exemplo: <b>Alfombras</b> ou <b>Refrigeradores</b>):

pt_acc_renamed = ✅ Título da campanha atualizado com sucesso para: <b>{ $title }</b>

pt_ask_acc_keywords =
    Insira palavras-chave para a campanha «{ $title }» separadas por vírgulas ou em linhas novas:
    <i>(Exemplo: sofá, cama, móveis)</i>

pt_acc_keywords_saved = ✅ Palavras-chave da campanha «{ $title }» salvas! Adicionados: <b>{ $count }</b> pcs.

Here is the translated content in Portuguese (pt):

pt_dialogs_syncing = ⏳ Escanear diálogos de conta via Telethon...

pt_dialogs_synced = ✅ Sincronização concluída! Encontrados e vinculados grupos/canais: <b>{ $count }</b> pcs.

pt_toggle_all_chats_done = «Modo de todos os Chats da Conta» para campanha «{ $title }»: <b>{ $status }</b>

pt_closed_group_hint =
    💡 <b>Suporte a Grupos Fechados:</b>
    • Enviar link de convite: <code>https://t.me/+hash</code>
    • Enviar ID numérico do chat fechado: <code>-100...</code>
    • Enviar título exato do chat fechado (onde o conta já é um membro)
    • Ou clique <b>«📥 Importar Chats da Conta»</b> para carregar instantaneamente todos os chats do tdata!
