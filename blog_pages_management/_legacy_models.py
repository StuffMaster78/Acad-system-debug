from django.db import transaction, models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils import timezone
import requests
from django.db.models import F
import math
import re
import uuid
from websites.models import Website
from django.utils.crypto import get_random_string
from bs4 import BeautifulSoup  # Extract headings
import json
from django.core.exceptions import ValidationError
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
import subprocess
from django.conf import settings
from PIL import Image, ImageEnhance
# import spacy
import numpy as np
from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache

# # Load NLP Model
# nlp = spacy.load("en_core_web_md")

User = settings.AUTH_USER_MODEL 

def generate_tracking_id():
    value = get_random_string(32)
    if not isinstance(value, str):
        raise ValueError("Tracking ID must be a string")
    return value
class BlogCategory(models.Model):
    """
    Represents a category for blog posts.
    Enhanced with SEO metadata and analytics tracking.
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blog_categories"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True)
    
    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="SEO title for category page"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="SEO description for category page"
    )
    category_image = models.ImageField(
        upload_to="blog_categories/",
        null=True,
        blank=True,
        help_text="Category featured image"
    )
    
    # Analytics
    post_count = models.PositiveIntegerField(
        default=0,
        help_text="Cached count of published posts in this category"
    )
    total_views = models.PositiveIntegerField(
        default=0,
        help_text="Total views across all posts in this category"
    )
    total_conversions = models.PositiveIntegerField(
        default=0,
        help_text="Total conversions from posts in this category"
    )
    
    # Display
    display_order = models.IntegerField(
        default=0,
        help_text="Order for displaying categories"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured categories appear first"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Active categories are visible"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['website', 'slug']
        ordering = ['is_featured', 'display_order', 'name']
        verbose_name_plural = "Blog Categories"
        indexes = [
            models.Index(fields=['website', 'is_active']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        """Auto-generates slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        # Ensure slug uniqueness within website
        if BlogCategory.objects.filter(website=self.website, slug=self.slug).exclude(pk=self.pk if self.pk else None).exists():
            counter = 2
            new_slug = f"{self.slug}-{counter}"
            while BlogCategory.objects.filter(website=self.website, slug=new_slug).exclude(pk=self.pk if self.pk else None).exists():
                counter += 1
                new_slug = f"{self.slug}-{counter}"
            self.slug = new_slug
        super().save(*args, **kwargs)
    
    def update_analytics(self):
        """Update cached analytics for this category."""
        from . import BlogPost, BlogClick, BlogConversion
        
        # Count published posts
        self.post_count = BlogPost.objects.filter(
            category=self,
            is_published=True,
            is_deleted=False
        ).count()
        
        # Sum views
        blog_ids = BlogPost.objects.filter(category=self).values_list('id', flat=True)
        self.total_views = BlogClick.objects.filter(blog_id__in=blog_ids).count()
        
        # Sum conversions
        self.total_conversions = BlogConversion.objects.filter(
            blog_id__in=blog_ids,
            order_placed=True
        ).count()
        
        self.save(update_fields=['post_count', 'total_views', 'total_conversions'])

    def __str__(self):
        return f"{self.name} ({self.website.name})"


class BlogTag(models.Model):
    """Represents a tag for blog posts."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="tags"
    )
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class BlogResource(models.Model):
    """Represents a resource linked within a blog post."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="resources"
    )
    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class BlogFAQ(models.Model):
    """Stores FAQ entries related to a blog post."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blog_faqs"
    )
    blog = models.ForeignKey(
        'BlogPost', on_delete=models.CASCADE, related_name="faqs"
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question


class AuthorProfile(models.Model):
    """Stores details of blog authors."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="authors"
    )
    name = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="author_images/", null=True, blank=True
    )
    designation = models.CharField(
        max_length=255, blank=True, null=True, help_text="e.g., Senior Writer"
    )
    social_links = models.JSONField(default=dict, blank=True)
    is_fake = models.BooleanField(default=False)  # Fake authors flag
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expertise = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    twitter_handle = models.CharField(max_length=100, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    personal_website = models.URLField(blank=True, null=True)
    facebook_profile = models.URLField(blank=True, null=True)
    instagram_profile = models.URLField(blank=True, null=True)
    pinterest_profile = models.URLField(blank=True, null=True)
    medium_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    youtube_channel = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # Active status
    display_order = models.IntegerField(default=0)  # For ordering authors
    specialties = models.CharField(max_length=255, blank=True, null=True)
    awards = models.TextField(blank=True, null=True, help_text="Awards and recognitions")
    notable_works = models.TextField(blank=True, null=True, help_text="Notable works or publications")

    class Meta:
        ordering = ['display_order', 'name']
    def save(self, *args, **kwargs):
        """Auto-generates slug if not provided."""
        if self.profile_picture:
            self.profile_picture = self.compress_image(self.profile_picture)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """
    Represents a blog post with:
    - SEO-friendly slugs & metadata
    - Autogenerated Table of Contents (TOC)
    - Soft delete & auto-expiration
    - Scheduled publishing support
    - Unique titles per website
    - Click & conversion tracking
    - Edit logging
    """
    RESERVED_SLUGS = {
        'admin', 'dashboard', 'api', 'login', 'logout', 'register'
    }
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blogs",
        db_index=True
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    meta_title = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="SEO-friendly title for search engines"
    )
    meta_description = models.TextField(
        blank=True, null=True, help_text="SEO-friendly description"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, blank=True, db_index=True,
        help_text="Custom blog URL (use hyphens)"
    )
    content = models.TextField()
    toc = models.JSONField(default=dict, blank=True) 
    authors = models.ManyToManyField("AuthorProfile", related_name="blog_posts")
    is_editorial = models.BooleanField(default=False)
    category = models.ForeignKey(
        "BlogCategory", on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField("BlogTag", blank=True)
    featured_image = models.ImageField(
        upload_to="blog_images/", null=True, blank=True,
        help_text="Primary image (used in Open Graph and previews)"
    )
    is_featured = models.BooleanField(default=False)
    
    # Status management
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
        help_text="Publication status"
    )
    is_published = models.BooleanField(default=False, db_index=True)
    scheduled_publish_date = models.DateTimeField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_engagement = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Last user who edited this blog"
    )
    is_deleted = models.BooleanField(default=False, db_index=True)  # Soft delete flag
    deleted_at = models.DateTimeField(null=True, blank=True)  # Auto-removal tracking
    
    media_files = models.ManyToManyField("BlogMediaFile", blank=True, related_name="blog_posts")

    freshness_score = models.IntegerField(default=100, help_text="Content freshness score (0-100)")
    embedding = ArrayField(models.FloatField(), size=300, null=True, blank=True)  # 300-d vector
    canonical_url = models.URLField(blank=True, null=True, help_text="Original source URL if republished")

     # Engagement Tracking
    click_count = models.PositiveIntegerField(default=0, db_index=True)  # All-time clicks
    daily_clicks = models.PositiveIntegerField(default=0)
    weekly_clicks = models.PositiveIntegerField(default=0)
    monthly_clicks = models.PositiveIntegerField(default=0)
    semi_annual_clicks = models.PositiveIntegerField(default=0)
    annual_clicks = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["publish_date"]),
            models.Index(fields=["click_count"]),
            models.Index(fields=["conversion_count"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["is_deleted"]),
        ]

    def generate_toc(self):
        """Generates a Table of Contents (TOC) based on H1-H6 headings."""
        soup = BeautifulSoup(self.content, "html.parser")
        headings = soup.find_all(["h2", "h3", "h4", "h5", "h6"])
        toc_data = []

        for heading in headings:
            toc_entry = {
                "level": heading.name,  # e.g., h2, h3, h4
                "text": heading.get_text(strip=True),
                "id": heading.get("id") or slugify(heading.get_text(strip=True))
            }
            heading["id"] = toc_entry["id"]  # Ensure headings have unique IDs
            toc_data.append(toc_entry)

        self.toc = toc_data
        self.content = str(soup)  # Save updated content with ID attributes

    def check_duplicate_content(self):
        """Detects duplicate blog content across different websites."""
        similar_blogs = BlogPost.objects.exclude(id=self.id).filter(content=self.content)
        return similar_blogs.exists()

    def clean_slug(self, slug):
        """Ensures the slug is lowercase and only contains letters, numbers, and hyphens."""
        cleaned_slug = slug.lower().strip()
        cleaned_slug = re.sub(r'[^a-z0-9-]', '', cleaned_slug)
        return cleaned_slug

    def save(self, *args, **kwargs):
        """Generates a strict slug, prevents duplicates, and ensures scheduled publishing."""
        # Track changes for edit history
        fields_changed = []
        previous_content = None
        if self.pk:
            try:
                old_instance = BlogPost.objects.get(pk=self.pk)
                previous_content = old_instance.content
                # Track changed fields
                for field in ['title', 'content', 'meta_title', 'meta_description']:
                    if getattr(old_instance, field) != getattr(self, field):
                        fields_changed.append(field)
                
                # Track slug changes
                if old_instance.slug != self.slug:
                    BlogSlugHistory.objects.create(blog=self, old_slug=old_instance.slug)
            except BlogPost.DoesNotExist:
                pass
        
        if not self.slug:
            base_slug = self.clean_slug(slugify(self.title))
        else:
            base_slug = self.clean_slug(slugify(self.slug))

        if base_slug in self.RESERVED_SLUGS:
            raise ValueError(
                f"The slug '{base_slug}' is reserved. Choose another."
            )

        # Ensure slug uniqueness within the same website
        if BlogPost.objects.filter(website=self.website, slug=base_slug).exclude(pk=self.pk if self.pk else None).exists():
            counter = 2
            new_slug = f"{base_slug}-{counter}"
            while BlogPost.objects.filter(website=self.website, slug=new_slug).exclude(pk=self.pk if self.pk else None).exists():
                counter += 1
                new_slug = f"{base_slug}-{counter}"
            base_slug = new_slug

        self.slug = base_slug

        # Sync status with is_published
        if self.status == "published":
            self.is_published = True
            if not self.publish_date:
                self.publish_date = now()
        elif self.status == "draft":
            # Drafts are not published, but keep existing publish_date if set
            pass
        elif self.status == "archived":
            self.is_published = False
        
        # Ensure scheduled blogs auto-publish
        if self.status == "scheduled" and self.scheduled_publish_date and self.scheduled_publish_date <= now():
            self.status = "published"
            self.is_published = True
            if not self.publish_date:
                self.publish_date = now()

        # Validate internal links only for published/scheduled posts
        if self.status in ["published", "scheduled"]:
            try:
                self.validate_internal_links()
            except ValidationError as e:
                # Allow saving even if links aren't perfect (for drafts)
                # But log the validation error
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Internal links validation failed for blog {self.id}: {str(e)}")
        
        self.generate_toc()

        super().save(*args, **kwargs)
        
        # Create edit history entry if content changed
        if previous_content and previous_content != self.content and fields_changed:
            try:
                from .models.content_blocks import BlogEditHistory
                BlogEditHistory.objects.create(
                    blog=self,
                    edited_by=self.last_edited_by,
                    previous_content=previous_content,
                    current_content=self.content,
                    fields_changed=fields_changed,
                    changes_summary=f"Updated: {', '.join(fields_changed)}"
                )
            except Exception:
                # Silently fail if edit history model doesn't exist yet (migration pending)
                pass

    def validate_internal_links(self):
        """Ensures all links are internal, belong to the same website, and count is within limits."""
        soup = BeautifulSoup(self.content, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True)]
        
        # Filter only internal links
        internal_links = [link for link in links if link.startswith("/")]

        # Enforce the minimum (5) and maximum (10) internal links rule
        if len(internal_links) < 5:
            raise ValidationError(
                f"At least 5 internal links are required. Found {len(internal_links)}."
            )
        if len(internal_links) > 10:
            raise ValidationError(
                f"Maximum 10 internal links allowed. Found {len(internal_links)}."
            )

        # Check if all internal links exist
        slugs = [link.strip("/").split("/")[-1] for link in internal_links]
        existing_slugs = set(
            BlogPost.objects.filter(website=self.website, slug__in=slugs).values_list("slug", flat=True)
        )
        for slug in slugs:
            if slug not in existing_slugs:
                raise ValidationError(f"Broken link detected: {slug}")

    @property
    def word_count(self):
        """Calculates the word count of the blog content."""
        return len(self.content.split())

    @property
    def estimated_read_time(self):
        """Estimates read time based on 200 words per minute."""
        return math.ceil(self.word_count / 200)

    def soft_delete(self):
        """Marks the blog post as deleted instead of permanent deletion."""
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    def restore(self):
        """Restores a soft-deleted blog post."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    def update_freshness_score(self):
        """
        Calculates and stores the freshness score in
        the database instead of computing it every request.
        """
        days_since_update = (now() - self.updated_at).days
        days_since_last_click = (now() - self.last_engagement).days if self.last_engagement else days_since_update

        # Higher weight for engagement to prioritize active blogs
        engagement_factor = max(1, 100 - (days_since_last_click * 1.2))  # Weighting engagement higher
        freshness_factor = max(1, 100 - days_since_update)

        self.freshness_score = int((freshness_factor + engagement_factor) / 2)  # Weighted avg
        self.save(update_fields=["freshness_score"])

    def needs_update(self):
        """Checks if the freshness score falls below 40, suggesting an update."""
        return self.freshness_score < 40

    def mark_engagement(self):
        """Updates the last engagement timestamp & refreshes freshness score."""
        self.last_engagement = now()
        self.save(update_fields=["last_engagement"])
        self.update_freshness_score()  # Recalculate freshness after new engagement

    def get_blog_engagement(blog):
        """Fetch engagement stats from cache (if available)."""
        cache_key = f"blog_engagement_{blog.id}"
        engagement = cache.get(cache_key)

        if not engagement:
            engagement = {
                "clicks": blog.click_count,
                "conversions": blog.conversion_count
            }
            cache.set(cache_key, engagement, timeout=600)  # Cache for 10 min

        return engagement

    def increment_clicks(self, user, ip_address):
        """Efficiently tracks unique clicks with Redis caching."""
        cache_key = f"click_{self.id}_{user.id if user else ip_address}"

        if cache.get(cache_key):
            return  # Prevent multiple rapid clicks
        
        if not cache.get(cache_key):
            BlogClick.objects.create(blog=self, user=user, ip_address=ip_address)
            
            # Update in Redis
            cache.incr(f"blog_clicks_{self.id}", 1)  
            cache.set(cache_key, "clicked", timeout=86400)  # Prevent duplicate clicks for 1 day

            # Bulk update to database periodically
            self.click_count = cache.get(f"blog_clicks_{self.id}", 0)
            self.save(update_fields=["click_count"])

    def increment_conversions(self, user, action):
        """Tracks order-related conversions."""
        conversion, created = BlogConversion.objects.get_or_create(
            blog=self, user=user
        )

        if action == "clicked_order_page":
            conversion.clicked_order_page = True
        elif action == "placed_order":
            conversion.order_placed = True

        conversion.save()
        self.conversion_count = BlogConversion.objects.filter(blog=self, order_placed=True).count()
        self.save(update_fields=['conversion_count'])

    # def generate_embedding(self):
    #     """Generates and stores a vector embedding of the blog content."""
    #     doc = nlp(self.content)
    #     self.embedding = doc.vector.tolist()  # Convert to list for storage
    #     self.save(update_fields=["embedding"])

    def find_related_blogs(self):
        """Finds related blogs using cosine similarity on embeddings."""
        if not self.embedding:
            return []

        all_blogs = BlogPost.objects.exclude(id=self.id).exclude(embedding__isnull=True)
        similarities = [
            (blog, np.dot(self.embedding, blog.embedding) / (np.linalg.norm(self.embedding) * np.linalg.norm(blog.embedding)))
            for blog in all_blogs
        ]
        return [b[0] for b in sorted(similarities, key=lambda x: x[1], reverse=True)[:5]]

    def get_personalized_recommendations(self, user):
        """Suggests blogs based on user engagement history."""
        favorite_tags = user.blogclick_set.values_list("blog__tags", flat=True)
        return BlogPost.objects.filter(tags__in=favorite_tags).order_by("-click_count")[:5]


    def __str__(self):
        return f"{self.title} - {self.slug} ({self.status})"
    
class BlogMediaFile(models.Model):
    """Stores images, videos, and PDF files attached to blogs."""
    BLOG_MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("pdf", "PDF"),
         ("gif", "GIF"),
    ]
    
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blog_media"
    )
    file = models.FileField(upload_to="blog_media/")
    file_type = models.CharField(
        max_length=10,
        choices=BLOG_MEDIA_TYPES
    )
    alt_text = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Alt text for SEO"
    )
    caption = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Caption for the media file"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Compress images before saving."""
        if self.file_type == "image":
            self.file = self.compress_image(self.file)

        if self.file_type == "image" and not self.alt_text:
            self.generate_alt_text()
        super().save(*args, **kwargs)

    def generate_alt_text(self):
        """Generates an AI-based alt text for images."""
        if self.file_type != "image":
            return

        # API Request to AI Model (e.g., OpenAI, DeepAI, Azure Vision)
        api_url = "https://api.openai.com/v1/images/generate_alt_text"
        headers = {"Authorization": f"Bearer {settings.AI_API_KEY}"}
        response = requests.post(api_url, headers=headers, json={"image_url": self.file.url})

        if response.status_code == 200:
            self.alt_text = response.json().get("alt_text", "Image description not available")
            self.save(update_fields=["alt_text"])

    def compress_image(self, file):
        """Compress image while maintaining quality."""
        img = Image.open(file)
        img = img.convert("RGB")

        # Resize if larger than 1200px width
        max_width = 1200
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.ANTIALIAS)

        # Save image with compression
        output = BytesIO()
        img.save(output, format="JPEG", quality=80)
        output.seek(0)

        return ContentFile(output.read(), file.name)

    def is_image(self):
        return self.file_type == "image"

    def is_video(self):
        return self.file_type == "video"

    def is_pdf(self):
        return self.file_type == "pdf"

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"

    
class BlogClick(models.Model):
    """Tracks unique clicks per user/IP."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blogs_clicks"
    )
    blog = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="clicks"
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blog', 'user', 'ip_address')  # Ensures uniqueness


class BlogConversion(models.Model):
    """Tracks conversions linked to order page interactions."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blog_conversions"
    )
    blog = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="conversions"
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    order_placed = models.BooleanField(default=False)  # Tracks order placement
    clicked_order_page = models.BooleanField(default=False)  # Tracks visit
    converted_at = models.DateTimeField(auto_now_add=True)


class NewsletterCategory(models.Model):
    """Newsletter categories (e.g., Tech, Business, Health)."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="newsletter_categories"
    )
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        """Auto-generates a slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class NewsletterSubscriber(models.Model):
    """
    Tracks newsletter subscribers:
    - Users can switch between weekly & monthly
    - Tracks category preferences
    """

    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="subscribers"
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscription_type = models.CharField(
        max_length=10,
        choices=[("weekly", "Weekly"), ("monthly", "Monthly")],
        default="weekly"
    )
    categories = models.ManyToManyField(NewsletterCategory, blank=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    tracking_id = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        default=generate_tracking_id
    )

    def increment_open_count(self):
        """Increments the open count when the email is viewed."""
        self.open_count += 1
        self.last_opened_at = now()
        self.save(update_fields=["open_count", "last_opened_at"])

    def increment_click(self):
        """Increments click count when a user clicks a link in the newsletter."""
        self.click_count += 1
        self.save(update_fields=["click_count"])

    def switch_subscription(self, new_type):
        """Switches the user's subscription type."""
        self.subscription_type = new_type
        self.save(update_fields=["subscription_type"])

    def __str__(self):
        return f"{self.email} - {self.subscription_type} (Opens: {self.open_count})"

    

class Newsletter(models.Model):
    """
    Stores newsletters supporting:
    - Admin-controlled scheduling
    - A/B testing (Version A & Version B)
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="newsletter"
    )
    category = models.ForeignKey(
        "NewsletterCategory", on_delete=models.CASCADE, related_name="newsletters"
    )
    subject_a = models.CharField(max_length=255, help_text="A/B Test: Subject A")
    subject_b = models.CharField(max_length=255, blank=True, null=True, help_text="A/B Test: Subject B")
    content_a = models.TextField(help_text="A/B Test: Content A")
    content_b = models.TextField(blank=True, null=True, help_text="A/B Test: Content B")
    is_sent = models.BooleanField(default=False)
    scheduled_send_date = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def send_newsletter(self, version="A"):
        """Marks the newsletter as sent and records the timestamp."""
        self.is_sent = True
        self.sent_at = now()
        self.save(update_fields=["is_sent", "sent_at"])

    def __str__(self):
        return f"{self.category.name} - Sent: {self.is_sent}"


class NewsletterAnalytics(models.Model):
    """
    Stores analytics data for newsletters:
    - Open rates
    - Click-through rates (CTR)
    - Conversion tracking for A/B testing
    """
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="newsletter_analytics"
    )
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name="analytics")
    version = models.CharField(max_length=1, choices=[("A", "Version A"), ("B", "Version B")])
    sent_count = models.PositiveIntegerField(default=0)  # Total sent
    open_count = models.PositiveIntegerField(default=0)  # Opened emails
    click_count = models.PositiveIntegerField(default=0)  # Clicked links
    conversion_count = models.PositiveIntegerField(default=0)  # Conversions from emails

    def open_rate(self):
        """Calculates the open rate percentage."""
        return round((self.open_count / self.sent_count) * 100, 2) if self.sent_count else 0

    def click_through_rate(self):
        """Calculates the click-through rate percentage."""
        return round((self.click_count / self.sent_count) * 100, 2) if self.sent_count else 0

    def conversion_rate(self):
        """Calculates the conversion rate percentage."""
        return round((self.conversion_count / self.sent_count) * 100, 2) if self.sent_count else 0

    def __str__(self):
        return f"{self.newsletter.category.name} - Version {self.version}"
    

class BlogActionLog(models.Model):
    """Logs all manual restores & deletions of blogs."""
    ACTION_CHOICES = [
        ("restored", "Restored"),
        ("deleted", "Permanently Deleted"),
    ]

    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name="blog_logs")
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="action_logs")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.action} '{self.blog.title}' on {self.timestamp}"

    
class AdminNotification(models.Model):
    """Stores notifications for admins about blog deletions."""
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        """Marks the notification as read."""
        self.is_read = True
        self.save(update_fields=["is_read"])

    def __str__(self):
        return f"Notification for {self.user} - {self.message[:50]}"
    

class BlogVideo(models.Model):
    """Stores embedded YouTube/Vimeo/self-hosted videos."""
    VIDEO_SOURCES = [
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
        ("self_hosted", "Self-Hosted"),
        ("other", "Other"),
    ]

    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blog_videos"
    )
    blog = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="videos"
    )
    video_url = models.URLField()
    source = models.CharField(max_length=15, choices=VIDEO_SOURCES)

    thumbnail = models.ImageField(
        upload_to="video_thumbnails/", null=True, blank=True,
        help_text="Auto-generated thumbnail for self-hosted videos"
    )

    def generate_thumbnail(self):
        """Extracts a frame from a self-hosted video and saves it as a thumbnail."""
        if self.source != "self_hosted":
            return  # Thumbnails are only for self-hosted videos

        video_path = os.path.join(settings.MEDIA_ROOT, self.video_url.name)
        thumbnail_path = video_path.replace(".mp4", ".jpg")

        # Extract frame using ffmpeg
        command = f"ffmpeg -i {video_path} -ss 00:00:01 -vframes 1 {thumbnail_path}"
        subprocess.run(command, shell=True)

        # Save generated thumbnail
        with open(thumbnail_path, "rb") as thumb_file:
            self.thumbnail.save(os.path.basename(thumbnail_path), ContentFile(thumb_file.read()), save=True)

    def save(self, *args, **kwargs):
        """Generates a video thumbnail before saving."""
        super().save(*args, **kwargs)
        if self.source == "self_hosted" and not self.thumbnail:
            self.generate_thumbnail()

    def embed_code(self):
        """Returns an embed code for YouTube, Vimeo, and self-hosted videos."""
        if self.source == "youtube":
            video_id = self.video_url.split("v=")[-1]
            return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe>'
        if self.source == "vimeo":
            video_id = self.video_url.split("/")[-1]
            return f'<iframe src="https://player.vimeo.com/video/{video_id}" width="560" height="315" frameborder="0" allowfullscreen></iframe>'
        if self.source == "self_hosted":
            return f'<video width="100%" controls poster="{self.thumbnail.url}"><source src="{self.video_url.url}" type="video/mp4"></video>'

    def __str__(self):
        return f"{self.video_url} ({self.source})"
    

class BlogDarkModeImage(models.Model):
    """Stores different versions of an image for light/dark mode."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="dark_mode_images"
    )
    blog = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE, related_name="dark_mode_images"
    )
    light_mode_image = models.ImageField(upload_to="blog_images/light_mode/")
    dark_mode_image = models.ImageField(upload_to="blog_images/dark_mode/")

    def generate_dark_mode_image(self):
        """Auto-generates a dark-mode version if brightness is too high."""
        img = Image.open(self.light_mode_image)
        grayscale = img.convert("L")  # Convert to grayscale
        brightness = sum(grayscale.getdata()) / (255 * grayscale.size[0] * grayscale.size[1])

        if brightness > 0.7:  # High brightness, needs adjustment
            enhancer = ImageEnhance.Brightness(img)
            darkened_img = enhancer.enhance(0.5)  # Reduce brightness by 50%

            buffer = BytesIO()
            darkened_img.save(buffer, format="JPEG")
            self.dark_mode_image.save(
                self.light_mode_image.name.replace("light_mode", "dark_mode"),
                ContentFile(buffer.getvalue()), save=True
            )

    def save(self, *args, **kwargs):
        """Generates a dark-mode image before saving."""
        super().save(*args, **kwargs)
        if not self.dark_mode_image:
            self.generate_dark_mode_image()

    def __str__(self):
        return f"Dark Mode Images for {self.blog.title}"
    

class BlogABTest(models.Model):
    """Handles A/B testing for headlines & featured images."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="ab_testing_blogs"
    )
    blog = models.OneToOneField(BlogPost, on_delete=models.CASCADE, related_name="ab_test")
    headline_a = models.CharField(max_length=255)
    headline_b = models.CharField(max_length=255)
    image_a = models.ImageField(upload_to="blog_images/ab_testing/", null=True, blank=True)
    image_b = models.ImageField(upload_to="blog_images/ab_testing/", null=True, blank=True)
    click_count_a = models.PositiveIntegerField(default=0)
    click_count_b = models.PositiveIntegerField(default=0)
    conversion_count_a = models.PositiveIntegerField(default=0)
    conversion_count_b = models.PositiveIntegerField(default=0)
    winning_version = models.CharField(max_length=7, choices=[("A", "Version A"), ("B", "Version B"), ("Pending", "Pending")], default="Pending")

    def determine_winner(self):
        """Determines the winning version based on engagement."""
        if self.click_count_a + self.click_count_b >= 100:  # Minimum 100 impressions
            ctr_a = self.click_count_a / max(1, self.click_count_a + self.click_count_b)
            ctr_b = self.click_count_b / max(1, self.click_count_a + self.click_count_b)

            if ctr_a > ctr_b:
                self.winning_version = "A"
            else:
                self.winning_version = "B"

            self.save(update_fields=["winning_version"])


class SocialPlatform(models.Model):
    """Stores social media platforms where blogs can be shared."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="social_platforms"
    )
    name = models.CharField(max_length=100, unique=True)
    share_url_format = models.CharField(
        max_length=255, 
        help_text="Use {url} as placeholder for the article URL."
    )
    logo_url = models.URLField(
        max_length=500, blank=True, null=True,
        help_text="URL to the platform's logo (CDN or self-hosted)."
    )
    is_disabled_by_owner = models.BooleanField(
        default=False, help_text="If True, this platform is disabled for this website."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("website", "name")

    def __str__(self):
        status = "Disabled" if self.is_disabled_by_owner else "Active"
        return f"{self.name} ({self.website.name}) - {status}"


class BlogShare(models.Model):
    """Tracks where blogs have been shared."""
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE, related_name="blog_shares"
    )
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="shares")
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE, related_name="blog_shares")
    share_count = models.PositiveIntegerField(default=0)  # Track number of shares
    last_shared_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("blog", "platform")

    def increment_share(self):
        """Increments the share count."""
        self.share_count += 1
        self.save(update_fields=["share_count", "last_shared_at"])

    def __str__(self):
        return f"{self.blog.title} shared on {self.platform.name} ({self.share_count} times)"
    
class BlogSlugHistory(models.Model):
    """Keeps a history of old slugs for blogs to manage redirects."""
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="slug_history")
    old_slug = models.SlugField()
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="User who changed the slug"
    )
    is_active = models.BooleanField(default=True, help_text="If True, redirect from old slug is active")
    redirected_count = models.PositiveIntegerField(default=0, help_text="Number of times this old slug was used for redirection")
    last_redirected_at = models.DateTimeField(null=True, blank=True, help_text="Last time this slug was used for redirection")
    class Meta:
        unique_together = ("blog", "old_slug")
        indexes = [
            models.Index(fields=["old_slug"]),
        ]
    def increment_redirect(self):
        """Increments the redirect count and updates the last redirected timestamp."""
        self.redirected_count += 1
        self.last_redirected_at = now()
        self.save(update_fields=["redirected_count", "last_redirected_at"])
    