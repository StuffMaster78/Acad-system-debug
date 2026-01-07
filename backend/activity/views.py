from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from activity.models import ActivityLog
from activity.serializers import ActivityLogSerializer
from activity.serializers_user_feed import UserActivityFeedSerializer
from activity.filters import ActivityLogFilter
from orders.models import Order


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

    def get_queryset(self):
        """Filter queryset based on user role permissions.
        
        For writers, clients, editors, and support: Only show actions they performed.
        This means filtering by user=user OR triggered_by=user (actions they did).
        """
        qs = super().get_queryset()
        user = self.request.user
        user_role = getattr(user, 'role', None)

        # Admin and Superadmin can see all activities
        if user_role in ['admin', 'superadmin']:
            # No filtering - show all activities
            pass
        
        # Support, Writers, Clients, Editors: Only see actions they performed
        # Filter by user=user OR triggered_by=user (actions they did themselves)
        elif user_role in ['support', 'writer', 'client', 'editor']:
            qs = qs.filter(
                models.Q(user=user) |  # Actions where they are the user
                models.Q(triggered_by=user)  # Actions they triggered/performed
            )
        
        # Default: users can only see their own activities
        else:
            qs = qs.filter(
                models.Q(user=user) | models.Q(triggered_by=user)
            )

        # Optional filters
        website_id = self.request.query_params.get("website_id")
        if website_id:
            qs = qs.filter(website_id=website_id)
        
        # Filter by actor type if provided
        actor_type = self.request.query_params.get("actor_type")
        if actor_type:
            qs = qs.filter(actor_type=actor_type)
        
        # Filter by action type if provided
        action_type = self.request.query_params.get("action_type")
        if action_type:
            qs = qs.filter(action_type=action_type)

        return qs

    def list(self, request, *args, **kwargs):
        """List activity logs with optional limit."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Support limit parameter for frontend
        limit = request.query_params.get('limit')
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except (ValueError, TypeError):
                pass
        
        # Use pagination if available, otherwise return all
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # No pagination - return all logs (or limited if limit was specified)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })


class UserActivityFeedViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User-facing activity feed with friendly descriptions and strict role scoping.
    This is what non-admin users should see in the UI.
    """

    serializer_class = UserActivityFeedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        User-facing activity feed showing only actions the user performed.
        
        For writers, clients, editors, and support: Only show "You did X" actions.
        This means filtering by user=user OR triggered_by=user (actions they performed).
        """
        qs = ActivityLog.objects.select_related(
            "user", "triggered_by", "website"
        ).order_by("-timestamp")

        user = self.request.user
        user_role = getattr(user, "role", None)

        # Admin / Superadmin: see all events
        if user_role in ["admin", "superadmin"]:
            pass

        # Support, Writers, Clients, Editors: Only see actions they performed
        # Filter by user=user OR triggered_by=user (actions they did themselves)
        elif user_role in ["support", "writer", "client", "editor"]:
            qs = qs.filter(
                models.Q(user=user) |  # Actions where they are the user
                models.Q(triggered_by=user)  # Actions they triggered/performed
            )

        # Default: only own events (actions they performed)
        else:
            qs = qs.filter(
                models.Q(user=user) | models.Q(triggered_by=user)
            )

        limit = self.request.query_params.get("limit")
        if limit:
            try:
                limit = int(limit)
                qs = qs[:limit]
            except (ValueError, TypeError):
                pass

        return qs