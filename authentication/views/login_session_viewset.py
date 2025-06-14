from rest_framework import viewsets, permissions
from authentication.models.login import LoginSession
from authentication.serializers import LoginSessionSerializer


class LoginSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for listing and retrieving user login sessions.
    """
    serializer_class = LoginSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns sessions only for the authenticated user and website.
        """
        return LoginSession.objects.filter(
            user=self.request.user,
            website=self.request.website  # website set via middleware/context
        )