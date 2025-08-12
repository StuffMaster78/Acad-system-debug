from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notifications_system.enums import (
    NotificationType,
    NotificationCategory,
    NotificationPriority
)
from rest_framework.decorators import action
from notifications_system.serializers import NotificationPriorityMetaSerializer
from notifications_system.utils.enums_export import export_notification_enums

class NotificationMetaView(APIView):
    """
    Expose enums / metadata to the frontend.
    Expose priority levels for dropdowns etc.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        priorities = [
            {"value": value, "label": label}
            for value, label in NotificationPriority.choices()
        ]
        channels = [
            {"value": value, "label": label}
            for value, label in NotificationType.choices()
        ]
        categories = [
            {"value": value, "label": label}
            for value, label in NotificationCategory.choices()
        ]
        return Response({
            "priorities": NotificationPriorityMetaSerializer(priorities, many=True).data,
            "channels": NotificationPriorityMetaSerializer(channels, many=True).data,
            "categories": NotificationPriorityMetaSerializer(categories, many=True).data
        })
    
    @action(
            detail=False, methods=["get"],
            url_path="notification-enum-choices"
    )
    def notification_enum_choices(self, request):
        return Response(export_notification_enums())