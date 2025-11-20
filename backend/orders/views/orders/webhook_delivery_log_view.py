from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from orders.models import WebhookDeliveryLog
from orders.serializers import WebhookDeliveryLogSerializer
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.filters import SearchFilter, OrderingFilter

class WebhookDeliveryLogListView(generics.ListAPIView):
    """List all webhook delivery logs."""
    queryset = WebhookDeliveryLog.objects.all().select_related("user", "website")
    serializer_class = WebhookDeliveryLogSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["success", "event", "test_mode", "user"]
    search_fields = ["user__email", "url", "event"]
    ordering_fields = ["created_at", "retry_count"]
    ordering = ["-created_at"]