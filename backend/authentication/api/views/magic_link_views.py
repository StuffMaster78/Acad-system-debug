from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.magic_link_serializers import (
    MagicLinkConfirmResponseSerializer,
    MagicLinkConfirmSerializer,
    MagicLinkRequestResponseSerializer,
    MagicLinkRequestSerializer,
)
from authentication.models.magic_links import MagicLink
from authentication.services.magic_link_service import MagicLinkService
from authentication.services.token_service import TokenService
from authentication.throttles.magic_link_throttles import (
    MagicLinkConfirmThrottle,
    MagicLinkRequestThrottle,
)

class MagicLinkRequestView(APIView):
    """
    Request a passwordless magic login link.
    """

    permission_classes = [AllowAny]
    throttle_classes = [MagicLinkRequestThrottle]

    def post(self, request, *args, **kwargs):
        serializer = MagicLinkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = MagicLinkService.request_magic_link(
            email=validated_data["email"],
            website=website,
        )

        response_serializer = MagicLinkRequestResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class MagicLinkConfirmView(APIView):
    """
    Consume a magic link token and authenticate the user.
    """

    permission_classes = [AllowAny]
    throttle_classes = [MagicLinkConfirmThrottle]

    def post(self, request, *args, **kwargs):
        serializer = MagicLinkConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_hash = TokenService.hash_value(validated_data["token"])

        magic_link = MagicLink.objects.filter(
            website=website,
            token_hash=token_hash,
            used_at__isnull=True,
        ).select_related("user", "website").first()

        if magic_link is None:
            return Response(
                {"detail": "Invalid magic link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = MagicLinkService(
            user=magic_link.user,
            website=website,
        )
        result = service.consume_magic_link(
            raw_token=validated_data["token"],
            request=request,
        )

        response_serializer = MagicLinkConfirmResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)