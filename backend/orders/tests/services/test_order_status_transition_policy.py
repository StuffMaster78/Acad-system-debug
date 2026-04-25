from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.services.policies.order_status_transition_policy import (
    can_transition,
    validate_status_transition,
)


class OrderStatusTransitionPolicyTests(SimpleTestCase):
    def test_validate_status_transition_allows_ready_for_staffing_to_in_progress(
        self,
    ) -> None:
        validate_status_transition(
            from_status="ready_for_staffing",
            to_status="in_progress",
        )

    def test_validate_status_transition_allows_in_progress_to_submitted(
        self,
    ) -> None:
        validate_status_transition(
            from_status="in_progress",
            to_status="submitted",
        )

    def test_validate_status_transition_allows_submitted_to_completed(
        self,
    ) -> None:
        validate_status_transition(
            from_status="submitted",
            to_status="completed",
        )

    def test_validate_status_transition_allows_completed_to_in_progress(
        self,
    ) -> None:
        validate_status_transition(
            from_status="completed",
            to_status="in_progress",
        )

    def test_validate_status_transition_allows_completed_to_archived(
        self,
    ) -> None:
        validate_status_transition(
            from_status="completed",
            to_status="archived",
        )

    def test_validate_status_transition_allows_completed_to_cancelled(
        self,
    ) -> None:
        validate_status_transition(
            from_status="completed",
            to_status="cancelled",
        )

    def test_validate_status_transition_rejects_invalid_transition(
        self,
    ) -> None:
        with self.assertRaisesMessage(
            ValidationError,
            "Invalid status transition: ready_for_staffing -> completed",
        ):
            validate_status_transition(
                from_status="ready_for_staffing",
                to_status="completed",
            )

    def test_validate_status_transition_rejects_cancelled_to_in_progress(
        self,
    ) -> None:
        with self.assertRaisesMessage(
            ValidationError,
            "Invalid status transition: cancelled -> in_progress",
        ):
            validate_status_transition(
                from_status="cancelled",
                to_status="in_progress",
            )

    def test_validate_status_transition_rejects_archived_to_cancelled(
        self,
    ) -> None:
        with self.assertRaisesMessage(
            ValidationError,
            "Invalid status transition: archived -> cancelled",
        ):
            validate_status_transition(
                from_status="archived",
                to_status="cancelled",
            )

    def test_can_transition_returns_true_for_valid_transition(self) -> None:
        result = can_transition(
            from_status="submitted",
            to_status="completed",
        )

        self.assertTrue(result)

    def test_can_transition_returns_false_for_invalid_transition(self) -> None:
        result = can_transition(
            from_status="submitted",
            to_status="archived",
        )

        self.assertFalse(result)

    def test_can_transition_returns_false_for_cancelled_terminal_state(
        self,
    ) -> None:
        result = can_transition(
            from_status="cancelled",
            to_status="completed",
        )

        self.assertFalse(result)

    def test_can_transition_returns_false_for_archived_terminal_state(
        self,
    ) -> None:
        result = can_transition(
            from_status="archived",
            to_status="completed",
        )

        self.assertFalse(result)