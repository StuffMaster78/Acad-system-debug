from __future__ import annotations

from rest_framework import serializers

from writer_compensation.models.writer_reward import (
    WriterReward,
)


class WriterRewardSerializer(
    serializers.ModelSerializer,
):
    """
    Immutable writer reward serializer.
    """

    writer_name = serializers.CharField(
        source="writer.display_name",
        read_only=True,
    )

    reward_rule_name = serializers.CharField(
        source="reward_rule.name",
        read_only=True,
    )

    website_name = serializers.CharField(
        source="website.name",
        read_only=True,
    )

    class Meta:
        model = WriterReward

        fields = [
            "id",
            "website",
            "website_name",
            "writer",
            "writer_name",
            "reward_rule",
            "reward_rule_name",
            "status",
            "average_rating",
            "percentile_rank",
            "trust_score",
            "completed_orders",
            "review_count",
            "composite_score",
            "reward_amount",
            "trust_score_bonus",
            "badge_name",
            "reward_title",
            "reward_description",
            "period_start",
            "period_end",
            "issued_at",
            "revoked_at",
            "metadata",
        ]

        read_only_fields = fields