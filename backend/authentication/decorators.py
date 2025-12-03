"""
Authentication Decorators
Decorators for account takeover protection and email verification enforcement.
"""
import functools
import logging
from typing import Callable
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def require_email_verified(view_func: Callable = None, redirect_to_verification: bool = True):
    """
    Decorator to require email verification before accessing view.
    
    Usage:
        @require_email_verified
        def my_view(request):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check email verification
            # Assuming email_verified field exists on user or profile
            is_verified = getattr(user, 'email_verified', None)
            
            # If field doesn't exist, check EmailVerification model
            if is_verified is None:
                from authentication.models.activation import EmailVerification
                from websites.utils import get_current_website
                website = get_current_website(request)
                
                if website:
                    verification = EmailVerification.objects.filter(
                        user=user,
                        website=website,
                        is_verified=True
                    ).first()
                    is_verified = verification is not None
                else:
                    is_verified = True  # Default to True if no website context
            
            if not is_verified:
                if redirect_to_verification:
                    return Response(
                        {
                            "error": "Email verification required",
                            "requires_email_verification": True,
                            "message": "Please verify your email address to access this feature."
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                else:
                    raise PermissionDenied("Email verification required")
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator


def require_additional_verification(
    methods: list = None,
    require_password: bool = True,
    require_2fa: bool = False
):
    """
    Decorator to require additional verification for sensitive operations.
    
    Args:
        methods: List of HTTP methods to protect (default: ['POST', 'PUT', 'PATCH', 'DELETE'])
        require_password: Whether to require current password
        require_2fa: Whether to require 2FA (for high-risk users)
    
    Usage:
        @require_additional_verification(require_password=True, require_2fa=True)
        def change_email(request):
            ...
    """
    if methods is None:
        methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return func(request, *args, **kwargs)
            
            user = request.user
            
            if not user.is_authenticated:
                return Response(
                    {"error": "Authentication required"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check password verification
            if require_password:
                password = request.data.get('current_password') or request.data.get('password')
                if not password:
                    return Response(
                        {
                            "error": "Current password required",
                            "requires_password": True
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if not user.check_password(password):
                    return Response(
                        {"error": "Invalid password"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check 2FA for high-risk users
            if require_2fa:
                # Check if user is high-risk (e.g., recent suspicious activity)
                is_high_risk = _is_high_risk_user(user, request)
                
                if is_high_risk:
                    totp_code = request.data.get('totp_code') or request.data.get('2fa_code')
                    if not totp_code:
                        return Response(
                            {
                                "error": "2FA verification required",
                                "requires_2fa": True
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Verify 2FA
                    if not _verify_2fa(user, totp_code):
                        return Response(
                            {"error": "Invalid 2FA code"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def _is_high_risk_user(user, request) -> bool:
    """Check if user is considered high-risk."""
    from authentication.models.security_events import SecurityEvent
    from django.utils import timezone
    from datetime import timedelta
    
    # Check for recent suspicious activity
    recent_suspicious = SecurityEvent.objects.filter(
        user=user,
        is_suspicious=True,
        timestamp__gte=timezone.now() - timedelta(days=30)
    ).exists()
    
    # Check for recent password reset
    from authentication.models.password_reset import PasswordResetRequest
    recent_reset = PasswordResetRequest.objects.filter(
        user=user,
        is_used=True,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).exists()
    
    # Check for login from new location
    from authentication.models.login import LoginSession
    from websites.utils import get_current_website
    website = get_current_website(request)
    
    if website:
        recent_sessions = LoginSession.objects.filter(
            user=user,
            website=website,
            logged_in_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # If multiple recent logins, might be suspicious
        if recent_sessions > 5:
            return True
    
    return recent_suspicious or recent_reset


def _verify_2fa(user, totp_code: str) -> bool:
    """Verify 2FA code."""
    if not hasattr(user, 'mfa_secret') or not user.mfa_secret:
        return False
    
    try:
        import pyotp
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(totp_code, valid_window=1)
    except Exception as e:
        logger.error(f"Error verifying 2FA: {e}")
        return False


def require_password_not_expired(view_func: Callable = None):
    """
    Decorator to require password change if expired.
    
    Usage:
        @require_password_not_expired
        def my_view(request):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            if not user.is_authenticated:
                return func(request, *args, **kwargs)
            
            from authentication.services.password_expiration_service import PasswordExpirationService
            expiration_service = PasswordExpirationService(user)
            
            if expiration_service.require_password_change():
                status_info = expiration_service.check_expiration_status()
                return Response(
                    {
                        "error": "Password expired",
                        "requires_password_change": True,
                        "expiration_info": status_info,
                        "message": "Your password has expired. Please change it to continue."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return func(request, *args, **kwargs)
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator

