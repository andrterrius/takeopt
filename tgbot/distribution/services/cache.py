from typing import Optional
from redis.asyncio import Redis
from tgbot.distribution.interfaces import ICacheService


class RedisCacheService(ICacheService):
    """Реализация кэш-сервиса на Redis"""

    def __init__(self, redis: Redis):
        self._redis = redis

    async def get(self, key: str) -> Optional[str]:
        return await self._redis.get(key)

    async def set(self, key: str, value: str, ex: int = None) -> bool:
        return await self._redis.set(key, value, ex=ex)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)

    async def set_nx(self, key: str, value: str, ex: int = None) -> bool:
        return await self._redis.set(key, value, ex=ex, nx=True)