from typing import Any, Optional

from django.core.cache import cache

from config_system.cache.keys import build_config_cache_key
from config_system.cache.redis_cache import RedisCacheClient


class ConfigCacheService:
    """
    Config caching layer (tenant + website + user aware)
    """

    redis = RedisCacheClient()

    @staticmethod
    def get(
        key: str,
        website_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Any:
        cache_key = build_config_cache_key(key, website_id, user_id=user_id)
        return cache.get(cache_key)

    @staticmethod
    def set(
        key: str,
        value: Any,
        ttl: Optional[int] = 300,
        website_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        cache_key = build_config_cache_key(key, website_id, user_id=user_id)

        if ttl is None:
            cache.set(cache_key, value)
        else:
            cache.set(cache_key, value, int(ttl))

    @staticmethod
    def delete(
        key: str,
        website_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        cache_key = build_config_cache_key(key, website_id, user_id=user_id)
        cache.delete(cache_key)

    @classmethod
    def invalidate_prefix(
        cls,
        key_prefix: str,
    ) -> None:
        """
        Best-effort bulk invalidation.
        """

        pattern = f"config:*{key_prefix}*"

        try:
            cls.redis.safe_delete_pattern(pattern)
        except Exception:
            pass