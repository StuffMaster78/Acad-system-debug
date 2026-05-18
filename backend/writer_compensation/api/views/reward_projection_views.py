from __future__ import annotations

from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import (
    Response,
)
from rest_framework.views import (
    APIView,
)

from writer_compensation.services.reward_projection_service import (
    RewardProjectionService,
)


class RewardProjectionAPIView(
    APIView,
):
    """
    Return projected rewards and milestones.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
    ) -> Response:
        """
        Return writer reward projections.
        """

        writer = getattr(
            request.user,
            "writer_profile",
            None,
        )

        if writer is None:
            return Response(
                {
                    "detail": (
                        "Writer profile not found."
                    )
                },
                status=400,
            )

        projections = (
            RewardProjectionService
            .project_for_writer(
                writer_id=writer.pk,
            )
        )

        return Response(
            projections,
        )