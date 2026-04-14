import os
from dotenv import load_dotenv

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
ID_ADMIN = int(os.getenv("ID_ADMIN", "5427391210"))

# API Endpoints
URL_ANCARAT = "https://giabac.ancarat.com/api/price-data"
URL_GOLDAPI = "https://www.goldapi.io/api"
URL_GOLDAPI_ALPHAVANTAGE = "https://www.alphavantage.co/query"
URL_SJC = "https://giavang.org/trong-nuoc/sjc/"
URL_DOJI = "https://www.vang.today/api/prices"