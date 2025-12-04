# authentication/views/mfa_settings.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from authentication.models.mfa_settings import MFASettings
from authentication.serializers import MFASettingsSerializer
from authentication.utils.mfa_utils import (
    generate_totp_qr_code,
    verify_totp,
    setup_passkey,
    verify_passkey_challenge
)

class MFASettingsView(APIView):
    """
    Handles retrieving and updating MFA preferences for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        mfa_settings, created = MFASettings.get_or_create_for_user(request.user)
        serializer = MFASettingsSerializer(mfa_settings)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        mfa_settings, _ = MFASettings.get_or_create_for_user(request.user)
        serializer = MFASettingsSerializer(mfa_settings, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        mfa_settings, _ = MFASettings.get_or_create_for_user(request.user)
        serializer = MFASettingsSerializer(mfa_settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MFAQRCodeView(APIView):
    """
    Handles the generation of a QR code for MFA setup (TOTP).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        mfa_settings = MFASettings.objects.get(user=request.user)
        if mfa_settings.mfa_method != 'qr_code':
            return Response({"error": "MFA method is not QR code."}, status=status.HTTP_400_BAD_REQUEST)

        secret, qr_code_base64 = generate_totp_qr_code(request.user.email)
        mfa_settings.mfa_secret = secret
        mfa_settings.save()

        return Response({
            'qr_code': qr_code_base64,
            'secret': secret
        })

class MFAOTPVerifyView(APIView):
    """
    Handles verifying a TOTP code entered by the user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        otp_code = request.data.get('otp_code')
        if not otp_code:
            return Response({"error": "OTP code is required."}, status=status.HTTP_400_BAD_REQUEST)

        mfa_settings = MFASettings.objects.get(user=request.user)
        if verify_totp(mfa_settings.mfa_secret, otp_code):
            return Response({"status": "OTP code verified successfully."})
        return Response({"error": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)

class MFAPasskeySetupView(APIView):
    """
    Handles passkey (WebAuthn) setup for the user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        public_key = request.data.get('public_key')
        if not public_key:
            return Response({"error": "Public key is required."}, status=status.HTTP_400_BAD_REQUEST)

        mfa_settings = MFASettings.objects.get(user=request.user)
        if mfa_settings.mfa_method != 'passkey':
            return Response({"error": "MFA method is not passkey."}, status=status.HTTP_400_BAD_REQUEST)

        setup_passkey(request.user, public_key)
        return Response({"status": "Passkey setup completed successfully."})

class MFAPasskeyVerifyView(APIView):
    """
    Handles verifying a passkey (WebAuthn) challenge.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        passkey_challenge = request.data.get('passkey_challenge')
        if not passkey_challenge:
            return Response({"error": "Passkey challenge is required."}, status=status.HTTP_400_BAD_REQUEST)

        mfa_settings = MFASettings.objects.get(user=request.user)
        if mfa_settings.mfa_method != 'passkey':
            return Response({"error": "MFA method is not passkey."}, status=status.HTTP_400_BAD_REQUEST)

        if verify_passkey_challenge(request.user, passkey_challenge):
            return Response({"status": "Passkey verified successfully."})
        return Response({"error": "Invalid passkey challenge."}, status=status.HTTP_400_BAD_REQUEST)