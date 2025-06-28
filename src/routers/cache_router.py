from fastapi import APIRouter, HTTPException
from src.services.weather_service import WeatherService

router = APIRouter(tags=["Cache"])

@router.post("/cache/clear", summary="Vider le cache")
async def clear_cache():
    """Vide le cache des données météo"""
    try:
        # Créé une instance du service
        weather_service = WeatherService()
        await weather_service.clear_cache()
        return {"status": "success", "message": "Cache vidé avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))