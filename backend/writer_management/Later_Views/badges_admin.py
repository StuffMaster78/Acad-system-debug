from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from writer_management.models.badges import WriterBadge
from writer_management.serializers import WriterBadgeSerializer


class WriterBadgeAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = WriterBadge.objects.select_related("writer", "badge")
    serializer_class = WriterBadgeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "badge__name", "writer__user__username",
        "notes", "badge__type"
    ]
    ordering_fields = ["issued_at", "badge__name"]
