from django.core.cache import cache


class AuditCache:

    @staticmethod
    def get(key: str):
        return cache.get(key)

    @staticmethod
    def set(key: str, value, timeout: int = 60):
        cache.set(key, value, timeout)

    @staticmethod
    def delete(key: str):
        cache.delete(key)