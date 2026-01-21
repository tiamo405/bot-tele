import os
from dotenv import load_dotenv
import ast

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
REMINDER_CHAT_IDS = ast.literal_eval(os.getenv("REMINDER_CHAT_IDS", "[]"))
REMINDER_CHAT_IDS_BADMINTON = ast.literal_eval(os.getenv("REMINDER_CHAT_IDS_BADMINTON", "[]"))
REMINDER_CHAT_IDS_TET = ast.literal_eval(os.getenv("REMINDER_CHAT_IDS_TET", "[]"))
API_KEY_1TOUCH = os.getenv("API_KEY_1TOUCH")
VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY")