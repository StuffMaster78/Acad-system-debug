from rest_framework import viewsets, permissions
from authentication.models.login import LoginSession
from authentication.serializers import LoginSessionSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django.conf import settings

from django.contrib.auth import authenticate
from django.utils.timezone import now

from authentication.serializers import LoginSerializer
from authentication.services.failed_login_attempts import FailedLoginService
from authentication.utils.ip import get_client_ip
from authentication.models.sessions import UserSession
from authentication.services.login_session_service import LoginSessionService
from authentication.services.login_service import LoginService

user = settings.AUTH_USER_MODEL

class LoginSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API viewset for listing and retrieving user login sessions.
    """
    serializer_class = LoginSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    # After successful auth, before token issuance
    if not user.mfa_enabled:
        return Response({
            "error": "2FA required",
            "setup_required": True,
            "totp_url": LoginService.generate_provisioning_uri(user)
        }, status=403)
    def get_queryset(self):
        """
        Returns sessions only for the authenticated user and website.
        """
        return LoginSession.objects.filter(
            user=self.request.user,
            website=self.request.website  # website set via middleware/context
        )
    
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
            # Log failed attempt
            FailedLoginService.log(user=None, website=website, ip=ip, user_agent=user_agent)
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
        if user.profile.is_2fa_enabled:
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