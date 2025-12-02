"""
Unified authentication service for production-grade login/logout/impersonation.
Provides consistent, secure, and scalable authentication operations.
"""
import logging
from typing import Optional, Dict, Any
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from authentication.services.failed_login_attempts import FailedLoginService
from authentication.services.login_session_service import LoginSessionService
from authentication.utils.ip import get_client_ip
from authentication.models import FailedLoginAttempt
from websites.utils import get_current_website

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthenticationService:
    """
    Production-grade authentication service.
    Handles login, logout, session management, and security features.
    """
    
    @staticmethod
    @transaction.atomic
    def login(
        request,
        email: str,
        password: str,
        remember_me: bool = False,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user and create session.
        
        Args:
            request: HTTP request object
            email: User email
            password: User password
            remember_me: Whether to extend session duration
            device_info: Optional device information dict
        
        Returns:
            Dict with tokens, user info, and session details
        
        Raises:
            ValidationError: For invalid credentials or locked account
        """
        website = get_current_website(request)
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        
        # Authenticate user
        user = authenticate(request=request, username=email, password=password)
        
        if not user:
            # Try to find user by email to log failed attempt (even if password is wrong)
            failed_attempts_remaining = None
            try:
                user_for_logging = User.objects.get(email=email)
                # Log failed attempt only if user exists and website exists
                if user_for_logging and website:
                    FailedLoginService.log(
                        user=user_for_logging,
                        website=website,
                        ip=ip_address,
                        user_agent=user_agent
                    )
                    
                    # Log security event for failed login
                    from authentication.models.security_events import SecurityEvent
                    try:
                        SecurityEvent.log_event(
                            user=user_for_logging,
                            website=website,
                            event_type='login_failed',
                            severity='medium',
                            is_suspicious=False,
                            ip_address=ip_address,
                            user_agent=user_agent,
                            metadata={'email_attempted': email}
                        )
                    except Exception as e:
                        logger.warning(f"Failed to log security event: {e}")
                    
                    # Get attempts remaining for user-friendly error
                    from authentication.services.smart_lockout_service import SmartLockoutService
                    smart_lockout = SmartLockoutService(user=user_for_logging, website=website)
                    lockout_info = smart_lockout.get_lockout_info(ip_address, False)
                    failed_attempts_remaining = lockout_info.get('attempts_remaining', 5)
            except User.DoesNotExist:
                # User doesn't exist, skip logging failed attempt
                pass
            
            # User-friendly error message
            if failed_attempts_remaining is not None and failed_attempts_remaining > 0:
                error_msg = f"The email or password you entered is incorrect. {failed_attempts_remaining} attempts remaining before your account is temporarily locked."
                guidance = "Forgot your password? Click here to reset it."
            else:
                error_msg = "The email or password you entered is incorrect."
                guidance = "Please check your credentials and try again."
            
            raise ValidationError({
                "error": "Invalid credentials",
                "message": error_msg,
                "guidance": guidance,
                "attempts_remaining": failed_attempts_remaining
            })
        
        # Check if account is active
        if not user.is_active:
            raise ValidationError("Account is disabled. Please contact support.")
        
        # Ensure website exists - use user's website or get first active website
        if not website:
            website = getattr(user, 'website', None)
        if not website:
            from websites.models import Website
            website = Website.objects.filter(is_active=True).first()
        
        if not website:
            raise ValidationError(
                "No active website found. Please contact support to set up your account."
            )
        
        # Check for account lockout using Smart Lockout Service
        from authentication.services.smart_lockout_service import SmartLockoutService
        from authentication.models.devices import TrustedDevice
        
        # Check if device is trusted
        device_fingerprint = request.data.get('device_fingerprint') or request.headers.get('X-Device-Fingerprint')
        is_trusted_device = False
        if device_fingerprint:
            is_trusted_device = TrustedDevice.objects.filter(
                user=user,
                website=website,
                device_token=device_fingerprint,
                expires_at__gt=timezone.now()
            ).exists()
        
        smart_lockout = SmartLockoutService(user=user, website=website)
        should_lock, lockout_reason = smart_lockout.should_lockout(ip_address, is_trusted_device)
        
        if should_lock:
            lockout_info = smart_lockout.get_lockout_info(ip_address, is_trusted_device)
            raise ValidationError({
                "error": "Account temporarily locked",
                "message": lockout_reason,
                "lockout_until": lockout_info.get('lockout_until'),
                "lockout_duration_minutes": lockout_info.get('lockout_duration_minutes'),
                "unlock_options": lockout_info.get('unlock_options'),
                "guidance": "You can request an unlock via email or wait for the lockout period to expire."
            })
        
        # Check for impersonation (prevent impersonating while impersonating)
        if hasattr(request, 'session') and request.session.get('_impersonator_id'):
            raise PermissionDenied(
                "Cannot login while impersonating another user. "
                "End impersonation first."
            )
        
        # Ensure user profile exists
        if not hasattr(user, 'user_main_profile') or user.user_main_profile is None:
            from users.models import UserProfile
            UserProfile.objects.get_or_create(user=user, defaults={'avatar': 'avatars/universal.png'})
        
        # Create login session (website is now guaranteed to exist)
        session = LoginSessionService.start_session(
            user=user,
            website=website,
            ip=ip_address,
            user_agent=user_agent,
            device_info=device_info
        )
        
        # Check for 2FA requirement
        # Try both methods of checking 2FA
        is_2fa_enabled = False
        if hasattr(user, 'user_main_profile') and user.user_main_profile:
            is_2fa_enabled = getattr(user.user_main_profile, 'is_2fa_enabled', False)
        if not is_2fa_enabled:
            is_2fa_enabled = getattr(user, 'is_mfa_enabled', False)
        
        if is_2fa_enabled:
            return {
                "requires_2fa": True,
                "session_id": str(session.id),
                "message": "2FA verification required."
            }
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Set session expiry based on remember_me
        if remember_me and hasattr(request, 'session'):
            request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
        elif hasattr(request, 'session'):
            request.session.set_expiry(60 * 60 * 24)  # 24 hours
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Log security event
        from authentication.models.security_events import SecurityEvent
        try:
            SecurityEvent.log_event(
                user=user,
                website=website,
                event_type='login',
                severity='low',
                is_suspicious=False,
                ip_address=ip_address,
                user_agent=user_agent,
                device=device_info.get('device_name') if device_info else None,
                metadata={'remember_me': remember_me}
            )
        except Exception as e:
            logger.warning(f"Failed to log security event: {e}")
        
        # Clear failed login attempts on successful login
        try:
            FailedLoginService(user=user, website=website).clear_attempts()
        except Exception as e:
            logger.warning(f"Failed to clear failed attempts: {e}")
        
        return {
            "access": access_token,
            "refresh": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.get_full_name(),
                "role": getattr(user, 'role', None),
            },
            "session_id": str(session.id),
            "expires_in": 3600 if not remember_me else 60 * 60 * 24 * 30
        }
    
    @staticmethod
    def verify_2fa(user, session_id: str, totp_code: str) -> Dict[str, Any]:
        """
        Verify 2FA code and complete login.
        
        Args:
            user: User instance
            session_id: Login session ID
            totp_code: TOTP verification code
        
        Returns:
            Dict with tokens and user info
        
        Raises:
            ValidationError: If 2FA code is invalid
        """
        if not hasattr(user, 'mfa_secret') or not user.mfa_secret:
            raise ValidationError("2FA is not enabled for this account.")
        
        # Verify TOTP code
        import pyotp
        totp = pyotp.TOTP(user.mfa_secret)
        
        if not totp.verify(totp_code, valid_window=1):
            raise ValidationError("Invalid 2FA code.")
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.get_full_name(),
                "role": getattr(user, 'role', None),
            },
        }
    
    @staticmethod
    @transaction.atomic
    def logout(request, user, logout_all: bool = False) -> Dict[str, Any]:
        """
        Logout user and invalidate session/tokens.
        
        Args:
            request: HTTP request object
            user: User instance
            logout_all: If True, logout from all devices
        
        Returns:
            Dict with logout confirmation
        """
        website = get_current_website(request)
        
        # End impersonation if active
        if hasattr(request, 'session') and request.session.get('_impersonator_id'):
            try:
                from authentication.services.impersonation_service import ImpersonationService
                service = ImpersonationService(request, website)
                service.end_impersonation()
                logger.info(f"Ended impersonation during logout for admin {user.id}")
            except Exception as e:
                logger.warning(f"Failed to end impersonation during logout: {e}")
        
        # Revoke login sessions
        if logout_all:
            LoginSessionService.revoke_all_sessions(user=user, website=website)
            message = "Logged out from all devices."
        else:
            session_id = getattr(request, 'session_id', None)
            LoginSessionService.revoke_session(user=user, session_id=session_id, website=website)
            message = "Logged out successfully."
        
        # Clear session
        if hasattr(request, 'session'):
            request.session.flush()
        
        # Log logout event
        try:
            from authentication.services.logout_event_service import LogoutEventService
            LogoutEventService.log_event(
                user=user,
                website=website,
                ip_address=get_client_ip(request),
                user_agent=request.headers.get('User-Agent', ''),
                reason="user_initiated"
            )
        except Exception as e:
            logger.warning(f"Failed to log logout event: {e}")
        
        return {
            "success": True,
            "message": message
        }
    
    @staticmethod
    def refresh_token(refresh_token_str: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token_str: Refresh token string
        
        Returns:
            Dict with new access token
        
        Raises:
            ValidationError: If refresh token is invalid
        """
        try:
            refresh = RefreshToken(refresh_token_str)
            access_token = str(refresh.access_token)
            
            return {
                "access_token": access_token,
                "expires_in": 3600,
            }
        except TokenError as e:
            raise ValidationError("Invalid or expired refresh token.")
    
    @staticmethod
    def validate_user_access(user, website) -> bool:
        """
        Validate that user has access to the website/tenant.
        
        Args:
            user: User instance
            website: Website instance
        
        Returns:
            bool: True if user has access
        """
        # Superadmins have access to all websites
        if hasattr(user, 'role') and user.role == 'superadmin':
            return True
        
        # Check if user belongs to this website
        if hasattr(user, 'website') and user.website == website:
            return True
        
        # Additional tenant access checks can be added here
        return False

