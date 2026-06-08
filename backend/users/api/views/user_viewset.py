from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.request import Request
from rest_framework.response import Response

from users.api.serializers.user import MeSerializer, UserSerializer
from users.models.user import User


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.none()

    def get_queryset(self) -> QuerySet: # pyright: ignore[reportIncompatibleMethodOverride]
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

    @action(
        detail=False,
        methods=["post"],
        url_path="me/avatar",
        permission_classes=[permissions.IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser],
    )
    def me_avatar(self, request: Request) -> Response:
        """
        Upload or replace the current user's profile avatar.
        Accepts multipart/form-data with field name 'avatar'.
        Returns the updated AuthUser shape.
        """
        avatar_file = request.FILES.get("avatar")
        if not avatar_file:
            return Response({"detail": "No avatar file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate content type
        allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if avatar_file.content_type not in allowed:
            return Response(
                {"detail": "Unsupported file type. Use JPEG, PNG, GIF, or WebP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.select_related("profile").get(pk=request.user.pk)
        from users.models.profile import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Delete old avatar file to avoid orphaned media
        if profile.avatar:
            try:
                profile.avatar.delete(save=False)
            except Exception:
                pass

        profile.avatar = avatar_file
        profile.save(update_fields=["avatar"])

        serializer = MeSerializer(user, context={"request": request})
        return Response(serializer.data)