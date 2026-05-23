"""
Engagement API Serializers
============================
"""

from rest_framework import serializers

from cms_engagement.models import EngagementSummary, PageReaction


class EngagementSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementSummary
        fields = [
            "total_views", "unique_views",
            "avg_time_on_page", "avg_scroll_depth", "bounce_rate",
            "thumbs_up_count", "thumbs_down_count",
            "love_count", "useful_count",
            "total_shares",
            "engagement_score", "helpfulness_ratio",
        ]


class ReactionInputSerializer(serializers.Serializer):
    reaction_type = serializers.ChoiceField(
        choices=["thumbs_up", "thumbs_down", "love", "useful"]
    )