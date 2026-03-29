from django.conf import settings
from django.db import models

from accounts.enums import AccountStatus, OnboardingStatus


class AccountProfile(models.Model):
    """Represents a user's account membership within a website."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_profiles",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_profiles",
    )
    status = models.CharField(
        max_length=30,
        choices=AccountStatus.choices,
        default=AccountStatus.PENDING,
    )
    onboarding_status = models.CharField(
        max_length=30,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.NOT_STARTED,
    )
    is_primary = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_account_profile"
        constraints = [
            models.UniqueConstraint(
                fields=["website", "user"],
                name="unique_account_profile_per_website_user",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a readable representation of the account profile."""
        return f"{self.user} @ {self.website}"