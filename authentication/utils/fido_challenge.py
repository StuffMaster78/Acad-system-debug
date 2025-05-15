# utils/fido_challenge.py

import json
from django.conf import settings
from django.core.cache import cache
from django.http import Http404


def build_redis_key(domain: str, token: str) -> str:
    """
    Build a namespaced Redis key for passkey operations.
    """
    return f"{settings.PASSKEY_REDIS_PREFIX}:{domain}:{token}"


def cache_challenge(
        domain: str,
        token: str,
        state: dict,
        ttl: int = None
) -> None:
    """
    Store challenge state in Redis under a domain-scoped key.
    """
    key = build_redis_key(domain, token)
    cache.set(
        key,
        json.dumps(state),
        timeout=ttl or settings.PASSKEY_CHALLENGE_TTL
    )


def get_cached_challenge(
        domain: str,
        token: str,
        delete: bool = True
) -> dict:
    """
    Retrieve and optionally delete challenge from Redis.
    """
    key = build_redis_key(domain, token)
    payload = cache.get(key)

    if not payload:
        raise Http404("Challenge not found or expired.")

    if delete:
        cache.delete(key)

    return json.loads(payload)


def delete_challenge(domain: str, token: str) -> None:
    """
    Manually delete a cached passkey challenge.
    """
    key = build_redis_key(domain, token)
    cache.delete(key)