"""
Magic Link Service - Passwordless authentication via secure email links.

Provides frictionless login experience while maintaining security through
time-limited, single-use tokens.
"""
import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.mail import send_mail
from typing import Dict, Any

from authentication.models import MagicLink
from authentication.services.auth_service import AuthenticationService
from authentication.utils.ip import get_client_ip


class MagicLinkService:
    """
    Service for passwordless authentication via magic links.
    
    Features:
    - Secure token generation
    - Time-limited links (15 minutes default)
    - Single-use tokens
    - IP address tracking
    - Automatic cleanup of expired tokens
    """
    
    TOKEN_LENGTH = 32
    DEFAULT_EXPIRY_MINUTES = 15
    
    @classmethod
    def generate_secure_token(cls):
        """Generate cryptographically secure token (UUID for MagicLink model)."""
        import uuid
        return uuid.uuid4()
    
    @classmethod
    def send_magic_link(cls, email: str, website, request, expiry_minutes: int = None) -> Dict[str, Any]:
        """
        Generate and send magic link for passwordless login.
        
        Args:
            email: User email address
            website: Website object
            request: HTTP request object
            expiry_minutes: Token expiry in minutes (default: 15)
        
        Returns:
            Dict with status and expiry information
        """
        if expiry_minutes is None:
            expiry_minutes = cls.DEFAULT_EXPIRY_MINUTES
        
        # Generate secure token
        token = cls.generate_secure_token()
        
        # Calculate expiry
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Get user by email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError("User not found with this email address.")
        
        # Store token (using existing MagicLink model)
        magic_token = MagicLink.objects.create(
            user=user,
            website=website,
            token=token,  # Will be stored as UUID
            expires_at=expires_at,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get('User-Agent', '')
        )
        
        # Generate magic link URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        magic_url = f"{frontend_url}/auth/magic-link?token={token}"
        
        # Send email
        cls._send_magic_link_email(email, magic_url, expiry_minutes)
        
        return {
            "message": "Magic link sent to your email",
            "expires_in": expiry_minutes * 60,  # seconds
            "expires_at": expires_at.isoformat(),
            "email_sent": True
        }
    
    @classmethod
    def verify_magic_link(cls, token: str, request) -> Dict[str, Any]:
        """
        Verify magic link and authenticate user.
        
        Args:
            token: Magic link token
            request: HTTP request object
        
        Returns:
            Dict with authentication tokens and user info
        
        Raises:
            ValidationError: If token is invalid or expired
        """
        try:
            magic_token = MagicLink.objects.get(
                token=token,
                expires_at__gt=timezone.now(),
                used_at__isnull=True
            )
        except MagicLink.DoesNotExist:
            raise ValidationError(
                "Invalid or expired magic link. Please request a new one."
            )
        
        # Check if already used
        if magic_token.used_at:
            raise ValidationError("This magic link has already been used.")
        
        # Mark as used
        magic_token.mark_used()
        
        # Get user from token
        user = magic_token.user
        
        # Check if account is active
        if not user.is_active:
            raise ValidationError("Account is disabled. Please contact support.")
        
        # Authenticate user (create session and tokens)
        # Note: We need to add login_with_user method or use existing login
        from authentication.services.auth_service import AuthenticationService
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Create session
        from authentication.services.login_session_service import LoginSessionService
        session = LoginSessionService.start_session(
            user=user,
            website=magic_token.website,
            ip=get_client_ip(request),
            user_agent=request.headers.get('User-Agent', ''),
            device_info={'type': 'magic_link'}
        )
        
        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            },
            "session_id": str(session.id)
        }
    
    @classmethod
    def _send_magic_link_email(cls, email: str, magic_url: str, expiry_minutes: int):
        """Send magic link email to user."""
        subject = "Your Magic Link Login"
        message = f"""
        Click the link below to log in to your account:
        
        {magic_url}
        
        This link will expire in {expiry_minutes} minutes and can only be used once.
        
        If you didn't request this link, please ignore this email.
        
        For security, never share this link with anyone.
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
    
    @classmethod
    def cleanup_expired_tokens(cls, days: int = 7):
        """Clean up expired and used tokens older than specified days."""
        cutoff = timezone.now() - timedelta(days=days)
        
        deleted_count = MagicLink.objects.filter(
            created_at__lt=cutoff
        ).delete()[0]
        
        return deleted_count
