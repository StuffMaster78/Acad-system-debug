from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.services.order_cancellation_service import (
    OrderCancellationService,
)


class OrderCancellationServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.staff_user = SimpleNamespace(pk=20, website_id=1)
        self.foreign_user = SimpleNamespace(pk=99, website_id=999)
        self.writer = SimpleNamespace(pk=30, website_id=1)

    def _make_order(self, **kwargs: Any) -> Any:
        defaults = {
            "pk": 1,
            "website": self.website,
            "status": "submitted",
            "approved_at": None,
            "cancelled_at": None,
            "cancelled_by": None,
            "cancellation_reason": "",
            "save": MagicMock(),
        }
        defaults.update(kwargs)
        return cast(Any, SimpleNamespace(**defaults))

    def _make_assignment(self, **kwargs: Any) -> Any:
        defaults = {
            "pk": 100,
            "writer": self.writer,
            "status": "active",
            "is_current": True,
            "released_at": None,
            "release_reason": "",
            "save": MagicMock(),
        }
        defaults.update(kwargs)
        return cast(Any, SimpleNamespace(**defaults))

    @patch.object(OrderCancellationService, "_create_timeline_event")
    @patch.object(OrderCancellationService, "_lock_order")
    @patch(
        "orders.services.order_cancellation_service.OrderStaffingStore.get_current_assignment"
    )
    @patch(
        "orders.services.order_cancellation_service.OrderCancellationPolicy.validate_can_cancel"
    )
    def test_cancel_order_releases_assignment_and_marks_order_cancelled(
        self,
        mock_validate_can_cancel: Any,
        mock_get_current_assignment: Any,
        mock_lock_order: Any,
        mock_create_timeline_event: Any,
    ) -> None:
        order = self._make_order(status="completed")
        assignment = self._make_assignment()

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = assignment

        result = OrderCancellationService.cancel_order(
            order=order,
            cancelled_by=self.staff_user,
            reason="Client requested cancellation",
            refund_destination=(
                OrderCancellationService.REFUND_DESTINATION_WALLET
            ),
            triggered_by=self.staff_user,
            notes="Handled by support",
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, "cancelled")
        self.assertIsNotNone(order.cancelled_at)
        self.assertEqual(order.cancelled_by, self.staff_user)
        self.assertEqual(
            order.cancellation_reason,
            "Client requested cancellation",
        )

        assignment.save.assert_called_once_with(
            update_fields=[
                "status",
                "is_current",
                "released_at",
                "release_reason",
                "updated_at",
            ]
        )
        self.assertEqual(assignment.status, "released")
        self.assertFalse(assignment.is_current)
        self.assertIsNotNone(assignment.released_at)
        self.assertEqual(
            assignment.release_reason,
            "order_cancelled:Client requested cancellation",
        )

        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "cancelled_at",
                "cancelled_by",
                "cancellation_reason",
                "updated_at",
            ]
        )

        mock_validate_can_cancel.assert_called_once_with(order=order)

        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "refund_destination"
            ],
            OrderCancellationService.REFUND_DESTINATION_WALLET,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "released_assignment_id"
            ],
            assignment.pk,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "released_writer_id"
            ],
            self.writer.pk,
        )

    @patch.object(OrderCancellationService, "_create_timeline_event")
    @patch.object(OrderCancellationService, "_lock_order")
    @patch(
        "orders.services.order_cancellation_service.OrderStaffingStore.get_current_assignment"
    )
    @patch(
        "orders.services.order_cancellation_service.OrderCancellationPolicy.validate_can_cancel"
    )
    def test_cancel_order_without_assignment_still_cancels_order(
        self,
        mock_validate_can_cancel: Any,
        mock_get_current_assignment: Any,
        mock_lock_order: Any,
        mock_create_timeline_event: Any,
    ) -> None:
        order = self._make_order(status="in_progress")

        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        result = OrderCancellationService.cancel_order(
            order=order,
            cancelled_by=self.staff_user,
            reason="Ops cancellation",
            refund_destination=(
                OrderCancellationService.REFUND_DESTINATION_EXTERNAL
            ),
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, "cancelled")
        self.assertIsNotNone(order.cancelled_at)

        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "cancelled_at",
                "cancelled_by",
                "cancellation_reason",
                "updated_at",
            ]
        )

        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "released_assignment_id"
            ],
            None,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "released_writer_id"
            ],
            None,
        )

    def test_validate_refund_destination_accepts_wallet(self) -> None:
        OrderCancellationService._validate_refund_destination(
            refund_destination=(
                OrderCancellationService.REFUND_DESTINATION_WALLET
            )
        )

    def test_validate_refund_destination_accepts_external_gateway(self) -> None:
        OrderCancellationService._validate_refund_destination(
            refund_destination=(
                OrderCancellationService.REFUND_DESTINATION_EXTERNAL
            )
        )

    def test_validate_refund_destination_raises_for_invalid_value(self) -> None:
        with self.assertRaisesMessage(
            ValueError,
            "refund_destination must be 'wallet' or 'external_gateway'.",
        ):
            OrderCancellationService._validate_refund_destination(
                refund_destination="bank_transfer"
            )

    def test_validate_actor_website_raises_for_cross_tenant_actor(self) -> None:
        order = self._make_order()

        with self.assertRaisesMessage(
            ValueError,
            "Actor website must match order website.",
        ):
            OrderCancellationService._validate_actor_website(
                actor=self.foreign_user,
                order=order,
            )

    @patch.object(OrderCancellationService, "_lock_order")
    @patch(
        "orders.services.order_cancellation_service.OrderStaffingStore.get_current_assignment"
    )
    @patch(
        "orders.services.order_cancellation_service.OrderCancellationPolicy.validate_can_cancel",
        side_effect=ValidationError("Approved orders cannot be cancelled."),
    )
    def test_cancel_order_raises_when_policy_blocks(
        self,
        mock_validate_can_cancel: Any,
        mock_get_current_assignment: Any,
        mock_lock_order: Any,
    ) -> None:
        order = self._make_order(status="completed", approved_at="set")
        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        with self.assertRaisesMessage(
            ValidationError,
            "Approved orders cannot be cancelled.",
        ):
            OrderCancellationService.cancel_order(
                order=order,
                cancelled_by=self.staff_user,
                reason="Too late",
                refund_destination=(
                    OrderCancellationService.REFUND_DESTINATION_WALLET
                ),
            )

    @patch.object(OrderCancellationService, "_create_timeline_event")
    @patch.object(OrderCancellationService, "_lock_order")
    @patch(
        "orders.services.order_cancellation_service.OrderStaffingStore.get_current_assignment"
    )
    @patch(
        "orders.services.order_cancellation_service.OrderCancellationPolicy.validate_can_cancel"
    )
    def test_cancel_order_records_triggered_by_on_timeline(
        self,
        mock_validate_can_cancel: Any,
        mock_get_current_assignment: Any,
        mock_lock_order: Any,
        mock_create_timeline_event: Any,
    ) -> None:
        order = self._make_order(status="submitted")
        mock_lock_order.return_value = order
        mock_get_current_assignment.return_value = None

        OrderCancellationService.cancel_order(
            order=order,
            cancelled_by=self.staff_user,
            reason="Client changed mind",
            refund_destination=(
                OrderCancellationService.REFUND_DESTINATION_WALLET
            ),
            triggered_by=self.client_user,
        )

        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["actor"],
            self.client_user,
        )