# class_management/state_machine.py

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassOrderStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassOrderStateError
from class_management.models.class_order import ClassOrder
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)


class ClassOrderStateMachine:
    """
    Central state transition engine for class orders.

    All class order status changes should pass through this class.
    Services should request transitions instead of mutating
    ``class_order.status`` directly.
    """

    ALLOWED_TRANSITIONS: Mapping[str, set[str]] = {
        ClassOrderStatus.DRAFT: {
            ClassOrderStatus.SUBMITTED,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.SUBMITTED: {
            ClassOrderStatus.UNDER_REVIEW,
            ClassOrderStatus.NEEDS_CLIENT_INFO,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.NEEDS_CLIENT_INFO: {
            ClassOrderStatus.SUBMITTED,
            ClassOrderStatus.UNDER_REVIEW,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.UNDER_REVIEW: {
            ClassOrderStatus.PRICE_PROPOSED,
            ClassOrderStatus.NEEDS_CLIENT_INFO,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.PRICE_PROPOSED: {
            ClassOrderStatus.NEGOTIATING,
            ClassOrderStatus.ACCEPTED,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.NEGOTIATING: {
            ClassOrderStatus.PRICE_PROPOSED,
            ClassOrderStatus.ACCEPTED,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.ACCEPTED: {
            ClassOrderStatus.PENDING_PAYMENT,
            ClassOrderStatus.PARTIALLY_PAID,
            ClassOrderStatus.PAID,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.PENDING_PAYMENT: {
            ClassOrderStatus.PARTIALLY_PAID,
            ClassOrderStatus.PAID,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.PARTIALLY_PAID: {
            ClassOrderStatus.PAID,
            ClassOrderStatus.ASSIGNED,
            ClassOrderStatus.IN_PROGRESS,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.PAID: {
            ClassOrderStatus.ASSIGNED,
            ClassOrderStatus.IN_PROGRESS,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.ASSIGNED: {
            ClassOrderStatus.IN_PROGRESS,
            ClassOrderStatus.PAUSED,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.IN_PROGRESS: {
            ClassOrderStatus.PAUSED,
            ClassOrderStatus.QUALITY_REVIEW,
            ClassOrderStatus.COMPLETED,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.PAUSED: {
            ClassOrderStatus.IN_PROGRESS,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.QUALITY_REVIEW: {
            ClassOrderStatus.IN_PROGRESS,
            ClassOrderStatus.COMPLETED,
            ClassOrderStatus.CANCELLED,
        },
        ClassOrderStatus.COMPLETED: {
            ClassOrderStatus.ARCHIVED,
        },
        ClassOrderStatus.CANCELLED: {
            ClassOrderStatus.ARCHIVED,
        },
        ClassOrderStatus.ARCHIVED: set(),
    }

    TIMELINE_TITLES: Mapping[str, str] = {
        ClassOrderStatus.SUBMITTED: "Class order submitted",
        ClassOrderStatus.NEEDS_CLIENT_INFO: "More information requested",
        ClassOrderStatus.UNDER_REVIEW: "Class order under review",
        ClassOrderStatus.PRICE_PROPOSED: "Class price proposed",
        ClassOrderStatus.NEGOTIATING: "Class price negotiation started",
        ClassOrderStatus.ACCEPTED: "Class price accepted",
        ClassOrderStatus.PENDING_PAYMENT: "Class pending payment",
        ClassOrderStatus.PARTIALLY_PAID: "Class partially paid",
        ClassOrderStatus.PAID: "Class fully paid",
        ClassOrderStatus.ASSIGNED: "Class writer assigned",
        ClassOrderStatus.IN_PROGRESS: "Class work in progress",
        ClassOrderStatus.PAUSED: "Class work paused",
        ClassOrderStatus.QUALITY_REVIEW: "Class under quality review",
        ClassOrderStatus.COMPLETED: "Class order completed",
        ClassOrderStatus.CANCELLED: "Class order cancelled",
        ClassOrderStatus.ARCHIVED: "Class order archived",
    }

    TIMELINE_EVENT_TYPES: Mapping[str, str] = {
        ClassOrderStatus.SUBMITTED: ClassTimelineEventType.SUBMITTED,
        ClassOrderStatus.NEEDS_CLIENT_INFO: (
            ClassTimelineEventType.NEEDS_CLIENT_INFO
        ),
        ClassOrderStatus.UNDER_REVIEW: (
            ClassTimelineEventType.REVIEW_STARTED
        ),
        ClassOrderStatus.PRICE_PROPOSED: (
            ClassTimelineEventType.PRICE_PROPOSED
        ),
        ClassOrderStatus.NEGOTIATING: (
            ClassTimelineEventType.COUNTER_OFFER_SENT
        ),
        ClassOrderStatus.ACCEPTED: (
            ClassTimelineEventType.PRICE_ACCEPTED
        ),
        ClassOrderStatus.PENDING_PAYMENT: (
            ClassTimelineEventType.INVOICE_CREATED
        ),
        ClassOrderStatus.PARTIALLY_PAID: (
            ClassTimelineEventType.PAYMENT_APPLIED
        ),
        ClassOrderStatus.PAID: ClassTimelineEventType.PAYMENT_APPLIED,
        ClassOrderStatus.ASSIGNED: (
            ClassTimelineEventType.WRITER_ASSIGNED
        ),
        ClassOrderStatus.IN_PROGRESS: ClassTimelineEventType.WORK_STARTED,
        ClassOrderStatus.PAUSED: ClassTimelineEventType.WORK_PAUSED,
        ClassOrderStatus.QUALITY_REVIEW: (
            ClassTimelineEventType.QUALITY_REVIEW_STARTED
        ),
        ClassOrderStatus.COMPLETED: ClassTimelineEventType.COMPLETED,
        ClassOrderStatus.CANCELLED: ClassTimelineEventType.CANCELLED,
        ClassOrderStatus.ARCHIVED: ClassTimelineEventType.ARCHIVED,
    }

    TERMINAL_STATUSES = {
        ClassOrderStatus.COMPLETED,
        ClassOrderStatus.CANCELLED,
        ClassOrderStatus.ARCHIVED,
    }

    @classmethod
    @transaction.atomic
    def transition(
        cls,
        *,
        class_order: ClassOrder,
        to_status: str,
        triggered_by=None,
        reason: str = "",
        metadata: dict[str, Any] | None = None,
        force: bool = False,
        save: bool = True,
    ) -> ClassOrder:
        """
        Move a class order from its current status to a new status.

        Args:
            class_order:
                The class order being transitioned.
            to_status:
                Target status.
            triggered_by:
                User or system actor responsible for the change.
            reason:
                Optional human-readable reason.
            metadata:
                Extra timeline metadata.
            force:
                Allows privileged callers to bypass the transition map.
            save:
                Whether to persist the class order immediately.

        Returns:
            The updated class order.

        Raises:
            ClassOrderStateError:
                If the transition is invalid.
        """
        from_status = class_order.status

        if from_status == to_status:
            return class_order

        if not force:
            cls.validate_transition(
                from_status=from_status,
                to_status=to_status,
            )

        cls._apply_status_fields(
            class_order=class_order,
            to_status=to_status,
            triggered_by=triggered_by,
            reason=reason,
        )

        if save:
            class_order.save(
                update_fields=cls._get_update_fields(to_status=to_status),
            )

        cls._record_transition(
            class_order=class_order,
            from_status=from_status,
            to_status=to_status,
            triggered_by=triggered_by,
            reason=reason,
            metadata=metadata,
            forced=force,
        )

        return class_order

    @classmethod
    def validate_transition(
        cls,
        *,
        from_status: str,
        to_status: str,
    ) -> None:
        """
        Validate whether a status transition is allowed.
        """
        allowed = cls.ALLOWED_TRANSITIONS.get(from_status, set())

        if to_status not in allowed:
            raise ClassOrderStateError(
                "Invalid class order transition: "
                f"{from_status} -> {to_status}."
            )

    @classmethod
    def can_transition(
        cls,
        *,
        from_status: str,
        to_status: str,
    ) -> bool:
        """
        Return whether a status transition is allowed.
        """
        return to_status in cls.ALLOWED_TRANSITIONS.get(from_status, set())

    @classmethod
    def get_allowed_next_statuses(
        cls,
        *,
        current_status: str,
    ) -> set[str]:
        """
        Return statuses reachable from the current status.
        """
        return set(cls.ALLOWED_TRANSITIONS.get(current_status, set()))

    @classmethod
    def require_not_terminal(
        cls,
        *,
        class_order: ClassOrder,
        action: str,
    ) -> None:
        """
        Block actions against terminal class orders.
        """
        if class_order.status in cls.TERMINAL_STATUSES:
            raise ClassOrderStateError(
                f"Cannot {action} class order while status is "
                f"{class_order.status}."
            )

    @classmethod
    def _apply_status_fields(
        cls,
        *,
        class_order: ClassOrder,
        to_status: str,
        triggered_by,
        reason: str,
    ) -> None:
        """
        Apply status and related timestamp fields to the class order.
        """
        now = timezone.now()

        class_order.status = to_status
        class_order.updated_by = triggered_by

        if to_status == ClassOrderStatus.SUBMITTED:
            class_order.submitted_at = now

        if to_status == ClassOrderStatus.ACCEPTED:
            class_order.accepted_at = now

        if to_status == ClassOrderStatus.PAUSED:
            class_order.is_work_paused = True
            class_order.pause_reason = reason or "state_transition"
            class_order.paused_at = now

        if to_status == ClassOrderStatus.IN_PROGRESS:
            class_order.is_work_paused = False
            class_order.pause_reason = ""
            class_order.paused_at = None

        if to_status == ClassOrderStatus.COMPLETED:
            class_order.completed_at = now

        if to_status == ClassOrderStatus.CANCELLED:
            class_order.cancelled_at = now

        if to_status == ClassOrderStatus.ARCHIVED:
            class_order.archived_at = now

    @classmethod
    def _get_update_fields(cls, *, to_status: str) -> list[str]:
        """
        Return model fields that should be persisted for a transition.
        """
        fields = [
            "status",
            "updated_by",
            "updated_at",
        ]

        if to_status == ClassOrderStatus.SUBMITTED:
            fields.append("submitted_at")

        if to_status == ClassOrderStatus.ACCEPTED:
            fields.append("accepted_at")

        if to_status == ClassOrderStatus.PAUSED:
            fields.extend(
                [
                    "is_work_paused",
                    "pause_reason",
                    "paused_at",
                ]
            )

        if to_status == ClassOrderStatus.IN_PROGRESS:
            fields.extend(
                [
                    "is_work_paused",
                    "pause_reason",
                    "paused_at",
                ]
            )

        if to_status == ClassOrderStatus.COMPLETED:
            fields.append("completed_at")

        if to_status == ClassOrderStatus.CANCELLED:
            fields.append("cancelled_at")

        if to_status == ClassOrderStatus.ARCHIVED:
            fields.append("archived_at")

        return fields

    @classmethod
    def _record_transition(
        cls,
        *,
        class_order: ClassOrder,
        from_status: str,
        to_status: str,
        triggered_by,
        reason: str,
        metadata: dict[str, Any] | None,
        forced: bool,
    ) -> None:
        """
        Record a timeline event for the transition.
        """
        event_type = cls.TIMELINE_EVENT_TYPES.get(
            to_status,
            ClassTimelineEventType.UPDATED,
        )
        title = cls.TIMELINE_TITLES.get(
            to_status,
            "Class order status updated",
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=event_type,
            title=title,
            description=reason,
            triggered_by=triggered_by,
            metadata={
                "from_status": from_status,
                "to_status": to_status,
                "forced": forced,
                **(metadata or {}),
            },
        )