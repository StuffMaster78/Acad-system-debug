from django.db import models
from django.conf import settings


class UserState(models.Model):
    """
    Tenant-aware user state.
    One user can have different state per website.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="states",
    )

    website = models.ForeignKey(
        "websites.Website",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="user_states",
    )

    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(null=True, blank=True)

    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(null=True, blank=True)

    is_on_probation = models.BooleanField(default=False)
    probation_reason = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_state"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "website"],
                name="unique_user_state_per_website",
            )
        ]