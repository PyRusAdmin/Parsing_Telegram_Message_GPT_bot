# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
api_id = os.getenv("ID")
api_hash = os.getenv("HASH")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("groq_api_key")

proxy_user = os.getenv("user")
proxy_password = os.getenv("password")
proxy_port = os.getenv("port")
proxy_ip = os.getenv("ip")

language = os.getenv("language")
