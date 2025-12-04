from celery import shared_task
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import BlogPost, AdminNotification, Newsletter, NewsletterSubscriber
from django.db.models import F
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.cache import cache
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from itertools import islice
# import spacy
# import numpy as np
# import pandas as pd
# from surprise import SVD, Dataset, Reader
from celery import shared_task
from django.core.cache import cache
from .models import BlogClick

# nlp = spacy.load("en_core_web_md")
User = get_user_model()

# @shared_task
# def generate_blog_embeddings():
#     """Computes and stores NLP-based vector embeddings for all blogs."""
#     blogs = BlogPost.objects.filter(embedding__isnull=True)
#     for blog in blogs:
#         doc = nlp(blog.content)
#         blog.embedding = doc.vector.tolist()  # Store vector representation
#         blog.save(update_fields=["embedding"])

#     return f"Generated embeddings for {blogs.count()} blogs."

# @shared_task
# def find_similar_blogs(blog_id):
#     """Finds and caches similar blogs using content similarity."""
#     blog = BlogPost.objects.get(id=blog_id)
#     if not blog.embedding:
#         return "No embedding found for this blog."

#     all_blogs = BlogPost.objects.exclude(id=blog.id).exclude(embedding__isnull=True)
    
#     similarities = [
#         (
#             other_blog,
#             np.dot(blog.embedding, other_blog.embedding) / (np.linalg.norm(blog.embedding) * np.linalg.norm(other_blog.embedding))
#         )
#         for other_blog in all_blogs
#     ]
    
#     sorted_blogs = sorted(similarities, key=lambda x: x[1], reverse=True)[:5]
#     similar_blog_data = [{"title": b[0].title, "slug": b[0].slug, "similarity": b[1]} for b in sorted_blogs]

#     cache.set(f"similar_blogs_{blog.id}", similar_blog_data, timeout=3600)
#     return f"Cached similar blogs for {blog.title}."

# @shared_task
# def train_blog_recommendation_model():
#     """Trains a collaborative filtering model for personalized blog recommendations."""
#     data = BlogClick.objects.values("user_id", "blog_id")
#     df = pd.DataFrame(data)

#     reader = Reader(rating_scale=(1, 1))  # Binary rating (clicked/not clicked)
#     dataset = Dataset.load_from_df(df[["user_id", "blog_id"]], reader)

#     trainset = dataset.build_full_trainset()
#     model = SVD()
#     model.fit(trainset)

#     cache.set("blog_recommendation_model", model, timeout=86400)
#     return "Trained blog recommendation model."

# @shared_task
# def recommend_blogs_for_user(user_id):
#     """Generates personalized blog recommendations using an ML model."""
#     model = cache.get("blog_recommendation_model")
#     if not model:
#         return "No trained model found."

#     blogs = BlogPost.objects.all()
#     predictions = [(blog, model.predict(user_id, blog.id).est) for blog in blogs]
#     sorted_blogs = sorted(predictions, key=lambda x: x[1], reverse=True)[:5]

#     recommended_blog_data = [{"title": b[0].title, "slug": b[0].slug, "score": b[1]} for b in sorted_blogs]
#     cache.set(f"user_recommendations_{user_id}", recommended_blog_data, timeout=86400)
    
#     return f"Generated recommendations for User {user_id}."


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
    Updates the freshness scores of all blogs daily.
    """
    blogs = BlogPost.objects.all()
    updated_count = 0

    for blog in blogs:
        days_since_update = (now() - blog.updated_at).days if blog.updated_at else 365
        engagement_decay = max(0, 10 - blog.click_count)

        new_freshness_score = max(0, 100 - (days_since_update * 2) - engagement_decay)

        if new_freshness_score < 40:
            AdminNotification.objects.create(
                user=blog.last_edited_by,
                message=f"Blog '{blog.title}' needs an update. Freshness Score: {new_freshness_score}"
            )

        blog.freshness_score = new_freshness_score
        blog.save(update_fields=["freshness_score"])
        updated_count += 1

    return f"Updated freshness scores for {updated_count} blogs."


@shared_task
def reset_click_counters():
    """Resets daily, weekly, and monthly click counts at correct intervals."""
    today = datetime.today().weekday()  # 0 = Monday, 6 = Sunday

    # Reset daily clicks
    BlogPost.objects.update(daily_clicks=0)

    # Reset weekly clicks only on **Monday**
    if today == 0:
        BlogPost.objects.update(weekly_clicks=0)

    # Reset monthly clicks only on the **1st of the month**
    if now().day == 1:
        BlogPost.objects.update(monthly_clicks=0)

    return "Click counters reset successfully."



@shared_task
def compress_image_task(image_field):
    """Compresses and resizes an image asynchronously before saving."""
    img = Image.open(image_field)

    img = img.convert("RGB")
    max_width = 1200
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.ANTIALIAS)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=80)
    buffer.seek(0)

    # Save back to the model field
    image_field.save(image_field.name, ContentFile(buffer.getvalue()), save=True)

    return f"Image {image_field.name} compressed successfully."


@shared_task
def send_newsletter(newsletter_id):
    """Sends newsletters in smaller batches to prevent email flooding."""
    newsletter = Newsletter.objects.get(id=newsletter_id)
    emails = list(NewsletterSubscriber.objects.filter(
        website=newsletter.website, is_active=True
    ).values_list("email", flat=True))

    batch_size = 100
    for i in range(0, len(emails), batch_size):
        send_mail(
            subject=newsletter.subject_a,
            message=newsletter.content_a,
            from_email="newsletters@yourdomain.com",
            recipient_list=emails[i:i + batch_size],  # Send in chunks
            fail_silently=True,
        )

    return f"Newsletter sent to {len(emails)} subscribers."



# send weekly newsletter
@shared_task
def send_weekly_newsletter():
    """Sends the latest published blogs to newsletter subscribers every week."""
    one_week_ago = now() - timedelta(days=7)
    blogs = BlogPost.objects.filter(is_published=True, publish_date__gte=one_week_ago)

    emails = NewsletterSubscriber.objects.filter(is_active=True).values_list("email", flat=True)

    if blogs.exists():
        blog_list = "\n".join([f"- {blog.title}: {blog.get_absolute_url()}" for blog in blogs])
        message = f"Here are the latest blogs from this week:\n\n{blog_list}"
        
        send_mail(
            subject="🔥 Weekly Blog Roundup",
            message=message,
            from_email="newsletters@yourdomain.com",
            recipient_list=list(emails),
            fail_silently=True,
        )


@shared_task
def update_blog_engagement_cache():
    """Batch update blog engagement stats in Redis."""
    blogs = BlogPost.objects.filter(is_published=True).values("id", "click_count", "conversion_count")
    for blog in blogs:
        cache.set(f"blog_engagement_{blog['id']}", blog, timeout=600)

@shared_task
def publish_scheduled_blogs():
    """Automatically publishes scheduled blog posts efficiently."""
    now_time = now()
    BlogPost.objects.filter(is_published=False, scheduled_publish_date__lte=now_time).update(
        is_published=True, publish_date=now_time
    )

@shared_task
def cleanup_expired_edit_locks():
    """Clean up expired edit locks."""
    from .services.draft_editing_service import DraftEditingService
    count = DraftEditingService.cleanup_expired_locks()
    return f"Cleaned up {count} expired locks"


@shared_task
def cleanup_old_autosaves():
    """Clean up old autosaves (older than 7 days)."""
    from .services.draft_editing_service import DraftEditingService
    count = DraftEditingService.cleanup_old_autosaves(days=7)
    return f"Cleaned up {count} old autosaves"


@shared_task
def auto_publish_scheduled_blogs():
    """Check and auto-publish scheduled blog posts."""
    from django.utils import timezone
    from .models import BlogPost
    from .services.draft_editing_service import DraftEditingService
    
    now = timezone.now()
    scheduled_blogs = BlogPost.objects.filter(
        status="scheduled",
        scheduled_publish_date__lte=now,
        is_published=False
    )
    
    published_count = 0
    for blog in scheduled_blogs:
        blog.status = "published"
        blog.is_published = True
        if not blog.publish_date:
            blog.publish_date = now()
        blog.save()
        
        # Create revision for published post
        try:
            DraftEditingService.create_revision(blog, blog.last_edited_by or blog.authors.first(), "Auto-published")
        except Exception:
            pass
        
        published_count += 1
    
    return f"Published {published_count} scheduled blog posts"


def check_for_broken_links():
    """Scans blog content for broken links and alerts admins."""
    for blog in BlogPost.objects.filter(is_published=True):
        soup = BeautifulSoup(blog.content, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]

        broken_links = []
        for link in links:
            try:
                response = requests.head(link, timeout=5)
                if response.status_code >= 400:
                    broken_links.append(link)
            except requests.RequestException:
                broken_links.append(link)

        if broken_links:
            for admin in User.objects.filter(is_staff=True):
                message = f"Blog '{blog.title}' contains {len(broken_links)} broken links."
                AdminNotification.objects.create(user=admin, message=message)


@shared_task
def update_engagement_stats():
    """Background task to cache trending and engaging blogs."""
    last_week = now() - timedelta(days=7)
    blogs = BlogPost.objects.filter(updated_at__gte=last_week).only("title", "slug", "click_count", "conversion_count")

    trending_blogs = blogs.order_by("-click_count")[:5]
    most_engaging_blogs = blogs.order_by("-conversion_count")[:5]


    engagement_stats = {
        "trending_blogs": [{"title": blog.title, "slug": blog.slug, "clicks": blog.click_count} for blog in trending_blogs],
        "most_engaging_blogs": [{"title": blog.title, "slug": blog.slug, "conversions": blog.conversion_count} for blog in most_engaging_blogs],
    }

    # Store new stats & version
    cache.set("engagement_stats", engagement_stats, timeout=3600)  # Cache for 1 hour
    cache.set("engagement_version", now().timestamp(), timeout=3600)  # Store new version for ETag


@shared_task
def sync_blog_clicks_to_db():
    """
    Periodically syncs blog click counts from Redis to the database in bulk.
    """
    updated_blogs = []
    cache_keys = cache.keys("blog_clicks_*")  # Fetch all cached click keys

    for cache_key in cache_keys:
        blog_id = cache_key.split("_")[-1]  # Extract blog ID from key
        click_count = cache.get(cache_key)

        if click_count:
            # Increment clicks in the database using F() expressions
            BlogPost.objects.filter(id=blog_id).update(click_count=F("click_count") + click_count)

            # Store updated blog IDs to log
            updated_blogs.append(blog_id)

            # Clear the cache after syncing
            cache.delete(cache_key)

    return f"Synced {len(updated_blogs)} blog clicks to DB."


@shared_task
def sync_blog_conversions_to_db():
    """
    Periodically syncs blog conversion counts from Redis to the database in bulk.
    """
    updated_blogs = []
    cache_keys = cache.keys("blog_conversions_*")

    for cache_key in cache_keys:
        blog_id = cache_key.split("_")[-1]  # Extract blog ID from cache key
        conversion_count = cache.get(cache_key)

        if conversion_count:
            BlogPost.objects.filter(id=blog_id).update(conversion_count=F("conversion_count") + conversion_count)
            updated_blogs.append(blog_id)
            cache.delete(cache_key)

    return f"Synced {len(updated_blogs)} blog conversions to DB."


@shared_task
def cleanup_soft_deleted_blogs():
    """
    Deletes soft-deleted blogs that have been expired for more than 30 days.
    """
    threshold_date = now() - timedelta(days=30)
    expired_blogs = BlogPost.objects.filter(is_deleted=True, deleted_at__lte=threshold_date)
    deleted_count = expired_blogs.count()

    for blog in expired_blogs:
        cache.delete(f"blog_{blog.id}")  # Clear related cache
        cache.delete(f"blog_clicks_{blog.id}")
        cache.delete(f"blog_conversions_{blog.id}")

    expired_blogs.delete()  # Permanently delete from DB

    return f"Deleted {deleted_count} expired soft-deleted blogs."

@shared_task
def update_trending_blogs():
    """Fetches and caches trending and most engaging blogs."""
    last_week = now() - timedelta(days=7)

    trending_blogs = BlogPost.objects.filter(updated_at__gte=last_week).order_by("-click_count")[:5]
    engaging_blogs = BlogPost.objects.filter(updated_at__gte=last_week).order_by("-conversion_count")[:5]

    engagement_stats = {
        "trending_blogs": [{"title": b.title, "slug": b.slug, "clicks": b.click_count} for b in trending_blogs],
        "most_engaging_blogs": [{"title": b.title, "slug": b.slug, "conversions": b.conversion_count} for b in engaging_blogs],
    }

    cache.set("engagement_stats", engagement_stats, timeout=3600)  # Cache for 1 hour
    return "Updated trending blog cache."


@shared_task
def aggregate_content_metrics():
    """
    Periodically aggregates ContentEvent data and updates cached metrics on BlogPosts.
    Runs every 6 hours to keep metrics fresh without overloading the system.
    """
    from .services.content_metrics_service import ContentMetricsService
    
    try:
        ContentMetricsService.update_all_blog_posts()
        return "Successfully updated content metrics for all published blog posts."
    except Exception as e:
        return f"Error updating content metrics: {str(e)}"


@shared_task
def recalculate_website_content_metrics():
    """
    Recalculates WebsiteContentMetrics for all websites.
    Runs daily to keep aggregated metrics fresh.
    """
    from websites.models import Website
    from .models.analytics_models import WebsiteContentMetrics
    
    try:
        websites = Website.objects.filter(is_active=True)
        results = []
        
        for website in websites:
            try:
                metrics = WebsiteContentMetrics.calculate_for_website(website)
                results.append({
                    'website_id': website.id,
                    'website_name': website.name,
                    'status': 'success',
                    'metrics_id': metrics.id
                })
            except Exception as e:
                results.append({
                    'website_id': website.id,
                    'website_name': website.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'total_websites': websites.count(),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
    except Exception as e:
        return f"Error recalculating website content metrics: {str(e)}"


@shared_task
def recalculate_service_website_content_metrics():
    """
    Recalculates ServiceWebsiteContentMetrics for all websites.
    Runs daily to keep aggregated service page metrics fresh.
    """
    from websites.models import Website
    from service_pages_management.models.enhanced_models import ServiceWebsiteContentMetrics
    
    try:
        websites = Website.objects.filter(is_active=True)
        results = []
        
        for website in websites:
            try:
                metrics = ServiceWebsiteContentMetrics.calculate_for_website(website)
                results.append({
                    'website_id': website.id,
                    'website_name': website.name,
                    'status': 'success',
                    'metrics_id': metrics.id
                })
            except Exception as e:
                results.append({
                    'website_id': website.id,
                    'website_name': website.name,
                    'status': 'error',
                    'error': str(e)
                })
        
        return {
            'total_websites': websites.count(),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
    except Exception as e:
        return f"Error recalculating service website content metrics: {str(e)}"


@shared_task
def send_content_freshness_reminders():
    """
    Send reminders to admins/superadmins about content that hasn't been updated.
    Uses website-specific thresholds if set, otherwise defaults to 3 months.
    Runs weekly.
    """
    from .models.analytics_models import ContentFreshnessReminder, WebsitePublishingTarget
    from websites.models import Website
    from django.contrib.auth import get_user_model
    from notifications_system.models import Notification
    from notifications_system.enums import NotificationType, NotificationCategory, EventType
    
    User = get_user_model()
    
    try:
        websites = Website.objects.filter(is_active=True)
        all_reminders = []
        
        # Process each website with its custom threshold
        for website in websites:
            try:
                target = WebsitePublishingTarget.objects.get(website=website)
                threshold = target.freshness_threshold_months
            except WebsitePublishingTarget.DoesNotExist:
                threshold = 3  # Default
            
            # Refresh reminders for this website
            reminders = ContentFreshnessReminder.create_or_update_reminders(
                months_threshold=threshold,
                website=website
            )
            all_reminders.extend(reminders)
        
        # Get all admins and superadmins
        admins = User.objects.filter(role__in=['admin', 'superadmin'], is_active=True)
        
        notifications_sent = 0
        for reminder in all_reminders:
            if reminder.is_acknowledged:
                continue
            
            # Check if we should send (not sent in last 7 days)
            from django.utils import timezone
            from datetime import timedelta
            if reminder.last_reminder_sent and reminder.last_reminder_sent > timezone.now() - timedelta(days=7):
                continue
            
            # Create notifications for all admins
            for admin in admins:
                # Filter by website if admin is website-specific
                if hasattr(admin, 'website') and admin.website != reminder.blog_post.website:
                    continue
                
                Notification.objects.create(
                    website=reminder.blog_post.website,
                    user=admin,
                    type=NotificationType.IN_APP,
                    title=f"Content Needs Updating: {reminder.blog_post.title}",
                    message=f"This blog post hasn't been updated in {reminder.days_since_update} days. Consider refreshing the content.",
                    link=f"/admin/blog/{reminder.blog_post.id}/",
                    category=NotificationCategory.WARNING,
                    event=EventType.CONTENT_FRESHNESS_REMINDER,
                    payload={
                        'blog_post_id': reminder.blog_post.id,
                        'blog_title': reminder.blog_post.title,
                        'days_since_update': reminder.days_since_update,
                    },
                    is_critical=False,
                )
                notifications_sent += 1
            
            # Update reminder
            reminder.last_reminder_sent = timezone.now()
            reminder.reminder_count += 1
            reminder.save()
        
        return f"Sent {notifications_sent} content freshness reminders for {len(all_reminders)} stale posts."
    except Exception as e:
        return f"Error sending content freshness reminders: {str(e)}"


@shared_task
def send_monthly_publishing_reminders():
    """
    Send reminders to admins about monthly publishing targets.
    Runs daily to check progress.
    """
    from .models.analytics_models import WebsitePublishingTarget
    from django.contrib.auth import get_user_model
    from notifications_system.models import Notification
    from notifications_system.enums import NotificationType, NotificationCategory, EventType
    from websites.models import Website
    
    User = get_user_model()
    
    try:
        websites = Website.objects.filter(is_active=True)
        notifications_sent = 0
        
        for website in websites:
            target = WebsitePublishingTarget.get_or_create_for_website(website)
            stats = target.get_current_month_stats()
            
            # Only send reminder if we're past mid-month and below target
            from datetime import datetime
            now = datetime.now()
            if now.day < 15:  # Don't remind in first half of month
                continue
            
            published = stats['published']
            target_count = stats['target']
            percentage = stats['percentage']
            
            # Send reminder if below 50% of target and past mid-month
            if published == 0:
                message = f"You have not published any content this month for {website.name}. Target: {target_count} posts/month."
            elif percentage < 50:
                message = f"You only published {published} article(s) this month for {website.name}. Target: {target_count} posts/month. Please strive to add more."
            else:
                continue  # Skip if doing well
            
            # Get admins for this website
            admins = User.objects.filter(
                role__in=['admin', 'superadmin'],
                is_active=True
            )
            
            for admin in admins:
                # Filter by website if admin is website-specific
                if hasattr(admin, 'website') and admin.website != website:
                    continue
                
                Notification.objects.create(
                    website=website,
                    user=admin,
                    type=NotificationType.IN_APP,
                    title=f"Monthly Publishing Target: {website.name}",
                    message=message,
                    link="/admin/content-metrics",
                    category=NotificationCategory.INFO,
                    event=EventType.MONTHLY_PUBLISHING_REMINDER,
                    payload={
                        'website_id': website.id,
                        'website_name': website.name,
                        'published': published,
                        'target': target_count,
                        'percentage': percentage,
                    },
                    is_critical=False,
                )
                notifications_sent += 1
        
        return f"Sent {notifications_sent} monthly publishing reminders."
    except Exception as e:
        return f"Error sending monthly publishing reminders: {str(e)}"


@shared_task
def send_content_reminder_email_digest():
    """
    Send weekly email digest of content reminders to admins.
    Includes stale content and publishing target progress.
    """
    from .models.analytics_models import ContentFreshnessReminder, WebsitePublishingTarget
    from websites.models import Website
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    User = get_user_model()
    
    try:
        websites = Website.objects.filter(is_active=True)
        emails_sent = 0
        
        for website in websites:
            # Get stale content
            try:
                target = WebsitePublishingTarget.objects.get(website=website)
                threshold = target.freshness_threshold_months
            except WebsitePublishingTarget.DoesNotExist:
                threshold = 3
            
            stale_posts = ContentFreshnessReminder.get_stale_content(
                months_threshold=threshold,
                website=website
            )[:10]  # Limit to 10 most stale
            
            # Get monthly stats
            target = WebsitePublishingTarget.get_or_create_for_website(website)
            stats = target.get_current_month_stats()
            
            # Only send if there are issues
            if stale_posts.count() == 0 and stats['percentage'] >= 50:
                continue
            
            # Get admins for this website
            admins = User.objects.filter(
                role__in=['admin', 'superadmin'],
                is_active=True,
                email__isnull=False
            )
            
            for admin in admins:
                if hasattr(admin, 'website') and admin.website != website:
                    continue
                
                # Prepare email content
                subject = f"Content Reminder Digest: {website.name}"
                
                # Simple text email (can be enhanced with HTML template)
                message = f"""
Content Reminder Digest for {website.name}

Monthly Publishing Progress:
- Published: {stats['published']} / {stats['target']} ({stats['percentage']:.1f}%)
- Remaining: {stats['remaining']} posts needed

Stale Content ({stale_posts.count()} items):
"""
                for post in stale_posts:
                    days_old = (timezone.now() - post.updated_at).days
                    message += f"- {post.title} (not updated in {days_old} days)\n"
                
                message += f"\nView full details: /admin/content-metrics"
                
                try:
                    send_mail(
                        subject,
                        message,
                        None,  # Use DEFAULT_FROM_EMAIL
                        [admin.email],
                        fail_silently=False,
                    )
                    emails_sent += 1
                except Exception as e:
                    # Log error but continue
                    print(f"Failed to send email to {admin.email}: {e}")
        
        return f"Sent {emails_sent} content reminder email digests."
    except Exception as e:
        return f"Error sending email digests: {str(e)}"
