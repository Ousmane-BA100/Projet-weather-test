# tests/test_contract/test_weather_contract.py
import pytest
from datetime import datetime

@pytest.fixture
def weather_response():
    """Retourne un exemple de réponse météo pour les tests de contrat."""
    return {
        "city": "Paris",
        "temperature": {
            "current": 22.5,
            "feels_like": 23.1
        },
        "humidity": 65.0,
        "wind_speed": 10.5,
        "weather_description": "partiellement nuageux",
        "source": "openweathermap",
        "timestamp": datetime.utcnow().isoformat()
    }

def test_weather_response_contract(weather_response):
    """Teste que la réponse de l'API météo respecte le contrat défini."""
    required_fields = {
        "city": str,
        "temperature": dict,
        "humidity": (int, float),
        "wind_speed": (int, float),
        "weather_description": str,
        "source": str,
        "timestamp": str
    }
    
    for field, field_type in required_fields.items():
        assert field in weather_response, f"Champ manquant: {field}"
        if isinstance(field_type, tuple):
            assert isinstance(weather_response[field], field_type), (
                f"Type invalide pour {field}: {type(weather_response[field])}"
            )
        else:
            assert isinstance(weather_response[field], field_type), (
                f"Type invalide pour {field}: {type(weather_response[field])}"
            )
    
    # Vérification supplémentaire pour les sous-champs de temperature
    assert "current" in weather_response["temperature"]
    assert "feels_like" in weather_response["temperature"]
    assert isinstance(weather_response["temperature"]["current"], (int, float))
    assert isinstance(weather_response["temperature"]["feels_like"], (int, float))