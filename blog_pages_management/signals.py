from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from .models import BlogPost, BlogClick, BlogConversion, AdminNotification
from django.core.cache import cache
from django.db.models import F

# ------------------ ENGAGEMENT TRACKING ------------------

@receiver(post_save, sender=BlogClick)
def update_blog_clicks(sender, instance, created, **kwargs):
    """
    Stores click counts in Redis instead of writing directly to DB.
    Celery task will sync Redis data to DB periodically.
    """
    if created:
        cache_key = f"blog_clicks_{instance.blog.id}"
        cache.incr(cache_key)  # Increment click count in Redis

@receiver(post_save, sender=BlogConversion)
def update_blog_conversions(sender, instance, created, **kwargs):
    """
    Stores conversion counts in Redis. Celery will sync them to the DB periodically.
    """
    if created:
        cache_key = f"blog_conversions_{instance.blog.id}"
        cache.incr(cache_key)  # Increment conversion count in Redis


# ------------------ BLOG AUTO-PUBLISH & SEO OPTIMIZATION ------------------

@receiver(post_save, sender=BlogPost)
def auto_publish_blog(sender, instance, created, **kwargs):
    """
    Automatically publishes scheduled blog posts when the time arrives.
    Clears the cache to refresh blog content.
    """
    if instance.scheduled_publish_date and instance.scheduled_publish_date <= now() and not instance.is_published:
        BlogPost.objects.filter(id=instance.id).update(
            is_published=True, publish_date=now()
        )
    
    # Invalidate sitemap cache when a new blog is published
    cache.delete(f"sitemap_{instance.website.id}")


# ------------------ BLOG SOFT DELETE HANDLING ------------------

@receiver(pre_delete, sender=BlogPost)
def log_blog_deletion(sender, instance, **kwargs):
    """
    Logs admin actions for soft-deleted blogs.
    Triggers an admin notification before permanent deletion.
    """
    if instance.is_deleted and instance.deleted_at:
        AdminNotification.objects.create(
            user=instance.last_edited_by,
            message=f"Blog '{instance.title}' is scheduled for permanent deletion."
        )


@receiver(post_delete, sender=BlogPost)
def clear_deleted_blog_cache(sender, instance, **kwargs):
    """
    Clears blog cache when a blog is permanently deleted.
    """
    cache.delete_many([
        f"blog_{instance.id}",
        f"blog_clicks_{instance.id}",
        f"blog_conversions_{instance.id}",
        f"sitemap_{instance.website.id}"
    ])


# ------------------ FRESHNESS SCORE & AI-BASED RECOMMENDATIONS ------------------

@receiver(post_save, sender=BlogPost)
def update_freshness_score(sender, instance, **kwargs):
    """
    Updates the freshness score based on engagement and last update.
    Suggests blog updates if the score is below 40.
    """
    days_since_update = (now() - instance.updated_at).days if instance.updated_at else 365
    engagement_decay = max(0, 10 - instance.click_count)  # Blogs with low clicks decay faster

    new_freshness_score = max(0, 100 - (days_since_update * 2) - engagement_decay)
    
    if new_freshness_score < 40:
        AdminNotification.objects.create(
            user=instance.last_edited_by,
            message=f"Blog '{instance.title}' needs an update. Freshness Score: {new_freshness_score}"
        )

    BlogPost.objects.filter(id=instance.id).update(freshness_score=new_freshness_score)