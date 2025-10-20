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
