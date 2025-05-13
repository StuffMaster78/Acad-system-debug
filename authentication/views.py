from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from websites.models import Website
from .models import TrustedDevice
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    UserSerializer,
    SignupSerializer,
    LoginUserSerializer,
    AccountDeletionRequestSerializer
)
from rest_framework.exceptions import APIException
from django.utils.timezone import now
from rest_framework import serializers
from .models import AuditLog, BlockedIP, MagicLinkToken
from .utils_backp import (
    generate_verification_token,
    generate_totp_secret,
    decode_verification_token,
    verify_email_otp,
    verify_recaptcha,
    log_mfa_action,
    recaptcha_response,
    log_audit_action,
    notify_mfa_reset,
    get_client_ip,
    get_device_info,
    send_magic_link_email,
    notify_mfa_reset,
    notify_mfa_enabled,
    require_mfa_verification,
    notify_mfa_disabled,
    store_active_token,
    is_token_revoked,
)
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
import pyotp 
from datetime import timedelta
from rest_framework.decorators import action
from ratelimit.decorators import ratelimit
import logging
import redis
import time
import requests
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import action, throttle_classes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity  # Fuzzy Search
from rest_framework.pagination import PageNumberPagination
# from .utils_backp import (
#     send_deletion_confirmation_email,
#     send_unlock_email,
#     send_security_alert
# )
from django.core.mail import send_mail
from .models import (
    User, AccountDeletionRequest, ProfileUpdateRequest,
    SecureToken, EncryptedRefreshToken, 
    UserSession, BlockedIP,   
    MagicLinkToken
)
# from authentication.models.magic_links import MagicLinkToken
User = get_user_model()


MAX_FAILED_ATTEMPTS = settings.MAX_FAILED_ATTEMPTS# Lockout threshold 
LOCKOUT_DURATION = timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES) # Lockout period 
SESSION_EXPIRATION_DAYS = settings.SESSION_EXPIRATION_DAYS

class ForbiddenAccess(APIException):
    status_code = 403
    default_detail = "You do not have permission to access this resource."
    default_code = "forbidden"

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
            max_age=settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        )

        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=settings.REFRESH_TOKEN_LIFETIME.total_seconds()
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

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save(is_active=False)  # Account is inactive until verified
            
            # Ask if the user wants to enable MFA (you can modify this with a checkbox or extra step)
            enable_mfa = request.data.get("enable_mfa", False)

            if enable_mfa:
                # Generate MFA secret (TOTP) for the user
                totp_secret = generate_totp_secret()  # This function generates a secret for the user
                user.mfa_secret = totp_secret  # Store the secret in the user profile (can be done in the User model)
                user.save()

                # Generate a QR code to allow the user to scan with an MFA app
                totp = pyotp.TOTP(totp_secret)
                mfa_qr_code = totp.provisioning_uri(name=user.email, issuer_name="MyApp")

                # Send verification email with the QR code
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{generate_verification_token(user)}"
                send_mail(
                    "Email Verification",
                    f"Click here to verify your email and set up MFA: {verification_url}\n\nScan this QR code with your MFA app: {mfa_qr_code}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            else:
                # If MFA is not enabled, just proceed with regular registration
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{generate_verification_token(user)}"
                send_mail(
                    "Email Verification",
                    f"Click here to verify your email: {verification_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

            return Response({"message": "User created. Please check your email to verify your account."},
                             status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        
        user = authenticate(email=email, password=password)
        
        if user is not None and user.is_active:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials or account not active."}, status=status.HTTP_400_BAD_REQUEST)
    

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Blacklist the refresh token to revoke access
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklisting the refresh token

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "An error occurred."}, status=status.HTTP_400_BAD_REQUEST)
        

class VerifyMFAView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        mfa_code = request.data.get('mfa_code')

        if not mfa_code:
            return Response({"error": "MFA code is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify MFA code using the user's stored secret
        totp = pyotp.TOTP(user.mfa_secret)
        if totp.verify(mfa_code):
            return Response({"message": "MFA verified successfully!"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid MFA code."}, status=status.HTTP_400_BAD_REQUEST)
    

class FinalizeAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        # Get the verification token from the request and verify it
        token = request.data.get('token')

        if not token:
            return Response({"error": "Verification token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use the token to find the user (you should already have a method to decode the token and find the user)
            user = decode_verification_token(token)
        except Exception as e:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user has already verified their email and MFA
        if user and not user.is_active:
            user.is_active = True  # Activate the user account
            user.save()

            return Response({"message": "Account activated successfully."}, status=status.HTTP_200_OK)

        return Response({"error": "Account is already activated."}, status=status.HTTP_400_BAD_REQUEST)
    



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