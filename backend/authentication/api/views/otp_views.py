from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.otp_serializers import (
    OTPCreateRequestSerializer,
    OTPCreateResponseSerializer,
    OTPListItemSerializer,
    OTPVerifyResponseSerializer,
    OTPVerifySerializer,
)
from authentication.selectors.otp_selectors import list_otps
from authentication.services.otp_service import OTPService


class OTPCreateView(APIView):
    """
    Create a new OTP for the authenticated user and a given purpose.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OTPCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = OTPService(
            user=request.user,
            website=website,
        )
        otp, raw_code = service.create_otp(
            purpose=validated_data["purpose"],
        )

        response_serializer = OTPCreateResponseSerializer(
            {
                "success": True,
                "otp_id": otp.pk,
                "purpose": otp.purpose,
                "expires_at": otp.expires_at,
                "raw_code": raw_code,
            }
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OTPVerifyView(APIView):
    """
    Verify and consume an OTP for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = OTPService(
            user=request.user,
            website=website,
        )
        service.consume_otp(
            purpose=validated_data["purpose"],
            raw_code=validated_data["code"],
        )

        response_serializer = OTPVerifyResponseSerializer(
            {
                "success": True,
                "purpose": validated_data["purpose"],
                "verified": True,
            }
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class OTPListView(APIView):
    """
    List OTP records for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        purpose = request.query_params.get("purpose")

        otps = list_otps(
            user=request.user,
            website=website,
            purpose=purpose,
        )

        payload = [
            {
                "id": otp.pk,
                "purpose": otp.purpose,
                "expires_at": otp.expires_at,
                "used_at": otp.used_at,
                "attempts": otp.attempts,
                "max_attempts": otp.max_attempts,
                "created_at": otp.created_at,
            }
            for otp in otps
        ]

        serializer = OTPListItemSerializer(payload, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)