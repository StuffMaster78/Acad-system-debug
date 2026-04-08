from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models.websites import Website


class EmailChangeRequest(models.Model):
    """
    Represents a request to change a user's email address.
    Tracks email change requests with verification and admin approval.
    """
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ADMIN_APPROVED = "admin_approved", "Admin Approved"
        OLD_EMAIL_CONFIRMED = "old_email_confirmed", "Old Email Confirmed"
        NEW_EMAIL_VERIFIED = "new_email_verified", "New Email Verified"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_change_requests',
        help_text=_("User requesting email change")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='email_change_requests',
        help_text=_("Website context")
    )
    old_email = models.EmailField(
        help_text=_("Current email address")
    )
    new_email = models.EmailField(
        help_text=_("New email address to change to")
    )
    new_email_token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Token for verifying new email")
    )
    old_email_token_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Token for confirming old email")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_("Current status of the email change request")
    )
    # verified = models.BooleanField(
    #     default=False,
    #     help_text=_("Whether new email has been verified")
    # )
    # old_email_confirmed = models.BooleanField(
    #     default=False,
    #     help_text=_("Whether old email change was confirmed")
    # )
    # admin_approved = models.BooleanField(
    #     default=False,
    #     help_text=_("Whether admin has approved the email change")
    # )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_email_changes',
        help_text=_("Admin who approved the email change")
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When admin approved the email change")
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text=_("Reason for rejection if rejected")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When change was requested")
    )
    expires_at = models.DateTimeField(
        help_text=_("When this request expires")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When email change was completed")
    )
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_expired(self) -> bool:
        """
        Return whether this request has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_active(self) -> bool:
        """
        Return whether this request is still active.
        """
        return (
            not self.is_expired
            and self.status not in {
                self.Status.COMPLETED,
                self.Status.REJECTED,
                self.Status.CANCELLED,
            }
        )
    
    def __str__(self):
        status = "Verified" if self.status else "Pending"
        return f"Email change: {self.old_email} → {self.new_email} ({status})"
    