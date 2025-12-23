"""
Service for managing user edit requests.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models.user_edit_requests import UserEditRequest
from users.models import User, UserProfile
from websites.models import Website
import logging

logger = logging.getLogger(__name__)


class UserEditService:
    """
    Service for managing user edit requests.
    """
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or getattr(user, 'website', None)
        if not self.website:
            self.website = Website.objects.filter(is_active=True).first()
    
    @staticmethod
    def get_fields_requiring_approval():
        """
        Get list of fields that require admin approval.
        """
        return [
            'email',
            'role',
            'website',
            'username',  # Username changes may need approval
            'is_active',  # Account activation/deactivation
        ]
    
    @staticmethod
    def get_auto_approve_fields():
        """
        Get list of fields that can be auto-approved.
        """
        return [
            'first_name',
            'last_name',
            'phone_number',
            'bio',
            'avatar',
            'profile_picture',
            'country',
            'state',
            'timezone',
        ]
    
    @transaction.atomic
    def create_edit_request(self, field_changes, request_type='profile_update', reason=''):
        """
        Create an edit request for fields requiring approval.
        
        Args:
            field_changes: Dict of {field_name: new_value}
            request_type: Type of request
            reason: User's reason for the change
            
        Returns:
            UserEditRequest instance
        """
        if not self.website:
            raise ValidationError("Website context is required for edit requests.")
        
        # Separate fields that need approval from auto-approve fields
        approval_fields = self.get_fields_requiring_approval()
        auto_approve_fields = self.get_auto_approve_fields()
        
        fields_requiring_approval = {}
        fields_for_auto_approve = {}
        
        # Build field changes with old and new values
        edit_request_changes = {}
        
        for field_name, new_value in field_changes.items():
            # Get current value
            old_value = self._get_current_field_value(field_name)
            
            if field_name in approval_fields:
                fields_requiring_approval[field_name] = new_value
                edit_request_changes[field_name] = {
                    'old_value': str(old_value) if old_value is not None else None,
                    'new_value': str(new_value) if new_value is not None else None
                }
            elif field_name in auto_approve_fields:
                fields_for_auto_approve[field_name] = new_value
            else:
                # Unknown field - require approval for safety
                fields_requiring_approval[field_name] = new_value
                edit_request_changes[field_name] = {
                    'old_value': str(old_value) if old_value is not None else None,
                    'new_value': str(new_value) if new_value is not None else None
                }
        
        # Apply auto-approve fields immediately
        if fields_for_auto_approve:
            self._apply_field_changes(fields_for_auto_approve)
        
        # Create edit request for fields requiring approval
        if fields_requiring_approval and edit_request_changes:
            edit_request = UserEditRequest.objects.create(
                user=self.user,
                website=self.website,
                request_type=request_type,
                field_changes=edit_request_changes,
                reason=reason,
                status='pending'
            )
            
            # Notify admins
            self._notify_admins(edit_request)
            
            return {
                'edit_request': edit_request,
                'auto_approved': fields_for_auto_approve,
                'pending_approval': fields_requiring_approval
            }
        
        return {
            'edit_request': None,
            'auto_approved': fields_for_auto_approve,
            'pending_approval': {}
        }
    
    def _get_current_field_value(self, field_name):
        """Get current value of a field from user or profile."""
        # Check User model first
        if hasattr(self.user, field_name):
            return getattr(self.user, field_name)
        
        # Check UserProfile
        try:
            profile = UserProfile.objects.get(user=self.user)
            if hasattr(profile, field_name):
                return getattr(profile, field_name)
        except UserProfile.DoesNotExist:
            pass
        
        return None
    
    def _apply_field_changes(self, field_changes):
        """Apply field changes to user or profile."""
        user_fields = []
        profile_fields = []
        
        # Separate User fields from UserProfile fields
        for field_name, value in field_changes.items():
            if hasattr(self.user, field_name):
                user_fields.append((field_name, value))
            else:
                profile_fields.append((field_name, value))
        
        # Update User fields
        for field_name, value in user_fields:
            setattr(self.user, field_name, value)
        if user_fields:
            self.user.save(update_fields=[f[0] for f in user_fields])
        
        # Update UserProfile fields
        if profile_fields:
            profile, _ = UserProfile.objects.get_or_create(user=self.user)
            for field_name, value in profile_fields:
                setattr(profile, field_name, value)
            profile.save(update_fields=[f[0] for f in profile_fields])
    
    def _notify_admins(self, edit_request):
        """Notify admins about new edit request."""
        try:
            from notifications_system.services.core import send_notification
            from users.models import User
            
            # Get all admins
            admins = User.objects.filter(role__in=['admin', 'superadmin'], is_active=True)
            
            for admin in admins:
                send_notification(
                    user=admin,
                    notification_type='user_edit_request',
                    title='New User Edit Request',
                    message=f"User {self.user.email} has requested profile changes: {edit_request.get_changes_summary()}",
                    priority='medium',
                    metadata={
                        'edit_request_id': edit_request.id,
                        'user_id': self.user.id,
                        'request_type': edit_request.request_type,
                    }
                )
        except Exception as e:
            logger.error(f"Error notifying admins about edit request {edit_request.id}: {e}", exc_info=True)
    
    @staticmethod
    @transaction.atomic
    def approve_request(edit_request, admin_user, notes=None):
        """
        Approve an edit request.
        
        Args:
            edit_request: UserEditRequest instance
            admin_user: Admin user approving
            notes: Optional admin notes
        """
        edit_request.approve(admin_user, notes)
    
    @staticmethod
    @transaction.atomic
    def reject_request(edit_request, admin_user, reason):
        """
        Reject an edit request.
        
        Args:
            edit_request: UserEditRequest instance
            admin_user: Admin user rejecting
            reason: Rejection reason
        """
        edit_request.reject(admin_user, reason)
    
    @staticmethod
    def get_user_edit_requests(user, status=None):
        """
        Get edit requests for a user.
        
        Args:
            user: User instance
            status: Optional status filter
        """
        queryset = UserEditRequest.objects.filter(user=user)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_pending_requests(website=None):
        """
        Get all pending edit requests (for admins).
        
        Args:
            website: Optional website filter
        """
        queryset = UserEditRequest.objects.filter(status='pending')
        if website:
            queryset = queryset.filter(website=website)
        return queryset.select_related('user', 'website', 'reviewed_by').order_by('-created_at')

