from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from writer_management.models.badges import WriterBadge
from writer_management.models.profile import WriterProfile
from writer_management.serializers import (
    WriterBadgeTimelineSerializer
)
from rest_framework.response import Response
from collections import defaultdict


class WriterBadgeTimelineViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        writer = WriterProfile.objects.get(user=request.user)
        badges = WriterBadge.objects.filter(
            writer=writer
        ).order_by("-issued_at")

        grouped = defaultdict(list)
        for badge in badges:
            date_str = badge.issued_at.strftime("%B %Y")
            grouped[date_str].append(
                WriterBadgeTimelineSerializer(badge).data
            )

        return Response(grouped)
