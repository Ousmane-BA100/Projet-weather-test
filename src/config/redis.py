# src/config/redis.py
import os
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)

# Variable globale pour stocker l'instance Redis
_redis = None

async def init_redis() -> Redis:
    """Initialise et retourne une connexion Redis."""
    global _redis
    if _redis is None:
        try:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
            logger.info(f"🔌 Tentative de connexion à Redis sur {redis_url}")
            _redis = Redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Tester la connexion
            await _redis.ping()
            logger.info("✅ Connecté à Redis avec succès")
        except Exception as e:
            logger.error(f"❌ Échec de la connexion à Redis: {str(e)}")
            _redis = None
            raise
    return _redis

async def get_redis() -> Redis:
    """Retourne l'instance Redis existante ou en crée une nouvelle."""
    if _redis is None:
        return await init_redis()
    return _redis

async def close_redis():
    """Ferme la connexion Redis."""
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("Connexion Redis fermée avec succès")