from __future__ import annotations

from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.orders.enums import OrderStatus
from orders.services.order_transition_service import OrderTransitionService


class OrderQAReviewService:
    """
    Handle QA review before client delivery.
    """

    @classmethod
    @transaction.atomic
    def submit_for_qa(
        cls,
        *,
        order,
        submitted_by,
        note: str = "",
    ):
        """
        Writer submits final work for QA review.
        """
        if order.status != OrderStatus.IN_PROGRESS:
            raise ValidationError(
                "Only in-progress orders can be submitted for QA."
            )

        return OrderTransitionService.mark_qa_review(
            order=order,
            actor=submitted_by,
        )

    @classmethod
    @transaction.atomic
    def approve_for_client_delivery(
        cls,
        *,
        order,
        reviewed_by,
        note: str = "",
    ):
        """
        QA approves order for client delivery.
        """
        if order.status != OrderStatus.QA_REVIEW:
            raise ValidationError(
                "Only QA review orders can be approved for delivery."
            )

        order.qa_approved_at = timezone.now()
        order.qa_reviewed_by = reviewed_by
        order.qa_review_note = note
        order.save(
            update_fields=[
                "qa_approved_at",
                "qa_reviewed_by",
                "qa_review_note",
                "updated_at",
            ]
        )

        return OrderTransitionService.mark_submitted(
            order=order,
            actor=reviewed_by,
        )

    @classmethod
    @transaction.atomic
    def return_to_writer(
        cls,
        *,
        order,
        reviewed_by,
        reason: str,
    ):
        """
        QA returns work to writer for correction.
        """
        if order.status != OrderStatus.QA_REVIEW:
            raise ValidationError(
                "Only QA review orders can be returned to writer."
            )

        order.qa_reviewed_by = reviewed_by
        order.qa_review_note = reason
        order.qa_returned_at = timezone.now()
        order.save(
            update_fields=[
                "qa_reviewed_by",
                "qa_review_note",
                "qa_returned_at",
                "updated_at",
            ]
        )

        return OrderTransitionService.transition(
            order=order,
            next_status=OrderStatus.IN_PROGRESS,
            actor=reviewed_by,
            event_type="qa_returned_to_writer",
            metadata={
                "reason": reason,
            },
        )