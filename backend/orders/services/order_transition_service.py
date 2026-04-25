from __future__ import annotations

from typing import Any, Optional

from django.db import transaction
from django.utils import timezone

from orders.models import OrderTimelineEvent
from orders.models.orders.enums import OrderStatus
from orders.workflows.order_transition_workflow import (
    OrderTransitionWorkflow,
)


class OrderTransitionService:
    """
    Apply legal order status transitions and record timeline events.
    """

    @classmethod
    @transaction.atomic
    def transition(
        cls,
        *,
        order,
        next_status: str,
        actor: Optional[Any] = None,
        event_type: str = "",
        metadata: Optional[dict[str, Any]] = None,
        save_fields: Optional[list[str]] = None,
    ):
        """
        Move order to next_status after workflow validation.
        """
        current_status = order.status

        OrderTransitionWorkflow.ensure_can_transition(
            current_status=current_status,
            next_status=next_status,
        )

        order.status = next_status

        fields = ["status", "updated_at"]
        if save_fields:
            fields.extend(save_fields)

        order.save(update_fields=list(dict.fromkeys(fields)))

        cls._create_timeline_event(
            order=order,
            actor=actor,
            event_type=event_type or f"status_changed_to_{next_status}",
            metadata={
                "from_status": current_status,
                "to_status": next_status,
                **(metadata or {}),
            },
        )

        return order

    @classmethod
    def mark_ready_for_staffing(
        cls,
        *,
        order,
        actor: Optional[Any] = None,
    ):
        """
        Move paid order into staffing queue.
        """
        return cls.transition(
            order=order,
            next_status=OrderStatus.READY_FOR_STAFFING,
            actor=actor,
            event_type="ready_for_staffing",
        )

    @classmethod
    def mark_in_progress(
        cls,
        *,
        order,
        actor: Optional[Any] = None,
    ):
        """
        Move assigned order into active work.
        """
        return cls.transition(
            order=order,
            next_status=OrderStatus.IN_PROGRESS,
            actor=actor,
            event_type="order_started",
        )

    @classmethod
    def mark_qa_review(
        cls,
        *,
        order,
        actor: Optional[Any] = None,
    ):
        """
        Move order into QA review.
        """
        order.submitted_for_qa_at = timezone.now()

        return cls.transition(
            order=order,
            next_status=OrderStatus.QA_REVIEW,
            actor=actor,
            event_type="qa_review_started",
            save_fields=["submitted_for_qa_at"],
        )

    @classmethod
    def mark_submitted(
        cls,
        *,
        order,
        actor: Optional[Any] = None,
    ):
        """
        Mark order submitted to client.
        """
        order.submitted_at = timezone.now()

        return cls.transition(
            order=order,
            next_status=OrderStatus.SUBMITTED,
            actor=actor,
            event_type="submitted_to_client",
            save_fields=["submitted_at"],
        )

    @classmethod
    def mark_completed(
        cls,
        *,
        order,
        actor: Optional[Any] = None,
        auto_approved: bool = False,
    ):
        """
        Mark order completed.
        """
        order.completed_at = timezone.now()

        return cls.transition(
            order=order,
            next_status=OrderStatus.COMPLETED,
            actor=actor,
            event_type="order_completed",
            metadata={
                "auto_approved": auto_approved,
            },
            save_fields=["completed_at"],
        )

    @classmethod
    def mark_archived(
        cls,
        *,
        order,
        actor: Optional[Any] = None,
    ):
        """
        Archive completed order.
        """
        order.archived_at = timezone.now()

        return cls.transition(
            order=order,
            next_status=OrderStatus.ARCHIVED,
            actor=actor,
            event_type="order_archived",
            save_fields=["archived_at"],
        )

    @staticmethod
    def _create_timeline_event(
        *,
        order,
        actor: Optional[Any],
        event_type: str,
        metadata: dict[str, Any],
    ) -> None:
        """
        Create order timeline event.
        """
        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            actor=actor,
            event_type=event_type,
            metadata=metadata,
        )