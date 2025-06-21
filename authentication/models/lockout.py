"""
Model for account lockouts and high-risk access restriction tracking.
"""

from django.db import models
from django.conf import settings


class AccountLockout(models.Model):
    """
    Represents an account lockout event due to suspicious activity or admin action.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="lockouts"
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="account_lockouts"
    )
    reason = models.TextField(
        help_text="Explanation for why the user account was locked out"
    )
    locked_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Lockout for {self.user} (active={self.active})"