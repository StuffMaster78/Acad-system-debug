import aioredis
from redis.asyncio import Redis
from django.conf import settings

r = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class PresenceService:
    """Service to manage user presence in chat threads using Redis."""
    TTL = 60  # seconds
    PREFIX = "active_users"

    @classmethod
    async def _get_redis(cls):
        return await aioredis.from_url(settings.REDIS_URL)

    @classmethod
    async def add_user(cls, thread_id, user_id, username):
        redis = await cls._get_redis()
        key = f"{cls.PREFIX}:{thread_id}"
        await redis.hset(key, user_id, username)
        await redis.expire(key, cls.TTL)

    @classmethod
    async def remove_user(cls, thread_id, user_id):
        redis = await cls._get_redis()
        key = f"{cls.PREFIX}:{thread_id}"
        await redis.hdel(key, user_id)

    @classmethod
    async def get_users(cls, thread_id):
        redis = await cls._get_redis()
        key = f"{cls.PREFIX}:{thread_id}"
        data = await redis.hgetall(key)
        return {int(k.decode()): v.decode() for k, v in data.items()}



    # @staticmethod
    # def _key(thread_id):
    #     return f"presence:{thread_id}"

    # @classmethod
    # async def add_user(cls, thread_id, user_id):
    #     await r.sadd(cls._key(thread_id), user_id)

    # @classmethod
    # async def remove_user(cls, thread_id, user_id):
    #     await r.srem(cls._key(thread_id), user_id)

    # @classmethod
    # async def get_users(cls, thread_id):
    #     return await r.smembers(cls._key(thread_id))