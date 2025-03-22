from django.core.cache import cache
from .models import BlogPost, AdminNotification

def get_trending_blogs():
    """Returns trending blogs from cache, or fetches and caches if missing."""
    cache_key = "trending_blogs"
    trending_blogs = cache.get(cache_key)

    if not trending_blogs:
        trending_blogs = list(
            BlogPost.objects.filter(is_published=True).order_by("-click_count")[:5].values("title", "slug", "click_count")
        )
        cache.set(cache_key, trending_blogs, timeout=3600)  # Cache for 1 hour

    return trending_blogs

def get_admin_notifications(user):
    """Returns unread admin notifications from cache."""
    cache_key = f"admin_notifications_{user.id}"
    notifications = cache.get(cache_key)

    if not notifications:
        notifications = list(AdminNotification.objects.filter(user=user, is_read=False).values("message", "created_at"))
        cache.set(cache_key, notifications, timeout=300)  # Cache for 5 minutes

    return notifications