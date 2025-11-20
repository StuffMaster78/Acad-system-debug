from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from authentication.serializers import (
    MagicLinkRequestSerializer,
    MagicLinkVerifySerializer,
)
from authentication.throttling import MagicLinkThrottle


class MagicLinkRequestViewSet(viewsets.ViewSet):
    """
    Public endpoint for requesting a magic login link.
    """
    permission_classes = [AllowAny]
    throttle_classes = [MagicLinkThrottle]

    def create(self, request, *args, **kwargs):
        serializer = MagicLinkRequestSerializer(
            data=request.data,
            context={
                "request": request,
                "website": request.website  # Assuming middleware sets this
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Magic link sent."},
            status=status.HTTP_200_OK
        )


class MagicLinkVerifyViewSet(viewsets.ViewSet):
    """
    Public endpoint for verifying a magic login link token.
    Returns JWT tokens for seamless login.
    """
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        from authentication.services.auth_service import AuthenticationService
        from authentication.services.login_session_service import LoginSessionService
        from authentication.utils.ip import get_client_ip
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.utils import timezone
        
        serializer = MagicLinkVerifySerializer(
            data=request.data,
            context={
                "request": request,
                "website": request.website
            }
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Check if account is active
        if not user.is_active:
            return Response(
                {"error": "Account is disabled. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get website
        website = request.website
        if not website:
            website = getattr(user, 'website', None)

        # Create login session
        ip_address = get_client_ip(request)
        user_agent = request.headers.get('User-Agent', '')
        
        session = LoginSessionService.start_session(
            user=user,
            website=website,
            ip=ip_address,
            user_agent=user_agent,
            device_info={'device_name': 'Magic Link Login'}
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                    "role": getattr(user, 'role', None),
                },
                "session_id": str(session.id),
                "expires_in": 3600,
                "message": f"Welcome back, {user.email}!"
            },
            status=status.HTTP_200_OK
        )
