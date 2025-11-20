"""
Production-grade impersonation service with proper security, audit logging,
and JWT token support.
"""
import logging
from typing import Optional, Dict, Any, Tuple
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from authentication.models.impersonation import (
    ImpersonationToken, ImpersonationLog
)
from websites.utils import get_current_website

logger = logging.getLogger(__name__)
User = get_user_model()


class ImpersonationService:
    """
    Production-grade impersonation service.
    
    Features:
    - Token-based impersonation for security
    - JWT token support for stateless authentication
    - Comprehensive permission checks
    - Audit logging
    - Session and token management
    """
    
    def __init__(self, request, website=None):
        """
        Initialize the impersonation service.
        
        Args:
            request: HTTP request object
            website: Website instance (optional, will be fetched if not provided)
        """
        self.request = request
        self.website = website or get_current_website(request)
        self.admin_user = request.user if request.user.is_authenticated else None
        
        if not self.website:
            raise ValueError("Website context is required for impersonation.")
    
    @staticmethod
    def can_impersonate(admin_user, target_user) -> Tuple[bool, str]:
        """
        Check if admin can impersonate target user.
        
        Args:
            admin_user: Admin user attempting impersonation
            target_user: Target user to impersonate
        
        Returns:
            Tuple of (can_impersonate: bool, reason: str)
        """
        if not admin_user or not admin_user.is_authenticated:
            return False, "Admin user must be authenticated."
        
        if not admin_user.is_staff:
            return False, "Only staff members can impersonate users."
        
        # Superadmins can impersonate anyone
        if hasattr(admin_user, 'role') and admin_user.role == 'superadmin':
            return True, ""
        
        # Admins can only impersonate clients and writers (not other admins/superadmins)
        if hasattr(admin_user, 'role') and admin_user.role == 'admin':
            target_role = getattr(target_user, 'role', None)
            if target_role in ['client', 'writer']:
                return True, ""
            else:
                return False, "Admins can only impersonate clients and writers."
        
        return False, "Insufficient permissions for impersonation."
    
    @staticmethod
    @transaction.atomic
    def generate_token(admin_user, target_user, website, expires_hours: int = 1) -> ImpersonationToken:
        """
        Generate an impersonation token.
        
        Args:
            admin_user: Admin user creating the token
            target_user: Target user to impersonate
            website: Website context
            expires_hours: Token expiration in hours (default: 1)
        
        Returns:
            ImpersonationToken instance
        
        Raises:
            PermissionDenied: If admin cannot impersonate target
            ValidationError: If validation fails
        """
        # Check permissions
        can_impersonate, reason = ImpersonationService.can_impersonate(admin_user, target_user)
        if not can_impersonate:
            raise PermissionDenied(reason)
        
        # Prevent impersonating yourself
        if admin_user.id == target_user.id:
            raise ValidationError("Cannot impersonate yourself.")
        
        # Prevent impersonating inactive users
        if not target_user.is_active:
            raise ValidationError("Cannot impersonate inactive users.")
        
        # Generate token
        token = ImpersonationToken.generate_token(
            admin_user=admin_user,
            target_user=target_user,
            website=website,
            expires_hours=expires_hours
        )
        
        logger.info(
            f"Admin {admin_user.id} generated impersonation token for user {target_user.id} "
            f"on website {website.id}"
        )
        
        return token
    
    @transaction.atomic
    def impersonate_user(self, token_str: str) -> Dict[str, Any]:
        """
        Impersonate a user using a valid impersonation token.
        Returns new JWT tokens for the target user.
        
        Args:
            token_str: Impersonation token string
        
        Returns:
            Dict with new JWT tokens and user info
        
        Raises:
            PermissionDenied: If token is invalid, expired, or unauthorized
        """
        # Get token
        try:
            token = ImpersonationToken.objects.select_related(
                'admin_user', 'target_user', 'website'
            ).get(token=token_str, website=self.website)
        except ImpersonationToken.DoesNotExist:
            raise PermissionDenied("Invalid impersonation token.")
        
        # Validate token
        if token.is_expired():
            raise PermissionDenied("Impersonation token has expired.")
        
        # Verify admin user matches
        if not self.admin_user or token.admin_user.id != self.admin_user.id:
            raise PermissionDenied("You are not authorized to use this token.")
        
        # Check if admin can still impersonate (role might have changed)
        can_impersonate, reason = self.can_impersonate(self.admin_user, token.target_user)
        if not can_impersonate:
            raise PermissionDenied(reason)
        
        # Store impersonator info in session (for JWT, this is also in token claims)
        if hasattr(self.request, 'session'):
            self.request.session['_impersonator_id'] = self.admin_user.id
            self.request.session['_impersonator_email'] = self.admin_user.email
            self.request.session['_impersonator_role'] = getattr(self.admin_user, 'role', None)
            self.request.session['_impersonation_started_at'] = timezone.now().isoformat()
            self.request.session.save()
        
        # Create audit log
        ImpersonationLog.objects.create(
            admin_user=self.admin_user,
            target_user=token.target_user,
            token=token,
            website=self.website
        )
        
        # Generate new JWT tokens for target user
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(token.target_user)
        
        # Add impersonation claims to token
        refresh['impersonated_by'] = self.admin_user.id
        refresh['is_impersonation'] = True
        
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        logger.info(
            f"Admin {self.admin_user.id} started impersonating user {token.target_user.id} "
            f"on website {self.website.id}"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": token.target_user.id,
                "email": token.target_user.email,
                "username": token.target_user.username,
                "full_name": token.target_user.get_full_name(),
                "role": getattr(token.target_user, 'role', None),
            },
            "impersonation": {
                "impersonated_by": {
                    "id": self.admin_user.id,
                    "email": self.admin_user.email,
                    "full_name": self.admin_user.get_full_name(),
                },
                "started_at": timezone.now().isoformat(),
            },
            "expires_in": 3600,
        }
    
    @transaction.atomic
    def end_impersonation(self) -> Dict[str, Any]:
        """
        End an active impersonation session and restore the original admin.
        Returns new JWT tokens for the admin user.
        
        Returns:
            Dict with new JWT tokens for admin and confirmation
        
        Raises:
            PermissionDenied: If no impersonation is in progress
        """
        # Get impersonator ID from session or token
        impersonator_id = None
        
        if hasattr(self.request, 'session'):
            impersonator_id = self.request.session.get('_impersonator_id')
        
        # Also check JWT token claims if session doesn't have it
        if not impersonator_id and hasattr(self.request, 'auth'):
            try:
                impersonator_id = self.request.auth.get('impersonated_by')
            except (AttributeError, TypeError):
                pass
        
        if not impersonator_id:
            raise PermissionDenied("No impersonation session found.")
        
        # Get original admin user
        try:
            original_admin = User.objects.get(pk=impersonator_id)
        except User.DoesNotExist:
            raise PermissionDenied("Original admin user not found.")
        
        # Get current user (the impersonated user)
        current_user = self.request.user if self.request.user.is_authenticated else None
        if not current_user:
            raise PermissionDenied("No authenticated user found.")
        
        # Create audit log for ending impersonation
        ImpersonationLog.objects.create(
            admin_user=original_admin,
            target_user=current_user,
            website=self.website,
            token=None  # No token for ending impersonation
        )
        
        # Clear impersonation session data
        if hasattr(self.request, 'session'):
            self.request.session.pop('_impersonator_id', None)
            self.request.session.pop('_impersonator_email', None)
            self.request.session.pop('_impersonator_role', None)
            self.request.session.pop('_impersonation_started_at', None)
            self.request.session.save()
        
        # Generate new JWT tokens for original admin
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(original_admin)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        logger.info(
            f"Admin {original_admin.id} ended impersonation of user {current_user.id} "
            f"on website {self.website.id}"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": original_admin.id,
                "email": original_admin.email,
                "username": original_admin.username,
                "full_name": original_admin.get_full_name(),
                "role": getattr(original_admin, 'role', None),
            },
            "message": "Impersonation ended. You are now logged in as yourself.",
        }
    
    def is_impersonating(self) -> bool:
        """
        Check if current session is impersonating another user.
        
        Returns:
            bool: True if impersonation is active
        """
        if hasattr(self.request, 'session'):
            return bool(self.request.session.get('_impersonator_id'))
        
        # Also check JWT token
        if hasattr(self.request, 'auth'):
            try:
                return self.request.auth.get('is_impersonation', False)
            except (AttributeError, TypeError):
                pass
        
        return False
    
    def get_impersonator_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the admin who is impersonating.
        
        Returns:
            Dict with impersonator info or None
        """
        if not self.is_impersonating():
            return None
        
        impersonator_id = None
        if hasattr(self.request, 'session'):
            impersonator_id = self.request.session.get('_impersonator_id')
        
        if not impersonator_id and hasattr(self.request, 'auth'):
            try:
                impersonator_id = self.request.auth.get('impersonated_by')
            except (AttributeError, TypeError):
                pass
        
        if not impersonator_id:
            return None
        
        try:
            admin_user = User.objects.get(pk=impersonator_id)
            return {
                "id": admin_user.id,
                "email": admin_user.email,
                "full_name": admin_user.get_full_name(),
                "role": getattr(admin_user, 'role', None),
            }
        except User.DoesNotExist:
            return None
