from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from authentication.serializers import (
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
)


class MagicLinkRequestViewSet(viewsets.ViewSet):
    """
    Public endpoint for requesting a magic login link.
    """
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = MagicLinkRequestSerializer(
            data=request.data,
            context={
                "request": request,
                "website": request.website  # Assuming middleware sets this
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Magic link sent."},
            status=status.HTTP_200_OK
        )


class MagicLinkVerifyViewSet(viewsets.ViewSet):
    """
    Public endpoint for verifying a magic login link token.
    """
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = MagicLinkVerifySerializer(
            data=request.data,
            context={
                "request": request,
                "website": request.website
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 🔐 Insert login logic here (e.g., create a session, or return JWT)
        # Example:
        # refresh = RefreshToken.for_user(user)
        # return Response({"access": str(refresh.access_token), "refresh": str(refresh)})

        return Response(
            {"detail": f"Welcome back, {user.email}!"},
            status=status.HTTP_200_OK
        )
