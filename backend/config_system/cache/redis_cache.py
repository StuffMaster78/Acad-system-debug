from typing import Optional, Any
from django.core.cache import cache


class RedisCacheClient:
    """
    Safe cache adapter with proper typing guarantees.
    """

    def __init__(self):
        client = getattr(cache, "client", None)
        self._client: Any = client  # force explicit typing for Pylance

    # ----------------------------
    # BASIC OPS
    # ----------------------------

    def get(self, key: str) -> Any:
        return cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            cache.set(key, value)
        else:
            cache.set(key, value, int(ttl))

    def delete(self, key: str) -> None:
        cache.delete(key)

    def delete_many(self, keys: list[str]) -> None:
        cache.delete_many(keys)

    # ----------------------------
    # REDIS FEATURES
    # ----------------------------

    def supports_pattern_delete(self) -> bool:
        return self._client is not None and hasattr(self._client, "delete_pattern")

    def delete_pattern(self, pattern: str) -> int:
        if not self.supports_pattern_delete():
            raise NotImplementedError(
                "Pattern delete not supported by current cache backend"
            )

        # runtime safety guarantee
        client = self._client
        return client.delete_pattern(pattern)

    def safe_delete_pattern(self, pattern: str) -> int:
        if self.supports_pattern_delete():
            return self.delete_pattern(pattern)
        return 0