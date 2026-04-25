from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from orders.models.orders.enums import OrderStatus
from orders.services.order_transition_service import OrderTransitionService


class OrderSubmissionService:
    """
    Handle final submission paths.
    """

    @classmethod
    @transaction.atomic
    def submit_directly_to_client(
        cls,
        *,
        order,
        submitted_by,
    ):
        """
        Submit order directly to client when QA is not required.
        """
        if order.status != OrderStatus.IN_PROGRESS:
            raise ValidationError(
                "Only in-progress orders can be submitted."
            )

        return OrderTransitionService.mark_submitted(
            order=order,
            actor=submitted_by,
        )

    @classmethod
    @transaction.atomic
    def submit_to_qa(
        cls,
        *,
        order,
        submitted_by,
    ):
        """
        Submit order to QA review.
        """
        if order.status != OrderStatus.IN_PROGRESS:
            raise ValidationError(
                "Only in-progress orders can be submitted to QA."
            )

        return OrderTransitionService.mark_qa_review(
            order=order,
            actor=submitted_by,
        )