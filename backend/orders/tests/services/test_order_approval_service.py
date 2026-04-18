from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from django.utils import timezone

from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_SUBMITTED,
    ORDER_TIMELINE_EVENT_APPROVED,
)
from orders.services.order_approval_service import OrderApprovalService


class OrderApprovalServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.staff_user = SimpleNamespace(pk=30, website_id=1)

    def _make_order(self, **kwargs: Any) -> Any:
        defaults = {
            "pk": 1,
            "website": self.website,
            "status": ORDER_STATUS_COMPLETED,
            "completed_at": timezone.now() - timedelta(days=2),
            "approved_at": None,
            "save": MagicMock(),
        }
        defaults.update(kwargs)
        return cast(Any, SimpleNamespace(**defaults))

    @patch.object(OrderApprovalService, "_create_timeline_event")
    @patch.object(OrderApprovalService, "_lock_order")
    def test_approve_order_sets_approved_at_only(
        self,
        mock_lock_order: Any,
        mock_create_timeline_event: Any,
    ) -> None:
        order = self._make_order()
        original_completed_at = order.completed_at
        mock_lock_order.return_value = order

        result = OrderApprovalService.approve_order(
            order=order,
            approved_by=self.client_user,
            triggered_by=self.client_user,
        )

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_COMPLETED)
        self.assertIsNotNone(order.approved_at)
        self.assertEqual(order.completed_at, original_completed_at)
        order.save.assert_called_once_with(
            update_fields=[
                "approved_at",
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_APPROVED,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "approval_mode"
            ],
            "explicit",
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "approved_by_id"
            ],
            self.client_user.pk,
        )

    @patch.object(OrderApprovalService, "_lock_order")
    def test_approve_order_preserves_completed_at(
        self,
        mock_lock_order: Any,
    ) -> None:
        completed_at = timezone.now() - timedelta(days=1)
        order = self._make_order(completed_at=completed_at)
        mock_lock_order.return_value = order

        OrderApprovalService.approve_order(
            order=order,
            approved_by=self.staff_user,
        )

        self.assertEqual(order.completed_at, completed_at)

    @patch.object(OrderApprovalService, "_create_timeline_event")
    @patch.object(OrderApprovalService, "_lock_order")
    def test_auto_approve_order_sets_approved_at_only(
        self,
        mock_lock_order: Any,
        mock_create_timeline_event: Any,
    ) -> None:
        order = self._make_order(
            completed_at=timezone.now()
            - timedelta(days=OrderApprovalService.AUTO_APPROVAL_WINDOW_DAYS + 1)
        )
        original_completed_at = order.completed_at
        mock_lock_order.return_value = order

        result = OrderApprovalService.auto_approve_order(order=order)

        self.assertEqual(result, order)
        self.assertEqual(order.status, ORDER_STATUS_COMPLETED)
        self.assertIsNotNone(order.approved_at)
        self.assertEqual(order.completed_at, original_completed_at)
        order.save.assert_called_once_with(
            update_fields=[
                "approved_at",
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_APPROVED,
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["metadata"][
                "approval_mode"
            ],
            "auto",
        )

    def test_can_auto_approve_returns_true_for_completed_unapproved_order_past_window(
        self,
    ) -> None:
        order = self._make_order(
            completed_at=timezone.now()
            - timedelta(days=OrderApprovalService.AUTO_APPROVAL_WINDOW_DAYS + 1)
        )

        result = OrderApprovalService.can_auto_approve(order=order)

        self.assertTrue(result)

    def test_can_auto_approve_returns_false_when_not_completed(self) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        result = OrderApprovalService.can_auto_approve(order=order)

        self.assertFalse(result)

    def test_can_auto_approve_returns_false_when_already_approved(self) -> None:
        order = self._make_order(approved_at=timezone.now())

        result = OrderApprovalService.can_auto_approve(order=order)

        self.assertFalse(result)

    def test_can_auto_approve_returns_false_when_completed_at_missing(self) -> None:
        order = self._make_order(completed_at=None)

        result = OrderApprovalService.can_auto_approve(order=order)

        self.assertFalse(result)

    def test_can_auto_approve_returns_false_when_window_not_elapsed(self) -> None:
        order = self._make_order(
            completed_at=timezone.now()
            - timedelta(days=OrderApprovalService.AUTO_APPROVAL_WINDOW_DAYS - 1)
        )

        result = OrderApprovalService.can_auto_approve(order=order)

        self.assertFalse(result)

    def test_ensure_can_be_approved_blocks_non_completed_order(self) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        with self.assertRaisesMessage(
            ValidationError,
            "You can only approve a completed order.",
        ):
            OrderApprovalService._ensure_can_be_approved(order)

    def test_ensure_can_be_approved_blocks_already_approved_order(self) -> None:
        order = self._make_order(approved_at=timezone.now())

        with self.assertRaisesMessage(
            ValidationError,
            "Order has already been approved.",
        ):
            OrderApprovalService._ensure_can_be_approved(order)

    def test_ensure_can_auto_approve_blocks_ineligible_order(self) -> None:
        order = self._make_order(
            completed_at=timezone.now()
            - timedelta(days=OrderApprovalService.AUTO_APPROVAL_WINDOW_DAYS - 1)
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Order is not eligible for automatic approval.",
        ):
            OrderApprovalService._ensure_can_auto_approve(order)