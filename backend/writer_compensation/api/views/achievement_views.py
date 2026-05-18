# writer_compensation/api/views/achievement_views.py

from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_management.models.writer_achievement import (
    WriterAchievement,
)


class WriterAchievementListView(
    APIView,
):
    """
    List achievements for a writer.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Return achievement list.
        """

        writer_id = (
            self.kwargs.get(
                "writer_id",
            )
        )

        achievements = (
            WriterAchievement.objects
            .filter(
                writer_id=writer_id,
            )
            .order_by(
                "-awarded_at",
            )
        )

        payload = [
            {
                "id": achievement.pk,
                "title": (
                    achievement.title
                ),
                "slug": (
                    achievement.slug
                ),
                "description": (
                    achievement.description
                ),
                "badge_name": (
                    achievement.badge_name
                ),
                "awarded_at": (
                    achievement.awarded_at
                ),
                "metadata": (
                    achievement.metadata
                ),
            }
            for achievement in achievements
        ]

        return Response(
            payload,
        )