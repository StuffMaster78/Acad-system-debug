# notifications_system/api/views_counters.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from notifications_system.utils.unread_counter import get as get_unread
from notifications_system.utils.unread_rebuild import rebuild_unread

class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        website = getattr(request, "website", None)
        wid = getattr(website, "id", None)

        count = get_unread(user.id, wid)
        if count is None:
            count = rebuild_unread(user, website)

        return Response({"unread_count": count})
