from rest_framework import viewsets, permissions
from authentication.models.logout import LogoutEvent
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication.serializers import LogoutEventSerializer
from authentication.utils.logout_utils import logout_user

class LogoutEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides read-only access to logout events for auditing.
    """
    serializer_class = LogoutEventSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return LogoutEvent.objects.filter(
            website=self.request.website
        ).select_related('user', 'website')


    def create(self, request):
        """
        POST /logout/
        Handles user logout for both JWT and session authentication.
        """
        reason = request.data.get("reason", "user_initiated")
        logout_user(request, reason=reason)
        return Response({"detail": "Logged out successfully."},
                        status=status.HTTP_200_OK)