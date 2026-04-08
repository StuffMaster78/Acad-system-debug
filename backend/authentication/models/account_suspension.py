from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models.websites import Website


class AccountSuspension(models.Model):
    """
    User-initiated account suspension for temporary account protection.
    A user can request the admin and support teams to suspend their account.
    """
    class SuspensionType(models.TextChoices):
        """The type of suspension."""
        USER_INITIATED = "user_initiated", "User Initiated"
        ADMIN = "admin", "Admin"
        SECURITY = "security", "Security"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='account_suspension',
        help_text=_("User whose account is suspended")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='account_suspensions',
        help_text=_("Website context")
    )
    is_suspended = models.BooleanField(
        default=False,
        help_text=_("Whether account is currently suspended")
    )
    suspension_type = models.CharField(
        max_length=30,
        choices=SuspensionType.choices,
        default=SuspensionType.USER_INITIATED,
    )
    suspension_reason = models.TextField(
        blank=True,
        help_text=_("Reason for suspension (user-provided)")
    )
    suspended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When account was suspended")
    )
    scheduled_reactivation_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Scheduled reactivation date (optional)")
    )
    reactivated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When account was reactivated")
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website"],
                name="unique_account_suspension_per_user_per_website",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "website", "is_suspended"]),
            models.Index(fields=["scheduled_reactivation_at"]),
        ]
    
    @property
    def is_effective(self) -> bool:
        """
        Return whether this suspension is currently effective.
        """
        if not self.is_suspended:
            return False

        if (
            self.scheduled_reactivation_at
            and timezone.now() >= self.scheduled_reactivation_at
        ):
            return False

        return True
    
    def __str__(self):
        status = "Suspended" if self.is_suspended else "Active"
        return f"Account suspension for {self.user.email} - {status}"