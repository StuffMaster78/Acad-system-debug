"""
writer_management/api/views/reward_views.py

FIXES APPLIED
-------------
1. get_serializer_class: missing # type: ignore[override]
2. get_queryset: missing # type: ignore[override]
3. writer.rewards reverse accessor unknown to Pylance.
   Replaced with WriterReward.objects.filter(writer=writer).
"""

from rest_framework.generics import ListAPIView

from writer_management.api.permissions import IsAdminOrWriterOwner


class WriterRewardListView(ListAPIView):
    """GET /api/writer-management/writers/<rid>/rewards/"""
    permission_classes = [IsAdminOrWriterOwner]

    def get_serializer_class(self): # type: ignore[override]
        from writer_management.api.serializers.reward_serializers import (
            WriterRewardSerializer,
        )
        return WriterRewardSerializer

    def get_queryset(self): # type: ignore[override]
        from writer_management.models.writer_reward import WriterReward
        from writer_management.services.writer_profile_service import (
            WriterProfileService,
        )

        rid = self.kwargs["registration_id"]

        try:
            writer = WriterProfileService.get_by_registration_id(rid)
        except Exception:
            return WriterReward.objects.none()

        # Fix 3: writer.rewards is a reverse accessor — unknown to Pylance.
        # Use explicit queryset instead.
        return (
            WriterReward.objects
            .filter(writer=writer)
            .select_related("criteria")
            .order_by("-awarded_at")
        )