from fastapi import FastAPI, HTTPException, Body
from backend import weather_api, db_service, models, utils
import json
from datetime import date
app = FastAPI(title="Weather API")

@app.on_event("startup")
def startup_event():
    db_service.create_table()

@app.get("/weather/current", summary="Get current weather by city")
def get_current_weather(city: str, units: str = "metric"):
    data = weather_api.fetch_current_weather(city, units)
    if not data:
        raise HTTPException(status_code=404, detail="Location not found")
    return data

@app.get("/weather/forecast", summary="Get weather forecast by city")
def get_forecast(city: str, units: str = "metric"):
    data = weather_api.fetch_forecast(city, units)
    if not data:
        raise HTTPException(status_code=404, detail="Location not found")
    return data

@app.post("/history", summary="Create a weather history record")
def create_weather_record(record: models.WeatherRecordCreate):
    return db_service.create_record(record)

@app.get("/history", summary="Get all weather history records")
def read_weather_records():
    return db_service.get_all_records()

@app.delete("/history/{record_id}", summary="Delete a weather history record")
def delete_weather_record(record_id: int):
    deleted = db_service.delete_record(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"detail": "Record deleted successfully"}

def _build_weather_summary(weather: dict) -> dict:
    w = (weather or {})
    main = w.get("main", {})
    wind = w.get("wind", {})
    weather_list = w.get("weather", [{}])
    desc = (weather_list[0] or {}).get("description", "")
    return {
        "condition": str(desc).capitalize() if desc else "N/A",
        "feels_like": main.get("feels_like"),
        "pressure": main.get("pressure"),
        "visibility": w.get("visibility", "N/A"),
        "temp": main.get("temp"),
        "humidity": main.get("humidity"),
        "wind_speed": wind.get("speed"),
    }

@app.put("/history/{record_id}")
def refresh_weather_record(record_id: int, payload: dict = Body(default={})):
    record = db_service.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    unit = payload.get("unit", "metric")
    fresh = weather_api.fetch_current_weather(user_input=record["city"], units=unit)
    if not fresh:
        raise HTTPException(status_code=502, detail="Failed to fetch current weather")

    summary = _build_weather_summary(fresh)
    today_str = date.today().isoformat()

    ok = db_service.update_record_to_today(
        record_id=record_id,
        date_str=today_str,
        data_json=json.dumps(summary),
    )
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update record")
    return db_service.get_record_by_id(record_id)

@app.post("/weather/summary")
def weather_summary(req: models.WeatherSummaryRequest):
    return {"summary": utils.summarize_weather(req.city, req.weather, req.forecast)}


