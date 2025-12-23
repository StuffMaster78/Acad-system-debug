"""
Unified User Edit Request Model
Handles all user edit requests that require admin approval.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class UserEditRequest(models.Model):
    """
    Unified model for user edit requests that require admin approval.
    Replaces and extends ProfileUpdateRequest and ProfileChangeRequest.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled by User'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('profile_update', 'Profile Update'),
        ('email_change', 'Email Change'),
        ('role_change', 'Role Change'),
        ('website_change', 'Website Change'),
        ('username_change', 'Username Change'),
        ('name_change', 'Name Change'),
        ('phone_change', 'Phone Number Change'),
        ('bio_change', 'Bio Change'),
        ('avatar_change', 'Avatar Change'),
        ('pen_name_change', 'Pen Name Change (Writers)'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='edit_requests',
        help_text=_("User requesting the edit")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='user_edit_requests',
        help_text=_("Website context")
    )
    request_type = models.CharField(
        max_length=50,
        choices=REQUEST_TYPE_CHOICES,
        help_text=_("Type of edit request")
    )
    
    # Store field changes as JSON
    # Format: {"field_name": {"old_value": "...", "new_value": "..."}}
    field_changes = models.JSONField(
        help_text=_("Dictionary of field changes: {field: {old: value, new: value}}")
    )
    
    # Request details
    reason = models.TextField(
        blank=True,
        help_text=_("User's reason for the change request")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Current status of the request")
    )
    
    # Admin handling
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_edit_requests',
        limit_choices_to={'role__in': ['admin', 'superadmin']},
        help_text=_("Admin who reviewed the request")
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the request was reviewed")
    )
    admin_notes = models.TextField(
        blank=True,
        help_text=_("Admin's notes or rejection reason")
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the request was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When the request was last updated")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the request was completed (approved/rejected)")
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
            models.Index(fields=['website', 'status']),
            models.Index(fields=['request_type', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name = _("User Edit Request")
        verbose_name_plural = _("User Edit Requests")
    
    def __str__(self):
        return f"Edit request for {self.user.email} - {self.get_request_type_display()} ({self.status})"
    
    def approve(self, admin_user, notes=None):
        """
        Approve the edit request and apply changes.
        
        Args:
            admin_user: Admin user approving the request
            notes: Optional admin notes
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Apply field changes
            for field_name, change_data in self.field_changes.items():
                if hasattr(self.user, field_name):
                    setattr(self.user, field_name, change_data.get('new_value'))
                else:
                    # Try UserProfile
                    from users.models import UserProfile
                    profile, _ = UserProfile.objects.get_or_create(user=self.user)
                    if hasattr(profile, field_name):
                        setattr(profile, field_name, change_data.get('new_value'))
                        profile.save()
            
            self.user.save()
            
            # Update request status
            self.status = 'approved'
            self.reviewed_by = admin_user
            self.reviewed_at = timezone.now()
            self.completed_at = timezone.now()
            if notes:
                self.admin_notes = notes
            self.save()
            
            # Log the approval
            from users.models import UserAuditLog
            UserAuditLog.objects.create(
                user=self.user,
                action='profile_edit_approved',
                details=f"Edit request {self.id} approved by {admin_user.email}. Changes: {self.field_changes}",
                ip_address=None,
                user_agent=None
            )
    
    def reject(self, admin_user, reason):
        """
        Reject the edit request.
        
        Args:
            admin_user: Admin user rejecting the request
            reason: Reason for rejection
        """
        self.status = 'rejected'
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.completed_at = timezone.now()
        self.admin_notes = reason
        self.save()
        
        # Log the rejection
        from users.models import UserAuditLog
        UserAuditLog.objects.create(
            user=self.user,
            action='profile_edit_rejected',
            details=f"Edit request {self.id} rejected by {admin_user.email}. Reason: {reason}",
            ip_address=None,
            user_agent=None
        )
    
    def cancel(self):
        """Cancel the request (by user)."""
        if self.status == 'pending':
            self.status = 'cancelled'
            self.completed_at = timezone.now()
            self.save()
    
    def get_changes_summary(self):
        """Get a human-readable summary of changes."""
        changes = []
        for field_name, change_data in self.field_changes.items():
            old_val = change_data.get('old_value', 'N/A')
            new_val = change_data.get('new_value', 'N/A')
            changes.append(f"{field_name}: {old_val} → {new_val}")
        return "; ".join(changes)

