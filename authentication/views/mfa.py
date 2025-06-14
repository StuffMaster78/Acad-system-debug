from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models.mfa_settings import MFASettings
from authentication.serializers import (
    MFASettingsSerializer,
    MFAOtpVerificationSerializer,
    MFAEnableSerializer,
    MFARecoveryTokenSerializer,
)
from authentication.services.mfa import MFAService


class MFASettingsViewSet(viewsets.ViewSet):
    """
    Manages Multi-Factor Authentication settings and verification.
    """
    permission_classes = [IsAuthenticated]

    def get_service(self):
        return MFAService(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        service = self.get_service()
        mfa_settings = service.get_or_create_settings()
        serializer = MFASettingsSerializer(mfa_settings)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="enable")
    def enable_mfa(self, request):
        """
        Enable MFA using chosen method.
        """
        serializer = MFAEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        phone_number = serializer.validated_data.get("phone_number")

        service = self.get_service()
        service.enable_mfa(method=method, phone_number=phone_number)

        return Response({"detail": f"MFA method '{method}' enabled."})

    @action(detail=False, methods=["post"], url_path="verify-otp")
    def verify_otp(self, request):
        """
        Verify OTP for login or MFA setup.
        """
        serializer = MFAOtpVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_code = serializer.validated_data["otp_code"]
        service = self.get_service()
        service.verify_otp(otp_code)

        return Response({"detail": "OTP verified."})

    @action(detail=False, methods=["post"], url_path="verify-recovery")
    def verify_recovery_token(self, request):
        """
        Verify recovery token to bypass MFA if OTP is lost.
        """
        serializer = MFARecoveryTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["recovery_token"]
        service = self.get_service()
        service.verify_recovery_token(token)

        return Response({"detail": "Recovery token accepted. MFA bypassed."})