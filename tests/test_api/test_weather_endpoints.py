from unittest.mock import patch, MagicMock
from fastapi import status

def test_get_weather(client):
    from fastapi import FastAPI
    app = FastAPI()
    print("\nRoutes enregistrées :")
    for route in app.routes:
        print(f"{route.path} - {route.methods}")
    
    # Créer un mock pour WeatherData
    mock_weather_data = {
        "city": "Paris",
        "temperature": {"current": 20.0, "feels_like": 18.0},
        "humidity": 60.0,
        "wind_speed": 10.0,
        "wind_direction": 180,
        "weather_description": "partiellement nuageux",
        "source": "test",
        "timestamp": "2025-01-01T00:00:00"
    }

    with patch('src.controllers.weather_controller.WeatherService.get_current_weather', return_value=mock_weather_data) as mock_get:
        response = client.get("/api/weather/Paris")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_weather_data

def test_get_weather_invalid_city(client):
    """Test avec une ville invalide"""
    with patch('src.controllers.weather_controller.WeatherService.get_current_weather') as mock_get:
        # Configurer le mock pour lever une exception
        from fastapi import HTTPException
        mock_get.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found"
        )

        # Faire la requête à l'API
        response = client.get("/api/weather/InvalidCity123")

        # Vérifier la réponse d'erreur
        assert response.status_code == status.HTTP_404_NOT_FOUND
        error_data = response.json()
        assert "detail" in error_data
        assert error_data["detail"] == "Not Found"