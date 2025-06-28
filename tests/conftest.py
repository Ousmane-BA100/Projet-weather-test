import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from src.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
async def cleanup_redis():
    """Nettoie Redis après chaque test"""
    yield  # Le test s'exécute
    
    # Cleanup après le test
    try:
        from src.config.redis import get_redis
        redis = await get_redis()
        await redis.flushdb()  # Vide la DB de test
        await redis.close()
    except Exception:
        pass  # Ignore les erreurs de cleanup