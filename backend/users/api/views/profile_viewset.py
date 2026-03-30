from __future__ import annotations

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


from users.api.serializers.profile import UserProfileSerializer
from users.services.profile_service import ProfileService


class ProfileViewSet(viewsets.ViewSet):
    """
    Endpoints for accessing the current user's profile.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_profile(self, request: Request):
        return ProfileService.get_or_create_profile(request.user)

    def list(self, request: Request) -> Response:
        """
        GET /profile/
        Return the current user's approved profile.
        """
        profile = self.get_profile(request)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def retrieve(self, request, pk: str | None = None) -> Response:
        """
        Optional: allow retrieving another profile if needed.
        """
        profile = self.get_profile(request)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)