import streamlit as st
from api_client import get_history, delete_history, update_history
import json
import time
import csv
import io
from datetime import datetime

st.header("Weather History")

if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False
    st.session_state.history_data = []


def load_history():
    """Load history from backend and store in session state."""
    history = get_history()
    st.session_state.history_loaded = True
    st.session_state.history_data = history or []


def fmt(value, decimals=1):
    """Format a number to fixed decimals, keep '-' for missing."""
    if isinstance(value, (int, float)):
        return round(value, decimals)
    return value


def safe_date(date_str):
    """Ensure dates are correctly parsed and returned in YYYY-MM-DD format."""
    if not date_str:
        return "-"
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return date_str


def export_csv(record):
    """Export given weather record as CSV with proper date handling."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    weather_data = json.loads(record['data']) if isinstance(record['data'], str) else record['data']
    unit = weather_data.get("unit", "C") if isinstance(weather_data, dict) else "C"

    # Header row
    if "daily_summary" in weather_data:
        writer.writerow(["Date", f"Avg Temp (°{unit})", f"Min Temp (°{unit})", f"Max Temp (°{unit})"])
        for day in weather_data["daily_summary"]:
            writer.writerow([
                safe_date(day.get("date", "-")),
                fmt(day.get("avg_temp")),
                fmt(day.get("min_temp")),
                fmt(day.get("max_temp")),
                #fmt(day.get("samples"), 0)
            ])
    elif isinstance(weather_data, dict):
        writer.writerow(["Field", "Value"])
        for key, label in [
            ("condition", "Condition"),
            ("temp", f"Temperature (°{unit})"),
            ("feels_like", f"Feels Like (°{unit})"),
            ("humidity", "Humidity (%)"),
            ("pressure", "Pressure (hPa)"),
            ("visibility", "Visibility (m)"),
            ("wind_speed", "Wind Speed (m/s)")
        ]:
            writer.writerow([label, fmt(weather_data.get(key))])
    elif isinstance(weather_data, list):
        writer.writerow(["Date", f"Avg Temp (°{unit})", f"Min Temp (°{unit})", f"Max Temp (°{unit})"])
        for day in weather_data:
            writer.writerow([
                safe_date(day.get("date", "-")),
                fmt(day.get("avg_temp")),
                fmt(day.get("min_temp")),
                fmt(day.get("max_temp")),
                #fmt(day.get("samples"), 0)
            ])

    filename = f"{record['city']} ({record['date_from']}→{record['date_to']}).csv".replace(" ", "_")
    st.download_button(
        label="📥 Export CSV",
        data=buffer.getvalue(),
        file_name=filename,
        mime="text/csv",
        key=f"csv_{record['id']}"
    )


col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Show History"):
        load_history()
with col2:
    if st.button("🔄 Refresh History"):
        st.rerun()

# Display weather history
if st.session_state.history_loaded:
    if not st.session_state.history_data:
        st.info("No weather history found.")
    else:
        for idx, record in enumerate(st.session_state.history_data):
            with st.expander(f"{record['city']} ({record['date_from']} → {record['date_to']})", expanded=False):
                try:
                    weather_data = json.loads(record['data']) if isinstance(record['data'], str) else record['data']
                except json.JSONDecodeError:
                    st.error("Invalid weather data format")
                    continue

                unit = "C"

                # Display for dict with daily_summary
                if isinstance(weather_data, dict):
                    unit = weather_data.get("unit", "C")
                    if "daily_summary" in weather_data:
                        st.write(f"**Unit:** {unit}")
                        for day in weather_data["daily_summary"]:
                            st.write(f"### {safe_date(day.get('date', '-'))}")
                            c1, c2, c3, c4 = st.columns(4)
                            with c1:
                                st.metric(f"Avg Temp (°{unit})", fmt(day.get("avg_temp")))
                            with c2:
                                st.metric(f"Min Temp (°{unit})", fmt(day.get("min_temp")))
                            with c3:
                                st.metric(f"Max Temp (°{unit})", fmt(day.get("max_temp")))
                           # with c4:
                               # st.metric("Samples", fmt(day.get("samples"), 0))
                            st.markdown("---")
                    else:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.metric("Condition", weather_data.get("condition", "-"))
                            st.metric(f"Temperature (°{unit})", fmt(weather_data.get("temp")))
                            st.metric(f"Feels Like (°{unit})", fmt(weather_data.get("feels_like")))
                        with c2:
                            st.metric("Humidity (%)", fmt(weather_data.get("humidity"), 0))
                            st.metric("Pressure (hPa)", fmt(weather_data.get("pressure"), 0))
                            st.metric("Visibility (m)", fmt(weather_data.get("visibility"), 0))
                        with c3:
                            st.metric("Wind Speed (m/s)", fmt(weather_data.get("wind_speed"), 1))

                elif isinstance(weather_data, list):
                    unit = "C"
                    for day in weather_data:
                        st.write(f"### {safe_date(day.get('date', '-'))}")
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric(f"Avg Temp (°{unit})", fmt(day.get("avg_temp")))
                        with c2:
                            st.metric(f"Min Temp (°{unit})", fmt(day.get("min_temp")))
                        with c3:
                            st.metric(f"Max Temp (°{unit})", fmt(day.get("max_temp")))
                        #with c4:
                            #st.metric("Samples", fmt(weather_data.get("visibility"), 0))
                        st.markdown("---")
                else:
                    st.warning("Unrecognized weather data format.")

                export_csv(record) 

                col_unit = st.columns(1)[0]
                with col_unit:
                    default_unit = record.get("unit", "metric")
                    unit_choice = st.selectbox(
                        "Unit",
                        options=["metric", "imperial"],
                        index=0 if default_unit == "metric" else 1,
                        format_func=lambda u: "Celsius (°C)" if u == "metric" else "Fahrenheit (°F)",
                        key=f"unit_{idx}"
                    )

                col_update, col_delete = st.columns(2)
                with col_update:
                    if st.button("Update to Current Weather", key=f"update_{idx}"):
                        try:
                            updated = update_history(record["id"], unit=unit_choice)
                            st.success(f"Updated {record['city']} to today's weather ({unit_choice})")
                            st.session_state.history_data[idx] = updated
                            time.sleep(0.8)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update: {e}")

                with col_delete:
                    if st.button("Delete", key=f"delete_{idx}"):
                        try:
                            delete_history(record["id"])
                            st.success(f"Deleted record for {record['city']}")
                            st.session_state.history_data = [
                                r for r in st.session_state.history_data if r["id"] != record["id"]
                            ]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete: {e}")
