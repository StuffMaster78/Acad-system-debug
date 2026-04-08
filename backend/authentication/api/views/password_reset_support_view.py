from typing import Any, cast

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.password_reset_support_serializers import (
    PasswordResetValidateTokenResponseSerializer,
    PasswordResetValidateTokenSerializer,
)
from authentication.models.password_reset_request import (
    PasswordResetRequest,
)
from authentication.services.password_reset_service import (
    PasswordResetService,
)
from authentication.services.token_service import TokenService


class PasswordResetValidateTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetValidateTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_hash = TokenService.hash_value(validated_data["token"])

        reset_request = PasswordResetRequest.objects.filter(
            website=website,
            token_hash=token_hash,
            used_at__isnull=True,
        ).select_related("user", "website").first()

        if reset_request is None:
            response_serializer = PasswordResetValidateTokenResponseSerializer(
                {
                    "valid": False,
                    "message": "Invalid reset token.",
                }
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        try:
            service = PasswordResetService(
                user=reset_request.user,
                website=website,
            )
            service.validate_token(validated_data["token"])

            response_serializer = PasswordResetValidateTokenResponseSerializer(
                {
                    "valid": True,
                    "message": "Reset token is valid.",
                }
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except ValidationError as exc:
            response_serializer = PasswordResetValidateTokenResponseSerializer(
                {
                    "valid": False,
                    "message": str(exc),
                }
            )
            return Response(response_serializer.data, status=status.HTTP_200_OK)