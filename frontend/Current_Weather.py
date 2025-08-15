import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple

import plotly.express as px
import streamlit as st
from api_client import create_history, get_current_weather, get_forecast, get_user_city
from config import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    MAX_FORECAST_DAYS,
    UNITS,
)

#API Wrappers (cached)
@st.cache_data(ttl=600)
def fetch_user_city() -> Optional[str]:
    """Get user's city from IP/location service."""
    try:
        return get_user_city()
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_current_weather(city: str, unit: str) -> Optional[Dict]:
    """Get current weather data for a given city and unit."""
    try:
        api_unit = "imperial" if unit == "Fahrenheit" else "metric"
        return get_current_weather(city, units=api_unit)
    except Exception:
        return None

@st.cache_data(ttl=60)
def fetch_forecast(city: str, unit: str) -> Optional[Dict]:
    """Get 5-day forecast for a given city and unit."""
    try:
        api_unit = "imperial" if unit == "Fahrenheit" else "metric"
        return get_forecast(city, units=api_unit)
    except Exception:
        return None

#Initialization  
def init_page() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=LAYOUT)
    st.title("☀️ Current Weather & 5-Day Forecast")

def init_session_state() -> None:
    """Initialize default session variables."""
    defaults = {
        "default_city": fetch_user_city() or "",
        "weather": None,
        "forecast": None,
        "range_daily": [],
        "last_city": None,
        "last_date_from": date.today(),
        "last_date_to": date.today(),
        "unit": "Celsius",  # Default unit
        "last_unit": "Celsius", # Remembers last selection in form
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.session_state.last_city = st.session_state.last_city or st.session_state.default_city

#Form   
def weather_form() -> Tuple[bool, bool, str, date, date, str]:
    """Weather input form. Returns submission states and inputs."""
    with st.form("weather_form"):
        city = st.text_input("Enter city name/Zip/GPS Coordinates", value=st.session_state.last_city, placeholder="e.g. London, New York")
        col1, col2 = st.columns(2)
        date_from = col1.date_input("Start Date", st.session_state.last_date_from)
        date_to = col2.date_input("End Date", st.session_state.last_date_to)

        st.markdown("---")

        b_col1, b_col2, b_col3 = st.columns([2, 2, 2])

        with b_col1:
            submit_current = st.form_submit_button(
                "Get Current Weather", use_container_width=False
            )

        with b_col2:
            unit = st.radio(
                "Select Temperature Unit",
                UNITS,
                index=UNITS.index(st.session_state.last_unit),
                horizontal=True,
                label_visibility="collapsed"
            )

        with b_col3:
            submit_range = st.form_submit_button(
                "Get Forecast in Date Range", use_container_width=False
            )

    return submit_current, submit_range, city.strip(), date_from, date_to, unit

#Submission Handlers        
def validate_inputs(city: str, date_from: date, date_to: date) -> bool:
    if not city:
        st.error("Please enter a valid city name.")
        return False
    if date_from > date_to:
        st.error("Start date cannot be after end date.")
        return False
    return True

def handle_current(city: str, date_from: date, date_to: date, unit: str) -> None:
    if not validate_inputs(city, date_from, date_to):
        return
    update_last_inputs(city, date_from, date_to, unit)

    with st.spinner("Fetching current weather..."):
        weather = fetch_current_weather(city, unit)
    if not weather:
        st.error("City not found ❌")
        st.session_state.weather = st.session_state.forecast = None
        return

    st.session_state.weather = weather
    st.session_state.unit = unit  # Update the active unit
    with st.spinner("Fetching forecast..."):
        st.session_state.forecast = fetch_forecast(city, unit) or None
    st.session_state.range_daily.clear()

def handle_range(city: str, date_from: date, date_to: date, unit: str) -> None:
    if not validate_inputs(city, date_from, date_to):
        return
    update_last_inputs(city, date_from, date_to, unit)

    with st.spinner("Fetching forecast data..."):
        forecast = fetch_forecast(city, unit)
    if not forecast or "list" not in forecast:
        st.warning("No forecast data available.")
        st.session_state.range_daily.clear()
        return

    today = date.today()
    eff_from = max(date_from, today)
    eff_to = min(date_to, today + timedelta(days=5))
    if eff_from > eff_to:
        st.warning("Date range must be within the next 5 days.")
        st.session_state.range_daily.clear()
        return

    st.session_state.range_daily = aggregate_forecast(forecast, eff_from, eff_to)
    st.session_state.unit = unit  # Update the active unit
    st.session_state.weather = None # Clear current weather data

def update_last_inputs(city: str, date_from: date, date_to: date, unit: str) -> None:
    st.session_state.last_city = city
    st.session_state.last_date_from = date_from
    st.session_state.last_date_to = date_to
    st.session_state.last_unit = unit

#Data Processing  
def aggregate_forecast(forecast_data: Dict, d_from: date, d_to: date) -> List[Dict]:
    """Aggregate 3-hour forecast data into daily averages."""
    daily = {}
    for entry in forecast_data.get("list", []):
        try:
            d = datetime.fromtimestamp(int(entry.get("dt", 0))).date()
            if d_from <= d <= d_to:
                daily.setdefault(d.isoformat(), []).append(float(entry["main"]["temp"]))
        except Exception:
            continue

    return [
        {"date": d, "avg_temp": sum(temps)/len(temps), "min_temp": min(temps), "max_temp": max(temps), "samples": len(temps)}
        for d, temps in sorted(daily.items())
    ]

def process_forecast(forecast_data: Dict) -> List[Dict]:
    """Compute average daily temperature for up to MAX_FORECAST_DAYS."""
    if not forecast_data or "list" not in forecast_data:
        return []
    daily_temps = {}
    for entry in forecast_data["list"]:
        try:
            d = datetime.fromtimestamp(int(entry["dt"])).date().isoformat()
            daily_temps.setdefault(d, []).append(float(entry["main"]["temp"]))
        except Exception:
            continue
    return [
        {"date": d, "avg_temp": sum(temps)/len(temps), "min_temp": min(temps), "max_temp": max(temps),}
        for d, temps in sorted(daily_temps.items())
    ][:MAX_FORECAST_DAYS]

#Rendering    
def get_unit_symbols() -> Tuple[str, str]:
    """Returns temperature and wind speed symbols based on session unit."""
    unit = st.session_state.get("unit", "Celsius")
    temp_symbol = "°F" if unit == "Fahrenheit" else "°C"
    wind_symbol = "mph" if unit == "Fahrenheit" else "m/s"
    return temp_symbol, wind_symbol

def render_current_weather() -> None:
    weather = st.session_state.weather
    if not weather:
        if not st.session_state.range_daily:
            st.info("No weather loaded. Use the form above.")
        return

    temp_symbol, wind_symbol = get_unit_symbols()
    city = st.session_state.last_city
    location = f"{weather.get('name', city)}, {weather.get('sys', {}).get('country', '')}"
    st.subheader(f"Current Weather in {location}")

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Temperature ({temp_symbol})", weather["main"]["temp"])
    col2.metric("Humidity (%)", weather["main"]["humidity"])
    col3.metric(f"Wind Speed ({wind_symbol})", weather["wind"]["speed"])

    st.write(f"**Condition:** {weather['weather'][0]['description'].capitalize()}")
    st.write(f"**Feels Like:** {weather['main']['feels_like']} {temp_symbol}")
    st.write(f"**Pressure:** {weather['main']['pressure']} hPa")
    st.write(f"**Visibility:** {weather.get('visibility', 'N/A')} m")

    if st.button("Save to History"):
        resolved_city = weather.get("name", city)
        save_history(resolved_city, st.session_state.last_date_from, st.session_state.last_date_to, weather)

def render_forecast_section() -> None:
    forecast_data = st.session_state.forecast
    daily_avg = process_forecast(forecast_data)
    #if not daily_avg and not st.session_state.range_daily:
        #st.info("No forecast data available.")
        #return

    temp_symbol, _ = get_unit_symbols()
    st.subheader("📅 5-Day Forecast")
    cols = st.columns(len(daily_avg))
    for col, row in zip(cols, daily_avg):
        col.markdown(f"**{row['date']}**")
        col.write(f"🌡 {row['avg_temp']:.1f} {temp_symbol}")
        col.caption(f"Min: {row['min_temp']:.1f} {temp_symbol} • Max: {row['max_temp']:.1f} {temp_symbol}")


    fig = px.line(
        daily_avg, x="date", y="avg_temp", title="5-Day Temperature Trend", markers=True,
        labels={"avg_temp": f"Average Temp ({temp_symbol})", "date": "Date"}
    )
    st.plotly_chart(fig, use_container_width=True)

def render_range_section() -> None:
    daily = st.session_state.range_daily
    if not daily:
        return

    temp_symbol, _ = get_unit_symbols()
    st.subheader(
        f"📆 Range Weather ({st.session_state.last_date_from} → {st.session_state.last_date_to})"
    )

    cols = st.columns(min(5, len(daily)))
    for i, row in enumerate(daily):
        with cols[i % len(cols)]:
            st.markdown(f"**{row['date']}**")
            st.write(f"Avg: {row['avg_temp']:.1f} {temp_symbol}")
            st.caption(f"Min: {row['min_temp']:.1f} {temp_symbol} • Max: {row['max_temp']:.1f} {temp_symbol}")

    fig = px.line(
        daily, x="date", y="avg_temp", title="Average Temperature (Selected Range)", markers=True,
        labels={"date": "Date", "avg_temp": f"Average Temp ({temp_symbol})"},
    )
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Save Range to History"):
        
        save_range_history(
            st.session_state.last_city,
            st.session_state.last_date_from,
            st.session_state.last_date_to,
            daily
        )

#History
def save_history(city: str, date_from: date, date_to: date, weather: Dict) -> None:
    try:
        weather_summary = {
            "unit": st.session_state.unit,
            "condition": weather["weather"][0]["description"].capitalize(),
            "feels_like": weather["main"]["feels_like"],
            "pressure": weather["main"]["pressure"],
            "visibility": weather.get("visibility", "N/A"),
            "temp": weather["main"]["temp"],
            "humidity": weather["main"]["humidity"],
            "wind_speed": weather["wind"]["speed"],
        }
        payload = {"city": city, "date_from": str(date_from), "date_to": str(date_to), "data": json.dumps(weather_summary)}
        resp = create_history(**payload)
        st.success(f"Weather saved to history ✅")
    except Exception as exc:
        st.error(f"Failed to save history: {exc}")

def save_range_history(city: str, date_from: date, date_to: date, range_data: List[Dict]) -> None:
    """Save aggregated range weather data."""
    try:
        # Create a dictionary to hold all data that will be saved as JSON
        data_to_save = {
            "unit": st.session_state.unit,
            "daily_summary": range_data,
        }

        # The payload for create_history only has city, dates, and the data blob
        payload = {
            "city": city,
            "date_from": str(date_from),
            "date_to": str(date_to),
            "data": json.dumps(data_to_save),
        }

        resp = create_history(**payload)
        st.success(f"Range weather saved to history ✅")
    except Exception as exc:
        st.error(f"Failed to save range history: {exc}")

#Main   
def main() -> None:
    init_page()
    init_session_state()

    submit_current, submit_range, city, date_from, date_to, unit = weather_form()

    if submit_current:
        handle_current(city, date_from, date_to, unit)
        st.session_state.mode = "current"
    elif submit_range:
        handle_range(city, date_from, date_to, unit)
        st.session_state.mode = "range"

    mode = st.session_state.get("mode", None)

    if mode == "current":
        render_current_weather()
        render_forecast_section()
    elif mode == "range":
        render_range_section()
    else:
        st.info("Please select an option above to view weather data.")


if __name__ == "__main__":
    st.markdown("Weather App — by Muhammd Muaaz Ulhaq, mmuaazulhaq@gmail.com")
    with st.expander("ℹ️ About PM Accelerator"):
        st.markdown("""
    **Overview**  
    The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations.

    Our Product Manager Accelerator community are ambitious and committed. Through our program they have learnt, honed and developed new PM and leadership skills, giving them a strong foundation for their future endeavors.

    **Here are the examples of services we offer:**  
     **PMA Pro** – End-to-end product manager job hunting program that helps you master FAANG-level Product Management skills, conduct unlimited mock interviews, and gain job referrals through our largest alumni network. 25% of our offers came from tier 1 companies and get paid as high as $800K/year.  

     **AI PM Bootcamp** – Gain hands-on AI Product Management skills by building a real-life AI product with a team of AI Engineers, data scientists, and designers. We will also help you launch your product with real user engagement using our 100,000+ PM community and social media channels.  

     **PMA Power Skills** – Designed for existing product managers to sharpen their product management skills, leadership skills, and executive presentation skills.  

     **PMA Leader** – We help you accelerate your product management career, get promoted to Director and product executive levels, and win in the board room.  

     **1:1 Resume Review** – We help you rewrite your killer product manager resume to stand out from the crowd, with an interview guarantee. Get started by using our FREE killer PM resume template used by over 14,000 product managers. [Resume Template](https://www.drnancyli.com/pmresume)  

     We also published over 500+ free training and courses. Please go to my [YouTube channel](https://www.youtube.com/c/drnancyli) and Instagram **@drnancyli** to start learning for free today.

    **Website:** [pmaccelerator.io](https://www.pmaccelerator.io/)  
    **Phone:** +1 954-889-1063  
    **Industry:** E-Learning Providers  
    **Company size:** 2-10 employees  
    **Headquarters:** Boston, MA  
    **Founded:** 2020  

    **Specialties:** Product Management, Product Manager, Product Management Training, Product Management Certification, Product Lead, Product Executive, Associate Product Manager, Product Management Coaching, Product Manager Resume, Product Management Interview, VP of Product, Director of Product, Chief Product Officer, and AI Product Management.
    """)

    main()
