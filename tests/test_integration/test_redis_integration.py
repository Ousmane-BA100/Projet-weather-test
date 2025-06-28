# tests/test_integration/test_redis_integration.py
import pytest
from src.main import app

@pytest.mark.asyncio
async def test_redis_integration(async_client):
    # Test que Redis fonctionne via l'endpoint de clear cache
    response = await async_client.post("/api/cache/clear")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "success"
    
    # Test d'une route météo pour vérifier l'intégration complète
    response = await async_client.get("/api/weather/Paris")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert data["city"] == "Paris"