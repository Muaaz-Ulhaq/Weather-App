import re
import google.generativeai as genai
from backend.config import LLM_API_KEY

genai.configure(api_key=LLM_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

def summarize_weather(city, weather_data, forecast_data):
    prompt = f"""
    Summarize the current weather and 5-day forecast for {city}.
    Here is the raw data:
    Current: {weather_data}
    Forecast: {forecast_data}
    Provide a user-friendly explanation and any recommendations.
    """
    response = model.generate_content(prompt)
    return response.text

def correct_city_name(user_input: str) -> str:
    """
    Use AI to correct typos or fuzzy match the city name.
    Returns a best-guess city string.
    """
    try:
        prompt = f"""
        You are a city name autocorrect system. 
        Given the user input: "{user_input}", return ONLY the corrected or most likely city name.
        If input is already correct, return it as-is.
        Do not add extra text, just the city name.
        """
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception:
        return user_input  # fallback


def detect_location_params(user_input: str, country_code: str = "us") -> dict:
    # Remove extra spaces
    user_input = user_input.strip()

    # Check if input is coordinates (latitude,longitude)
    coord_pattern = re.compile(r"^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$")
    if coord_pattern.match(user_input):
        lat, lon = [x.strip() for x in user_input.split(",")]
        return {"lat": lat, "lon": lon}

    # Check if input is numeric (likely ZIP/Postal code)
    if user_input.isdigit():
        return {"zip": f"{user_input},{country_code}"}

    # --- NEW: AI correction for city typos ---
    resolved_city = correct_city_name(user_input)

    return {"q": resolved_city}