# notifications_system/utils/last_seen.py
from django.utils import timezone
from . import cache_helpers

def last_seen_key(user_id): return f"notif:last_seen:{user_id}"

def set_last_seen(user):
    cache_helpers.cache_notification_prefs(user.id, {"_last_seen": timezone.now().isoformat()})
    # If you prefer DB as source of truth:
    if hasattr(user, "notif_meta"):
        user.notif_meta.touch()

def get_last_seen(user):
    meta = getattr(user, "notif_meta", None)
    return getattr(meta, "last_seen_at", None)