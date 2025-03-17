from rest_framework import serializers
from .models import (
    BlogCategory, BlogTag, BlogResource, BlogFAQ, AuthorProfile,
    BlogPost, BlogClick, BlogConversion, NewsletterSubscriber,
    Newsletter, NewsletterAnalytics, NewsletterCategory,
    BlogMediaFile, BlogVideo, BlogDarkModeImage,
    BlogABTest, SocialPlatform, BlogShare,
    AdminNotification
)
from django.utils.text import slugify
import re


# ------------------ BLOG CATEGORY SERIALIZER ------------------

class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories."""

    class Meta:
        model = BlogCategory
        fields = ["id", "website", "name", "slug"]
        read_only_fields = ["slug"]

    def validate_name(self, value):
        """Ensures unique category name per website."""
        website = self.context["request"].data.get("website")
        if BlogCategory.objects.filter(
            website=website, name=value
        ).exists():
            raise serializers.ValidationError(
                "Category already exists for this website."
            )
        return value


# ------------------ BLOG TAG SERIALIZER ------------------

class BlogTagSerializer(serializers.ModelSerializer):
    """Serializer for blog tags."""

    class Meta:
        model = BlogTag
        fields = ["id", "website", "name"]


# ------------------ BLOG RESOURCE SERIALIZER ------------------

class BlogResourceSerializer(serializers.ModelSerializer):
    """Serializer for blog post resources."""

    class Meta:
        model = BlogResource
        fields = ["id", "website", "title", "url", "description"]


# ------------------ BLOG FAQ SERIALIZER ------------------

class BlogFAQSerializer(serializers.ModelSerializer):
    """Serializer for blog post FAQs."""

    class Meta:
        model = BlogFAQ
        fields = ["id", "blog", "question", "answer"]


# ------------------ AUTHOR PROFILE SERIALIZER ------------------

class AuthorProfileSerializer(serializers.ModelSerializer):
    """Serializer for author profiles."""

    class Meta:
        model = AuthorProfile
        fields = [
            "id", "website", "name", "bio", "profile_picture",
            "designation", "social_links", "is_fake"
        ]


# ------------------ BLOG POST SERIALIZER ------------------

class BlogMediaFileSerializer(serializers.ModelSerializer):
    """Serializer for handling blog media files (images, videos, PDFs)."""
    def validate_file(self, value):
        """Ensures only valid file types are uploaded."""
        ALLOWED_EXTENSIONS = {
            "image": ["jpg", "jpeg", "png", "webp", "gif"],  # GIFs allowed
            "video": ["mp4", "mov", "avi"],
            "pdf": ["pdf"],
        }

        extension = value.name.split(".")[-1].lower()
        file_type = self.initial_data.get("file_type")

        if file_type not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(f"Invalid file type: {file_type}")
        if extension not in ALLOWED_EXTENSIONS[file_type]:
            raise serializers.ValidationError(f"Invalid extension: {extension}")

        return value

    class Meta:
        model = BlogMediaFile
        fields = ["id", "website", "file", "file_type", "alt_text", "caption", "uploaded_at"]

class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer for blog posts with related fields."""
    authors = AuthorProfileSerializer(many=True, read_only=True)
    category = BlogCategorySerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    resources = BlogResourceSerializer(many=True, read_only=True)
    faqs = BlogFAQSerializer(many=True, read_only=True)
    word_count = serializers.ReadOnlyField()
    estimated_read_time = serializers.ReadOnlyField()
    media_files = BlogMediaFileSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id", "website", "uuid", "meta_title", "meta_description",
            "title", "slug", "content", "toc", "authors", "category", "tags",
            "featured_image", "is_featured", "is_published",
            "scheduled_publish_date", "publish_date", "created_at",
            "updated_at", "last_edited_by", "is_deleted", "deleted_at",
            "click_count", "conversion_count", "word_count",
            "estimated_read_time"
        ]
        read_only_fields = ["slug", "click_count", "conversion_count"]

    def validate_title(self, value):
        """Ensures unique title per website."""
        website = self.context["request"].data.get("website")
        if BlogPost.objects.filter(website=website, title=value).exists():
            raise serializers.ValidationError(
                "A blog with this title already exists."
            )
        return value

    def validate_slug(self, value):
        """Ensures valid slug formatting."""
        RESERVED_SLUGS = {
            'admin', 'dashboard', 'api', 'login', 'logout', 'register'
        }
        if " " in value:
            raise serializers.ValidationError(
                "Slug cannot contain spaces. Use hyphens instead."
            )
        if not re.match(r"^[a-zA-Z0-9-]+$", value):
            raise serializers.ValidationError(
                "Slug can only contain letters, numbers, and hyphens."
            )
        if value in RESERVED_SLUGS:
            raise serializers.ValidationError(
                f"The slug '{value}' is reserved. Choose another."
            )
        return value


# ------------------ BLOG CLICK SERIALIZER ------------------

class BlogClickSerializer(serializers.ModelSerializer):
    """Serializer for tracking unique blog clicks."""

    class Meta:
        model = BlogClick
        fields = ["id", "blog", "user", "ip_address", "clicked_at"]
        read_only_fields = ["clicked_at"]


# ------------------ BLOG CONVERSION SERIALIZER ------------------

class BlogConversionSerializer(serializers.ModelSerializer):
    """Serializer for tracking conversions from blog posts."""

    class Meta:
        model = BlogConversion
        fields = [
            "id", "blog", "user", "order_placed", "clicked_order_page",
            "converted_at"
        ]
        read_only_fields = ["converted_at"]


# ------------------ NEWSLETTER CATEGORY SERIALIZER ------------------

class NewsletterCategorySerializer(serializers.ModelSerializer):
    """Serializer for newsletter categories."""

    class Meta:
        model = NewsletterCategory
        fields = ["id", "website", "name", "slug"]
        read_only_fields = ["slug"]


# ------------------ NEWSLETTER SUBSCRIBER SERIALIZER ------------------

class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    """Serializer for newsletter subscribers."""

    class Meta:
        model = NewsletterSubscriber
        fields = [
            "id", "website", "email", "is_active", "subscription_type",
            "categories", "open_count", "click_count"
        ]
        read_only_fields = ["open_count", "click_count"]


# ------------------ NEWSLETTER SERIALIZER ------------------

class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for newsletters."""

    class Meta:
        model = Newsletter
        fields = [
            "id", "website", "category", "subject_a", "subject_b",
            "content_a", "content_b", "is_sent", "scheduled_send_date",
            "sent_at"
        ]
        read_only_fields = ["is_sent", "sent_at"]


# ------------------ NEWSLETTER ANALYTICS SERIALIZER ------------------

class NewsletterAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for tracking newsletter analytics."""
    open_rate = serializers.SerializerMethodField()
    click_through_rate = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()

    class Meta:
        model = NewsletterAnalytics
        fields = [
            "id", "website", "newsletter", "version", "sent_count", "open_count",
            "click_count", "conversion_count", "open_rate",
            "click_through_rate", "conversion_rate"
        ]

    def get_open_rate(self, obj):
        """Returns open rate percentage."""
        return obj.open_rate()

    def get_click_through_rate(self, obj):
        """Returns click-through rate percentage."""
        return obj.click_through_rate()

    def get_conversion_rate(self, obj):
        """Returns conversion rate percentage."""
        return obj.conversion_rate()


class BlogVideoSerializer(serializers.ModelSerializer):
    """Handles YouTube/Vimeo/self-hosted video embedding."""

    class Meta:
        model = BlogVideo
        fields = ["id", "website", "blog", "video_url", "source", "thumbnail"]

class BlogDarkModeImageSerializer(serializers.ModelSerializer):
    """Handles serving dark mode images via API."""

    class Meta:
        model = BlogDarkModeImage
        fields = ["website", "light_mode_image", "dark_mode_image"]

class BlogABTestSerializer(serializers.ModelSerializer):
    """Handles serialization for A/B testing on blog headlines & images."""

    total_clicks = serializers.SerializerMethodField()
    total_conversions = serializers.SerializerMethodField()
    click_through_rate_a = serializers.SerializerMethodField()
    click_through_rate_b = serializers.SerializerMethodField()
    conversion_rate_a = serializers.SerializerMethodField()
    conversion_rate_b = serializers.SerializerMethodField()

    class Meta:
        model = BlogABTest
        fields = [
            "id", "blog", "website", "headline_a", "headline_b",
            "image_a", "image_b", "click_count_a", "click_count_b",
            "conversion_count_a", "conversion_count_b", "winning_version",
            "total_clicks", "total_conversions",
            "click_through_rate_a", "click_through_rate_b",
            "conversion_rate_a", "conversion_rate_b",
        ]
        read_only_fields = [
            "click_count_a", "click_count_b",
            "conversion_count_a", "conversion_count_b",
            "winning_version", "total_clicks", "total_conversions",
            "click_through_rate_a", "click_through_rate_b",
            "conversion_rate_a", "conversion_rate_b",
        ]

    def get_total_clicks(self, obj):
        """Calculates total clicks for both versions."""
        return obj.click_count_a + obj.click_count_b

    def get_total_conversions(self, obj):
        """Calculates total conversions for both versions."""
        return obj.conversion_count_a + obj.conversion_count_b

    def get_click_through_rate_a(self, obj):
        """Calculates CTR for version A."""
        total_clicks = obj.click_count_a + obj.click_count_b
        return round((obj.click_count_a / max(1, total_clicks)) * 100, 2)

    def get_click_through_rate_b(self, obj):
        """Calculates CTR for version B."""
        total_clicks = obj.click_count_a + obj.click_count_b
        return round((obj.click_count_b / max(1, total_clicks)) * 100, 2)

    def get_conversion_rate_a(self, obj):
        """Calculates conversion rate for version A."""
        return round((obj.conversion_count_a / max(1, obj.click_count_a)) * 100, 2)

    def get_conversion_rate_b(self, obj):
        """Calculates conversion rate for version B."""
        return round((obj.conversion_count_b / max(1, obj.click_count_b)) * 100, 2)
    

class SocialPlatformSerializer(serializers.ModelSerializer):
    """Serializes available social platforms."""

    class Meta:
        model = SocialPlatform
        fields = ["id", "website", "name", "share_url_format", "logo_url", "is_active", "is_disabled_by_owner"]


class BlogShareSerializer(serializers.ModelSerializer):
    """Serializes blog share tracking data."""

    class Meta:
        model = BlogShare
        fields = ["id", "website", "blog", "platform", "share_count", "last_shared_at"]


class BlogShareURLSerializer(serializers.Serializer):
    """Generates shareable URLs for blog posts dynamically."""
    blog_id = serializers.IntegerField()
    platform_id = serializers.IntegerField()

    def validate(self, data):
        """Ensure the blog and platform exist and are active."""
        blog = BlogPost.objects.filter(id=data["blog_id"], is_published=True).first()
        platform = SocialPlatform.objects.filter(id=data["platform_id"], is_active=True).first()

        if not blog:
            raise serializers.ValidationError("Invalid or unpublished blog.")
        if not platform:
            raise serializers.ValidationError("Invalid or inactive platform.")

        return data

    def get_share_url(self):
        """Dynamically generates a shareable URL."""
        blog = BlogPost.objects.get(id=self.validated_data["blog_id"])
        platform = SocialPlatform.objects.get(id=self.validated_data["platform_id"])

        return platform.share_url_format.replace("{url}", f"https://example.com/blogs/{blog.slug}")
    

class AdminNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Admin Notifications.
    - Displays unread notifications.
    - Supports marking notifications as read.
    """

    class Meta:
        model = AdminNotification
        fields = ["id", "user", "message", "is_read", "created_at"]

    def update(self, instance, validated_data):
        """
        Allows marking notifications as read.
        """
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.save()
        return instance