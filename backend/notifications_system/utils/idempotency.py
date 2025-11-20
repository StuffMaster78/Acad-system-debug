import hashlib, time
from django.core.cache import cache

def idempotent(key: str, ttl=60):
    """
    Returns True if this call is first use of the key (and locks it), else False.
    """
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    cache_key = f"idemp:{digest}"
    # add() returns True only if key did not exist
    return cache.add(cache_key, int(time.time()), ttl)