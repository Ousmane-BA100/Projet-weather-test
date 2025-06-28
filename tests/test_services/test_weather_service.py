import pytest
from unittest.mock import patch, AsyncMock
from src.services.weather_service import WeatherService, WeatherData
from datetime import datetime

@pytest.mark.asyncio
async def test_get_weather():
    service = WeatherService()
    
    # Créer un mock pour les données de température
    temperature = {
        "current": 20.0,
        "feels_like": 18.0,
        "min": 15.0,
        "max": 22.0
    }
    
    # Créer un objet WeatherData valide
    mock_weather_data = WeatherData(
        city="Paris",
        temperature=temperature,
        humidity=60.0,
        wind_speed=10.0,
        wind_direction=180,
        weather_description="partiellement nuageux",
        source="test",
        timestamp=datetime.now().isoformat()
    )
    
    with patch.object(service, '_get_weather_from_openweather', new_callable=AsyncMock) as mock_ow, \
         patch.object(service, '_get_weather_from_weatherapi', new_callable=AsyncMock) as mock_wa, \
         patch.object(service, '_get_weather_from_openmeteo', new_callable=AsyncMock) as mock_om:
        
        # Configurer les mocks pour retourner des données valides
        mock_ow.return_value = mock_weather_data
        mock_wa.return_value = mock_weather_data
        mock_om.return_value = mock_weather_data
        
        # Appeler la méthode à tester
        result = await service.get_current_weather("Paris")
        
        # Vérifier les résultats
        assert result.city == "Paris"
        assert result.temperature.current == 20.0
        assert result.humidity == 60.0