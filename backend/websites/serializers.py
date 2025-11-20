from rest_framework import serializers
from .models import Website, WebsiteActionLog, WebsiteStaticPage
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils import timezone

class WebsiteSerializer(serializers.ModelSerializer):
    """Serializer for Website Model, including SEO & Branding Settings"""

    class Meta:
        model = Website
        fields = [
            "id", "name", "domain", "slug",
            "is_active", "logo", "theme_color",
            "contact_email", "contact_phone",
            "meta_title", "meta_description",
            "allow_registration", "allow_guest_checkout",
            "google_analytics_id", "google_search_console_id", "bing_webmaster_id",
            "is_deleted", "deleted_at",
        ]
        read_only_fields = ["slug", "deleted_at"]

    def update(self, instance, validated_data):
        """Allow Admins to Restore Soft-Deleted Websites"""
        request = self.context.get("request")

        if "is_deleted" in validated_data:
            if request and request.user.is_superuser:
                if validated_data["is_deleted"]:
                    instance.soft_delete()
                else:
                    instance.restore()
            else:
                raise serializers.ValidationError("Only superadmins can modify deletion status.")

        return super().update(instance, validated_data)

class WebsiteActionLogSerializer(serializers.ModelSerializer):
    """Serializer for website action logs"""

    user = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()

    class Meta:
        model = WebsiteActionLog
        fields = ["id", "website", "user", "action", "details", "timestamp"]
        read_only_fields = fields

    def get_user(self, obj):
        return obj.user.get_full_name() if obj.user else "System"

    def get_website(self, obj):
        return obj.website.name

    @staticmethod
    def get_queryset():
        """Limit API calls to latest 100 logs for performance"""
        return WebsiteActionLog.objects.order_by("-timestamp")[:100]

class WebsiteStaticPageSerializer(serializers.ModelSerializer):
    """Serializer for managing static pages with full controls"""
    
    views = serializers.IntegerField(read_only=True)
    previous_versions = serializers.ListField(child=serializers.JSONField(), read_only=True)

    class Meta:
        model = WebsiteStaticPage
        fields = [
            "title", "slug", "content", "meta_title", "meta_description", 
            "language", "scheduled_publish_date", "views", "last_updated", "previous_versions"
        ]
        read_only_fields = ["views", "slug", "last_updated", "previous_versions"]

    def validate_scheduled_publish_date(self, value):
        """Ensure scheduled publish date is in the future"""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Scheduled publish date must be in the future.")
        return value

    def create(self, validated_data):
        """Auto-generate slug if not provided"""
        if "slug" not in validated_data or not validated_data["slug"]:
            base_slug = slugify(validated_data["title"])
            counter = 2
            while WebsiteStaticPage.objects.filter(slug=base_slug).exists():
                base_slug = f"{slugify(validated_data['title'])}-{counter}"
                counter += 1
            validated_data["slug"] = base_slug

        return super().create(validated_data)


class WebsiteSEOUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = [
            'meta_title',
            'meta_description',
            'meta_keywords',
            'og_title',
            'og_description',
            'og_image',
        ]


class WebsiteSoftDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['is_active']  # or use ['is_deleted'] if your model uses that

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', False)
        instance.save()
        return instance