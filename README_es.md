### 📡 Bot de Telegram para seguimiento de palabras clave y búsqueda con IA (https://t.me/AutoParseAlertBot)

<p align="center">
  <a href="README_en.md">English</a> •
  <a href="README_zh.md">中文 (简体)</a> •
  <a href="README_hi.md">हिन्दी</a> •
  <b>Español</b> •
  <a href="README_fr.md">Français</a> •
  <a href="README_ar.md">العربية</a> •
  <a href="README_bn.md">বাংলা</a> •
  <a href="README_pt.md">Português</a> •
  <a href="README.md">Русский</a>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange.svg)](https://docs.aiogram.dev/)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-blueviolet.svg)](https://docs.telethon.dev/)

- **Versión:** 0.1.0
- **Fecha de actualización:** 04 de septiembre de 2026

El bot analiza nuevos mensajes en grupos y canales de Telegram especificados en tiempo real, notificando al instante sobre coincidencias de palabras clave. Además, utiliza IA (Groq, OpenRouter) para descubrir de manera inteligente nuevas comunidades temáticas de Telegram.

## ✨ Características clave

- 🚀 **Monitoreo en tiempo real:** Reenvío instantáneo de mensajes que coinciden con palabras clave a su grupo de destino.
- 🤖 **Búsqueda con IA de dos niveles:** Búsqueda en la base de datos local y búsqueda global en todo Telegram.
- 📊 **Exportación a XLSX:** Descarga de resultados de búsqueda y monitoreo a Excel con filtrado por categoría y actividad.
- 🛡️ **Panel de administración:** Herramientas para actualizar la BD, categorización masiva mediante IA y detección de idioma de los chats.
- 🌍 **Multilingüe:** Soporte completo para español, ruso, inglés y otros idiomas (Fluent i18n).
- 🔐 **Multicuenta:** Soporte para múltiples archivos `.session` (StringSession) para evitar límites de Telegram.
- 💰 **Límites y Telegram Stars:** Límite de exportación gratuita de la base de datos (1 vez cada 24 horas). Descargas adicionales disponibles por 5 Telegram Stars.

<p align="center">
  <img src="doc/MessageParser.jpg" alt="Vista previa de la interfaz del bot" width="30%" />
</p>

## 📝 Funciones principales

- **Monitoreo:** Rastreo de palabras clave en una lista ilimitada de grupos y canales.
- **Búsqueda con IA:** Descubrimiento de nuevos grupos objetivo mediante consultas semánticas.
- **Exportación inteligente:** Descarga de la base de datos por categorías específicas (negocios, criptomonedas, empleo, etc.).
- **Detección de actividad:** Etiquetado de comunidades con los estados `active`, `inactive` o `unknown`.
- **Adición masiva:** Carga de listas de monitoreo a través de archivos `.txt`.
- **Soporte de proxy:** Compatibilidad con proxies HTTP/SOCKS5 para un funcionamiento estable con la API de IA y Telegram.

## ⚙️ Inicio rápido

1. **Instalar dependencias:**
   ```bash
   python setup.py
   ```
   *El script instalará `requirements.txt` y ayudará a crear el archivo `.env`.*

2. **Configuración del entorno:**
   Complete el archivo `.env` en la raíz del proyecto:
   ```env
   BOT_TOKEN=...
   ID=... # API_ID de my.telegram.org
   HASH=... # API_HASH de my.telegram.org
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

3. **Ejecutar:**
   ```bash
   python main.py
   ```

## 👑 Funciones de administrador

Los usuarios con privilegios de administrador tienen acceso a un panel de control dedicado:

- **🏷️ Categorización:** Distribución automática de grupos por temáticas mediante modelos de lenguaje (LLM).
- **🌐 Filtro de idioma:** Determinación del idioma de comunicación en los chats para una selección regional precisa.
- **🔄 Actualización:** Actualización masiva de metadatos de grupos y verificación de disponibilidad.

## 📊 Determinación de actividad

| Estado        | Descripción                                                   |
|:--------------|:--------------------------------------------------------------|
| 🟢 `active`   | El último mensaje fue publicado hace **≤ 30 días**            |
| 🔴 `inactive` | El último mensaje fue publicado hace **> 30 días**            |
| ⚪ `unknown`  | No se pudo obtener la fecha (restricciones de privacidad)     |

---

## Configuración del entorno virtual

Windows:

En el símbolo del sistema (cmd):
```cmd
venv\Scripts\activate.bat
```

En PowerShell:
```powershell
venv\Scripts\Activate.ps1
```

## 🧑‍💻 Tecnologías utilizadas

- **Framework:** `aiogram 3.x` (Bot API), `Telethon` (User API)
- **Base de datos:** `SQLite` + `Peewee ORM`
- **IA:** `Groq`, `OpenRouter`, `G4F`
- **Localización:** `Project Fluent`

---
> 📘 Para más detalles, consulte la documentación en [doc/doc.md](doc/doc.md) o mediante el comando `/help` en el bot.
