from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from users.api.serializers.user import MeSerializer, UserSerializer
from users.models.user import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.none()

    def get_queryset(self) -> QuerySet:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Return users visible to the current request context.
        """
        return User.objects.select_related("website", "profile")

    @action(detail=False, methods=["get", "patch"], url_path="me", permission_classes=[permissions.IsAuthenticated])
    def me(self, request: Request) -> Response:
        user = User.objects.select_related("profile").get(pk=request.user.pk)
        if request.method == "PATCH":
            serializer = MeSerializer(user, data=request.data, partial=True, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        serializer = MeSerializer(user, context={"request": request})
        return Response(serializer.data)