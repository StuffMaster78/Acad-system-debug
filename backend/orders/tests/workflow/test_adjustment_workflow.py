from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.enums import OrderAdjustmentStatus
from orders.workflows.adjustment_workflow import AdjustmentWorkflow


class AdjustmentWorkflowTests(SimpleTestCase):
    def test_pending_can_move_to_client_countered(self) -> None:
        AdjustmentWorkflow.ensure_can_transition(
            current_status=OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
            next_status=OrderAdjustmentStatus.CLIENT_COUNTERED,
        )

    def test_client_countered_can_move_to_funding_pending(self) -> None:
        AdjustmentWorkflow.ensure_can_transition(
            current_status=OrderAdjustmentStatus.CLIENT_COUNTERED,
            next_status=OrderAdjustmentStatus.FUNDING_PENDING,
        )

    def test_funding_pending_can_move_to_counter_funded_final(self) -> None:
        AdjustmentWorkflow.ensure_can_transition(
            current_status=OrderAdjustmentStatus.FUNDING_PENDING,
            next_status=OrderAdjustmentStatus.COUNTER_FUNDED_FINAL,
        )

    def test_invalid_transition_raises(self) -> None:
        with self.assertRaises(ValidationError):
            AdjustmentWorkflow.ensure_can_transition(
                current_status=OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
                next_status=OrderAdjustmentStatus.COUNTER_FUNDED_FINAL,
            )

    def test_terminal_status_detection(self) -> None:
        self.assertTrue(
            AdjustmentWorkflow.is_terminal_status(
                status=OrderAdjustmentStatus.CANCELLED,
            )
        )
        self.assertFalse(
            AdjustmentWorkflow.is_terminal_status(
                status=OrderAdjustmentStatus.CLIENT_COUNTERED,
            )
        )