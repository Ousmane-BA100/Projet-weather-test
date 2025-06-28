from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Temperature(BaseModel):
    current: float = Field(..., description="Température actuelle en degrés Celsius")
    feels_like: float = Field(..., description="Température ressentie en degrés Celsius")
    unit: str = "celsius"

class WeatherData(BaseModel):
    city: str = Field(..., description="Nom de la ville")
    temperature: Temperature
    humidity: int = Field(..., ge=0, le=100, description="Taux d'humidité en pourcentage")
    wind_speed: float = Field(..., ge=0, description="Vitesse du vent en km/h")
    wind_direction: int = Field(..., ge=0, le=360, description="Direction du vent en degrés")
    weather_description: str = Field(..., description="Description des conditions météorologiques")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Source des données météorologiques")