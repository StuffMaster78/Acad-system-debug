from __future__ import annotations

from rest_framework import serializers

from writer_compensation.models.reward_rule import (
    RewardRule,
)


class RewardRuleSerializer(
    serializers.ModelSerializer,
):
    """
    Reward rule API serializer.
    """

    class Meta:
        model = RewardRule

        fields = [
            "id",
            "website",
            "name",
            "slug",
            "description",
            "rule_type",
            "reward_type",
            "minimum_avg_rating",
            "minimum_review_count",
            "minimum_percentile_rank",
            "minimum_trust_score",
            "minimum_completed_orders",
            "maximum_lateness_rate",
            "maximum_dispute_rate",
            "reward_amount",
            "trust_score_bonus",
            "badge_name",
            "priority_boost_multiplier",
            "cooldown_days",
            "max_rewards_per_period",
            "is_active",
            "is_repeatable",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]