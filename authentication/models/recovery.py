"""
Model for managing one-time backup codes used during multi-factor authentication.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

class BackupCode(models.Model):
    """
    Represents a single-use recovery code for MFA fallback.

    Attributes:
        user (User): The user the backup code belongs to.
        website (Website): Tenant context for multitenancy.
        code_hash (str): SHA-256 hash of the backup code.
        used (bool): Whether the code has been used.
        created_at (datetime): When the code was created.
        used_at (datetime): When the code was used (if used).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="backup_codes"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="backup_codes"
    )
    code_hash = models.CharField(
        max_length=128,
        help_text="SHA-256 hash of the one-time backup code"
    )
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def mark_used(self):
        """
        Marks the backup code as used and timestamps its usage.
        """
        self.used = True
        self.used_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Backup code for {self.user} (used={self.used})"