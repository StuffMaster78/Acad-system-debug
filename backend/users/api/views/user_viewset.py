from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import permissions, viewsets

from users.api.serializers.user import UserSerializer
from users.models.user import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.none()

    def get_queryset(self) -> QuerySet:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Return users visible to the current request context.
        """
        return User.objects.select_related(
            "website",
            "profile"
        )