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
from datetime import timedelta
from django.utils.timezone import now



# ------------------ BLOG CATEGORY SERIALIZER ------------------

class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories."""
    website_name = serializers.SerializerMethodField()
    website_domain = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ["id", "website", "website_name", "website_domain", "name", "slug", "description", 
                  "meta_title", "meta_description", "display_order", "is_featured", "is_active", 
                  "post_count", "total_views", "total_conversions", "created_at", "updated_at"]
        read_only_fields = ["slug", "post_count", "total_views", "total_conversions", "created_at", "updated_at"]

    def get_website_name(self, obj):
        """Get website name for display."""
        return obj.website.name if obj.website else None

    def get_website_domain(self, obj):
        """Get website domain for display."""
        return obj.website.domain if obj.website else None

    def validate_name(self, value):
        """Ensures unique category name per website."""
        website_id = self.initial_data.get("website") or (self.instance.website_id if self.instance else None)
        if not website_id:
            # Try to get from request context
            request = self.context.get("request")
            if request and hasattr(request, "data"):
                website_id = request.data.get("website")
        
        if website_id:
            existing = BlogCategory.objects.filter(website_id=website_id, name=value)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError(
                    "Category already exists for this website."
                )
        return value


# ------------------ BLOG TAG SERIALIZER ------------------

class BlogTagSerializer(serializers.ModelSerializer):
    """Serializer for blog tags."""
    website_name = serializers.SerializerMethodField()
    website_domain = serializers.SerializerMethodField()
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogTag
        fields = ["id", "website", "website_name", "website_domain", "name", "post_count"]
        read_only_fields = ["post_count"]

    def get_website_name(self, obj):
        """Get website name for display."""
        return obj.website.name if obj.website else None

    def get_website_domain(self, obj):
        """Get website domain for display."""
        return obj.website.domain if obj.website else None

    def get_post_count(self, obj):
        """Get count of published posts using this tag."""
        from .models import BlogPost
        return BlogPost.objects.filter(tags=obj, is_published=True, is_deleted=False).count()


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
        read_only_fields = ["id", "blog"]


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
        detected_type = None

        # Determine file type based on extension
        for media_type, extensions in ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                detected_type = media_type
                break

        if not detected_type:
            raise serializers.ValidationError(f"Invalid file type: {extension}")

        return value

    class Meta:
        model = BlogMediaFile
        fields = ["id", "website", "file", "file_type", "alt_text", "caption", "uploaded_at"]

class BlogPostSerializer(serializers.ModelSerializer):
    """Serializer for blog posts with related fields."""
    authors = AuthorProfileSerializer(many=True, read_only=True)
    category = BlogCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    tags = BlogTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=BlogTag.objects.all(),
        source='tags',
        write_only=True,
        many=True,
        required=False
    )
    resources = BlogResourceSerializer(many=True, read_only=True)
    faqs = BlogFAQSerializer(many=True, read_only=True)
    faqs_data = BlogFAQSerializer(many=True, write_only=True, required=False)
    resources_data = BlogResourceSerializer(many=True, write_only=True, required=False)
    word_count = serializers.ReadOnlyField()
    estimated_read_time = serializers.ReadOnlyField()
    media_files = BlogMediaFileSerializer(many=True, read_only=True)
    website = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id", "website", "uuid", "meta_title", "meta_description",
            "title", "slug", "content", "toc", "authors", "category", "category_id",
            "tags", "tag_ids", "resources", "resources_data", "faqs", "faqs_data",
            "featured_image", "is_featured", "status", "is_published",
            "scheduled_publish_date", "publish_date", "created_at",
            "updated_at", "last_edited_by", "is_deleted", "deleted_at",
            "click_count", "conversion_count", "word_count",
            "estimated_read_time", "media_files"
        ]
        read_only_fields = ["slug", "click_count", "conversion_count", "uuid"]
    
    def create(self, validated_data):
        """Create blog post with FAQs and resources."""
        faqs_data = validated_data.pop('faqs_data', [])
        resources_data = validated_data.pop('resources_data', [])
        website = validated_data.get('website')
        
        blog_post = super().create(validated_data)
        
        # Create FAQs
        for faq_data in faqs_data:
            BlogFAQ.objects.create(
                blog=blog_post,
                website=website,
                question=faq_data.get('question'),
                answer=faq_data.get('answer')
            )
        
        # Note: BlogResource doesn't have a direct blog FK, so we'll just create them for the website
        # If you need blog-specific resources, you'd need to add a blog FK to BlogResource model
        for resource_data in resources_data:
            BlogResource.objects.create(
                website=website,
                title=resource_data.get('title'),
                url=resource_data.get('url'),
                description=resource_data.get('description', '')
            )
        
        return blog_post
    
    def update(self, instance, validated_data):
        """Update blog post with FAQs and resources."""
        faqs_data = validated_data.pop('faqs_data', None)
        resources_data = validated_data.pop('resources_data', None)
        website = validated_data.get('website') or instance.website
        
        blog_post = super().update(instance, validated_data)
        
        # Update FAQs if provided
        if faqs_data is not None:
            # Delete existing FAQs
            BlogFAQ.objects.filter(blog=blog_post).delete()
            # Create new FAQs
            for faq_data in faqs_data:
                BlogFAQ.objects.create(
                    blog=blog_post,
                    website=website,
                    question=faq_data.get('question'),
                    answer=faq_data.get('answer')
                )
        
        # Update Resources if provided
        if resources_data is not None:
            # Delete existing resources (or you might want to keep them and just update)
            # For now, we'll replace them
            BlogResource.objects.filter(website=website).delete()
            # Create new resources
            for resource_data in resources_data:
                BlogResource.objects.create(
                    website=website,
                    title=resource_data.get('title'),
                    url=resource_data.get('url'),
                    description=resource_data.get('description', '')
                )
        
        return blog_post
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None

    def validate_title(self, value):
        """Ensures unique title per website."""
        website = self.context["request"].data.get("website")
        if BlogPost.objects.filter(website=website, title=value).exists():
            raise serializers.ValidationError(
                "A blog with this title already exists."
            )
        return value

    def validate_content(self, value):
        request = self.context.get("request")
        blog_id = self.instance.id if self.instance else None  # Handle update cases
        
        if BlogPost.objects.exclude(id=blog_id).filter(content=value).exists():
            raise serializers.ValidationError("This content is too similar to an existing blog.")
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
        if value.lower() in RESERVED_SLUGS:
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

    def validate(self, data):
        """Prevents duplicate clicks within 24 hours."""
        user = data.get("user")
        blog = data.get("blog")
        time_threshold = now() - timedelta(hours=24)

        if BlogClick.objects.filter(user=user, blog=blog, clicked_at__gte=time_threshold).exists():
            raise serializers.ValidationError("You have already clicked on this blog in the last 24 hours.")

        return data


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

    def validate(self, data):
        """Prevents duplicate conversions per blog post per user."""
        user = data.get("user")
        blog = data.get("blog")

        if BlogConversion.objects.filter(user=user, blog=blog, order_placed=True).exists():
            raise serializers.ValidationError("You have already converted from this blog.")

        return data


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

        domain = blog.website.domain  # Assuming Website model has a `domain` field
        return platform.share_url_format.replace("{url}", f"https://{domain}/blogs/{blog.slug}")
    

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
        """Ensures admins can only mark their own notifications as read."""
        request = self.context["request"]
        if instance.user != request.user:
            raise serializers.ValidationError("You cannot update another admin's notifications.")

        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.save()
        return instance