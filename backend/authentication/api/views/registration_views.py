from typing import Any, cast

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.registration_serializers import (
    RegistrationConfirmSerializer,
    RegistrationRequestSerializer,
    RegistrationResponseSerializer,
)
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.registration_token_service import (
    RegistrationTokenService,
)
from authentication.services.password_policy_service import (
    SmartPasswordPolicy,
)
from authentication.throttles.registration_throttles import (
    RegistrationConfirmThrottle,
    RegistrationRequestThrottle,
    RegistrationResendThrottle,
)

User = get_user_model()


class RegistrationRequestView(APIView):
    """
    Register a new user and issue a registration confirmation token.
    """

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRequestThrottle]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = RegistrationRequestSerializer(data=request.data)
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

        email = validated_data["email"]
        username = validated_data["username"]
        password = validated_data["password"]

        existing_user = User.objects.filter(
            email=email,
            website=website,
        ).first()
        if existing_user is not None:
            return Response(
                {"detail": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(
            username=username,
            website=website,
        ).exists():
            return Response(
                {"detail": "A user with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        policy = SmartPasswordPolicy()
        result = policy.validate_password(
            password=password,
            email=email,
            context=SmartPasswordPolicy.Context.REGISTRATION,
        )
        if not result["valid"]:
            return Response(
                {
                    "detail": "Password validation failed.",
                    "errors": result["errors"],
                    "warnings": result["warnings"],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            website=website,
            is_active=False,
        )

        token_service = RegistrationTokenService(
            user=user,
            website=website,
        )
        registration_token, raw_token = token_service.create_token()

        AuthNotificationBridgeService.send_registration_verification_notification(
            user=user,
            website=website,
            verification_link=verification_link,
            raw_token=raw_token,
            expiry_minutes=expiry_minutes,
        )

        response_serializer = RegistrationResponseSerializer(
            {
                "success": True,
                "user_id": user.pk,
                "message": (
                    "Registration started. Please verify your account."
                ),
            }
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class RegistrationConfirmView(APIView):
    """
    Confirm user registration with token and OTP.
    """

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationConfirmThrottle]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = RegistrationConfirmSerializer(data=request.data)
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

        token_value = validated_data["token"]
        otp_code = validated_data["otp_code"]

        from authentication.models.registration_token import RegistrationToken
        from authentication.services.otp_service import OTPService

        token_hash = RegistrationTokenService.hash_token_value(token_value) \
            if hasattr(RegistrationTokenService, "hash_token_value") else None

        registration_token = None
        if token_hash:
            registration_token = RegistrationToken.objects.filter(
                website=website,
                token_hash=token_hash,
                used_at__isnull=True,
            ).select_related("user", "website").first()

        if registration_token is None:
            return Response(
                {"detail": "Invalid or used registration token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = registration_token.user

        token_service = RegistrationTokenService(
            user=user,
            website=website,
        )
        otp_service = OTPService(
            user=user,
            website=website,
        )

        token_service.confirm_registration(
            raw_token=token_value,
            otp_code=otp_code,
            otp_service=otp_service,
        )

        user.is_active = True
        user.save(update_fields=["is_active"])

        response_serializer = RegistrationResponseSerializer(
            {
                "success": True,
                "user_id": user.pk,
                "message": "Registration confirmed successfully.",
            }
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )