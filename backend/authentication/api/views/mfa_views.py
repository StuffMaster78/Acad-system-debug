from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.mfa_serializers import (
    MFAChallengeRequestSerializer,
    MFAVerifySerializer,
)
from authentication.services.mfa_orchestration_service import (
    MFAOrchestrationService,
)
from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)
from typing import Any, cast

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.mfa_serializers import (
    MFAChallengeRequestSerializer,
    MFAChallengeResponseSerializer,
    MFADeviceListItemSerializer,
    MFAStateResponseSerializer,
    MFAVerifyResponseSerializer,
    MFAVerifySerializer,
    BackupCodeGenerateRequestSerializer,
    BackupCodeGenerateResponseSerializer,
    BackupCodeUseSerializer,
    MFADeviceListItemSerializer,
    MFARegisterDeviceSerializer,
    MFASetPrimaryDeviceSerializer,
    MFAToggleDeviceSerializer,
    MFAVerifyDeviceResponseSerializer,
    MFAVerifyDeviceSerializer,
)
from authentication.services.mfa_orchestration_service import (
    MFAOrchestrationService,
)
from authentication.models.mfa_device import MFADevice
from authentication.services.backup_code_service import BackupCodeService
from authentication.services.mfa_device_service import MFADeviceService
from authentication.throttles.mfa_throttles import (
    MFAVerifyThrottle,
    BackupCodeGenerateThrottle,
    MFAChallengeThrottle,
)

class MFAStateView(APIView):
    """
    Return MFA login state for the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = MFAOrchestrationService.get_login_state(
            user=request.user,
            website=website,
        )

        serializer = MFAStateResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MFADeviceListView(APIView):
    """
    List available MFA devices for the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        devices = MFAOrchestrationService.get_available_devices(
            user=request.user,
            website=website,
        )

        payload = [
            {
                "id": device.pk,
                "name": device.name,
                "method": device.method,
                "is_active": device.is_active,
                "is_verified": device.is_verified,
                "is_primary": getattr(device, "is_primary", False),
            }
            for device in devices
        ]

        serializer = MFADeviceListItemSerializer(payload, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MFAChallengeView(APIView):
    """
    Begin MFA for the authenticated user's login flow.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]
    throttle_classes = [
        MFAChallengeThrottle,
    ]

    def post(self, request, *args, **kwargs):
        serializer = MFAChallengeRequestSerializer(data=request.data)
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

        device = None
        device_id = validated_data.get("device_id")
        if device_id is not None:
            device = MFAOrchestrationService.get_available_devices(
                user=request.user,
                website=website,
            ).filter(pk=device_id).first()

            if device is None:
                return Response(
                    {"detail": "MFA device not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        result = MFAOrchestrationService.begin_mfa_for_login(
            user=request.user,
            website=website,
            request=request,
            device=device,
        )

        response_serializer = MFAChallengeResponseSerializer(result)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class MFAVerifyView(APIView):
    """
    Verify MFA code for the authenticated user's login flow.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]
    throttle_classes = [MFAVerifyThrottle]
    
    def post(self, request, *args, **kwargs):
        serializer = MFAVerifySerializer(data=request.data)
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

        result = MFAOrchestrationService.verify_login_mfa(
            user=request.user,
            website=website,
            code=validated_data["code"],
            device_id=validated_data.get("device_id"),
        )

        response_serializer = MFAVerifyResponseSerializer(result)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class MFARegisterDeviceView(APIView):
    """
    Register a new MFA device for the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = MFARegisterDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = MFADeviceService.register_device(
            user=request.user,
            website=website,
            method=validated_data["method"],
            name=validated_data["name"],
            secret=validated_data.get("secret", ""),
            phone_number=validated_data.get("phone_number", ""),
            email=validated_data.get("email", ""),
            is_primary=validated_data.get("is_primary", False),
        )

        payload = {
            "id": device.pk,
            "name": device.name,
            "method": device.method,
            "is_active": device.is_active,
            "is_verified": device.is_verified,
            "is_primary": getattr(device, "is_primary", False),
        }

        response_serializer = MFADeviceListItemSerializer(payload)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class MFASetPrimaryDeviceView(APIView):
    """
    Set an MFA device as primary.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = MFASetPrimaryDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = MFAOrchestrationService.get_available_devices(
            user=request.user,
            website=website,
        ).filter(pk=validated_data["device_id"]).first()

        if device is None:
            return Response(
                {"detail": "MFA device not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        device = MFADeviceService.set_primary_device(device=device)

        payload = {
            "id": device.pk,
            "name": device.name,
            "method": device.method,
            "is_active": device.is_active,
            "is_verified": device.is_verified,
            "is_primary": getattr(device, "is_primary", False),
        }

        response_serializer = MFADeviceListItemSerializer(payload)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class MFADeactivateDeviceView(APIView):
    """
    Deactivate an MFA device.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = MFAToggleDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = MFADevice.objects.filter(
            user=request.user,
            website=website,
            pk=validated_data["device_id"],
        ).first()

        if device is None:
            return Response(
                {"detail": "MFA device not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        device = MFADeviceService.deactivate_device(device=device)

        payload = {
            "id": device.pk,
            "name": device.name,
            "method": device.method,
            "is_active": device.is_active,
            "is_verified": device.is_verified,
            "is_primary": getattr(device, "is_primary", False),
        }

        response_serializer = MFADeviceListItemSerializer(payload)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class MFAActivateDeviceView(APIView):
    """
    Activate an MFA device.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    def post(self, request, *args, **kwargs):
        serializer = MFAToggleDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = MFADevice.objects.filter(
            user=request.user,
            website=website,
            pk=validated_data["device_id"],
        ).first()

        if device is None:
            return Response(
                {"detail": "MFA device not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        device = MFADeviceService.activate_device(device=device)

        payload = {
            "id": device.pk,
            "name": device.name,
            "method": device.method,
            "is_active": device.is_active,
            "is_verified": device.is_verified,
            "is_primary": getattr(device, "is_primary", False),
        }

        response_serializer = MFADeviceListItemSerializer(payload)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class BackupCodeGenerateView(APIView):
    """
    Generate a new set of backup codes for the authenticated user.
    """

    permission_classes = [
        IsAuthenticated,
        NotImpersonatingPermission,
    ]

    throttle_classes = [BackupCodeGenerateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = BackupCodeGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = BackupCodeService(
            user=request.user,
            website=website,
        )
        codes = service.generate_backup_codes(
            count=validated_data.get("count", service.DEFAULT_CODE_COUNT),
        )

        response_serializer = BackupCodeGenerateResponseSerializer(
            {"codes": codes}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )
    


class MFAVerifyDeviceView(APIView):
    """
    Verify a newly registered MFA device.
    """

    permission_classes = [IsAuthenticated, NotImpersonatingPermission]

    def post(self, request, *args, **kwargs):
        serializer = MFAVerifyDeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = MFADevice.objects.filter(
            user=request.user,
            website=website,
            pk=validated_data["device_id"],
        ).first()

        if device is None:
            return Response(
                {"detail": "MFA device not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        device = MFADeviceService.verify_totp_device(
            device=device,
            code=validated_data["code"],
        )

        response_serializer = MFAVerifyDeviceResponseSerializer(
            {
                "success": True,
                "device_id": device.pk,
                "message": "MFA device verified successfully.",
            }
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)