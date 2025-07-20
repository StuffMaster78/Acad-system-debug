from django.core.cache import cache
from notifications_system.models.notification_preferences import NotificationPreference
from notifications_system.services.preferences import assign_default_preferences

def get_cached_preferences(user):
    """
    Get user preferences from cache or fallback to DB or default.
    """
    if not user or not user.is_authenticated:
        return None

    key = f"notif_prefs:{user.id}"
    pref = cache.get(key)

    if pref:
        return pref

    try:
        pref = NotificationPreference.objects.get(user=user, website=user.website)
    except NotificationPreference.DoesNotExist:
        pref = assign_default_preferences(user, user.website)

    cache.set(key, pref, timeout=3600)
    return pref


def invalidate_preferences_cache(user_id):
    cache.delete(f"notif_prefs:{user_id}")


def update_preferences_cache(user):
    pref = NotificationPreference.objects.get(user=user, website=user.website)
    cache.set(f"notif_prefs:{user.id}", pref, timeout=3600)