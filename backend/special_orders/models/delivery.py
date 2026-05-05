from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    DeliveryCheckpointStatus,
    DeliveryCheckpointType,
    SpecialOrderDeliverableStatus,
)


class SpecialOrderDeliveryCheckpoint(TimeStampedModel):
    """
    Funding or approval gate for a special order workflow.

    Replaces loose fields like admin_unlocked_files with an auditable
    checkpoint record.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_delivery_checkpoints",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="delivery_checkpoints",
    )

    checkpoint_type = models.CharField(
        max_length=50,
        choices=DeliveryCheckpointType.CHOICES,
    )
    status = models.CharField(
        max_length=50,
        choices=DeliveryCheckpointStatus.CHOICES,
        default=DeliveryCheckpointStatus.BLOCKED,
    )

    required_milestone = models.ForeignKey(
        "special_orders.SpecialOrderFundingMilestone",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="delivery_checkpoints",
    )

    unlocked_at = models.DateTimeField(null=True, blank=True)
    unlocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unlocked_special_order_checkpoints",
    )

    waiver_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["special_order", "checkpoint_type"],
                name="unique_special_order_delivery_checkpoint_type",
            ),
        ]
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "checkpoint_type"]),
            models.Index(fields=["website", "status"]),
        ]

    def __str__(self) -> str:
        return (
            f"DeliveryCheckpoint("
            f"order={self.special_order_id}, "
            f"type={self.checkpoint_type})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int
        required_milestone_id: int | None


class SpecialOrderDeliverable(TimeStampedModel):
    """
    Tracks a deliverable expected from a special order.

    Actual file storage should live in files_management. This model stores
    workflow metadata and references file records by ID/reference.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_deliverables",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="deliverables",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=50,
        choices=SpecialOrderDeliverableStatus.CHOICES,
        default=SpecialOrderDeliverableStatus.PENDING,
    )

    file_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reference to a files_management record.",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_special_order_deliverables",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_special_order_deliverables",
    )

    uploaded_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    review_notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["file_reference"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderDeliverable("
            f"order={self.special_order_id}, "
            f"title={self.title})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderCompletionLog(TimeStampedModel):
    """
    Immutable log of special order completion actions.

    Replaces the old completion log while avoiding hardcoded completion
    actions inside the model.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_completion_logs",
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="completion_logs",
    )

    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_order_completion_logs",
    )

    action = models.CharField(max_length=100)
    justification = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "special_order"]),
            models.Index(fields=["website", "created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self) -> str:
        return (
            f"SpecialOrderCompletionLog("
            f"order={self.special_order_id}, "
            f"action={self.action})"
        )

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int