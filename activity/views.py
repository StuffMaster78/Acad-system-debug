from rest_framework import viewsets, filters
from activity.models import ActivityLog
from activity.serializers import ActivityLogSerializer
from activity.filters import ActivityLogFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAdminUser


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API view for listing and filtering activity logs."""
    queryset = ActivityLog.objects.select_related(
        "user", "triggered_by", "website"
    ).order_by("-timestamp")
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminUser] 
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]
    filterset_class = ActivityLogFilter
    ordering_fields = ["timestamp", "action_type"]
    search_fields = [
        "description", "metadata",
        "user__username", "triggered_by__username"
    
    ]
    ordering_fields = ["timestamp", "action_type"]
    ordering = ["-timestamp"]  # Default ordering by timestamp descending

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_staff:
            qs = qs.filter(user=user)

        # Optional filters
        website_id = self.request.query_params.get("website_id")
        if website_id:
            qs = qs.filter(website_id=website_id)

        return qs

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API view for listing and filtering activity logs."""
    queryset = ActivityLog.objects.select_related(
        "user", "triggered_by", "website"
    ).order_by("-timestamp")
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAdminUser]  # Only allow admin users to access this view
    # Use DjangoFilterBackend for filtering, OrderingFilter for ordering, and SearchFilter for searching
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter
    ]
    filterset_class = ActivityLogFilter
    ordering_fields = ["timestamp", "action_type"]
    search_fields = ["description", "metadata"]
    ordering = ["-timestamp"]  # Default ordering by timestamp descending