from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from activity.models import ActivityLog
from activity.serializers import ActivityLogSerializer
from activity.filters import ActivityLogFilter
from django_filters.rest_framework import DjangoFilterBackend


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API view for listing and filtering activity logs."""
    queryset = ActivityLog.objects.select_related(
        "user", "triggered_by", "website"
    ).order_by("-timestamp")
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]  # Allow authenticated users
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
    ordering = ["-timestamp"]  # Default ordering by timestamp descending
    pagination_class = None  # Disable pagination to return all logs

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        qs = super().get_queryset()
        user = self.request.user

        # Non-staff users only see their own logs
        if not user.is_staff:
            qs = qs.filter(user=user)

        # Optional filters
        website_id = self.request.query_params.get("website_id")
        if website_id:
            qs = qs.filter(website_id=website_id)

        return qs
    
    def list(self, request, *args, **kwargs):
        """Override list to ensure all logs are returned."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # If pagination is disabled, return all results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # No pagination - return all logs
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)