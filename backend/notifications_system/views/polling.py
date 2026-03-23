"""
Lightweight polling endpoint.
Frontend calls this every 30 seconds to check for new notifications.
"""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications_system.services.inapp_service import InAppService
from notifications_system.throttles import NotificationPollThrottle


class NotificationPollView(APIView):
    """
    GET /notifications/poll/

    Returns unread count and the most recent unread notification
    for toast display. Designed to be fast — one integer read
    and one indexed query.

    Frontend calls this every 30 seconds. The throttle
    (4/minute) prevents faster polling.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [NotificationPollThrottle]

    def get(self, request):
        website = getattr(request.user, 'website', None)
        payload = InAppService.get_for_poll(request.user, website)
        return Response(payload)