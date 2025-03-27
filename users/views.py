import logging
import redis
import time
import requests
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import action, throttle_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity  # Fuzzy Search
from rest_framework.pagination import PageNumberPagination
from users.utils import send_deletion_confirmation_email, send_unlock_email, send_security_alert
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import (
    User, AccountDeletionRequest, ProfileUpdateRequest,
    SecureToken, EncryptedRefreshToken, 
    UserSession, BlockedIP,   
    MagicLinkToken
)
from users.utils import (
    notify_mfa_enabled, notify_mfa_disabled, notify_mfa_reset,
    send_mfa_recovery_email,log_audit_action
)

from users.serializers import (
    ImpersonationSerializer,
    UserActivitySerializer,
    ClientProfileSerializer,
    WriterProfileSerializer,
    AdminProfileSerializer,
    SuperadminProfileSerializer,
    EditorProfileSerializer,
    SupportProfileSerializer,
    UserProfileSerializer,
    SignupSerializer,
    LoginSerializer, 
    AccountDeletionRequestSerializer
)
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from superadmin_management.models import SuperadminProfile
from admin_management.models import AdminProfile
from websites.models import Website
from users.utils import get_client_ip, generate_otp, send_otp_email, send_otp_sms, verify_totp
from django.utils.timezone import now, timedelta
import pyotp
from users.models import UserSession
from users.utils import get_client_ip, get_device_info
from django.http import JsonResponse
from datetime import timedelta
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import base64
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from user_agents import parse
from django.utils.timezone import now, timedelta
import base64
from .utils import generate_totp_qr_code, send_unlock_email
from users.utils import store_active_token, revoke_token, is_token_revoked
import qrcode
from io import BytesIO
from users.throttling import LoginThrottle, MagicLinkThrottle
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ViewSet
import uuid
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


MAX_FAILED_ATTEMPTS = settings.MAX_FAILED_ATTEMPTS# Lockout threshold 
LOCKOUT_DURATION = timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES) # Lockout period 
SESSION_EXPIRATION_DAYS = settings.SESSION_EXPIRATION_DAYS

def custom_rate_limit_handler(request, exception):
    """Custom response when rate limit is exceeded, with retry instructions."""
    retry_after = 60  # Assume a 1-minute cooldown (adjust based on actual throttle)
    return Response(
        {
            "error": "Too many requests. Please slow down.",
            "retry_after_seconds": retry_after
        },
        status=status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": str(retry_after)}
    )

class ForbiddenAccess(APIException):
    status_code = 403
    default_detail = "You do not have permission to access this resource."
    default_code = "forbidden"

def check_admin_access(user):
    """Ensures only Superadmins & Admins can manage users."""
    if user.role not in ["superadmin", "admin"]:
        raise ForbiddenAccess()
    
def get_device_info(request):
    """Detects device type (Mobile, Tablet, Desktop)."""
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    parsed_agent = parse(user_agent)

    device_type = "Desktop"
    if parsed_agent.is_mobile:
        device_type = "Mobile"
    elif parsed_agent.is_tablet:
        device_type = "Tablet"

    browser = f"{parsed_agent.browser.family} {parsed_agent.browser.version_string}"
    return f"{device_type} - {browser}"


# Helper function to verify Google reCAPTCHA
def verify_recaptcha(recaptcha_response):
    """Verifies reCAPTCHA response with Google API."""
    recaptcha_secret = settings.RECAPTCHA_SECRET_KEY
    payload = {'secret': recaptcha_secret, 'response': recaptcha_response}
    
    try:
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload, timeout=3)
        response.raise_for_status()  # Raise error for HTTP failures
        result = response.json()
        return result.get("success", False)
    except requests.RequestException as e:
        logger.error(f"reCAPTCHA verification failed: {e}")
        return False  # Fail securely if reCAPTCHA check is unavailable

class CustomUserPagination(PageNumberPagination):
    """Pagination settings for user listings."""
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AuthViewSet(viewsets.ViewSet):
    """Handles user signup, login, and logout"""

    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """Rate-limited login (5 attempts per minute)."""
        return super().login(request)

    @method_decorator(ratelimit(key="ip", rate="3/m", method="POST", block=True))
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def signup(self, request):
        """Rate-limited signup (3 attempts per minute)."""
        return super().signup(request)

    @method_decorator(ratelimit(key="ip", rate="2/m", method="POST", block=True))
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def token_refresh(self, request):
        """Rate-limited token refresh (2 per minute)."""
        return super().token_refresh(request)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def password_reset_request(self, request):
        """Sends a password reset email."""
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        token = default_token_generator.make_token(user)
        reset_link = f"https://yourfrontend.com/reset-password/{token}"
        
        send_mail(
            "Password Reset Request",
            f"Click here to reset your password: {reset_link}",
            "no-reply@yourdomain.com",
            [user.email]
        )
        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def password_reset_confirm(self, request):
        """Confirms the password reset."""
        email = request.data.get("email")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        user = get_object_or_404(User, email=email)
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password successfully reset."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Allows users to change their password."""
        user = request.user
        otp_code = request.data.get("otp_code")
        require_mfa_verification(user, otp_code)

        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        # Log action
        log_audit_action(user, "PASSWORD_CHANGED", request)

        # Send notification if enabled
        if user.notify_password_change:
            send_password_change_alert(user, request)

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def enable_2fa(self, request):
        """Enables two-factor authentication (2FA) for a user."""
        user = request.user
        secret = pyotp.random_base32()
        user.otp_secret = secret
        user.save()
        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(user.email, issuer_name="YourCompany")
        return Response({"message": "2FA enabled. Scan this QR code.", "otp_uri": otp_uri}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def disable_2fa(self, request):
        """Disables 2FA for a user."""
        user = request.user
        user.otp_secret = ""
        user.save()
        return Response({"message": "2FA disabled successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_2fa(self, request):
        """Verifies a 2FA code."""
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")

        user = get_object_or_404(User, email=email)
        totp = pyotp.TOTP(user.otp_secret)

        if totp.verify(otp_code):
            return Response({"message": "2FA verified."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid 2FA code."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_otp(self, request):
        """Verifies OTP and completes the login process."""
        email = request.data.get("email")
        otp = request.data.get("otp")

        user = User.objects.filter(email=email).first()
        if not user or user.otp_code != otp:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Clear OTP after verification
        user.otp_code = None
        user.save()

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enable_mfa(self, request):
        """Allows users to enable MFA."""
        user = request.user
        mfa_method = request.data.get("mfa_method")
        otp_code = request.data.get("otp_code")

        if mfa_method not in ["email_otp", "sms_otp", "totp"]:
            return Response({"error": "Invalid MFA method."}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_mfa_enabled:
            return Response({"error": "MFA is already enabled."}, status=status.HTTP_400_BAD_REQUEST)
    
        user.is_mfa_enabled = True
        user.mfa_method = mfa_method
        user.generate_mfa_secret()
        user.generate_backup_codes()
        user.save()

        # Validate OTP before enabling MFA
        if mfa_method == 'totp':
            return Response({"message": "Scan this QR code to set up TOTP."}, status=status.HTTP_200_OK)

        elif mfa_method == 'email_otp':
            if not verify_email_otp(otp_code):
                return Response({"error": "Invalid or expired OTP code"}, status=400)

        elif mfa_method == 'sms_otp':
            if not self.verify_otp(user, otp_code):
                return Response({"error": "Invalid OTP"}, status=400)

        # Log action
        log_audit_action(user, "MFA_ENABLED", request)

        user.save()
        return Response({"message": "MFA enabled successfully."}, status=status.HTTP_200_OK)


        # # For QR code
        # if mfa_method == 'totp':
        # qr_code = generate_totp_qr_code(user)
        # return HttpResponse(base64.b64encode(qr_code), content_type="image/png")

        # return Response({"message": f"MFA enabled via {mfa_method}"}, status=status.HTTP_200_OK)
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_mfa(request):
        """Verify MFA code."""
        email = request.data.get("email")
        otp_code = request.data.get("otp_code")

        if not email or not otp_code:
            return Response({"error": "Email and OTP code are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_mfa_enabled:
            return Response({"error": "MFA is not enabled"}, status=status.HTTP_400_BAD_REQUEST)

        if user.mfa_method in ["sms", "email"]:
            if user.verify_otp(otp_code):
                user.otp_code = None  # Clear OTP after successful use
                user.save()
                return Response({"message": "MFA verified successfully"}, status=status.HTTP_200_OK)
        
        elif user.mfa_method == "totp":
            totp = pyotp.TOTP(user.mfa_secret)
            if totp.verify(otp_code):
                return Response({"message": "MFA verified successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def disable_mfa(self, request):
        """Allows users to disable MFA."""
        user = request.user
        if user.role in ["superadmin", "admin", "support", "editor"]:
            return Response({"error": "Admins cannot disable MFA."}, status=status.HTTP_403_FORBIDDEN)
        user.is_mfa_enabled = False
        user.mfa_method = "none"
        user.mfa_secret = None
        user.save()
        # Log action
        log_audit_action(user, "MFA_DISABLED", request)
        # Send notification
        notify_mfa_disabled(user)
        return Response({"message": "MFA disabled successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def signup(self, request):
        """Handles user registration while detecting IP and assigning a website"""
        serializer = SignupSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.save()

            # Detect user IP and auto-assign location
            ip_address = get_client_ip(request)
            user.auto_detect_country(ip_address)
            user.save()
            # Send welcome email
            send_mail(
                "Welcome to YourApp!",
                f"Hello {user.username},\n\nThank you for signing up with us!",
                "no-reply@yourapp.com",
                [user.email]
            )

            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    @throttle_classes([LoginThrottle])
    def login(self, request):
        """Login with MFA verification, secure session tracking, and rate limiting"""
        
        email = request.data.get("email")
        password = request.data.get("password")
        otp_code = request.data.get("otp_code")

        # Identify the request host
        request_host = request.get_host().replace("www.", "")

        # Validate website domain
        website = Website.objects.filter(domain__icontains=request_host, is_active=True).first()
        if not website:
            return Response({"error": "This website is not registered or inactive."}, status=status.HTTP_403_FORBIDDEN)

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Ensure the user logs in from the correct site
        if user.role == "client" and user.website != website:
            return Response({"error": "Access denied. Please log in from your assigned website."}, status=status.HTTP_403_FORBIDDEN)

        # Prevent admins from logging in on client websites
        if user.role in ["superadmin", "admin", "support", "editor"] and request_host != user.website.domain:
            return Response({"error": "Admins must log in from the admin panel."}, status=status.HTTP_403_FORBIDDEN)

        # Detect device info once and reuse
        device_info = get_device_info(request)
        session_key = str(RefreshToken.for_user(user))

        # Detect new device or IP
        session_exists = UserSession.objects.filter(user=user, ip_address=ip_address).exists()
        if not session_exists:
            send_security_alert(user, request)

        # Check if IP is blocked
        blocked_ip = BlockedIP.objects.filter(ip_address=ip_address).first()
        if blocked_ip and blocked_ip.is_blocked():
            return Response({"error": "Too many failed attempts. Try again later."}, status=403)

        # Account Lockout Handling
        if user.is_locked and user.lockout_until and now() < user.lockout_until:
            remaining_time = (user.lockout_until - now()).total_seconds() / 60
            return Response(
                {"error": f"Account locked. Try again in {int(remaining_time)} minutes."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Track failed attempts per user
        if not user:
            failed_attempts = request.session.get("failed_attempts", 0) + 1
            request.session["failed_attempts"] = failed_attempts

            if failed_attempts >= MAX_FAILED_ATTEMPTS:
                BlockedIP.objects.create(ip_address=ip_address, blocked_until=now() + LOCKOUT_DURATION)
                return Response({"error": "Too many failed attempts. Your IP is blocked for 30 minutes."}, status=403)

        else:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.is_locked = True
                user.lockout_until = now() + LOCKOUT_DURATION
                user.save()
                return Response({"error": "Account locked. Try again later."}, status=403)

        # Block IP after 5 failed attempts

        # Track failed attempts per user & per IP
        failed_attempts = request.session.get("failed_attempts", 0) + 1
        request.session["failed_attempts"] = failed_attempts

        user.failed_login_attempts += 1
        user.save()

        
        if failed_attempts >= 5:
            BlockedIP.objects.create(ip_address=ip_address, blocked_until=now() + timedelta(minutes=15))
            return Response({"error": "Too many failed attempts. Your IP is blocked for 15 minutes."}, status=403)

        # If reCAPTCHA is required, verify it
        if user and user.recaptcha_required:
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                return Response({"error": "reCAPTCHA verification failed. Try again."}, status=400)

        # Lock account if too many failed attempts
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.is_locked = True
            user.lockout_until = now() + LOCKOUT_DURATION
            user.save()
            return Response({"error": "Account locked. Try again later."}, status=403)

        # **MFA Handling**
        if user.is_mfa_enabled:
            if not otp_code:
                return Response({"error": "MFA code required"}, status=status.HTTP_403_FORBIDDEN)

            # Verify MFA Code
            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(otp_code):
                return Response({"error": "Invalid MFA code"}, status=status.HTTP_400_BAD_REQUEST)

        # Track Session Details (IP, Device, Expiry)
        session_key = str(RefreshToken.for_user(user))
        ip_address = get_client_ip(request)
        device_type = get_device_info(request)
       
        # Detect new login location
        session_exists = UserSession.objects.filter(user=user, ip_address=ip_address).exists()
        if not session_exists:
            send_security_alert(user, request)


        UserSession.objects.update_or_create(
            user=user,
            session_key=session_key,
            defaults={"ip_address": ip_address, "device_type": device_type, "expires_at": now() + timedelta(days=7)}
        )


        # **Generate JWT Tokens**
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # **Store Encrypted Refresh Token in DB**
        EncryptedRefreshToken.objects.create_encrypted_token(user, str(refresh))

        # **Store Active Token in Redis for session tracking**
        store_active_token(user.id, str(refresh))

        # **Secure Refresh Token Storage**
        SecureToken.objects.create(
            user=user,
            encrypted_token=SecureToken().encrypt_token(refresh_token),
            purpose="refresh_token",
            expires_at=now() + timedelta(days=7),
        )

        # **Prepare Secure Response**
        response = Response({
            "message": "Login successful",
            "access": access_token,
            "refresh": refresh_token,
            "role": user.role,
            "redirect_url": f"https://{user.website.domain}/dashboard",
        }, status=status.HTTP_200_OK)

        # **Secure HTTP-only Cookies (Prevents XSS & CSRF Attacks)**
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()
        )

        return response
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke_token(self, request, pk=None):
        """Revokes a specific token for the user."""
        token = get_object_or_404(SecureToken, user=request.user, id=pk, is_active=True)
        token.revoke()
        return Response({"message": "Token revoked successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke_all_tokens(self, request):
        """Revokes all active tokens for the user."""
        SecureToken.objects.filter(user=request.user, is_active=True).update(is_active=False)
        return Response({"message": "All tokens revoked successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def admin_revoke_all_tokens(self, request, pk=None):
        """Admin forcibly revokes all tokens for a user."""
        user = get_object_or_404(User, id=pk)
        tokens = SecureToken.objects.filter(user=user, is_active=True)

        for token in tokens:
            token.revoke()

        return Response({"message": f"All tokens for {user.email} revoked."}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reset_mfa(self, request, pk=None):
        """
        Allows an admin to reset MFA for a user.
        """
        user = get_object_or_404(User, id=pk)

        # Generate new MFA secret
        new_secret = user.generate_mfa_secret()
        new_backup_codes = user.generate_backup_codes()

        # Send notification
        notify_mfa_reset(user)

        # Log the action
        log_audit_action(request.user, "MFA_RESET", request)

        return Response({
            "message": f"MFA reset successfully for {user.email}.",
            "new_mfa_secret": new_secret,
            "backup_codes": new_backup_codes
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Blacklist the refresh token and revoke it from Redis to log out the user."""


        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user  # Get authenticated user

        # Check if token is already revoked
        if is_token_revoked(user.id, refresh_token):
            return Response({"error": "Token already revoked."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Blacklist token using Django SimpleJWT
            token = RefreshToken(refresh_token)
            token.blacklist()
            session_key = request.session.session_key
            request.user.sessions.filter(session_key=session_key).delete()
            logout(request)

            user = request.user
            # Revoke all active tokens
            SecureToken.objects.filter(user=user, purpose="refresh_token").delete()  # Remove from DB
            revoke_token(user.id, None)  # Remove from Redis


            response = Response({"message": "Logout successful"})
            # Delete session
            request.user.sessions.all().delete()
            response.delete_cookie("trusted_device")
            logout(request)

        

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=["post"], url_path="request-magic-link")
    @throttle_classes([MagicLinkThrottle])
    def request_magic_link(self, request):
        """
        Sends a magic link to the user's email for passwordless login.
        """
        email = request.data.get("email")

        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

        # Generate magic link token
        token = MagicLinkToken.objects.create(
            user=user,
            expires_at=now() + timedelta(minutes=15)  # Token valid for 15 minutes
        )

        # Send magic link via email
        magic_link = f"{settings.FRONTEND_URL}/magic-login/{token.token}"
        send_mail(
            subject="Your Magic Login Link",
            message=f"Click the link to log in: {magic_link}\n\nThis link is valid for 15 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Magic link sent to your email."})

    @action(detail=False, methods=["get"], url_path="magic-login/(?P<token>[0-9a-fA-F-]+)")
    def magic_login(self, request, token):
        """Handles magic link login with expiration and one-time use protection."""
        magic_link = get_object_or_404(MagicLinkToken, token=token)
        
        if not magic_link.is_valid():
            return Response({"error": "Magic link expired."}, status=400)

        # Capture login IP and device info
        ip_address = get_client_ip(request)
        device_type = get_device_info(request)

        # Log in the user
        login(request, magic_link.user)

        # Track session
        UserSession.objects.create(
            user=magic_link.user,
            ip_address=ip_address,
            device_type=device_type,
            expires_at=now() + timedelta(days=7),
        )

        # Delete token after use (one-time use)
        magic_link.delete()

        return Response({"message": "Login successful."})

class UserViewSet(viewsets.ModelViewSet):
    """Handles user-related operations including profile, impersonation, and activity"""
    
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomUserPagination  # Enable pagination
    serializer_class = UserProfileSerializer  # Default serializer

    role_serializers = {
        "client": ClientProfileSerializer,
        "writer": WriterProfileSerializer,
        "editor": EditorProfileSerializer,
        "support": SupportProfileSerializer,
        "admin": AdminProfileSerializer,
        "superadmin": SuperadminProfileSerializer,
    }

    def get_serializer_class(self):
        """Dynamically return the correct serializer based on the user role."""
        return role_serializers.get(self.request.user.role, UserProfileSerializer)

    # user = User.objects.select_related("writer_profile", "client_profile").get(id=request.user.id)


    def get_queryset(self):
        """Restrict access based on user roles."""
        user = self.request.user

        if user.role in ["client", "writer"]:
            return User.objects.filter(id=user.id)  # Clients & Writers only see themselves

        elif user.role == "editor":
            return User.objects.filter(role="writer")  # Editors only see writers

        elif user.role == "support":
            return User.objects.filter(role="client")  # Support staff only see clients

        return User.objects.all()  # Admins & Superadmins see all users



    def list(self, request, *args, **kwargs):
        """List users with filtering, search, sorting, and pagination."""
    
        check_admin_access(request.user)

        # Filters
        role = request.query_params.get("role")
        search_query = request.query_params.get("search")
        sort_by = request.query_params.get("sort")

        # Validate role filter
        allowed_roles = ["client", "writer", "editor", "support", "admin", "superadmin"]
        if role and role not in allowed_roles:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        # Get queryset based on role

        # Get queryset based on role
        users = User.objects.filter(role=role) if role else User.objects.all()

        # Apply search filter if provided
        direct_matches = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

        if not direct_matches.exists():
            users = users.annotate(similarity=TrigramSimilarity("username", search_query)).filter(similarity__gt=0.3)

        users = users.order_by("-similarity")

        # Sorting
        sorting_options = {
            "newest": "-date_joined",
            "oldest": "date_joined",
            "alphabetical": "username",
            "reverse-alphabetical": "-username",
            "last-active": "-last_active",
        }
        if sort_by in sorting_options:
            users = users.order_by(sorting_options[sort_by])

        # Paginate results
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request, view=self)
        return paginator.get_paginated_response(serializer_class(paginated_users, many=True).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def active_tokens(self, request):
        """Retrieve all active tokens for the logged-in user."""
        tokens = SecureToken.objects.filter(user=request.user, is_active=True).order_by("-created_at")
        token_data = [
            {
                "id": token.id,
                "purpose": token.purpose,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "is_active": token.is_active,
            }
            for token in tokens
        ]
        return Response({"active_tokens": token_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_update(self, request, pk=None):
        """Allows clients & writers to request a profile update."""
        user = self.get_object()
        if request.user != user:
            raise PermissionDenied("You can only request updates for your own profile.")

        requested_data = request.data
        ProfileUpdateRequest.objects.create(user=user, requested_data=requested_data)

        return Response({"message": "Profile update request submitted successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def request_deletion(self, request, pk=None):
        """Allows clients & writers to request account deletion."""
        user = self.get_object()
        if request.user != user:
            raise PermissionDenied("You can only request deletion for your own account.")

        reason = request.data.get("reason")
        AccountDeletionRequest.objects.create(user=user, reason=reason)

        return Response({"message": "Account deletion request submitted successfully."}, status=status.HTTP_201_CREATE)
        if request.user != user:
            raise PermissionDenied("You can only request deletion for your own account.")

        reason = request.data.get("reason")
        AccountDeletionRequest.objects.create(user=user, reason=reason)

        # Notify admins
        admin_emails = User.objects.filter(role="admin").values_list("email", flat=True)
        send_mail(
            "New Account Deletion Request",
            f"User {user.email} has requested account deletion. Please review.",
            settings.DEFAULT_FROM_EMAIL,
            list(admin_emails),
            fail_silently=False,
        )

        return Response({"message": "Account deletion request submitted successfully."}, status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Retrieve the authenticated user's profile."""
        user = request.user
        profile_map = {
            "client": (ClientProfile, ClientProfileSerializer),
            "writer": (WriterProfile, WriterProfileSerializer),
            "editor": (EditorProfile, EditorProfileSerializer),
            "support": (SupportProfile, SupportProfileSerializer),
            "admin": (User, AdminProfileSerializer),
            "superadmin": (User, AdminProfileSerializer),
        }

        profile_model, serializer_class = profile_map.get(user.role, (None, None))
        if profile_model:
            profile_instance = get_object_or_404(profile_model, user=user)
            serializer = serializer_class(profile_instance)
            return Response(serializer.data)

        raise PermissionDenied("Invalid role or unauthorized access.")

    @method_decorator(ratelimit(key="user", rate="3/m", method="POST", block=True))
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def impersonate(self, request, pk=None):
        """Allows Superadmins/Admins to impersonate another user."""
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if target_user.is_impersonated:
            return Response({"error": "User is already being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.impersonate(request.user)

        # Log impersonation action
        log_audit_action(request.user, "USER_IMPERSONATION", request)

        return Response(ImpersonationSerializer(target_user).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAdminUser])
    def stop_impersonation(self, request, pk=None):
        """Stops impersonation of a user."""
        check_admin_access(request.user)
        target_user = get_object_or_404(User, id=pk)

        if not target_user.is_impersonated:
            return Response({"error": "User is not being impersonated."}, status=status.HTTP_400_BAD_REQUEST)

        target_user.stop_impersonation()
        return Response({"message": "Impersonation stopped."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def activity(self, request, pk=None):
        """Fetches user activity logs."""
        check_admin_access(request.user)

        user = get_object_or_404(User, id=pk)
        serializer = UserActivitySerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unlock_user(self, request, pk=None):
        """Admin manually unlocks a locked user account."""
        user = get_object_or_404(User, id=pk)
        if not user.is_locked:
            return Response({"message": "User is not locked."}, status=status.HTTP_400_BAD_REQUEST)

        user.unlock_account()
        return Response({"message": "User account has been unlocked."}, status=status.HTTP_200_OK)
    

    @action(detail=False, methods=['get'])
    def active_sessions(self, request):
        """Returns a list of active sessions for the logged-in user."""
        sessions = UserSession.objects.filter(user=request.user).order_by("-last_active")
        session_data = [
            {
                "session_key": session.session_key,
                "ip_address": session.ip_address,
                "device": session.device,
                "login_time": session.login_time,
                "last_active": session.last_active,
                "expires_at": session.expires_at,
            }
            for session in sessions
        ]
        return Response({"active_sessions": session_data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def logout_session(self, request, pk=None):
        """Allows a user to log out from a specific session."""
        session = get_object_or_404(UserSession, session_key=pk, user=request.user)
        session.delete()  # Ends session
        return Response({"message": "Session logged out successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path="terminate-session")
    def terminate_session(self, request, pk=None):
        """Terminates a specific session for the user."""
        session = get_object_or_404(UserSession, id=pk, user=request.user, is_active=True)
        if not session:
            return Response({"error": "Session not found or already logged out."}, status=404)
        session.terminate()
        return Response({"message": "Session terminated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def force_logout_all(self, request):
        """Admin can log out all users from all sessions."""
        current_admin_session = request.session.session_key
        UserSession.objects.exclude(session_key=current_admin_session).delete()
        return Response({"message": "All user sessions have been terminated, except the current admin.."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout_all_sessions(self, request):
        """Terminates all active sessions for the user."""
        sessions = UserSession.objects.filter(user=request.user, is_active=True)
        
        for session in sessions:
            session.terminate()
        
        return Response({"message": "All sessions terminated successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="logout-from-all-devices")
    def logout_from_all_devices(self, request):
        """
        Logs out the user from all devices except the current session.
        """
        current_session = request.session.session_key
        request.user.sessions.exclude(session_key=current_session).update(is_active=False)
        
        for session in request.user.sessions.exclude(session_key=current_session):
            session.terminate()

        return Response({"message": "Logged out from all devices except the current one."})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def admin_terminate_all_sessions(self, request, pk=None):
        """Admin forcibly logs out all sessions of a user."""
        user = get_object_or_404(User, id=pk)
        sessions = UserSession.objects.filter(user=user, is_active=True)

        for session in sessions:
            session.terminate()

        return Response({"message": f"All sessions for {user.email} terminated."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="expire-old-sessions")
    def expire_old_sessions(self, request):
        """
        Automatically expires sessions inactive for more than 24 hours.
        """
        expired_sessions = request.user.sessions.filter(last_activity__lt=now() - timedelta(hours=24))
        count = expired_sessions.count()

        for session in expired_sessions:
            session.terminate()

        return Response({"message": f"{count} expired sessions have been removed."})


class AccountDeletionRequestViewSet(viewsets.ViewSet):
    """Handles user account deletion requests."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def request_deletion(self, request):
        """Clients & Writers request account deletion."""
        user = request.user
        if user.is_frozen:
            return Response({"error": "Your account is already scheduled for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get("reason", "No reason provided")
        AccountDeletionRequest.objects.create(user=user, reason=reason)
        user.freeze_account()

        return Response({"message": "Your account is now frozen and scheduled for deletion in 3 months."}, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def confirm_deletion(self, request, pk=None):
        """Confirms the account deletion request and freezes the account."""
        user = get_object_or_404(User, id=pk)

        # Ensure the request exists and is pending confirmation
        deletion_request = AccountDeletionRequest.objects.filter(user=user, status="Pending Confirmation").first()
        if not deletion_request:
            return Response({"error": "No pending deletion request found."}, status=status.HTTP_400_BAD_REQUEST)

        # Freeze account and update request status
        user.freeze_account()
        deletion_request.status = "confirmed"
        deletion_request.save()

        return Response({"message": "Account deletion confirmed. Your account is now frozen for 3 months."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_deletion(self, request, pk=None):
        """Admin approves account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")

        # Log admin action
        logger.info(f"Admin {request.user.email} approved deletion for {deletion_request.user.email}")

        deletion_request.status = "approved"
        deletion_request.save()

         # Freeze the user
        deletion_request.user.freeze_account()

        return Response({"message": "Account deletion request approved. Account is now frozen."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject_deletion(self, request, pk=None):
        """Admin rejects account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")
        reason = request.data.get("reason", "No reason provided")
        deletion_request.status = "rejected"
        deletion_request.admin_response = reason
        deletion_request.save()

        return Response({"message": "Account deletion request rejected."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reinstate_account(self, request, pk=None):
        """Admin reinstates a frozen account."""
        user = get_object_or_404(User, id=pk, is_frozen=True)
        user.reinstate_account()

        return Response({"message": "User account has been reinstated."}, status=status.HTTP_200_OK)

class AdminProfileRequestViewSet(viewsets.ViewSet):
    """Allows admins to review and approve/reject profile update and deletion requests."""

    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def approve_update(self, request, pk=None):
        """Approve a profile update request."""
        update_request = get_object_or_404(ProfileUpdateRequest, id=pk, status="pending")
        update_request.approve()
        return Response({"message": "Profile update approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject_update(self, request, pk=None):
        """Reject a profile update request."""
        update_request = get_object_or_404(ProfileUpdateRequest, id=pk, status="pending")
        reason = request.data.get("reason")
        update_request.reject(reason)
        return Response({"message": "Profile update rejected."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def approve_deletion(self, request, pk=None):
        """Approve an account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")
        deletion_request.approve()
        return Response({"message": "Account deletion approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject_deletion(self, request, pk=None):
        """Reject an account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")
        reason = request.data.get("reason")
        deletion_request.reject(reason)
        return Response({"message": "Account deletion rejected."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["patch"], url_path="update-profile")
    def update_profile(self, request):
        """
        Allows users to update their profile. 
        - Basic updates (bio, phone number, avatar) are auto-approved.
        - Sensitive updates (email, role, website) require admin approval.
        """
        user = request.user
        update_fields = request.data

        # Fields that require admin approval
        admin_approval_fields = ["email", "role", "website"]

        # Separate updates
        auto_approve_updates = {}
        admin_approval_updates = {}

        for field, value in update_fields.items():
            if field in admin_approval_fields:
                admin_approval_updates[field] = value
            else:
                auto_approve_updates[field] = value

        # Auto-approve basic updates
        for field, value in auto_approve_updates.items():
            setattr(user, field, value)
        user.save()

        # Store admin approval request if necessary
        if admin_approval_updates:
            ProfileUpdateRequest.objects.create(user=user, requested_data=admin_approval_updates)
            return Response({"message": "Profile updated. Some changes require admin approval."})

        return Response({"message": "Profile updated successfully."})

    @action(detail=False, methods=["get"], url_path="profile-update-requests", permission_classes=[IsAuthenticated])
    def get_update_requests(self, request):
        """
        Allows users to view their pending profile update requests.
        """
        requests = request.user.update_requests.filter(status="pending").values()
        return Response({"pending_requests": list(requests)})
class AdminUserManagementViewSet(viewsets.ViewSet):
    """Allows admins to manage user accounts."""

    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['post'])
    def restore_archived_account(self, request, pk=None):
        """Restores an archived account."""
        user = get_object_or_404(User, id=pk, is_archived=True)
        user.is_archived = False
        user.is_active = True
        user.save()

        return Response({"message": "User account restored successfully."}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key="user", rate="2/m", method="POST", block=True))    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """Admin suspends a user."""
        user = get_object_or_404(User, id=pk)
        user.is_suspended = True
        user.suspension_reason = request.data.get("reason", "No reason provided")
        user.suspension_start_date = now()
        user.suspension_end_date = now() + timedelta(days=30)  # Default 30-day suspension
        user.save()

        logger.info(f"Admin {request.user.email} suspended {user.email}")
        return Response({"message": "User suspended."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def lift_suspension(self, request, pk=None):
        """Admin lifts a user's suspension."""
        user = get_object_or_404(User, id=pk)
        user.is_suspended = False
        user.suspension_reason = None
        user.suspension_start_date = None
        user.suspension_end_date = None
        user.save()

        logger.info(f"Admin {request.user.email} lifted suspension for {user.email}")
        return Response({"message": "User suspension lifted."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def force_reset_password(self, request, pk=None):
        """Admin forces a user to reset their password."""
        user = get_object_or_404(User, id=pk)
        new_password = "TemporaryPass123"  # Generate a secure random password in production
        user.set_password(new_password)
        user.save()

        send_mail(
            "Your Password Has Been Reset",
            f"Your new temporary password is: {new_password}. Please change it after login.",
            "no-reply@yourdomain.com",
            [user.email]
        )

        logger.info(f"Admin {request.user.email} forced password reset for {user.email}")
        return Response({"message": "User password has been reset and emailed to them."}, status=status.HTTP_200_OK)

    @method_decorator(ratelimit(key="user", rate="1/m", method="POST", block=True))
    @action(detail=False, methods=['get'])
    def user_reports(self, request):
        """Admin gets reports on user activities."""
        active_users = User.objects.filter(is_active=True).count()
        suspended_users = User.objects.filter(is_suspended=True).count()
        pending_deletion = AccountDeletionRequest.objects.filter(status="pending").count()

        return Response({
            "total_users": User.objects.count(),
            "active_users": active_users,
            "suspended_users": suspended_users,
            "pending_deletion_requests": pending_deletion
        }, status=status.HTTP_200_OK)

class AccountDeletionRequestViewSet(viewsets.ViewSet):
    """Handles user account deletion requests."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def request_deletion(self, request):
        """Clients & Writers request account deletion, requiring confirmation."""
        user = request.user
        if user.is_frozen:
            return Response({"error": "Your account is already scheduled for deletion."}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get("reason", "No reason provided")
        
        # Create deletion request but do not freeze yet
        deletion_request, created = AccountDeletionRequest.objects.get_or_create(user=user, reason=reason)
        
        if created:
            send_deletion_confirmation_email(user)  # Send confirmation email
            return Response({"message": "A confirmation email has been sent. Please confirm to proceed."}, status=status.HTTP_201_CREATED)

        return Response({"error": "You have already submitted a deletion request."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_deletion_status(self, request):
        """Allows users to check the status of their deletion request."""
        user = request.user
        deletion_request = AccountDeletionRequest.objects.filter(user=user).first()

        if not deletion_request:
            return Response({"message": "No deletion request found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AccountDeletionRequestSerializer(deletion_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve_deletion(self, request, pk=None):
        """Admin approves account deletion request but schedules soft deletion."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")

        # Update the request status
        deletion_request.status = "approved"
        deletion_request.save()

        # Freeze the user account but DO NOT delete immediately
        user = deletion_request.user
        user.freeze_account()

        return Response({"message": "Account deletion request approved. Account is now frozen and will be deleted in 3 months."}, status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject_deletion(self, request, pk=None):
        """Admin rejects account deletion request."""
        deletion_request = get_object_or_404(AccountDeletionRequest, id=pk, status="pending")
        reason = request.data.get("reason", "No reason provided")
        deletion_request.reject(reason)

        return Response({"message": "Account deletion request rejected."}, status=status.HTTP_200_OK)
    

class CustomTokenRefreshView(TokenRefreshView):
    """Handles secure token refresh using cookies."""

    def post(self, request, *args, **kwargs):
        """Refresh token if valid and return a new access token."""
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except InvalidToken:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        response = JsonResponse({"message": "Token refreshed successfully"})
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        )
        return response

class MFAViewSet(viewsets.ViewSet):
    """Handles MFA-related actions for users"""

    permission_classes = [permissions.IsAuthenticated]

    def __init__(self):
        # Initialize Redis connection (Adjust with your actual Redis setup)
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def store_otp(self, user, otp_code, expiry=300):
        """
        Store OTP in Redis with an expiration time.
        :param user: The user object.
        :param otp_code: The OTP to store.
        :param expiry: Expiration time in seconds (default 5 minutes).
        """
        redis_key = f"otp:{user.id}:{user.mfa_method}"
        self.redis_client.setex(redis_key, expiry, otp_code)

    def verify_otp(self, user, otp_code):
        """
        Verify the OTP stored in Redis.
        :param user: The user object.
        :param otp_code: The OTP provided by the user.
        :return: True if OTP is valid, False otherwise.
        """
        redis_key = f"otp:{user.id}:{user.mfa_method}"
        stored_otp = self.redis_client.get(redis_key)

        if stored_otp and stored_otp == otp_code:
            self.redis_client.delete(redis_key)  # Remove OTP after successful verification
            return True
        return False

    def send_otp_via_sms(self, phone_number, otp_code):
        """
        Simulate sending OTP via SMS (Replace with actual SMS gateway integration).
        :param phone_number: The user's phone number.
        :param otp_code: The OTP to send.
        """
        print(f"Sending SMS OTP: {otp_code} to {phone_number}")
        # Integrate with Twilio, Nexmo, or any SMS gateway here

    def send_otp_via_email(self, email, otp_code):
        """
        Simulate sending OTP via Email (Replace with actual email service).
        :param email: The user's email address.
        :param otp_code: The OTP to send.
        """
        print(f"Sending Email OTP: {otp_code} to {email}")
        # Integrate with an email service (SMTP, SendGrid, AWS SES, etc.)

    @action(detail=False, methods=['post'])
    def enable_mfa(self, request):
        """Enable MFA for the user."""
        user = request.user
        mfa_method = request.data.get('mfa_method')

        if mfa_method not in ['totp', 'sms', 'email']:
            return Response({"error": "Invalid MFA method"}, status=status.HTTP_400_BAD_REQUEST)


        if user.is_mfa_enabled:
            return Response({"error": "MFA is already enabled."}, status=status.HTTP_400_BAD_REQUEST)
    

        user.mfa_method = mfa_method
        user.is_mfa_enabled = True
        user.generate_mfa_secret()
        user.generate_backup_codes()
        user.save()

        otp_code = request.data.get("otp_code")

        if mfa_method == 'totp':
            # Generate TOTP URI
            totp_uri = user.get_totp_uri()  # Ensure this method exists
            
            # Generate QR Code
            qr = qrcode.make(totp_uri)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            buffer.seek(0)

            # Convert QR to Base64
            qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return Response(
                {"message": "TOTP Enabled", "qr_code": qr_base64},
                status=status.HTTP_200_OK
            )
        elif mfa_method == 'email_otp':
            if not verify_email_otp(otp_code):
                return Response({"error": "Invalid or expired OTP code"}, status=400)

        else:
            return Response({"error": "MFA not enabled"}, status=400)

        # Log action
        log_audit_action(user, "MFA_ENABLED", request)

        # Send notification
        notify_mfa_enabled(user)

        return Response({"message": f"MFA enabled via {mfa_method}"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def verify_mfa(self, request):
        """Verify MFA code."""
        user = request.user
        otp_code = request.data.get("otp_code")
        token = request.data.get("token")

        if not user.is_mfa_enabled:
            return Response({"error": "MFA is not enabled"}, status=status.HTTP_400_BAD_REQUEST)

        if user.mfa_method == "totp":
            if not user.mfa_secret:
                return Response({"error": "TOTP is not set up"}, status=status.HTTP_400_BAD_REQUEST)

            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(otp_code):
                return Response({"error": "Invalid TOTP Code"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "MFA verified successfully"}, status=status.HTTP_200_OK)

        elif user.mfa_method in ["sms", "email"]:
            # OTP retrieval and verification (e.g., using Redis)
            otp_verified = self.verify_otp(user, otp_code)
            if not otp_verified:
                return Response({"error": "Invalid OTP Code"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "MFA verified successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Unsupported MFA method"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def request_mfa_recovery(self, request):
        """
        Sends an email with an MFA recovery link.
        """
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)

        if not user.is_mfa_enabled:
            return Response({"error": "MFA is not enabled for this account."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate recovery token and send email
        user.generate_mfa_recovery_token()
        send_mfa_recovery_email(user)

        return Response({"message": "MFA recovery email sent. Check your inbox."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def verify_mfa_recovery(self, request):
        """
        Verifies the MFA recovery token and resets MFA.
        """
        token = request.data.get("token")
        user = get_object_or_404(User, mfa_recovery_token=token)

        if not user.mfa_recovery_expires or now() > user.mfa_recovery_expires:
            return Response({"error": "Recovery token expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Reset MFA
        user.generate_mfa_secret()
        user.generate_backup_codes()
        user.mfa_recovery_token = None
        user.mfa_recovery_expires = None
        user.save()

        return Response({"message": "MFA has been reset successfully. Set up a new authenticator app."}, status=status.HTTP_200_OK)


class AccountUnlockViewSet(viewsets.ViewSet):
    """Handles account unlocking actions"""

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def request_unlock(self, request):
        """Request account unlock via email if locked out."""
        email = request.data.get("email")
        user = User.objects.filter(email=email, is_locked=True).first()

        if not user:
            return Response({"error": "No locked account found with this email."}, status=status.HTTP_400_BAD_REQUEST)

        # Send unlock email
        send_unlock_email(user)
        return Response({"message": "Unlock instructions have been sent to your email."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def admin_unlock_account(self, request, pk=None):
        """Admin unlocks a locked account."""
        user = get_object_or_404(User, id=pk, is_locked=True)
        user.unlock_account()
        # Log admin action
        log_audit_action(request.user, "ADMIN_UNLOCKED_ACCOUNT", request)

        return Response({"message": "User account has been unlocked."}, status=status.HTTP_200_OK)


    @action(detail=False, methods=["post"], url_path="mfa-login")
    def mfa_login(self, request):
        """
        Handles MFA authentication, allowing users to skip MFA on trusted devices.
        """
        email = request.data.get("email")
        mfa_code = request.data.get("mfa_code")
        remember_device = request.data.get("remember_device", False)

        # Validate User
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User not found"}, status=404)

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
        if not user.verify_totp(mfa_code):
            return Response({"error": "Invalid MFA code"}, status=400)

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
            response.set_cookie("trusted_device", device_token, httponly=True, secure=True, max_age=30 * 24 * 60 * 60)
            return response

        return Response({"message": "MFA passed, logged in successfully"})

    @action(detail=False, methods=["post"], url_path="logout", permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logs out the user and removes trusted device cookies.
        """
        response = Response({"message": "Logout successful"})
        response.delete_cookie("trusted_device")
        logout(request)
        return response


class SessionViewSet(viewsets.ViewSet):
    """Allows users to manage their active sessions."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def active_sessions(self, request):
        """Retrieve active sessions."""
        sessions = UserSession.objects.filter(user=request.user)
        data = [{"id": s.id, "device": s.device_info, "ip": s.ip_address, "last_active": s.last_active} for s in sessions]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def logout_session(self, request, pk=None):
        """Log out a specific session."""
        session = get_object_or_404(UserSession, id=pk, user=request.user)

        if session.session_key == request.session.session_key:
            return Response({"error": "Cannot log out current session."}, status=status.HTTP_400_BAD_REQUEST)

        session.delete()
        return Response({"message": "Session logged out."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def logout_all(self, request):
        """Log out all sessions except current one."""
        UserSession.objects.filter(user=request.user).exclude(session_key=request.session.session_key).delete()
        return Response({"message": "All other sessions logged out."}, status=status.HTTP_200_OK)
