from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.device_serializers import (
    DeviceFingerprintSerializer,
    TrustDeviceSerializer,
    UntrustDeviceSerializer,
)
from authentication.selectors.device_fingerprint_selectors import (
    get_fingerprint_by_hash,
    list_user_fingerprints,
)
from authentication.services.device_fingerprint_service import (
    DeviceFingerprintService,
)
from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)


class DeviceFingerprintListView(APIView):
    """
    List device fingerprints for the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        fingerprints = list_user_fingerprints(
            user=request.user,
            website=website,
        )
        serializer = DeviceFingerprintSerializer(
            fingerprints,
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrustDeviceView(APIView):
    """
    Mark a device fingerprint as trusted.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = TrustDeviceSerializer(data=request.data)
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

        fingerprint_hash = validated_data["fingerprint_hash"]

        fingerprint = get_fingerprint_by_hash(
            user=request.user,
            website=website,
            fingerprint_hash=fingerprint_hash,
        )
        if fingerprint is None:
            return Response(
                {"detail": "Fingerprint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = DeviceFingerprintService(
            user=request.user,
            website=website,
        )
        success = service.mark_trusted(
            fingerprint_hash=fingerprint_hash,
            revoke_others=False,
        )

        if not success:
            return Response(
                {"detail": "Fingerprint could not be trusted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refreshed = get_fingerprint_by_hash(
            user=request.user,
            website=website,
            fingerprint_hash=fingerprint_hash,
        )

        if refreshed is None:
            return Response(
                {"detail": "Trusted fingerprint could not be reloaded."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_serializer = DeviceFingerprintSerializer(refreshed)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
    

class UntrustDeviceView(APIView):
    """
    Mark a device fingerprint as untrusted.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = UntrustDeviceSerializer(data=request.data)
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

        fingerprint_hash = validated_data["fingerprint_hash"]

        fingerprint = get_fingerprint_by_hash(
            user=request.user,
            website=website,
            fingerprint_hash=fingerprint_hash,
        )
        if fingerprint is None:
            return Response(
                {"detail": "Fingerprint not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        service = DeviceFingerprintService(
            user=request.user,
            website=website,
        )
        success = service.mark_untrusted(
            fingerprint_hash=fingerprint_hash,
        )

        if not success:
            return Response(
                {"detail": "Fingerprint could not be untrusted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refreshed = get_fingerprint_by_hash(
            user=request.user,
            website=website,
            fingerprint_hash=fingerprint_hash,
        )

        if refreshed is None:
            return Response(
                {"detail": "Fingerprint could not be reloaded."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response_serializer = DeviceFingerprintSerializer(refreshed)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )