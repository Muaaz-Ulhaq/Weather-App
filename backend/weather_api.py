import requests
from backend.utils import detect_location_params
from backend.config import WEATHER_API_KEY, BASE_URL

def fetch_current_weather(user_input, units: str = "metric"):
    url = f"{BASE_URL}/weather"
    params = detect_location_params(user_input, country_code="us")
    params["appid"] = WEATHER_API_KEY
    params["units"] = units
    resp = requests.get(url, params=params)
    return resp.json() if resp.status_code == 200 else None

def fetch_forecast(user_input, units: str = "metric"):
    url = f"{BASE_URL}/forecast"
    params = detect_location_params(user_input, country_code="us") 
    params["appid"] = WEATHER_API_KEY
    params["units"] = units
    resp = requests.get(url, params=params)
    return resp.json() if resp.status_code == 200 else None