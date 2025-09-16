# notifications_system/utils/dedupe.py
import hashlib
from django.core.cache import cache

def _key(user_id, event_key, website_id=None, sig=None):
    s = sig or ""
    return f"notif:dedupe:{user_id}:{website_id or 'global'}:{event_key}:{s}"

def signature(payload: dict, keep=("title","message","link")):
    # fold only stable keys
    parts = [f"{k}={payload.get(k)}" for k in keep]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

def allow_once(user_id, event_key, website_id=None, payload=None, ttl=60):
    sig = signature(payload or {})
    k = _key(user_id, event_key, website_id, sig)
    return cache.add(k, "1", ttl)  # True if it did not exist (i.e., allowed)

def clear_dedupe(user_id, event_key, website_id=None, payload=None):
    sig = signature(payload or {})
    k = _key(user_id, event_key, website_id, sig)
    cache.delete(k)