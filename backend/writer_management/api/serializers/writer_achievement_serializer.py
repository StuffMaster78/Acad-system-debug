# writer_management/api/serializers/writer_achievement_serializer.py

from __future__ import annotations

from rest_framework import serializers

from writer_management.models.writer_achievement import (
    WriterAchievement,
)


class WriterAchievementSerializer(
    serializers.ModelSerializer,
):
    """
    Writer achievement serializer.
    """

    class Meta:
        model = WriterAchievement

        fields = [
            "id",
            "writer",
            "website",
            "achievement_type",
            "slug",
            "title",
            "description",
            "badge_name",
            "icon",
            "points",
            "is_featured",
            "earned_at",
            "metadata",
        ]

        read_only_fields = [
            "id",
            "earned_at",
        ]
