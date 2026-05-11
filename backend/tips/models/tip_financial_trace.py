from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class TipFinancialTrace(models.Model):
    """
    Immutable operational execution trace.

    Purpose:
        - forensic debugging
        - payment investigations
        - webhook replay analysis
        - operational observability
        - support diagnostics
        - audit support

    IMPORTANT:
        These records should NEVER be mutated after creation.
    """

    # ------------------------------------------------------------ #
    # PRIMARY IDENTITY
    # ------------------------------------------------------------ #

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # ------------------------------------------------------------ #
    # DOMAIN RELATION
    # ------------------------------------------------------------ #

    tip = models.ForeignKey(
        "tips.Tip",
        on_delete=models.CASCADE,
        related_name="financial_traces",
        db_index=True,
    )

    # ------------------------------------------------------------ #
    # TRACE DETAILS
    # ------------------------------------------------------------ #

    event = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Domain event or operational action name.",
    )

    step = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Specific execution step.",
    )

    status = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Execution status for the step/event.",
    )

    severity = models.CharField(
        max_length=50,
        default="info",
        db_index=True,
        help_text="info | warning | error | critical",
    )

    source = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Originating service or subsystem.",
    )

    correlation_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Cross-service request correlation identifier.",
    )

    # ------------------------------------------------------------ #
    # ACTOR
    # ------------------------------------------------------------ #

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tip_financial_traces",
    )

    # ------------------------------------------------------------ #
    # STRUCTURED CONTEXT
    # ------------------------------------------------------------ #

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    # ------------------------------------------------------------ #
    # TIMESTAMPS
    # ------------------------------------------------------------ #

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    # ------------------------------------------------------------ #
    # META
    # ------------------------------------------------------------ #

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=[
                    "tip",
                    "created_at",
                ],
                name="tip_trace_tip_created_idx",
            ),
            models.Index(
                fields=[
                    "event",
                    "created_at",
                ],
                name="tip_trace_event_created_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="tip_trace_status_created_idx",
            ),
            models.Index(
                fields=[
                    "severity",
                    "created_at",
                ],
                name="tip_trace_severity_created_idx",
            ),
            models.Index(
                fields=[
                    "correlation_id",
                ],
                name="tip_trace_correlation_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.event} | "
            f"{self.status} | "
            f"Tip {self.tip.pk}"
        )