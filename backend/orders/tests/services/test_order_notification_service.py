"""
Tests for OrderNotificationService.

Verifies that each notify_* method calls NotificationService.notify()
with the correct event_key and recipient without errors. Uses
unittest.mock to avoid hitting the real notification pipeline.
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.services.order_notification_service import OrderNotificationService
from websites.models.websites import Website

User = get_user_model()

NOTIFY_PATH = (
    "orders.services.order_notification_service."
    "NotificationService.notify"
)


def _mock_order(website, client=None, writer=None, status="in_progress"):
    order = MagicMock()
    order.pk = 1
    order.website = website
    order.client = client
    order.status = status
    order.topic = "Test topic"
    order.reference = "ORD-001"
    order.assigned_writer = writer
    return order


def _mock_interest(order, writer):
    interest = MagicMock()
    interest.pk = 99
    interest.order = order
    interest.writer = writer
    return interest


class OrderNotificationServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Test", domain="ons.test")
        self.client_user = User.objects.create_user(
            username="client_ons", email="c@ons.test", password="pass", website=self.website,
        )
        self.writer_user = User.objects.create_user(
            username="writer_ons", email="w@ons.test", password="pass", website=self.website,
        )
        self.order = _mock_order(
            self.website, client=self.client_user, writer=self.writer_user,
        )

    # ── Lifecycle notifications ──────────────────────────────────────────

    @patch(NOTIFY_PATH)
    def test_notify_assigned_notifies_writer(self, mock_notify):
        OrderNotificationService.notify_order_assigned(
            order=self.order, writer_user=self.writer_user,
        )
        calls = mock_notify.call_args_list
        keys = [c.kwargs["event_key"] for c in calls]
        self.assertIn("order.assigned", keys)
        # Writer must be among recipients
        recipients = [c.kwargs["recipient"] for c in calls]
        self.assertIn(self.writer_user, recipients)

    @patch(NOTIFY_PATH)
    def test_notify_assigned_notifies_client_too(self, mock_notify):
        OrderNotificationService.notify_order_assigned(
            order=self.order, writer_user=self.writer_user,
        )
        recipients = [c.kwargs["recipient"] for c in mock_notify.call_args_list]
        self.assertIn(self.client_user, recipients)

    @patch(NOTIFY_PATH)
    def test_notify_submitted_notifies_client(self, mock_notify):
        OrderNotificationService.notify_order_submitted(
            order=self.order, submitted_by=self.writer_user,
        )
        recipients = [c.kwargs["recipient"] for c in mock_notify.call_args_list]
        self.assertIn(self.client_user, recipients)

    @patch(NOTIFY_PATH)
    def test_notify_approved_notifies_writer(self, mock_notify):
        with patch.object(
            OrderNotificationService, "_resolve_writer_user", return_value=self.writer_user,
        ):
            OrderNotificationService.notify_order_approved(
                order=self.order, approved_by=self.client_user,
            )
        recipients = [c.kwargs["recipient"] for c in mock_notify.call_args_list]
        self.assertIn(self.writer_user, recipients)

    @patch(NOTIFY_PATH)
    def test_notify_cancelled_notifies_both(self, mock_notify):
        with patch.object(
            OrderNotificationService, "_resolve_writer_user", return_value=self.writer_user,
        ):
            OrderNotificationService.notify_order_cancelled(
                order=self.order, cancelled_by=MagicMock(), reason="test",
            )
        recipients = [c.kwargs["recipient"] for c in mock_notify.call_args_list]
        self.assertIn(self.client_user, recipients)
        self.assertIn(self.writer_user, recipients)

    @patch(NOTIFY_PATH)
    def test_notify_completed_notifies_both(self, mock_notify):
        with patch.object(
            OrderNotificationService, "_resolve_writer_user", return_value=self.writer_user,
        ):
            OrderNotificationService.notify_order_completed(
                order=self.order, completed_by=MagicMock(),
            )
        recipients = [c.kwargs["recipient"] for c in mock_notify.call_args_list]
        self.assertIn(self.client_user, recipients)
        self.assertIn(self.writer_user, recipients)

    @patch(NOTIFY_PATH)
    def test_notify_revision_requested_uses_correct_event(self, mock_notify):
        with patch.object(
            OrderNotificationService, "_resolve_writer_user", return_value=self.writer_user,
        ):
            OrderNotificationService.notify_order_revision_requested(
                order=self.order, requested_by=self.client_user, reason="Needs rework",
            )
        keys = [c.kwargs["event_key"] for c in mock_notify.call_args_list]
        self.assertIn("order.revision_requested", keys)

    # ── Bid notifications ────────────────────────────────────────────────

    @patch(NOTIFY_PATH)
    def test_notify_bid_placed(self, mock_notify):
        interest = _mock_interest(self.order, self.writer_user)
        OrderNotificationService.notify_bid_placed(interest=interest)
        self.assertTrue(mock_notify.called)
        keys = [c.kwargs["event_key"] for c in mock_notify.call_args_list]
        self.assertIn("order.bid.placed", keys)

    @patch(NOTIFY_PATH)
    def test_notify_bid_accepted(self, mock_notify):
        interest = _mock_interest(self.order, self.writer_user)
        OrderNotificationService.notify_bid_accepted(interest=interest)
        keys = [c.kwargs["event_key"] for c in mock_notify.call_args_list]
        self.assertIn("order.bid.accepted", keys)

    @patch(NOTIFY_PATH)
    def test_notify_bid_rejected(self, mock_notify):
        interest = _mock_interest(self.order, self.writer_user)
        OrderNotificationService.notify_bid_rejected(interest=interest)
        keys = [c.kwargs["event_key"] for c in mock_notify.call_args_list]
        self.assertIn("order.bid.rejected", keys)

    # ── Hold / reopen ────────────────────────────────────────────────────

    @patch(NOTIFY_PATH)
    def test_notify_on_hold_notifies_both(self, mock_notify):
        hold = MagicMock()
        hold.pk = 5
        hold.reason = "Client request"
        with patch.object(
            OrderNotificationService, "_resolve_writer_user", return_value=self.writer_user,
        ):
            OrderNotificationService.notify_order_on_hold(
                order=self.order, hold=hold,
            )
        recipients = [c.kwargs["recipient"] for c in mock_notify.call_args_list]
        self.assertIn(self.client_user, recipients)
        self.assertIn(self.writer_user, recipients)

    # ── Resilience ───────────────────────────────────────────────────────

    @patch(NOTIFY_PATH, side_effect=Exception("boom"))
    def test_notify_swallows_exceptions(self, _):
        """Notification failures must never raise."""
        try:
            OrderNotificationService.notify_order_submitted(
                order=self.order, submitted_by=self.writer_user,
            )
        except Exception as exc:
            self.fail(f"notify_order_submitted raised {exc}")

    def test_resolve_writer_user_returns_none_gracefully(self):
        bad_order = MagicMock()
        bad_order.assigned_writer = property(lambda self: (_ for _ in ()).throw(Exception()))
        result = OrderNotificationService._resolve_writer_user(bad_order)
        self.assertIsNone(result)
