from __future__ import annotations

from rest_framework import serializers


class RewardLeaderboardSerializer(
    serializers.Serializer,
):
    """
    Leaderboard projection serializer.
    """

    writer_id = serializers.UUIDField()

    writer_name = serializers.CharField()

    rating = serializers.DecimalField(
        max_digits=4,
        decimal_places=2,
    )

    review_count = serializers.IntegerField()

    percentile_rank = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    trust_score = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    leaderboard_position = serializers.IntegerField()

    completed_orders = serializers.IntegerField()

    badges = serializers.ListField(
        child=serializers.CharField(),
    )