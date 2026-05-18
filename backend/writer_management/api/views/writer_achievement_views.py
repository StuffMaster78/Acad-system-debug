# writer_management/api/views/writer_achievement_views.py

from __future__ import annotations

from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    IsAuthenticated,
)

from writer_management.api.serializers.writer_achievement_serializers import (
    WriterAchievementSerializer,
)
from writer_management.models.writer_achievement import (
    WriterAchievement,
)


class WriterAchievementListView(
    ListAPIView,
):
    """
    List writer achievements.
    """

    serializer_class = (
        WriterAchievementSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(
        self,
    ):
        """
        Return writer achievements.
        """

        writer_id = (
            self.kwargs.get(
                "writer_id",
            )
        )

        return (
            WriterAchievement.objects
            .filter(
                writer_id=writer_id,
            )
            .order_by(
                "-earned_at",
            )
        )