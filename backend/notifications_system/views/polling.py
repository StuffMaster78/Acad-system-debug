# notifications_system/views/polling.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from notifications_system.models.notifications import Notification
from notifications_system.serializers import NotificationSerializer

@api_view(["GET"])
def poll_notifications(request):
    # Optionally filter by user
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by("-created_at")[:20]
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)