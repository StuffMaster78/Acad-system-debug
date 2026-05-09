from __future__ import annotations

from django.conf import settings
from django.db import models

from websites.models.websites import Website

User = settings.AUTH_USER_MODEL


class FinancialStateTransitionLog(models.Model):
    """
    Immutable audit trail of all state transitions in money lifecycle.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="state_transition_logs",
    )

    entity_type = models.CharField(max_length=64)
    entity_id = models.CharField(max_length=64)

    from_state = models.CharField(max_length=64)
    to_state = models.CharField(max_length=64)

    trigger = models.CharField(
        max_length=64,
        help_text="SYSTEM / ADMIN / DISPUTE / DEADLINE / AUTO_RULE",
    )

    reason = models.TextField(blank=True)

    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["from_state", "to_state"]),
        ]