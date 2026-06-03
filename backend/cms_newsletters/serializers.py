from rest_framework import serializers

from cms_newsletters.models import (
    Newsletter,
    NewsletterAnalytics,
    Subscriber,
    SubscriberCategory,
)


class SubscriberCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriberCategory
        fields = ["id", "name", "slug"]


class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    frequency = serializers.ChoiceField(
        choices=["weekly", "monthly", "instant"],
        default="weekly",
    )
    consent_marketing = serializers.BooleanField(default=False)
    source = serializers.CharField(default="blog_form")
    source_detail = serializers.CharField(default="", required=False)


class UnsubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reason = serializers.ChoiceField(
        choices=["too_frequent", "not_relevant", "never_subscribed", "other"],
        default="other",
    )


class SubscriberListSerializer(serializers.ModelSerializer):
    categories = SubscriberCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Subscriber
        fields = [
            "id", "email", "is_active", "frequency",
            "source", "source_detail", "categories",
            "consent_marketing",
            "open_count", "click_count",
            "last_opened_at", "last_clicked_at",
            "unsubscribed_at", "unsubscribe_reason",
            "created_at",
        ]
        read_only_fields = fields


class NewsletterListSerializer(serializers.ModelSerializer):
    analytics = serializers.SerializerMethodField()

    class Meta:
        model = Newsletter
        fields = [
            "id", "title", "subject_line", "preview_text",
            "status", "scheduled_send_date", "sent_at",
            "sender_name", "sender_email",
            "created_at", "analytics",
        ]

    def get_analytics(self, obj):
        try:
            return NewsletterAnalyticsSerializer(obj.analytics).data
        except Exception:
            return None


class NewsletterDetailSerializer(serializers.ModelSerializer):
    category = SubscriberCategorySerializer(read_only=True)
    analytics = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Newsletter
        fields = [
            "id", "title", "subject_line", "preview_text",
            "subject_line_b", "ab_split_percentage",
            "category", "sender_name", "sender_email",
            "status", "scheduled_send_date", "sent_at",
            "created_by_name", "created_at", "updated_at",
            "analytics",
        ]

    def get_analytics(self, obj):
        try:
            return NewsletterAnalyticsSerializer(obj.analytics).data
        except Exception:
            return None

    def get_created_by_name(self, obj):
        if obj.created_by is None:
            return None
        return obj.created_by.get_full_name() or obj.created_by.email


class NewsletterAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterAnalytics
        fields = [
            "sent_count", "delivered_count",
            "open_count", "open_rate",
            "click_count", "click_rate",
            "bounce_count", "bounce_rate",
            "unsubscribe_count",
            "conversion_count", "conversion_revenue",
            "winning_subject",
        ]
