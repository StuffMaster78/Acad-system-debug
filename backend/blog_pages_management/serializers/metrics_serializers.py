"""
Serializers for website-level content metrics and SEO health.
"""
from rest_framework import serializers
from ..models.analytics_models import (
    WebsiteContentMetrics,
    WebsitePublishingTarget,
    CategoryPublishingTarget,
    ContentFreshnessReminder,
)
from ..models import BlogPost


class SEOHealthSerializer(serializers.Serializer):
    """
    Lightweight serializer for SEO health flags per blog post.
    Intended for use inside website-level metrics responses.
    """

    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.SlugField()
    meta_title = serializers.CharField(allow_null=True, allow_blank=True)
    meta_description = serializers.CharField(allow_null=True, allow_blank=True)
    meta_title_ok = serializers.BooleanField()
    meta_description_ok = serializers.BooleanField()
    meta_title_too_long = serializers.BooleanField()
    meta_description_too_long = serializers.BooleanField()
    meta_title_missing = serializers.BooleanField()
    meta_description_missing = serializers.BooleanField()


class WebsiteContentMetricsSerializer(serializers.ModelSerializer):
    """
    Serializer exposing website-level content metrics,
    plus a compact SEO health summary for blog posts.
    """

    seo_health = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteContentMetrics
        fields = [
            "id",
            "website",
            "calculated_at",
            "total_posts",
            "published_posts",
            "draft_posts",
            "category_metrics",
            "tag_metrics",
            "seo_health",
        ]
        read_only_fields = ["id", "calculated_at"]

    def get_seo_health(self, obj):
        """
        Return a minimal SEO health overview for the website's posts:
        - missing / over-length meta titles and descriptions.
        """
        # Allow caller to limit number of posts for performance
        limit = int(self.context.get("seo_health_limit", 50))
        posts_qs = (
            BlogPost.objects.filter(website=obj.website, is_deleted=False)
            .order_by("-created_at")[:limit]
        )

        results = []
        for post in posts_qs:
            meta_title = post.meta_title or ""
            meta_description = post.meta_description or ""

            title_len = len(meta_title)
            desc_len = len(meta_description)

            title_missing = title_len == 0
            desc_missing = desc_len == 0
            title_too_long = title_len > 60
            desc_too_long = desc_len > 160

            results.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "meta_title": post.meta_title,
                    "meta_description": post.meta_description,
                    "meta_title_ok": not (title_missing or title_too_long),
                    "meta_description_ok": not (desc_missing or desc_too_long),
                    "meta_title_too_long": title_too_long,
                    "meta_description_too_long": desc_too_long,
                    "meta_title_missing": title_missing,
                    "meta_description_missing": desc_missing,
                }
            )
        return results


class WebsitePublishingTargetSerializer(serializers.ModelSerializer):
    """Serializer for WebsitePublishingTarget."""
    current_month_stats = serializers.SerializerMethodField()
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    class Meta:
        model = WebsitePublishingTarget
        fields = [
            'id', 'website', 'website_name', 'monthly_target', 'is_auto_estimated',
            'estimation_reason', 'last_updated', 'updated_by', 'current_month_stats'
        ]
        read_only_fields = ['last_updated', 'current_month_stats']
    
    def get_current_month_stats(self, obj):
        """Get current month publishing stats."""
        return obj.get_current_month_stats()


class ContentFreshnessReminderSerializer(serializers.ModelSerializer):
    """Serializer for ContentFreshnessReminder."""
    blog_title = serializers.CharField(source='blog_post.title', read_only=True)
    blog_slug = serializers.CharField(source='blog_post.slug', read_only=True)
    blog_url = serializers.SerializerMethodField()
    website_name = serializers.CharField(source='blog_post.website.name', read_only=True)
    days_since_update = serializers.SerializerMethodField()
    
    class Meta:
        model = ContentFreshnessReminder
        fields = [
            'id', 'blog_post', 'blog_title', 'blog_slug', 'blog_url', 'website_name',
            'last_reminder_sent', 'reminder_count', 'is_acknowledged', 'acknowledged_at',
            'acknowledged_by', 'created_at', 'updated_at', 'days_since_update'
        ]
        read_only_fields = ['created_at', 'updated_at', 'days_since_update']
    
    def get_blog_url(self, obj):
        """Get URL to edit the blog post."""
        return f"/admin/blog/{obj.blog_post.id}/"
    
    def get_days_since_update(self, obj):
        """Calculate days since last update."""
        from django.utils import timezone
        delta = timezone.now() - obj.blog_post.updated_at
        return delta.days


class CategoryPublishingTargetSerializer(serializers.ModelSerializer):
    """Serializer for CategoryPublishingTarget."""
    current_month_stats = serializers.SerializerMethodField()
    website_name = serializers.CharField(source='website.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CategoryPublishingTarget
        fields = [
            'id', 'website', 'website_name', 'category', 'category_name',
            'monthly_target', 'is_active', 'created_at', 'updated_at', 'current_month_stats'
        ]
        read_only_fields = ['created_at', 'updated_at', 'current_month_stats']
    
    def get_current_month_stats(self, obj):
        """Get current month publishing stats."""
        return obj.get_current_month_stats()

