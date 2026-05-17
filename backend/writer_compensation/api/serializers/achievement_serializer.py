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

    writer_name = serializers.CharField(
        source="writer.display_name",
        read_only=True,
    )

    class Meta:
        model = WriterAchievement

        fields = [
            "id",
            "writer",
            "writer_name",
            "slug",
            "title",
            "description",
            "icon",
            "category",
            "awarded_at",
            "metadata",
        ]

        read_only_fields = fields