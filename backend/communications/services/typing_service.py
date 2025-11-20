import asyncio
from django.conf import settings
from redis.asyncio import Redis

r = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class TypingService:
    @staticmethod
    async def set_typing(thread_id: str, user_id: str, ttl=5):
        key = f"typing:{thread_id}:{user_id}"
        await r.set(key, "1", ex=ttl)

    @staticmethod
    async def is_typing(thread_id: str, user_id: str) -> bool:
        key = f"typing:{thread_id}:{user_id}"
        return await r.exists(key) == 1