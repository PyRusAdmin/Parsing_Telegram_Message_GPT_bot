### 📡 用于关键词监控和 AI 搜索的 Telegram 机器人 (https://t.me/AutoParseAlertBot)

<p align="center">
  <a href="README_en.md">English</a> •
  <b>中文 (简体)</b> •
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

- **版本:** 0.1.0
- **更新日期:** 2026年9月4日

该机器人可实时分析指定 Telegram 群组和频道中的新消息，即时通知关键词匹配项。它还利用人工智能（Groq、OpenRouter）智能发现新的利基 Telegram 社区。

## ✨ 主要特性

- 🚀 **实时监控:** 关键词匹配消息即时转发至您的目标群组。
- 🤖 **两级 AI 搜索:** 本地数据库检索与 Telegram 全网深度智能挖掘。
- 📊 **导出为 XLSX:** 将搜索结果和监控渠道导出为 Excel，支持按分类和活跃度筛选。
- 🛡️ **管理面板:** 包含数据库更新、AI 批量分类和群聊语种识别等工具。
- 🌍 **多语言支持:** 完整支持中文、俄语和英语等语言（Fluent i18n）。
- 🔐 **多账号支持:** 支持多 `.session` 文件（StringSession），有效避免 Telegram API 限制。
- 💰 **限制与 Telegram Stars:** 免费数据库导出限制（每 24 小时 1 次）。额外下载可通过 5 个 Telegram Stars 解锁（从余额扣除或直接支付）。

<p align="center">
  <img src="doc/MessageParser.jpg" alt="机器人界面预览" width="30%" />
</p>

## 📝 核心功能

- **监控:** 在不限数量的群组/频道中实时跟踪关键词。
- **AI 搜索:** 通过语义自然语言提示词发现目标社群。
- **智能导出:** 按特定分类（商业、加密货币、招聘等）下载群组数据。
- **活跃度检测:** 自动标记社群状态为 `active`（活跃）、`inactive`（不活跃）或 `unknown`（未知）。
- **批量导入:** 支持通过 `.txt` 文本文件批量上传监控列表。
- **代理支持:** 支持 HTTP/SOCKS5 代理，确保 AI 和 Telegram API 稳定连接。

## ⚙️ 快速上手

1. **安装依赖:**
   ```bash
   python setup.py
   ```
   *该脚本会自动安装 `requirements.txt` 并帮助生成 `.env` 配置文件。*

2. **配置环境变量:**
   填写项目根目录下的 `.env` 文件：
   ```env
   BOT_TOKEN=...
   ID=... # 来自 my.telegram.org 的 API_ID
   HASH=... # 来自 my.telegram.org 的 API_HASH
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

3. **启动运行:**
   ```bash
   python main.py
   ```

## 👑 管理员功能

拥有管理员权限的用户可使用专属控制面板：

- **🏷️ 分类归档:** 使用大语言模型 (LLM) 自动将群组按主题分类。
- **🌐 语言过滤:** 识别群组交流语种，精准提取优质区域数据。
- **🔄 数据更新:** 批量更新群组元数据并校验社群有效性。

## 📊 活跃度判定标准

| 状态          | 说明                                                  |
|:--------------|:------------------------------------------------------|
| 🟢 `active`   | 最新一条消息发布时间 **≤ 30 天**                       |
| 🔴 `inactive` | 最新一条消息发布时间 **> 30 天**                       |
| ⚪ `unknown`  | 无法获取日期（隐私设置或权限限制）                      |

---

## 虚拟环境配置

Windows:

命令提示符 (cmd):
```cmd
venv\Scripts\activate.bat
```

PowerShell:
```powershell
venv\Scripts\Activate.ps1
```

## 🧑‍💻 技术栈

- **开发框架:** `aiogram 3.x` (Bot API), `Telethon` (User API)
- **数据库:** `SQLite` + `Peewee ORM`
- **人工智能:** `Groq`, `OpenRouter`, `G4F`
- **本地化:** `Project Fluent`

---
> 📘 详细文档请参见 [doc/doc.md](doc/doc.md) 或在机器人内部发送 `/help` 命令获取。
