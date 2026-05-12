from __future__ import annotations

from django.db import models

from websites.models.websites import Website


class ReversalChain(models.Model):
    """
    Tracks full lifecycle of reversals.

    Ensures no silent money corrections.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="reversal_chains",
    )

    original_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.CASCADE,
        related_name="reversal_origins",
    )

    reversal_event = models.ForeignKey(
        "writer_compensation.CompensationEvent",
        on_delete=models.CASCADE,
        related_name="reversal_targets",
    )

    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    metadata = models.JSONField(default=dict, blank=True)