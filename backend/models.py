from pydantic import BaseModel, Field
from typing import Optional, Any

class WeatherRecordBase(BaseModel):
    city: str = Field(..., example="London")
    date_from: Optional[str] = Field(None, example="2025-08-01")
    date_to: Optional[str] = Field(None, example="2025-08-05")
    data: Optional[str] = Field(None, example="{'temp': 25, 'condition': 'Clear'}")

class WeatherRecordCreate(WeatherRecordBase):
    """Used for creating a new weather record."""
    pass

class WeatherRecordUpdate(BaseModel):
    """Used for updating an existing weather record."""
    city: Optional[str] = Field(None, example="Paris")
    date_from: Optional[str] = Field(None, example="2025-08-02")
    date_to: Optional[str] = Field(None, example="2025-08-06")
    data: Optional[str] = Field(None, example="{'temp': 26, 'condition': 'Cloudy'}")

class WeatherRecordInDB(WeatherRecordBase):
    """Represents a record stored in the database."""
    id: int

    class Config:
        orm_mode = True  # Allows ORM objects to be returned directly

class WeatherSummaryRequest(BaseModel):
    city: str
    weather: dict[str, Any]
    forecast: dict[str, Any]