# writer_compensation/api/views/achievement_progress_views.py

from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from writer_management.services.achievement_service import (
    AchievementService,
)


class WriterAchievementProgressView(
    APIView,
):
    """
    Achievement progression endpoint.
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
        Return achievement progression.
        """

        writer_id = (
            self.kwargs.get(
                "writer_id",
            )
        )

        payload = (
            AchievementService
            .achievement_progress(
                writer_id=writer_id,
            )
        )

        return Response(
            payload,
        )