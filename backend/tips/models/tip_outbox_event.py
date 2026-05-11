from __future__ import annotations

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone

from tips.enums.tip_events import TipEvents


class TipOutboxEvent(models.Model):
    """
    Durable transactional outbox event.

    Guarantees:
        - at least once delivery
        - retry safety
        - crash recovery
        - replay protection
        - idempotent consumers
    """

    # ----------------------------------------------------- #
    # CORE
    # ----------------------------------------------------- #

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    tip = models.ForeignKey(
        "tips.Tip",
        on_delete=models.CASCADE,
        related_name="outbox_events",
        db_index=True,
    )

    # ----------------------------------------------------- #
    # EVENT
    # ----------------------------------------------------- #

    event_type = models.CharField(
        max_length=255,
        choices=TipEvents.choices,
        db_index=True,
    )

    payload = models.JSONField(
        default=dict,
    )

    deduplication_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("sent", "Sent"),
            ("failed", "Failed"),
        ],
        default="pending",
    )

    # ----------------------------------------------------- #
    # PROCESSING
    # ----------------------------------------------------- #

    processed = models.BooleanField(
        default=False,
        db_index=True,
    )

    failed = models.BooleanField(
        default=False,
        db_index=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    available_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )

    # ----------------------------------------------------- #
    # RETRIES
    # ----------------------------------------------------- #

    retry_count = models.PositiveIntegerField(
        default=0,
    )

    max_retries = models.PositiveIntegerField(
        default=5,
    )

    next_retry_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    last_error = models.TextField(
        blank=True,
    )

    # ----------------------------------------------------- #
    # AUDIT
    # ----------------------------------------------------- #

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ----------------------------------------------------- #
    # META
    # ----------------------------------------------------- #

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=[
                    "processed",
                    "available_at",
                ],
                name="tip_outbox_ready_idx",
            ),
            models.Index(
                fields=[
                    "failed",
                    "next_retry_at",
                ],
                name="tip_outbox_retry_idx",
            ),
            models.Index(
                fields=[
                    "event_type",
                    "processed",
                ],
                name="tip_outbox_type_idx",
            ),
        ]

    # ----------------------------------------------------- #
    # REPRESENTATION
    # ----------------------------------------------------- #

    def __str__(self) -> str:
        return (
            f"{self.event_type} :: "
            f"{self.tip.pk}"
        )

    # ----------------------------------------------------- #
    # HELPERS
    # ----------------------------------------------------- #

    def mark_processed(self) -> None:

        self.processed = True
        self.failed = False

        self.processed_at = timezone.now()

        self.last_error = ""
        self.next_retry_at = None

        self.save(
            update_fields=[
                "processed",
                "failed",
                "processed_at",
                "last_error",
                "next_retry_at",
                "updated_at",
            ]
        )

    def mark_failed(self, error: str) -> None:

        self.retry_count += 1
        self.last_error = error

        if self.retry_count >= self.max_retries:

            self.failed = True
            self.next_retry_at = None

        else:

            backoff_minutes = min(
                2 ** self.retry_count,
                60,
            )

            self.next_retry_at = (
                timezone.now()
                + timedelta(minutes=backoff_minutes)
            )

        self.save(
            update_fields=[
                "retry_count",
                "failed",
                "last_error",
                "next_retry_at",
                "updated_at",
            ]
        )