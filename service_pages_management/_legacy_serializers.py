from rest_framework import serializers
from datetime import timedelta
from django.utils.timezone import now
from .models import (
    ServicePage,
    ServicePageClick,
    ServicePageConversion
)


class FAQItemSerializer(serializers.Serializer):
    """
    Validates each item in the faq_json list.
    """
    question = serializers.CharField()
    answer = serializers.CharField()


class ServicePageSerializer(serializers.ModelSerializer):
    """
    Serializer for managing service pages with SEO and FAQ data.
    """
    faq_json = FAQItemSerializer(many=True, required=False)

    class Meta:
        model = ServicePage
        fields = [
            'id',
            'website',
            'title',
            'slug',
            'header',
            'content',
            'meta_title',
            'meta_description',
            'image',
            'og_image',
            'faq_json',
            'is_published',
            'publish_date',
            'is_deleted',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_by',
            'updated_by',
            'created_at',
            'updated_at'
        ]

    def validate_faq_json(self, value):
        """
        Ensures faq_json is a list of dictionaries with Q&A.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("FAQ must be a list.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    "Each FAQ item must be a dictionary."
                )
            if 'question' not in item or 'answer' not in item:
                raise serializers.ValidationError(
                    "Each FAQ must include 'question' and 'answer'."
                )
        return value


class ServicePageAnalyticsSerializer(serializers.ModelSerializer):
    """
    Read-only analytics data for a service page.
    Supports ?days=N filtering via serializer context.
    """
    click_count = serializers.SerializerMethodField()
    conversion_count = serializers.SerializerMethodField()
    since = serializers.SerializerMethodField()

    class Meta:
        model = ServicePage
        fields = [
            'id',
            'title',
            'slug',
            'is_published',
            'publish_date',
            'click_count',
            'conversion_count',
            'since'
        ]

    def get_days(self):
        try:
            return int(self.context.get('days', 30))
        except (ValueError, TypeError):
            return 30

    def get_since(self, obj):
        return (now() - timedelta(days=self.get_days())).isoformat()

    def get_click_count(self, obj):
        since = now() - timedelta(days=self.get_days())
        return ServicePageClick.objects.filter(
            service_page=obj,
            timestamp__gte=since
        ).count()

    def get_conversion_count(self, obj):
        since = now() - timedelta(days=self.get_days())
        return ServicePageConversion.objects.filter(
            service_page=obj,
            timestamp__gte=since
        ).count()