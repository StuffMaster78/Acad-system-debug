from django.conf import settings
from django.db import models

from accounts.enums import OnboardingStatus, OnboardingType


class OnboardingSession(models.Model):
    """Tracks onboarding progress for an account profile."""

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="onboarding_sessions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="onboarding_sessions",
    )
    account_profile = models.ForeignKey(
        "accounts.AccountProfile",
        on_delete=models.CASCADE,
        related_name="onboarding_sessions",
    )
    onboarding_type = models.CharField(
        max_length=30,
        choices=OnboardingType.choices,
    )
    target_role = models.ForeignKey(
        "accounts.RoleDefinition",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="onboarding_sessions",
    )
    status = models.CharField(
        max_length=30,
        choices=OnboardingStatus.choices,
        default=OnboardingStatus.NOT_STARTED,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_step = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_onboarding_sessions",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_onboarding_session"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        """Return a readable representation of the onboarding session."""
        return f"{self.user} {self.onboarding_type} onboarding"