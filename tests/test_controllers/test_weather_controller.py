# tests/test_controllers/test_weather_controller.py
import pytest
from fastapi import HTTPException, status
from unittest.mock import AsyncMock, patch
from src.controllers.weather_controller import router
from src.services.weather_service import WeatherService
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api")

client = TestClient(app)

@pytest.fixture
def mock_weather_data():
    return {
        "city": "Paris",
        "temperature": {"current": 20.0, "feels_like": 18.0},
        "humidity": 60.0,
        "wind_speed": 10.0,
        "wind_direction": 180,
        "weather_description": "partiellement nuageux",
        "source": "test",
        "timestamp": "2025-01-01T00:00:00"
    }

@pytest.mark.asyncio
async def test_get_weather_success(mock_weather_data):
    with patch.object(WeatherService, 'get_current_weather', new_callable=AsyncMock) as mock_get_weather:
        # Configurer le mock pour retourner des données de test
        mock_get_weather.return_value = mock_weather_data
        
        # Faire la requête à l'API
        response = client.get("/api/weather/Paris")
        
        # Vérifier la réponse
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["city"] == "Paris"
        assert data["temperature"]["current"] == 20.0
        assert data["humidity"] == 60.0

@pytest.mark.asyncio
async def test_get_weather_not_found():
    with patch.object(WeatherService, 'get_current_weather', new_callable=AsyncMock) as mock_get_weather:
        # Configurer le mock pour lever une exception 404
        mock_get_weather.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ville non trouvée"
        )
        
        # Faire la requête à l'API
        response = client.get("/api/weather/UnknownCity")
        
        # Vérifier la réponse d'erreur
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Ville non trouvée"

@pytest.mark.asyncio
async def test_get_weather_server_error():
    with patch.object(WeatherService, 'get_current_weather', new_callable=AsyncMock) as mock_get_weather:
        # Configurer le mock pour lever une exception générique
        mock_get_weather.side_effect = Exception("Erreur serveur")
        
        # Faire la requête à l'API
        response = client.get("/api/weather/Paris")
        
        # Vérifier la réponse d'erreur
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Impossible de récupérer les données météo" in response.json()["detail"]