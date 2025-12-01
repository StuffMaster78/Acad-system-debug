from rest_framework import permissions, viewsets

from notifications_system.models.webhook_endpoint import (
    NotificationWebhookEndpoint,
)
from notifications_system.serializers import (
    NotificationWebhookEndpointSerializer,
)


class NotificationWebhookEndpointViewSet(viewsets.ModelViewSet):
    """Allow any authenticated user to manage their webhook endpoints."""

    serializer_class = NotificationWebhookEndpointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = NotificationWebhookEndpoint.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
        website_id = (
            self.request.query_params.get("website_id")
            or self.request.query_params.get("website")
        )
        if website_id:
            qs = qs.filter(website_id=website_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

