from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.services.order_qa_review_service import OrderQAReviewService


class OrderQAReviewServiceTests(SimpleTestCase):
    def _order(
        self,
        *,
        status: str = "in_progress",
    ) -> Any:
        return cast(
            Any,
            SimpleNamespace(
                pk=100,
                status=status,
                qa_approved_at=None,
                qa_returned_at=None,
                qa_reviewed_by=None,
                qa_review_note="",
                save=lambda *args, **kwargs: None,
            ),
        )

    def test_submit_for_qa_requires_in_progress_order(self) -> None:
        order = self._order(status="submitted")

        with self.assertRaises(ValidationError):
            OrderQAReviewService.submit_for_qa(
                order=order,
                submitted_by=SimpleNamespace(pk=1),
                note="Ready.",
            )

    @patch(
        "orders.services.order_qa_review_service."
        "OrderTransitionService.mark_qa_review"
    )
    def test_submit_for_qa_transitions_order(
        self,
        mock_mark_qa_review: Any,
    ) -> None:
        order = self._order(status="in_progress")
        mock_mark_qa_review.return_value = order

        result = OrderQAReviewService.submit_for_qa(
            order=order,
            submitted_by=SimpleNamespace(pk=1),
            note="Ready.",
        )

        self.assertEqual(result, order)
        mock_mark_qa_review.assert_called_once_with(
            order=order,
            actor=mock_mark_qa_review.call_args.kwargs["actor"],
        )

    def test_approve_for_client_delivery_requires_qa_review(self) -> None:
        order = self._order(status="in_progress")

        with self.assertRaises(ValidationError):
            OrderQAReviewService.approve_for_client_delivery(
                order=order,
                reviewed_by=SimpleNamespace(pk=1),
                note="Good.",
            )

    @patch(
        "orders.services.order_qa_review_service."
        "OrderTransitionService.mark_submitted"
    )
    def test_approve_for_client_delivery_transitions_to_submitted(
        self,
        mock_mark_submitted: Any,
    ) -> None:
        order = self._order(status="qa_review")
        reviewer = SimpleNamespace(pk=1)
        mock_mark_submitted.return_value = order

        result = OrderQAReviewService.approve_for_client_delivery(
            order=order,
            reviewed_by=reviewer,
            note="Approved.",
        )

        self.assertEqual(result, order)
        self.assertEqual(order.qa_reviewed_by, reviewer)
        self.assertEqual(order.qa_review_note, "Approved.")
        mock_mark_submitted.assert_called_once_with(
            order=order,
            actor=reviewer,
        )

    def test_return_to_writer_requires_qa_review(self) -> None:
        order = self._order(status="submitted")

        with self.assertRaises(ValidationError):
            OrderQAReviewService.return_to_writer(
                order=order,
                reviewed_by=SimpleNamespace(pk=1),
                reason="Fix citations.",
            )

    @patch(
        "orders.services.order_qa_review_service."
        "OrderTransitionService.transition"
    )
    def test_return_to_writer_transitions_back_to_in_progress(
        self,
        mock_transition: Any,
    ) -> None:
        order = self._order(status="qa_review")
        reviewer = SimpleNamespace(pk=1)
        mock_transition.return_value = order

        result = OrderQAReviewService.return_to_writer(
            order=order,
            reviewed_by=reviewer,
            reason="Fix citations.",
        )

        self.assertEqual(result, order)
        self.assertEqual(order.qa_reviewed_by, reviewer)
        self.assertEqual(order.qa_review_note, "Fix citations.")
        mock_transition.assert_called_once()
        self.assertEqual(
            mock_transition.call_args.kwargs["next_status"],
            "in_progress",
        )