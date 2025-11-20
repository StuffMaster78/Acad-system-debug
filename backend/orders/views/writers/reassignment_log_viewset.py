from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from orders.models import WriterReassignmentLog
from orders.serializers import (
    WriterReassignmentLogSerializer,
)


class WriterReassignmentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for listing/auditing writer reassignment logs.
    """
    queryset = WriterReassignmentLog.objects.select_related(
        "order", "previous_writer", "new_writer", "reassigned_by"
    )
    serializer_class = WriterReassignmentLogSerializer
    permission_classes = [permissions.IsAdminUser]  # override as needed

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        "order_id", "new_writer", "previous_writer", "reassigned_by"
    ]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.all()
        return self.queryset.filter(
            writer_from__user=user
        ) | self.queryset.filter(writer_to__user=user)