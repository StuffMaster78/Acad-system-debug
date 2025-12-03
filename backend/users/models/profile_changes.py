"""
Profile Change Request Models
Handles profile change requests that require admin approval (for writers).
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models import Website


class ProfileChangeRequest(models.Model):
    """
    Tracks profile change requests that require admin approval.
    Writers must request profile changes and get admin approval.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile_change_requests',
        help_text=_("User requesting profile change")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='profile_change_requests',
        help_text=_("Website context")
    )
    change_type = models.CharField(
        max_length=50,
        choices=[
            ('bio', 'Bio'),
            ('avatar', 'Avatar'),
            ('pen_name', 'Pen Name'),
            ('other', 'Other'),
        ],
        help_text=_("Type of profile change")
    )
    current_value = models.TextField(
        blank=True,
        help_text=_("Current value of the field being changed")
    )
    requested_value = models.TextField(
        help_text=_("Requested new value")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Current status of the request")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_profile_changes',
        help_text=_("Admin who approved/rejected the change")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the request was approved/rejected")
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text=_("Reason for rejection if rejected")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the request was created")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the change was completed")
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status', '-created_at']),
            models.Index(fields=['website', 'status']),
            models.Index(fields=['change_type', 'status']),
        ]
        verbose_name = _("Profile Change Request")
        verbose_name_plural = _("Profile Change Requests")
    
    def __str__(self):
        return f"Profile change request for {self.user.email} - {self.get_change_type_display()} ({self.status})"


class WriterAvatarUpload(models.Model):
    """
    Tracks writer avatar uploads that require admin approval.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avatar_uploads',
        help_text=_("Writer uploading the avatar")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='avatar_uploads',
        help_text=_("Website context")
    )
    avatar_file = models.ImageField(
        upload_to='writer_avatars/pending/',
        help_text=_("Uploaded avatar file")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Approval status")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_avatars',
        help_text=_("Admin who approved/rejected")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When approved/rejected")
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text=_("Reason for rejection")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['website', 'status']),
        ]
        verbose_name = _("Writer Avatar Upload")
        verbose_name_plural = _("Writer Avatar Uploads")
    
    def __str__(self):
        return f"Avatar upload for {self.user.email} - {self.status}"

