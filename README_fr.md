### 📡 Bot Telegram pour le suivi des mots-clés et la recherche par IA (https://t.me/AutoParseAlertBot)

<p align="center">
  <a href="README_en.md">English</a> •
  <a href="README_zh.md">中文 (简体)</a> •
  <a href="README_hi.md">हिन्दी</a> •
  <a href="README_es.md">Español</a> •
  <b>Français</b> •
  <a href="README_ar.md">العربية</a> •
  <a href="README_bn.md">বাংলা</a> •
  <a href="README_pt.md">Português</a> •
  <a href="README.md">Русский</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange.svg)](https://docs.aiogram.dev/)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-blueviolet.svg)](https://docs.telethon.dev/)

- **Version :** 0.1.0
- **Date de mise à jour :** 04 septembre 2026

Le bot analyse les nouveaux messages dans des groupes et canaux Telegram sélectionnés en temps réel, vous alertant immédiatement des correspondances de mots-clés. Il exploite également l'IA (Groq, OpenRouter) pour découvrir intelligemment de nouvelles communautés Telegram ciblées.

## ✨ Fonctionnalités clés

- 🚀 **Surveillance en temps réel :** Transfert instantané des messages contenant les mots-clés vers votre groupe de destination.
- 🤖 **Recherche IA à deux niveaux :** Recherche locale dans la base de données et recherche globale sur l'ensemble de Telegram.
- 📊 **Exportation XLSX :** Téléchargement des résultats de recherche et de surveillance sous Excel avec filtrage par catégorie et niveau d'activité.
- 🛡️ **Panneau d'administration :** Outils de mise à jour de la base de données, catégorisation par lots par IA et détection de la langue des discussions.
- 🌍 **Multilingue :** Prise en charge complète du français, du russe, de l'anglais et d'autres langues (Fluent i18n).
- 🔐 **Multi-comptes :** Prise en charge de plusieurs fichiers `.session` (StringSession) pour contourner les limites imposées par Telegram.
- 💰 **Limites et Telegram Stars :** Exportation gratuite de la base de données (1 fois toutes les 24 heures). Téléchargements supplémentaires disponibles pour 5 Telegram Stars.

<p align="center">
  <img src="doc/MessageParser.jpg" alt="Aperçu de l'interface du bot" width="30%" />
</p>

## 📝 Fonctions principales

- **Surveillance :** Suivi des mots-clés dans une liste illimitée de groupes et de canaux.
- **Recherche IA :** Découverte de nouveaux groupes cibles grâce à des requêtes sémantiques.
- **Export intelligent :** Téléchargement de la base de données selon des catégories spécifiques (business, crypto, emploi, etc.).
- **Détection d'activité :** Marquage des communautés avec les statuts `active`, `inactive` ou `unknown`.
- **Ajout groupé :** Chargement de listes de canaux via des fichiers `.txt`.
- **Support Proxy :** Prise en charge des proxys HTTP/SOCKS5 pour une connectivité stable avec l'IA et l'API Telegram.

## ⚙️ Démarrage rapide

1. **Installer les dépendances :**
   ```bash
   python setup.py
   ```
   *Le script installe `requirements.txt` et vous guide dans la configuration du fichier `.env`.*

2. **Configuration de l'environnement :**
   Remplissez le fichier `.env` à la racine du projet :
   ```env
   BOT_TOKEN=...
   ID=... # API_ID depuis my.telegram.org
   HASH=... # API_HASH depuis my.telegram.org
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

3. **Lancement :**
   ```bash
   python main.py
   ```

## 👑 Fonctionnalités Administrateur

Les utilisateurs disposant des droits d'administrateur ont accès à un panneau de gestion dédié :

- **🏷️ Catégorisation :** Distribution automatique des groupes par thématiques grâce aux modèles de langage (LLM).
- **🌐 Filtre de langue :** Détection de la langue de communication pour une extraction régionale ciblée.
- **🔄 Actualisation :** Mise à jour groupée des métadonnées des groupes et vérification de leur validité.

## 📊 Détermination de l'activité

| Statut        | Description                                                   |
|:--------------|:--------------------------------------------------------------|
| 🟢 `active`   | Le dernier message a été publié il y a **≤ 30 jours**          |
| 🔴 `inactive` | Le dernier message a été publié il y a **> 30 jours**          |
| ⚪ `unknown`  | Impossible de récupérer la date (restrictions de sécurité)    |

---

## Configuration de l'environnement virtuel

Windows :

Dans l'invite de commandes (cmd) :
```cmd
venv\Scripts\activate.bat
```

Dans PowerShell :
```powershell
venv\Scripts\Activate.ps1
```

## 🧑‍💻 Stack technique

- **Framework :** `aiogram 3.x` (Bot API), `Telethon` (User API)
- **Base de données :** `SQLite` + `Peewee ORM`
- **IA :** `Groq`, `OpenRouter`, `G4F`
- **Localisation :** `Project Fluent`

---
> 📘 Une documentation détaillée est disponible dans [doc/doc.md](doc/doc.md) ou via la commande `/help` dans le bot.
