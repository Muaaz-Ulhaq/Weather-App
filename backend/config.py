import os
from dotenv import load_dotenv
load_dotenv()

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

DB_PATH = 'weather_app.db'
TABLE_NAME = 'history'
BASE_URL = "https://api.openweathermap.org/data/2.5"
