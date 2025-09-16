# notifications_system/utils/unread_counter.py
from django.core.cache import cache

def _key(user_id, website_id=None):
    w = website_id or "global"
    return f"notif:unread:{user_id}:{w}"

def get(user_id, website_id=None):
    v = cache.get(_key(user_id, website_id))
    return int(v) if v is not None else None

def set_(user_id, value, website_id=None, ttl=3600):
    cache.set(_key(user_id, website_id), int(value), ttl)

def incr(user_id, website_id=None, by=1):
    cache.incr(_key(user_id, website_id), by=by)

def decr(user_id, website_id=None, by=1):
    # guard against negative
    k = _key(user_id, website_id)
    v = cache.get(k) or 0
    v = max(0, int(v) - by)
    cache.set(k, v, 3600)

def invalidate(user_id, website_id=None):
    cache.delete(_key(user_id, website_id))