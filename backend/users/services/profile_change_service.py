"""
Profile Change Service
Manages profile change requests for writers (requires admin approval).
"""
import logging
from typing import Optional
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models.profile_changes import ProfileChangeRequest, WriterAvatarUpload
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class ProfileChangeService:
    """
    Service for managing profile change requests.
    """
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def request_profile_change(
        self,
        change_type: str,
        requested_value: str,
        current_value: str = None
    ) -> ProfileChangeRequest:
        """
        Request a profile change (for writers, requires admin approval).
        
        Args:
            change_type: Type of change (bio, avatar, pen_name, other)
            requested_value: New value requested
            current_value: Current value (optional)
        
        Returns:
            Created ProfileChangeRequest instance
        """
        if not self.website:
            raise ValueError("Website context required")
        
        # Only writers need approval for profile changes
        if self.user.role not in ['writer']:
            raise ValidationError("Only writers need approval for profile changes")
        
        # Get current value if not provided
        if not current_value:
            current_value = self._get_current_value(change_type)
        
        # Create request
        request = ProfileChangeRequest.objects.create(
            user=self.user,
            website=self.website,
            change_type=change_type,
            current_value=current_value or '',
            requested_value=requested_value,
            status='pending'
        )
        
        # Notify admins
        self._notify_admins(request)
        
        return request
    
    def _get_current_value(self, change_type: str) -> str:
        """Get current value for the change type."""
        if change_type == 'bio':
            profile = getattr(self.user, 'user_main_profile', None)
            return getattr(profile, 'bio', '') if profile else ''
        elif change_type == 'pen_name':
            from users.models.privacy_settings import PenName
            pen_name = PenName.objects.filter(
                user=self.user,
                website=self.website,
                is_active=True
            ).first()
            return pen_name.pen_name if pen_name else ''
        elif change_type == 'avatar':
            profile = getattr(self.user, 'user_main_profile', None)
            return str(profile.profile_picture.url) if profile and profile.profile_picture else ''
        return ''
    
    def _notify_admins(self, request: ProfileChangeRequest):
        """Notify admins of profile change request."""
        from users.models import User
        from django.core.mail import send_mail
        from django.conf import settings
        
        admins = User.objects.filter(
            role__in=['admin', 'superadmin'],
            is_active=True
        )
        
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if admin_emails:
            admin_url = f"{settings.FRONTEND_URL}/admin/profile-changes/{request.id}/"
            send_mail(
                subject=f"Profile Change Request - {self.user.email}",
                message=f"""
                A writer has requested a profile change.
                
                Writer: {self.user.email} (ID: {self.user.id})
                Change Type: {request.get_change_type_display()}
                Current Value: {request.current_value[:100]}...
                Requested Value: {request.requested_value[:100]}...
                
                Please review and approve/reject:
                {admin_url}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
    
    def approve_change(self, admin_user, request_id: int, rejection_reason: str = None) -> bool:
        """
        Admin approves or rejects profile change.
        
        Args:
            admin_user: Admin user
            request_id: Request ID
            rejection_reason: Reason for rejection
        
        Returns:
            True if approved, False if rejected
        """
        if admin_user.role not in ['admin', 'superadmin']:
            raise ValidationError("Only admins can approve profile changes")
        
        try:
            request = ProfileChangeRequest.objects.get(
                id=request_id,
                website=self.website,
                status='pending'
            )
        except ProfileChangeRequest.DoesNotExist:
            raise ValidationError("Profile change request not found")
        
        if rejection_reason:
            request.status = 'rejected'
            request.rejection_reason = rejection_reason
            request.approved_by = admin_user
            request.approved_at = timezone.now()
            request.save()
            
            # Notify user
            self._notify_user(request, approved=False)
            return False
        else:
            # Apply the change
            self._apply_change(request)
            
            request.status = 'approved'
            request.approved_by = admin_user
            request.approved_at = timezone.now()
            request.completed_at = timezone.now()
            request.save()
            
            # Notify user
            self._notify_user(request, approved=True)
            return True
    
    def _apply_change(self, request: ProfileChangeRequest):
        """Apply the approved profile change."""
        if request.change_type == 'bio':
            profile = getattr(request.user, 'user_main_profile', None)
            if profile:
                profile.bio = request.requested_value
                profile.save(update_fields=['bio'])
                
                # Update privacy settings
                from users.models.privacy_settings import WriterPrivacySettings
                privacy, _ = WriterPrivacySettings.objects.get_or_create(
                    user=request.user,
                    website=self.website
                )
                privacy.bio_approved = True
                privacy.bio_approved_by = request.approved_by
                privacy.bio_approved_at = timezone.now()
                privacy.save()
        
        elif request.change_type == 'pen_name':
            from users.models.privacy_settings import PenName
            # Deactivate old pen name
            PenName.objects.filter(
                user=request.user,
                website=self.website,
                is_active=True
            ).update(is_active=False)
            
            # Create new pen name
            pen_name, created = PenName.objects.get_or_create(
                user=request.user,
                website=self.website,
                pen_name=request.requested_value,
                defaults={
                    'is_active': True,
                    'is_approved': True,
                    'approved_by': request.approved_by,
                    'approved_at': timezone.now()
                }
            )
            if not created:
                pen_name.is_active = True
                pen_name.is_approved = True
                pen_name.approved_by = request.approved_by
                pen_name.approved_at = timezone.now()
                pen_name.save()
    
    def _notify_user(self, request: ProfileChangeRequest, approved: bool):
        """Notify user of approval/rejection."""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "Profile Change Request Approved" if approved else "Profile Change Request Rejected"
        message = f"""
        Your profile change request has been {'approved' if approved else 'rejected'}.
        
        Change Type: {request.get_change_type_display()}
        """
        
        if not approved:
            message += f"\nReason: {request.rejection_reason}"
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )


class WriterAvatarService:
    """
    Service for managing writer avatar uploads (requires admin approval).
    """
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def upload_avatar(self, avatar_file) -> WriterAvatarUpload:
        """
        Upload avatar for approval.
        
        Args:
            avatar_file: Uploaded image file
        
        Returns:
            Created WriterAvatarUpload instance
        """
        if not self.website:
            raise ValueError("Website context required")
        
        if self.user.role != 'writer':
            raise ValidationError("Only writers can upload avatars")
        
        # Create upload record
        upload = WriterAvatarUpload.objects.create(
            user=self.user,
            website=self.website,
            avatar_file=avatar_file,
            status='pending'
        )
        
        # Notify admins
        self._notify_admins(upload)
        
        return upload
    
    def _notify_admins(self, upload: WriterAvatarUpload):
        """Notify admins of avatar upload."""
        from users.models import User
        from django.core.mail import send_mail
        from django.conf import settings
        
        admins = User.objects.filter(
            role__in=['admin', 'superadmin'],
            is_active=True
        )
        
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if admin_emails:
            admin_url = f"{settings.FRONTEND_URL}/admin/avatar-uploads/{upload.id}/"
            send_mail(
                subject=f"Avatar Upload Request - {self.user.email}",
                message=f"""
                A writer has uploaded a new avatar.
                
                Writer: {self.user.email} (ID: {self.user.id})
                
                Please review and approve/reject:
                {admin_url}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
    
    def approve_avatar(self, admin_user, upload_id: int, rejection_reason: str = None) -> bool:
        """
        Admin approves or rejects avatar.
        
        Args:
            admin_user: Admin user
            upload_id: Upload ID
            rejection_reason: Reason for rejection
        
        Returns:
            True if approved, False if rejected
        """
        if admin_user.role not in ['admin', 'superadmin']:
            raise ValidationError("Only admins can approve avatars")
        
        try:
            upload = WriterAvatarUpload.objects.get(
                id=upload_id,
                website=self.website,
                status='pending'
            )
        except WriterAvatarUpload.DoesNotExist:
            raise ValidationError("Avatar upload not found")
        
        if rejection_reason:
            upload.status = 'rejected'
            upload.rejection_reason = rejection_reason
            upload.approved_by = admin_user
            upload.approved_at = timezone.now()
            upload.save()
            return False
        else:
            # Apply avatar to user profile
            profile = getattr(upload.user, 'user_main_profile', None)
            if profile:
                profile.profile_picture = upload.avatar_file
                profile.save(update_fields=['profile_picture'])
            
            upload.status = 'approved'
            upload.approved_by = admin_user
            upload.approved_at = timezone.now()
            upload.save()
            return True

