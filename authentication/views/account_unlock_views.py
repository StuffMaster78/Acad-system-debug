from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from datetime import timedelta

from authentication.models import User, TrustedDevice
from authentication.utils_backp import send_unlock_email, log_audit_action, now


class AccountUnlockAPIView(APIView):
    """Handles account unlocking actions"""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Handles the account unlock request"""
        email = request.data.get("email")
        user = User.objects.filter(email=email, is_locked=True).first()

        if not user:
            return Response({"error": "No locked account found with this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Send unlock email
        send_unlock_email(user)
        return Response({"message": "Unlock instructions have been sent to your email."}, status=status.HTTP_200_OK)


class AdminUnlockAccountAPIView(APIView):
    """Admin unlocks a locked user account"""

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk=None, *args, **kwargs):
        """Admin unlocks a locked account"""
        user = get_object_or_404(User, id=pk, is_locked=True)
        user.unlock_account()  # Assuming unlock_account is a method on your User model

        # Log admin action
        log_audit_action(request.user, "ADMIN_UNLOCKED_ACCOUNT", request)

        return Response({"message": "User account has been unlocked."}, status=status.HTTP_200_OK)


class MFALoginAPIView(APIView):
    """Handles MFA login and trusted device management"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Handles MFA authentication, allowing users to skip MFA on trusted devices."""
        email = request.data.get("email")
        mfa_code = request.data.get("mfa_code")
        remember_device = request.data.get("remember_device", False)

        # Validate User
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check for trusted device (skip MFA)
        device_token = request.COOKIES.get("trusted_device")
        if device_token:
            trusted_device = TrustedDevice.objects.filter(
                user=user, device_token=device_token, expires_at__gt=now()
            ).first()
            if trusted_device:
                login(request, user)
                log_audit_action(user, "MFA_BYPASSED_TRUSTED_DEVICE", request)
                return Response({"message": "MFA skipped, logged in successfully"})

        # Verify MFA code
        if not user.verify_totp(mfa_code):  # Assuming verify_totp is a method on your User model
            return Response({"error": "Invalid MFA code"}, status=status.HTTP_400_BAD_REQUEST)

        # Successful MFA Login
        login(request, user)
        log_audit_action(user, "MFA_LOGIN_SUCCESS", request)

        # If "Remember This Device" is selected, store trusted device
        if remember_device:
            device_token = TrustedDevice.generate_token()
            TrustedDevice.objects.create(
                user=user,
                device_token=device_token,
                device_info=request.META.get("HTTP_USER_AGENT", "Unknown"),
                expires_at=now() + timedelta(days=30)  # Device remains trusted for 30 days
            )

            response = Response({"message": "MFA passed, logged in successfully"})
            response.set_cookie(
                "trusted_device", device_token,
                httponly=True, secure=True,
                max_age=30 * 24 * 60 * 60
            )
            return response

        return Response({"message": "MFA passed, logged in successfully"})


class LogoutAPIView(APIView):
    """Handles user logout and trusted device cookie removal"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Logs out the user and removes trusted device cookies."""
        response = Response({"message": "Logout successful"})
        response.delete_cookie("trusted_device")
        logout(request)
        return response