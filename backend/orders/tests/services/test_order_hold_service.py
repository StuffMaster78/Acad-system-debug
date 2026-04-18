from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from orders.models.orders.constants import (
    ORDER_HOLD_STATUS_ACTIVE,
    ORDER_HOLD_STATUS_CANCELLED,
    ORDER_HOLD_STATUS_PENDING,
    ORDER_HOLD_STATUS_RELEASED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_ON_HOLD,
    ORDER_STATUS_READY_FOR_STAFFING,
    ORDER_TIMELINE_EVENT_HOLD_ACTIVATED,
    ORDER_TIMELINE_EVENT_HOLD_RELEASED,
    ORDER_TIMELINE_EVENT_HOLD_REQUESTED,
)
from orders.services.order_hold_service import OrderHoldService


class OrderHoldServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)
        self.client_user = SimpleNamespace(pk=10, website_id=1)
        self.writer = SimpleNamespace(pk=20, website_id=1)
        self.staff_user = SimpleNamespace(pk=30, website_id=1)
        self.other_user = SimpleNamespace(pk=31, website_id=1)

    def _make_order(
        self,
        *,
        status: str = ORDER_STATUS_IN_PROGRESS,
    ) -> MagicMock:
        order = MagicMock()
        order.pk = 100
        order.website = self.website
        order.client = self.client_user
        order.status = status
        order.save = MagicMock()
        return order

    def _make_hold(
        self,
        *,
        order,
        requested_by,
        status: str = ORDER_HOLD_STATUS_PENDING,
    ) -> MagicMock:
        hold = MagicMock()
        hold.pk = 200
        hold.order = order
        hold.website = order.website
        hold.requested_by = requested_by
        hold.status = status
        hold.reason = "Need clarification"
        hold.internal_notes = ""
        hold.remaining_seconds = None
        hold.save = MagicMock()
        return hold

    @patch.object(OrderHoldService, "_create_timeline_event")
    @patch.object(OrderHoldService, "_validate_actor_website")
    @patch.object(OrderHoldService, "_ensure_no_open_hold")
    @patch.object(OrderHoldService, "_ensure_can_request_hold")
    @patch.object(OrderHoldService, "_lock_order")
    @patch("orders.services.order_hold_service.OrderHold.objects.create")
    def test_request_hold_creates_pending_hold(
        self,
        mock_hold_create,
        mock_lock_order,
        mock_ensure_can_request_hold,
        mock_ensure_no_open_hold,
        mock_validate_actor_website,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order()
        hold = self._make_hold(order=order, requested_by=self.writer)

        mock_lock_order.return_value = order
        mock_hold_create.return_value = hold

        result = OrderHoldService.request_hold(
            order=order,
            requested_by=self.writer,
            reason="Need clarification",
            internal_notes="Waiting on client answer",
            triggered_by=self.writer,
        )

        self.assertEqual(result, hold)
        mock_hold_create.assert_called_once_with(
            website=order.website,
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_PENDING,
            reason="Need clarification",
            internal_notes="Waiting on client answer",
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_HOLD_REQUESTED,
        )

    @patch.object(OrderHoldService, "_create_timeline_event")
    @patch.object(OrderHoldService, "_validate_actor_website")
    @patch.object(OrderHoldService, "_ensure_pending_hold")
    @patch.object(OrderHoldService, "_lock_order")
    @patch.object(OrderHoldService, "_lock_hold")
    def test_activate_hold_moves_order_to_on_hold(
        self,
        mock_lock_hold,
        mock_lock_order,
        mock_ensure_pending_hold,
        mock_validate_actor_website,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_IN_PROGRESS)
        hold = self._make_hold(
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_PENDING,
        )

        mock_lock_hold.return_value = hold
        mock_lock_order.return_value = order

        result = OrderHoldService.activate_hold(
            hold=hold,
            activated_by=self.staff_user,
            remaining_seconds=7200,
            internal_notes="Approved hold",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, hold)
        self.assertEqual(hold.status, ORDER_HOLD_STATUS_ACTIVE)
        self.assertEqual(hold.placed_by, self.staff_user)
        self.assertIsNotNone(hold.placed_at)
        self.assertEqual(hold.remaining_seconds, 7200)
        self.assertEqual(hold.internal_notes, "Approved hold")
        hold.save.assert_called_once()
        self.assertEqual(order.status, ORDER_STATUS_ON_HOLD)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_HOLD_ACTIVATED,
        )

    @patch.object(OrderHoldService, "_validate_actor_website")
    @patch.object(OrderHoldService, "_ensure_pending_hold")
    @patch.object(OrderHoldService, "_lock_order")
    @patch.object(OrderHoldService, "_lock_hold")
    def test_activate_hold_rejects_negative_remaining_seconds(
        self,
        mock_lock_hold,
        mock_lock_order,
        mock_ensure_pending_hold,
        mock_validate_actor_website,
    ) -> None:
        order = self._make_order()
        hold = self._make_hold(order=order, requested_by=self.writer)

        mock_lock_hold.return_value = hold
        mock_lock_order.return_value = order

        with self.assertRaisesMessage(
            ValidationError,
            "remaining_seconds cannot be negative.",
        ):
            OrderHoldService.activate_hold(
                hold=hold,
                activated_by=self.staff_user,
                remaining_seconds=-1,
            )

    @patch.object(OrderHoldService, "_create_timeline_event")
    @patch.object(OrderHoldService, "_validate_actor_website")
    @patch.object(OrderHoldService, "_ensure_active_hold")
    @patch.object(OrderHoldService, "_lock_order")
    @patch.object(OrderHoldService, "_lock_hold")
    def test_release_hold_moves_order_back_to_in_progress(
        self,
        mock_lock_hold,
        mock_lock_order,
        mock_ensure_active_hold,
        mock_validate_actor_website,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_ON_HOLD)
        hold = self._make_hold(
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_ACTIVE,
        )
        hold.remaining_seconds = 3600

        mock_lock_hold.return_value = hold
        mock_lock_order.return_value = order

        result = OrderHoldService.release_hold(
            hold=hold,
            released_by=self.staff_user,
            internal_notes="Issue resolved",
            triggered_by=self.staff_user,
        )

        self.assertEqual(result, order)
        self.assertEqual(hold.status, ORDER_HOLD_STATUS_RELEASED)
        self.assertEqual(hold.released_by, self.staff_user)
        self.assertIsNotNone(hold.released_at)
        self.assertEqual(hold.internal_notes, "Issue resolved")
        hold.save.assert_called_once()
        self.assertEqual(order.status, ORDER_STATUS_IN_PROGRESS)
        order.save.assert_called_once_with(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        self.assertEqual(
            mock_create_timeline_event.call_args.kwargs["event_type"],
            ORDER_TIMELINE_EVENT_HOLD_RELEASED,
        )

    @patch.object(OrderHoldService, "_create_timeline_event")
    @patch.object(OrderHoldService, "_ensure_pending_hold")
    @patch.object(OrderHoldService, "_lock_hold")
    def test_cancel_hold_request_marks_hold_cancelled(
        self,
        mock_lock_hold,
        mock_ensure_pending_hold,
        mock_create_timeline_event,
    ) -> None:
        order = self._make_order()
        hold = self._make_hold(
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_PENDING,
        )

        mock_lock_hold.return_value = hold

        result = OrderHoldService.cancel_hold_request(
            hold=hold,
            cancelled_by=self.writer,
            internal_notes="No longer needed",
            triggered_by=self.writer,
        )

        self.assertEqual(result, hold)
        self.assertEqual(hold.status, ORDER_HOLD_STATUS_CANCELLED)
        self.assertIsNotNone(hold.cancelled_at)
        self.assertEqual(hold.internal_notes, "No longer needed")
        hold.save.assert_called_once()

    @patch.object(OrderHoldService, "_ensure_pending_hold")
    @patch.object(OrderHoldService, "_lock_hold")
    def test_cancel_hold_request_blocks_non_requester(
        self,
        mock_lock_hold,
        mock_ensure_pending_hold,
    ) -> None:
        order = self._make_order()
        hold = self._make_hold(
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_PENDING,
        )

        mock_lock_hold.return_value = hold

        with self.assertRaisesMessage(
            ValidationError,
            "Only the requester can cancel this hold request.",
        ):
            OrderHoldService.cancel_hold_request(
                hold=hold,
                cancelled_by=self.other_user,
            )

    def test_ensure_can_request_hold_blocks_non_in_progress_order(self) -> None:
        order = self._make_order(status=ORDER_STATUS_READY_FOR_STAFFING)

        with self.assertRaisesMessage(
            ValidationError,
            "Only in progress orders can request hold.",
        ):
            OrderHoldService._ensure_can_request_hold(order)

    @patch(
        "orders.services.order_hold_service.OrderHold.objects.select_for_update"
    )
    def test_ensure_no_open_hold_raises_when_pending_exists(
        self,
        mock_select_for_update,
    ) -> None:
        order = self._make_order()
        mock_select_for_update.return_value.filter.return_value.exists.return_value = True

        with self.assertRaisesMessage(
            ValidationError,
            "Order already has an open hold request.",
        ):
            OrderHoldService._ensure_no_open_hold(order)

    def test_ensure_pending_hold_raises_for_non_pending_hold(self) -> None:
        order = self._make_order()
        hold = self._make_hold(
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_ACTIVE,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only pending hold requests can be reviewed.",
        ):
            OrderHoldService._ensure_pending_hold(hold)

    def test_ensure_active_hold_raises_for_non_active_hold(self) -> None:
        order = self._make_order()
        hold = self._make_hold(
            order=order,
            requested_by=self.writer,
            status=ORDER_HOLD_STATUS_PENDING,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Only active holds can be released.",
        ):
            OrderHoldService._ensure_active_hold(hold)

    def test_validate_actor_website_raises_for_cross_tenant_actor(self) -> None:
        order = self._make_order()
        foreign_actor = SimpleNamespace(pk=99, website_id=999)

        with self.assertRaisesMessage(
            ValidationError,
            "Actor website must match order website.",
        ):
            OrderHoldService._validate_actor_website(
                actor=foreign_actor,
                order=order,
            )