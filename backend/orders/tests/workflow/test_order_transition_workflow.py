from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.enums import OrderStatus
from orders.workflows.order_transition_workflow import (
    OrderTransitionWorkflow,
)


class OrderTransitionWorkflowTests(SimpleTestCase):
    def test_pending_payment_can_move_to_ready_for_staffing(self) -> None:
        OrderTransitionWorkflow.ensure_can_transition(
            current_status=OrderStatus.PENDING_PAYMENT,
            next_status=OrderStatus.READY_FOR_STAFFING,
        )

    def test_ready_for_staffing_can_move_to_in_progress(self) -> None:
        OrderTransitionWorkflow.ensure_can_transition(
            current_status=OrderStatus.READY_FOR_STAFFING,
            next_status=OrderStatus.IN_PROGRESS,
        )

    def test_in_progress_can_move_to_qa_review(self) -> None:
        OrderTransitionWorkflow.ensure_can_transition(
            current_status=OrderStatus.IN_PROGRESS,
            next_status=OrderStatus.QA_REVIEW,
        )

    def test_qa_review_can_move_to_submitted(self) -> None:
        OrderTransitionWorkflow.ensure_can_transition(
            current_status=OrderStatus.QA_REVIEW,
            next_status=OrderStatus.SUBMITTED,
        )

    def test_submitted_can_move_to_completed(self) -> None:
        OrderTransitionWorkflow.ensure_can_transition(
            current_status=OrderStatus.SUBMITTED,
            next_status=OrderStatus.COMPLETED,
        )

    def test_completed_can_move_to_archived(self) -> None:
        OrderTransitionWorkflow.ensure_can_transition(
            current_status=OrderStatus.COMPLETED,
            next_status=OrderStatus.ARCHIVED,
        )

    def test_invalid_transition_raises(self) -> None:
        with self.assertRaises(ValidationError):
            OrderTransitionWorkflow.ensure_can_transition(
                current_status=OrderStatus.CREATED,
                next_status=OrderStatus.COMPLETED,
            )