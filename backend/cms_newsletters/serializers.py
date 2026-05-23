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


class NewsletterListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ["id", "title", "subject_line", "status", "sent_at", "created_at"]


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
