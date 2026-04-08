from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.password_serializers import (
    ChangePasswordSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordRequestSerializer,
)
from authentication.services.password_reset_service import (
    PasswordResetService,
)
from authentication.services.password_security_service import (
    PasswordSecurityService,
)
from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)
from authentication.throttles.password_throttles import (
    PasswordResetRequestThrottle,
    PasswordResetConfirmThrottle,
)


class ChangePasswordView(APIView):
    """
    Change password for the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
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

        if not request.user.check_password(
            validated_data["old_password"]
        ):
            return Response(
                {"detail": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = PasswordSecurityService(
            user=request.user,
            website=website,
        ).change_password(
            raw_password=validated_data["new_password"],
            context="password_change",
            revoke_other_sessions=True,
            notify_user=True,
        )

        return Response(result, status=status.HTTP_200_OK)


class ResetPasswordRequestView(APIView):
    """
    Start password reset flow.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordRequestSerializer(data=request.data)
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

        result = PasswordResetService.request_reset(
            email=validated_data["email"],
            website=website,
            request=request,
        )

        return Response(result, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(APIView):
    """
    Complete password reset flow.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetConfirmThrottle]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
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

        result = PasswordResetService.confirm_reset(
            website=website,
            raw_token=validated_data["token"],
            otp_code=validated_data["otp_code"],
            new_password=validated_data["new_password"],
        )

        return Response(result, status=status.HTTP_200_OK)