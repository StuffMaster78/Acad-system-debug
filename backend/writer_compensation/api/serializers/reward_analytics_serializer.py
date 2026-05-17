from __future__ import annotations

from rest_framework import serializers


class RewardAnalyticsSerializer(
    serializers.Serializer,
):
    """
    Reward analytics projection serializer.
    """

    total_rewards_issued = serializers.IntegerField()

    total_reward_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    average_reward_amount = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
    )

    revoked_rewards = serializers.IntegerField()

    active_reward_rules = serializers.IntegerField()

    top_reward_type = serializers.CharField()

    top_writer_id = serializers.UUIDField(
        allow_null=True,
    )

    top_writer_name = serializers.CharField(
        allow_null=True,
    )