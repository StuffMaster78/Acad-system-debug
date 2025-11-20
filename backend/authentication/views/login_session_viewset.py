from rest_framework import viewsets, permissions
from authentication.models.login import LoginSession
from authentication.serializers import LoginSessionSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.conf import settings
from rest_framework.exceptions import APIException

from django.contrib.auth import authenticate
from django.utils.timezone import now
from django.utils import timezone

from authentication.serializers import LoginSerializer
from authentication.services.failed_login_attempts import FailedLoginService
from authentication.utils.ip import get_client_ip
from authentication.models.sessions import UserSession
from authentication.services.login_session_service import LoginSessionService
from authentication.services.login_service import LoginService

user = settings.AUTH_USER_MODEL

# Optional: raise a 403 with a structured body if MFA isn't set up
class MFANotSetup(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "mfa_required"

    def __init__(self, user):
        detail = {
            "error": "2FA required",
            "setup_required": True,
            "totp_url": LoginService.generate_provisioning_uri(user),
        }
        super().__init__(detail=detail)


class RequireMFAOrDeny(permissions.BasePermission):
    """
    Gate endpoints until user has enabled MFA.
    Use only where it makes sense (read APIs are fine;
    most folks enforce this at auth/token endpoints).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, "mfa_enabled", False):
            return True
        # Raise a structured 403 payload
        raise MFANotSetup(request.user)


class LoginSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List/retrieve the caller's login sessions (tenant-scoped).
    """
    serializer_class = LoginSessionSerializer
    permission_classes = [permissions.IsAuthenticated, RequireMFAOrDeny]

    def get_queryset(self):
        """
        Only sessions for the authenticated user AND current website.
        Assumes middleware sets request.website (or website_id).
        """
        user = self.request.user
        website = getattr(self.request, "website", None)
        website_id = getattr(website, "id", website)  # supports id or raw int

        qs = LoginSession.objects.select_related("user", "website") \
                                 .filter(user=user)
        if website_id is not None:
            qs = qs.filter(website_id=website_id)
        return qs.order_by("-last_activity")

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        """
        Revoke (logout) a specific session by marking it expired.
        """
        session = self.get_object()  # already filtered to owner & website
        if session.is_active:
            session.is_active = False
            session.revoked_at = timezone.now()
            session.revoked_by_id = request.user.id  # if you track it
            session.save(update_fields=["is_active", "revoked_at", "revoked_by_id"])
        return Response({"ok": True, "revoked": True})

    @action(detail=False, methods=["post"], url_path="revoke-all")
    def revoke_all(self, request):
        """
        Revoke all other active sessions for this user on this website.
        """
        qs = self.get_queryset().filter(is_active=True)
        if "keep_current" in request.query_params and request.query_params["keep_current"] == "1":
            qs = qs.exclude(id=getattr(request, "session_id", None))  # if you track current
        count = qs.update(is_active=False, revoked_at=timezone.now())
        return Response({"ok": True, "revoked_count": count})
class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        website = getattr(request, "website", None)
        ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")

        # Try authenticating
        user = authenticate(request=request, username=email, password=password)

        if not user:
            # Try to find user by email to log failed attempt (even if password is wrong)
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_for_logging = User.objects.get(email=email)
                # Log failed attempt only if user exists
                if user_for_logging and website:
                    FailedLoginService.log(user=user_for_logging, website=website, ip=ip, user_agent=user_agent)
            except User.DoesNotExist:
                # User doesn't exist, skip logging failed attempt
                pass
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # If account is locked, suspended, etc.
        if not user.is_active:
            return Response({"detail": "Account disabled."}, status=status.HTTP_403_FORBIDDEN)

        # Optional: Lockout check
        from authentication.models import FailedLoginAttempt
        if FailedLoginAttempt.is_locked_out(user=user, website=website):
            return Response({"detail": "Account locked. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # ✅ Log successful session
        session = LoginSessionService.start_session(user, website, ip=ip, user_agent=user_agent)

        # Optional: Check if user needs 2FA challenge
        # Ensure user profile exists
        if not hasattr(user, 'user_main_profile') or user.user_main_profile is None:
            from users.models import UserProfile
            UserProfile.objects.get_or_create(user=user, defaults={'avatar': 'avatars/universal.png'})
        
        profile = getattr(user, 'user_main_profile', None)
        if profile and hasattr(profile, 'is_2fa_enabled') and profile.is_2fa_enabled:
            # Initiate 2FA challenge here (send OTP, mark session pending)
            return Response({
                "detail": "2FA required.",
                "session_id": str(session.id),
                "challenge": "otp",
            }, status=status.HTTP_202_ACCEPTED)

        # 🎉 Return access tokens/session info
        return Response({
            "token": session.token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.get_full_name(),
            }
        }, status=status.HTTP_200_OK)