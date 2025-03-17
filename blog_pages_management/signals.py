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
    Updates the blog click count when a new click is recorded.
    Uses F() expressions to avoid race conditions.
    """
    if created:
        BlogPost.objects.filter(id=instance.blog.id).update(
            click_count=F("click_count") + 1,
            daily_clicks=F("daily_clicks") + 1,
            weekly_clicks=F("weekly_clicks") + 1,
            monthly_clicks=F("monthly_clicks") + 1,
            semi_annual_clicks=F("semi_annual_clicks") + 1,
            annual_clicks=F("annual_clicks") + 1,
            last_engagement=now(),
        )


@receiver(post_save, sender=BlogConversion)
def update_blog_conversions(sender, instance, created, **kwargs):
    """
    Updates the blog conversion count when an order is placed.
    Uses F() expressions to avoid race conditions.
    """
    if created and instance.order_placed:
        BlogPost.objects.filter(id=instance.blog.id).update(
            conversion_count=F("conversion_count") + 1
        )


# ------------------ BLOG AUTO-PUBLISH & SEO OPTIMIZATION ------------------

@receiver(post_save, sender=BlogPost)
def auto_publish_blog(sender, instance, created, **kwargs):
    """
    Automatically publishes scheduled blog posts when the time arrives.
    Clears the cache to refresh blog content.
    """
    if instance.scheduled_publish_date and instance.scheduled_publish_date <= now():
        instance.is_published = True
        instance.save(update_fields=["is_published", "publish_date"])
    
    # Invalidate sitemap cache when a new blog is published
    cache_key = f"sitemap_{instance.website.id}"
    cache.delete(cache_key)


# ------------------ BLOG SOFT DELETE HANDLING ------------------

@receiver(pre_delete, sender=BlogPost)
def log_blog_deletion(sender, instance, **kwargs):
    """
    Logs admin actions for soft-deleted blogs.
    Triggers an admin notification before permanent deletion.
    """
    if instance.is_deleted:
        AdminNotification.objects.create(
            user=instance.last_edited_by,
            message=f"Blog '{instance.title}' is scheduled for permanent deletion."
        )


@receiver(post_delete, sender=BlogPost)
def clear_deleted_blog_cache(sender, instance, **kwargs):
    """
    Clears blog cache when a blog is permanently deleted.
    """
    cache_key = f"blog_{instance.id}"
    cache.delete(cache_key)


# ------------------ FRESHNESS SCORE & AI-BASED RECOMMENDATIONS ------------------

@receiver(post_save, sender=BlogPost)
def update_freshness_score(sender, instance, **kwargs):
    """
    Updates the freshness score based on engagement and last update.
    Suggests blog updates if the score is below 40.
    """
    days_since_update = (now() - instance.updated_at).days
    engagement_decay = max(0, 10 - instance.click_count)  # Blogs with low clicks decay faster

    new_freshness_score = max(0, 100 - (days_since_update * 2) - engagement_decay)
    
    if new_freshness_score < 40:
        AdminNotification.objects.create(
            user=instance.last_edited_by,
            message=f"Blog '{instance.title}' needs an update. Freshness Score: {new_freshness_score}"
        )

    BlogPost.objects.filter(id=instance.id).update(freshness_score=new_freshness_score)