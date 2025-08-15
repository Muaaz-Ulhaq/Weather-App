import requests
from config import (
    API_BASE_URL,
    CURRENT_WEATHER_PATH,
    FORECAST_PATH,
    HISTORY_PATH,
    WEATHER_RANGE_PATH,
    USER_LOCATION_URL
)


def get_current_weather(city, units="metric"):
    url = f"{API_BASE_URL}{CURRENT_WEATHER_PATH}"
    r = requests.get(url, params={"city": city, "units": units})
    return r.json() if r.status_code == 200 else None

def get_forecast(city, units="metric"):
    url = f"{API_BASE_URL}{FORECAST_PATH}"
    r = requests.get(url, params={"city": city, "units": units})
    return r.json() if r.status_code == 200 else None

def get_user_city():
    try:
        res = requests.get(USER_LOCATION_URL)
        if res.status_code == 200:
            return res.json().get("city")
    except Exception:
        pass
    return None

def get_history():
    url = f"{API_BASE_URL}{HISTORY_PATH}"
    r = requests.get(url)
    print("STATUS:", r.status_code)
    print("RAW TEXT:", r.text)
    r.raise_for_status()
    return r.json()

def create_history(city, date_from, date_to, data=None):
    url = f"{API_BASE_URL}{HISTORY_PATH}"
    payload = {"city": city, "date_from": date_from, "date_to": date_to}
    if data is not None:
        payload["data"] = data
    r = requests.post(url, json=payload)
    r.raise_for_status()
    return r.json()

def get_weather_range(city, date_from, date_to):
    url = f"{API_BASE_URL}{WEATHER_RANGE_PATH}"
    r = requests.get(url, params={"city": city, "date_from": date_from, "date_to": date_to})
    r.raise_for_status()
    return r.json()

def delete_history(record_id):
    url = f"{API_BASE_URL}{HISTORY_PATH}/{record_id}"
    r = requests.delete(url)
    r.raise_for_status()
    return r.json()

def update_history(record_id, city=None, unit=None):
    url = f"{API_BASE_URL}{HISTORY_PATH}/{record_id}"
    payload = {}
    if city:
        payload["city"] = city
    if unit:
        payload["unit"] = unit
    r = requests.put(url, json=payload)
    r.raise_for_status()
    return r.json()
