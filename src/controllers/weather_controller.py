from fastapi import APIRouter, HTTPException
from src.services.weather_service import WeatherService

router = APIRouter()
weather_service = WeatherService()

@router.get("/weather/{city}")
async def get_weather(city: str):
    """Récupère les données météo pour une ville donnée"""
    try:
        # Utiliser get_current_weather qui gère déjà la récupération et la fusion
        weather_data = await weather_service.get_current_weather(city)
        return weather_data
    except HTTPException as he:
        # Si c'est déjà une HTTPException, on la relance telle quelle
        raise he
    except Exception as e:
        # Pour les autres exceptions, on renvoie une 500
        raise HTTPException(
            status_code=500,
            detail=f"Impossible de récupérer les données météo pour {city}: {str(e)}"
        )