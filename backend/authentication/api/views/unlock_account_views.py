from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.unlock_account_serializers import (
    AccountUnlockConfirmSerializer,
    AccountUnlockRequestSerializer,
    AccountUnlockResponseSerializer,
)
from authentication.models.account_unlock_request import (
    AccountUnlockRequest,
)
from authentication.services.account_unlock_service import (
    AccountUnlockService,
)
from authentication.services.token_service import TokenService
from authentication.throttles.unlock_throttles import (
    AccountUnlockConfirmThrottle,
    AccountUnlockRequestThrottle,
)

User = get_user_model()


class AccountUnlockRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AccountUnlockRequestThrottle]

    def post(self, request, *args, **kwargs):
        serializer = AccountUnlockRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = AccountUnlockService.request_unlock(
            email=validated_data["email"],
            website=website,
        )

        response_serializer = AccountUnlockResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class AccountUnlockConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AccountUnlockConfirmThrottle]

    def post(self, request, *args, **kwargs):
        serializer = AccountUnlockConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_hash = TokenService.hash_value(validated_data["token"])

        unlock_request = AccountUnlockRequest.objects.filter(
            website=website,
            token_hash=token_hash,
            used_at__isnull=True,
        ).select_related("user", "website").first()

        if unlock_request is None:
            return Response(
                {"detail": "Invalid unlock token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = AccountUnlockService(
            user=unlock_request.user,
            website=website,
        )
        result = service.confirm_unlock(
            raw_token=validated_data["token"],
            otp_code=validated_data["otp_code"],
        )

        response_serializer = AccountUnlockResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)