from django.core.cache import cache

def cache_notification_prefs(user_id, prefs):
    cache.set(f"notif_prefs:{user_id}", prefs, timeout=3600)

def clear_notification_prefs_cache(user_id):
    cache.delete(f"notif_prefs:{user_id}")