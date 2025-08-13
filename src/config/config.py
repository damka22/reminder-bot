import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TOKEN = os.getenv("TOKEN") # token of bot
DB_LITE = os.getenv("DB_LITE") # db
TIMEZONE = os.getenv("TIMEZONE") # your timezone
ADMIN_ID: int = int(os.getenv("ADMIN_ID")) # admins tg id