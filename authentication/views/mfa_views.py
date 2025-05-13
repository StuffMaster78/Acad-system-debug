import pyotp  # type: ignore
import qrcode  # type: ignore
import base64
import redis
from io import BytesIO

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from users.models import User
from authentication.utilsy import (
    log_audit_action, notify_mfa_enabled,
    send_mfa_recovery_email, verify_email_otp
)
from django.utils.timezone import now



# --- Redis Client Setup ---
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


# --- Helper Functions ---
def store_otp(user, otp_code, expiry=300):
    redis_key = f"otp:{user.id}:{user.mfa_method}"
    redis_client.setex(redis_key, expiry, otp_code)


def verify_otp(user, otp_code):
    redis_key = f"otp:{user.id}:{user.mfa_method}"
    stored_otp = redis_client.get(redis_key)
    if stored_otp == otp_code:
        redis_client.delete(redis_key)
        return True
    return False


# --- API Views ---

class EnableMFA(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        mfa_method = request.data.get("mfa_method")
        otp_code = request.data.get("otp_code")

        if mfa_method not in ["totp", "sms", "email"]:
            return Response({"error": "Invalid MFA method"}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_mfa_enabled:
            return Response({"error": "MFA already enabled."}, status=status.HTTP_400_BAD_REQUEST)

        user.mfa_method = mfa_method
        user.is_mfa_enabled = True
        user.generate_mfa_secret()
        user.generate_backup_codes()
        user.save()

        if mfa_method == "totp":
            totp_uri = user.get_totp_uri()
            qr = qrcode.make(totp_uri)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            log_audit_action(user, "MFA_ENABLED", request)
            notify_mfa_enabled(user)

            return Response({"message": "TOTP MFA enabled.", "qr_code": qr_base64}, status=status.HTTP_200_OK)

        if mfa_method == "email":
            if not verify_email_otp(otp_code):
                return Response({"error": "Invalid or expired email OTP"}, status=status.HTTP_400_BAD_REQUEST)

        elif mfa_method == "sms":
            if not otp_code or not verify_otp(user, otp_code):
                return Response({"error": "Invalid SMS OTP"}, status=status.HTTP_400_BAD_REQUEST)

        log_audit_action(user, "MFA_ENABLED", request)
        notify_mfa_enabled(user)

        return Response({"message": f"MFA enabled via {mfa_method}"}, status=status.HTTP_200_OK)


class VerifyMFA(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get("otp_code")

        if not user.is_mfa_enabled:
            return Response({"error": "MFA not enabled"}, status=status.HTTP_400_BAD_REQUEST)

        if user.mfa_method == "totp":
            if not user.mfa_secret:
                return Response({"error": "TOTP not configured"}, status=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(otp_code):
                return Response({"error": "Invalid TOTP code"}, status=status.HTTP_400_BAD_REQUEST)

        elif user.mfa_method in ["sms", "email"]:
            if not verify_otp(user, otp_code):
                return Response({"error": "Invalid OTP code"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Unsupported MFA method"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "MFA verified successfully"}, status=status.HTTP_200_OK)


class RequestMFARecovery(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)

        if not user.is_mfa_enabled:
            return Response({"error": "MFA not enabled on account"}, status=status.HTTP_400_BAD_REQUEST)

        user.generate_mfa_recovery_token()
        send_mfa_recovery_email(user)

        return Response({"message": "MFA recovery email sent."}, status=status.HTTP_200_OK)


class VerifyMFARecovery(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get("token")
        user = get_object_or_404(User, mfa_recovery_token=token)

        if not user.mfa_recovery_expires or now() > user.mfa_recovery_expires:
            return Response({"error": "Recovery token expired"}, status=status.HTTP_400_BAD_REQUEST)

        user.generate_mfa_secret()
        user.generate_backup_codes()
        user.mfa_recovery_token = None
        user.mfa_recovery_expires = None
        user.save()

        return Response({
            "message": "MFA reset successfully. You may now set up a new authenticator app."
        }, status=status.HTTP_200_OK)