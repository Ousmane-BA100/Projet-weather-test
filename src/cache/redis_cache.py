import json
import redis
from typing import Optional, Any
from redis.asyncio import Redis

class RedisCache:
    _instance = None
    _redis: Redis = None

    def __new__(cls, *args, **kwargs):from typing import Any, Optional
import json
from redis.asyncio import Redis
from .config.redis import get_redis

class RedisCache:
    def __init__(self):
        pass  # L'instance Redis sera récupérée à chaque appel
    
    async def get(self, key: str) -> Optional[Any]:
        redis = await get_redis()
        value = await redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 600) -> bool:
        redis = await get_redis()
        return await redis.set(key, json.dumps(value), ex=ttl)
    
    async def delete(self, key: str) -> bool:
        redis = await get_redis()
        return bool(await redis.delete(key))
    
    async def clear(self) -> bool:
        redis = await get_redis()
        return await redis.flushdb()
    
    async def close(self):
        redis = await get_redis()
        await redis.close()
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        if not hasattr(self, '_initialized'):
            self._redis = Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            self._initialized = True
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self._redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 600) -> bool:
        return await self._redis.set(key, json.dumps(value), ex=ttl)
    
    async def delete(self, key: str) -> bool:
        return bool(await self._redis.delete(key))
    
    async def clear(self) -> bool:
        return await self._redis.flushdb()
    
    async def close(self):
        if self._redis:
            await self._redis.close()
            await self._redis.connection_pool.disconnect()