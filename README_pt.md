### 📡 Bot do Telegram para monitoramento de palavras-chave e busca com IA (https://t.me/AutoParseAlertBot)

<p align="center">
  <a href="README_en.md">English</a> •
  <a href="README_zh.md">中文 (简体)</a> •
  <a href="README_hi.md">हिन्दी</a> •
  <a href="README_es.md">Español</a> •
  <a href="README_fr.md">Français</a> •
  <a href="README_ar.md">العربية</a> •
  <a href="README_bn.md">বাংলা</a> •
  <b>Português</b> •
  <a href="README.md">Русский</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange.svg)](https://docs.aiogram.dev/)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-blueviolet.svg)](https://docs.telethon.dev/)

- **Versão:** 0.1.0
- **Data de atualização:** 04 de setembro de 2026

O bot analisa novas mensagens em grupos e canais selecionados do Telegram em tempo real, notificando instantaneamente sobre correspondências de palavras-chave. Ele também utiliza IA (Groq, OpenRouter) para descobrir inteligentemente novas comunidades temáticas no Telegram.

## ✨ Principais recursos

- 🚀 **Monitoramento em tempo real:** Encaminhamento instantâneo de mensagens com palavras-chave correspondentes para o seu grupo de destino.
- 🤖 **Busca com IA em dois níveis:** Pesquisa no banco de dados local e pesquisa global em todo o Telegram.
- 📊 **Exportação para XLSX:** Exportação de resultados de pesquisa e monitoramento para Excel com filtros por categoria e nível de atividade.
- 🛡️ **Painel de administração:** Ferramentas para atualização do banco de dados, categorização em massa via IA e detecção do idioma das conversas.
- 🌍 **Multilíngue:** Suporte completo para português, russo, inglês e outros idiomas (Fluent i18n).
- 🔐 **Multicontas:** Suporte a múltiplos arquivos `.session` (StringSession) para contornar limites do Telegram.
- 💰 **Limites e Telegram Stars:** Limite de exportação gratuita do banco de dados (1 vez a cada 24 horas). Downloads adicionais disponíveis por 5 Telegram Stars.

<p align="center">
  <img src="doc/MessageParser.jpg" alt="Prévia da interface do bot" width="30%" />
</p>

## 📝 Funções principais

- **Monitoramento:** Rastreamento de palavras-chave em uma lista ilimitada de grupos e canais.
- **Busca com IA:** Descoberta de novos grupos-alvo por meio de prompts semânticos em linguagem natural.
- **Exportação inteligente:** Download do banco de dados filtrado por categorias específicas (negócios, cripto, empregos, etc.).
- **Detecção de atividade:** Marcação de comunidades com os status `active`, `inactive` ou `unknown`.
- **Adição em massa:** Envio de listas de monitoramento através de arquivos `.txt`.
- **Suporte a Proxy:** Compatibilidade com proxies HTTP/SOCKS5 para conexão estável com IA e a API do Telegram.

## ⚙️ Início rápido

1. **Instalar dependências:**
   ```bash
   python setup.py
   ```
   *O script instalará `requirements.txt` e ajudará a gerar o arquivo `.env`.*

2. **Configuração de ambiente:**
   Preencha o arquivo `.env` na raiz do projeto:
   ```env
   BOT_TOKEN=...
   ID=... # API_ID em my.telegram.org
   HASH=... # API_HASH em my.telegram.org
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

3. **Executar:**
   ```bash
   python main.py
   ```

## 👑 Recursos de Administrador

Usuários com privilégios de administrador têm acesso a um painel de controle exclusivo:

- **🏷️ Categorização:** Distribuição automática de grupos em tópicos temáticos usando modelos de linguagem (LLMs).
- **🌐 Filtro de idioma:** Identificação do idioma de comunicação nos chats para amostragem regional precisa.
- **🔄 Atualização:** Atualização em lote dos metadados dos grupos e verificação de disponibilidade.

## 📊 Determinação de atividade

| Status        | Descrição                                                     |
|:--------------|:--------------------------------------------------------------|
| 🟢 `active`   | A última mensagem foi postada há **≤ 30 dias**               |
| 🔴 `inactive` | A última mensagem foi postada há **> 30 dias**               |
| ⚪ `unknown`  | Não foi possível obter a data (restrições de privacidade)     |

---

## Configuração do ambiente virtual

Windows:

No prompt de comando (cmd):
```cmd
venv\Scripts\activate.bat
```

No PowerShell:
```powershell
venv\Scripts\Activate.ps1
```

## 🧑‍💻 Stack tecnológica

- **Framework:** `aiogram 3.x` (Bot API), `Telethon` (User API)
- **Banco de dados:** `SQLite` + `Peewee ORM`
- **IA:** `Groq`, `OpenRouter`, `G4F`
- **Localização:** `Project Fluent`

---
> 📘 A documentação detalhada está disponível em [doc/doc.md](doc/doc.md) ou através do comando `/help` dentro do bot.
