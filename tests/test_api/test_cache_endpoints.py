import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_clear_cache(async_client):
    """Test de l'endpoint de nettoyage du cache"""
    
    # Nettoie avant le test
    try:
        from src.config.redis import get_redis
        redis = await get_redis()
        await redis.flushdb()
        # Supprime la ligne close() problématique
    except:
        pass
    
    # Test avec méthode POST
    response = await async_client.post("/api/cache/clear")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "success",
        "message": "Cache vidé avec succès"
    }
    
    # Test avec méthode non autorisée (GET)
    response = await async_client.get("/api/cache/clear")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED