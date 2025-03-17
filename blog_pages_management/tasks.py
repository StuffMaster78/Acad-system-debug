from celery import shared_task
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import BlogPost, AdminNotification
from django.db.models import F

User = get_user_model()

@shared_task
def auto_delete_soft_deleted_blogs():
    """Deletes blogs that have been soft-deleted for over 30 days."""
    expiration_date = now() - timedelta(days=30)
    deleted_blogs = BlogPost.objects.filter(is_deleted=True, deleted_at__lte=expiration_date)

    if not deleted_blogs.exists():
        return "No soft-deleted blogs to remove."

    count = deleted_blogs.count()
    blog_titles = list(deleted_blogs.values_list("title", flat=True))

    # Bulk delete
    deleted_blogs.delete()

    # Send notifications to all admins
    admin_emails = User.objects.filter(is_staff=True, is_superuser=True, email__isnull=False).values_list("email", flat=True)

    if admin_emails:
        send_mail(
            subject="Auto-Deleted Soft-Deleted Blogs",
            message=f"The following {count} soft-deleted blogs were permanently removed:\n\n" + "\n".join(blog_titles),
            from_email="no-reply@yourdomain.com",
            recipient_list=list(admin_emails),
            fail_silently=True,
        )

    return f"Auto-deleted {count} expired soft-deleted blog posts."


@shared_task
def warn_admins_before_deletion():
    """Notifies admins 7 days before soft-deleted blogs are permanently removed."""
    warning_threshold = now() - timedelta(days=23)  # 7 days before auto-delete
    expiring_blogs = BlogPost.objects.filter(is_deleted=True, deleted_at__lte=warning_threshold)

    if not expiring_blogs.exists():
        return "No blogs require admin warnings."

    count = expiring_blogs.count()
    admins = User.objects.filter(is_staff=True, is_superuser=True)

    notifications = [
        AdminNotification(user=admin, message=f"Warning: {count} blogs will be permanently deleted in 7 days. Review and restore if necessary.")
        for admin in admins
    ]

    AdminNotification.objects.bulk_create(notifications)  # Bulk insert for efficiency
    return f"Notified admins about {count} soon-to-be-deleted blogs."


@shared_task
def update_freshness_scores():
    """
    Decreases freshness scores over time while rewarding engagement.
    """
    # Use F() expressions to calculate the new freshness scores dynamically
    days_since_update = now() - timedelta(days=1)  # Every 24 hours update

    BlogPost.objects.filter(is_published=True).update(
        freshness_score=F("freshness_score") - (F("freshness_score") * 0.02),  # 2% decay per day
        last_engagement=now()
    )

    return "Updated freshness scores for all published blogs."


@shared_task
def reset_click_counters():
    """Resets daily, weekly, and monthly click counts."""
    BlogPost.objects.update(
        daily_clicks=0,
        weekly_clicks=F("weekly_clicks") - F("daily_clicks"),
        monthly_clicks=F("monthly_clicks") - F("daily_clicks"),
        last_engagement=now(),
    )

    return "Click counters reset successfully."