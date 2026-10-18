### 📡 Telegram Bot for Keyword Tracking & AI Search (https://t.me/AutoParseAlertBot)

<p align="center">
  <b>English</b> •
  <a href="README_zh.md">中文 (简体)</a> •
  <a href="README_hi.md">हिन्दी</a> •
  <a href="README_es.md">Español</a> •
  <a href="README_fr.md">Français</a> •
  <a href="README_ar.md">العربية</a> •
  <a href="README_bn.md">বাংলা</a> •
  <a href="README_pt.md">Português</a> •
  <a href="README.md">Русский</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange.svg)](https://docs.aiogram.dev/)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-blueviolet.svg)](https://docs.telethon.dev/)

- **Version:** 0.1.0
- **Release Date:** September 04, 2026

The bot analyzes new messages in specified Telegram groups and channels in real-time, instantly notifying about keyword matches. It also leverages AI (Groq, OpenRouter) for intelligent discovery of new niche Telegram communities.

## ✨ Key Features

- 🚀 **Real-time Monitoring:** Instant forwarding of keyword-matched messages to your destination group.
- 🤖 **Two-level AI Search:** Local database search and global search across Telegram.
- 📊 **XLSX Export:** Export search results and monitored channels to Excel with filtering by category and activity.
- 🛡️ **Admin Panel:** Tools for database updates, bulk AI categorization, and chat language detection.
- 🌍 **Multi-language:** Full support for Russian and English (Fluent i18n).
- 🔐 **Multi-account:** Support for multiple `.session` files (StringSession) to bypass Telegram limits.
- 💰 **Limits & Telegram Stars:** Free database export limit (once every 24 hours). Additional downloads available for 5 Telegram Stars (balance deduction or direct payment).

<p align="center">
  <img src="doc/MessageParser.jpg" alt="Bot interface preview" width="30%" />
</p>

## 📝 Core Functions

- **Monitoring:** Track keywords across an unlimited list of groups/channels.
- **AI Search:** Discover target groups using semantic natural language prompts.
- **Smart Export:** Download groups filtered by specific categories (business, crypto, jobs, etc.).
- **Activity Detection:** Tag communities with `active`, `inactive`, or `unknown` statuses.
- **Batch Addition:** Upload monitoring lists via `.txt` files.
- **Proxy Support:** HTTP/SOCKS5 proxy support for stable AI and Telegram API connectivity.

## ⚙️ Quick Start

1. **Install Dependencies:**
   ```bash
   python setup.py
   ```
   *The script installs `requirements.txt` and helps generate your `.env` configuration.*

2. **Environment Configuration:**
   Fill in `.env` in the root directory:
   ```env
   BOT_TOKEN=...
   ID=... # API_ID from my.telegram.org
   HASH=... # API_HASH from my.telegram.org
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

3. **Run:**
   ```bash
   python main.py
   ```

## 👑 Administrator Features

Users with admin privileges have access to a dedicated management dashboard:

- **🏷️ Categorization:** Automatic classification of groups into topics using LLMs.
- **🌐 Language Filter:** Detect chat language to build high-quality regional datasets.
- **🔄 Actualization:** Bulk update group metadata and check community availability.

## 📊 Activity Detection

| Status        | Description                                           |
|:--------------|:------------------------------------------------------|
| 🟢 `active`   | Latest message was posted **≤ 30 days** ago           |
| 🔴 `inactive` | Latest message was posted **> 30 days** ago           |
| ⚪ `unknown`  | Could not determine date (privacy/access limitations) |

---

## Setting up Virtual Environment

Windows:

In Command Prompt (cmd):
```cmd
venv\Scripts\activate.bat
```

In PowerShell:
```powershell
venv\Scripts\Activate.ps1
```

## 🧑‍💻 Tech Stack

- **Framework:** `aiogram 3.x` (Bot API), `Telethon` (User API)
- **Database:** `SQLite` + `Peewee ORM`
- **AI:** `Groq`, `OpenRouter`, `G4F`
- **Localization:** `Project Fluent`

---
> 📘 Detailed documentation is available in [doc/doc.md](doc/doc.md) or via the `/help` command inside the bot.
