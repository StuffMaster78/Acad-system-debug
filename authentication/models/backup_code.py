from django.db import models
from django.utils import timezone


class BackupCode(models.Model):
    """
    Stores backup codes for 2FA as a fallback when other MFA methods are unavailable.
    """
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="backup_codes"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="backup_codes"
    )
    code = models.CharField(
        max_length=32,
        help_text="One-time backup code"
    )
    used = models.BooleanField(
        default=False,
        help_text="Has this code been used?"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    used_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when the code was used"
    )

    def mark_as_used(self):
        """Mark the backup code as used and record the timestamp."""
        self.used = True
        self.used_at = timezone.now()
        self.save()

    def __str__(self):
        return f"BackupCode for {self.user.email} ({'Used' if self.used else 'Unused'})"