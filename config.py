import os
from dotenv import load_dotenv
from utils.json_storage import JSONStorage

# Load environment variables from .env file
load_dotenv()

# Directory paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Environment variables (simple configuration values)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_KEY = os.getenv("WEATHER_KEY")
API_KEY_1TOUCH = os.getenv("API_KEY_1TOUCH")
VNSTOCK_API_KEY = os.getenv("VNSTOCK_API_KEY")
API_KEY_ALPHAVANTAGE = os.getenv("API_KEY_ALPHAVANTAGE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Load chat IDs from JSON file (proper way to store structured data)
_chat_ids_file = os.path.join(DATA_DIR, "chat_ids.json")
_chat_ids_storage = JSONStorage(_chat_ids_file, default_data={
    "reminder_lunch": [],
    "reminder_badminton": [],
    "reminder_tet": [],
    "schedule_aug": [],
    "schedule_silver": []
})
_chat_ids = _chat_ids_storage.load()

REMINDER_CHAT_IDS_LUNCH = _chat_ids.get("reminder_lunch", [])
REMINDER_CHAT_IDS_BADMINTON = _chat_ids.get("reminder_badminton", [])
REMINDER_CHAT_IDS_TET = _chat_ids.get("reminder_tet", [])
SCHEDULE_AUG_CHAT_IDS = _chat_ids.get("schedule_aug", [])
SCHEDULE_SILVER_CHAT_IDS = _chat_ids.get("schedule_silver", [])

# API Endpoints
URL_ANCARAT = "https://giabac.ancarat.com/api/price-data"
URL_GOLDAPI = "https://www.goldapi.io/api"
URL_GOLDAPI_ALPHAVANTAGE = "https://www.alphavantage.co/query"
URL_SJC = "https://giavang.org/trong-nuoc/sjc/"
URL_DOJI = "https://www.vang.today/api/prices"