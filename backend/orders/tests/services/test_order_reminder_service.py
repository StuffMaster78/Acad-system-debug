from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from django.test import SimpleTestCase
from django.utils import timezone

from orders.models.orders.constants import (
    ORDER_STATUS_COMPLETED,
    ORDER_STATUS_IN_PROGRESS,
    ORDER_STATUS_SUBMITTED,
)
from orders.services.order_reminder_service import OrderReminderService


class OrderReminderServiceTests(SimpleTestCase):
    def setUp(self) -> None:
        self.website = SimpleNamespace(pk=1)

    def _make_order(self, **kwargs: Any) -> Any:
        defaults = {
            "pk": 1,
            "website": self.website,
            "status": ORDER_STATUS_IN_PROGRESS,
            "last_writer_acknowledged_at": None,
            "submitted_at": None,
            "completed_at": None,
            "approved_at": None,
            "writer_deadline": timezone.now() + timedelta(hours=5),
            "updated_at": timezone.now() - timedelta(hours=3),
            "client": SimpleNamespace(pk=10),
        }
        defaults.update(kwargs)
        return cast(Any, SimpleNamespace(**defaults))

    # -------------------------
    # Writer acknowledgement
    # -------------------------

    @patch.object(
        OrderReminderService,
        "_get_current_assignment_time",
        return_value=timezone.now() - timedelta(hours=3),
    )
    def test_should_send_writer_acknowledgement_reminder_true(
        self,
        mock_assignment_time: Any,
    ) -> None:
        order = self._make_order()

        result = OrderReminderService.should_send_writer_acknowledgement_reminder(
            order=order
        )

        self.assertTrue(result)

    @patch.object(
        OrderReminderService,
        "_get_current_assignment_time",
        return_value=timezone.now() - timedelta(hours=3),
    )
    def test_should_send_writer_acknowledgement_reminder_false_when_acknowledged(
        self,
        mock_assignment_time: Any,
    ) -> None:
        order = self._make_order(
            last_writer_acknowledged_at=timezone.now()
        )

        result = OrderReminderService.should_send_writer_acknowledgement_reminder(
            order=order
        )

        self.assertFalse(result)

    def test_should_send_writer_acknowledgement_reminder_false_when_not_in_progress(
        self,
    ) -> None:
        order = self._make_order(status=ORDER_STATUS_SUBMITTED)

        result = OrderReminderService.should_send_writer_acknowledgement_reminder(
            order=order
        )

        self.assertFalse(result)

    @patch.object(
        OrderReminderService,
        "_get_current_assignment_time",
        return_value=timezone.now() - timedelta(minutes=30),
    )
    def test_should_send_writer_acknowledgement_reminder_false_before_grace_period(
        self,
        mock_assignment_time: Any,
    ) -> None:
        order = self._make_order()

        result = OrderReminderService.should_send_writer_acknowledgement_reminder(
            order=order
        )

        self.assertFalse(result)

    def test_should_send_writer_acknowledgement_reminder_uses_updated_at_fallback(
        self,
    ) -> None:
        order = self._make_order(
            updated_at=timezone.now() - timedelta(hours=3)
        )

        with patch.object(
            OrderReminderService,
            "_get_current_assignment_time",
            return_value=None,
        ):
            result = OrderReminderService.should_send_writer_acknowledgement_reminder(
                order=order
            )

        self.assertTrue(result)

    # -------------------------
    # Approval reminder
    # -------------------------

    def test_should_send_approval_reminder_true_for_completed_unapproved_order(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(hours=2),
            approved_at=None,
        )

        result = OrderReminderService.should_send_approval_reminder(
            order=order
        )

        self.assertTrue(result)

    def test_should_send_approval_reminder_false_when_approved(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(hours=2),
            approved_at=timezone.now(),
        )

        result = OrderReminderService.should_send_approval_reminder(
            order=order
        )

        self.assertFalse(result)

    def test_should_send_approval_reminder_false_when_not_completed(self) -> None:
        order = self._make_order(
            status=ORDER_STATUS_SUBMITTED,
            completed_at=None,
        )

        result = OrderReminderService.should_send_approval_reminder(
            order=order
        )

        self.assertFalse(result)

    def test_should_send_approval_reminder_false_when_completed_at_missing(
        self,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=None,
            approved_at=None,
        )

        result = OrderReminderService.should_send_approval_reminder(
            order=order
        )

        self.assertFalse(result)

    # -------------------------
    # Sending reminders
    # -------------------------

    @patch("orders.services.order_reminder_service.NotificationService.notify")
    def test_send_approval_reminder_for_completed_unapproved_order(
        self,
        mock_notify: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(hours=2),
        )

        result = OrderReminderService.send_approval_reminder(order=order)

        self.assertTrue(result)
        mock_notify.assert_called_once()

    @patch("orders.services.order_reminder_service.NotificationService.notify")
    def test_send_approval_reminder_returns_false_when_client_missing(
        self,
        mock_notify: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(hours=2),
            client=None,
        )

        result = OrderReminderService.send_approval_reminder(order=order)

        self.assertFalse(result)
        mock_notify.assert_not_called()

    # -------------------------
    # Operational reminder
    # -------------------------

    @patch(
        "orders.services.order_reminder_service.OrderMonitoringService.build_operational_state"
    )
    @patch("orders.services.order_reminder_service.NotificationService.notify")
    def test_send_operational_writer_reminder_for_critical_order(
        self,
        mock_notify: Any,
        mock_state: Any,
    ) -> None:
        order = self._make_order()
        writer = SimpleNamespace(pk=2)

        mock_state.return_value = SimpleNamespace(
            state_label="critical",
            seconds_to_writer_deadline=1200,
        )

        result = OrderReminderService.send_operational_writer_reminder(
            order=order,
            writer=writer,
        )

        self.assertTrue(result)
        mock_notify.assert_called_once()

    # -------------------------
    # Auto approval
    # -------------------------

    @patch(
        "orders.services.order_reminder_service.OrderApprovalService.can_auto_approve"
    )
    def test_should_auto_approve_true(
        self,
        mock_can_auto_approve: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=5),
        )
        mock_can_auto_approve.return_value = True

        result = OrderReminderService.should_auto_approve(order=order)

        self.assertTrue(result)

    @patch(
        "orders.services.order_reminder_service.OrderApprovalService.can_auto_approve"
    )
    def test_should_auto_approve_false(
        self,
        mock_can_auto_approve: Any,
    ) -> None:
        order = self._make_order(
            status=ORDER_STATUS_COMPLETED,
            completed_at=timezone.now() - timedelta(days=1),
        )
        mock_can_auto_approve.return_value = False

        result = OrderReminderService.should_auto_approve(order=order)

        self.assertFalse(result)