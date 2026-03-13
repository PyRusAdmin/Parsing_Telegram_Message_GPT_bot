# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = os.getenv("ID")
API_HASH = os.getenv("HASH")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

PROXY_USER = os.getenv("USER")
PROXY_PASSWORD = os.getenv("PASSWORD")
PROXY_PORT = os.getenv("PORT")
PROXY_IP = os.getenv("IP")
