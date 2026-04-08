from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class SessionLimitPolicy(models.Model):
    """
    Define concurrent session limit policy for a user on a website.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="session_limit_policies",
        help_text=_("User whose session limits are configured."),
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="session_limit_policies",
        help_text=_("Website context."),
    )
    max_concurrent_sessions = models.PositiveIntegerField(
        default=3,
        help_text=_("Maximum number of concurrent active sessions."),
    )
    allow_unlimited_trusted = models.BooleanField(
        default=False,
        help_text=_("Allow unlimited sessions from trusted devices."),
    )
    revoke_oldest_on_limit = models.BooleanField(
        default=True,
        help_text=_(
            "Revoke the oldest active session when the limit is reached."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website"],
                name="unique_session_limit_policy_per_user_website",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "website"]),
        ]
        verbose_name = _("Session Limit Policy")
        verbose_name_plural = _("Session Limit Policies")

    def clean(self) -> None:
        """
        Validate policy values.
        """
        if self.max_concurrent_sessions < 1:
            raise ValidationError(
                {
                    "max_concurrent_sessions": _(
                        "Maximum concurrent sessions must be at least 1."
                    )
                }
            )

    def __str__(self) -> str:
        """
        Return a human-readable representation of the session policy.
        """
        return (
            f"Session limit for {self.user.email} on "
            f"{self.website}: {self.max_concurrent_sessions}"
        )