from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    WriterProfile, WriterLevel, WriterConfig, WriterOrderRequest, WriterOrderTake,
    WriterPayoutPreference, WriterPayment, PaymentHistory, WriterEarningsHistory,
    WriterReward, Probation, WriterPenalty, WriterSuspension, WriterSupportTicket,
    WriterDeadlineExtensionRequest, WriterOrderHoldRequest, WriterOrderReopenRequest
)
from orders.models import Order

User = get_user_model()


class WriterTests(TestCase):
    """
    Tests for writer management features.
    """

    def setUp(self):
        """Setup users, writer profiles, and test data."""
        self.client = APIClient()

        # Create users
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="password", role="admin")
        self.writer_user = User.objects.create_user(username="writer1", email="writer1@test.com", password="password", role="writer")

        # Create writer profile
        self.writer_profile = WriterProfile.objects.create(
            user=self.writer_user,
            registration_id="W12345",
            email=self.writer_user.email,
            writer_level=None,
            completed_orders=10,
            total_earnings=500.00,
        )

        # Create a writer level
        self.writer_level = WriterLevel.objects.create(
            name="Beginner",
            max_orders=5,
            base_pay_per_page=10.00
        )

        # Assign the level to the writer
        self.writer_profile.writer_level = self.writer_level
        self.writer_profile.save()

        # Create test order
        self.order = Order.objects.create(
            title="Test Order",
            description="Test Description",
            deadline=now(),
            price=100.00
        )

        # Create Writer Config
        self.writer_config = WriterConfig.objects.create(
            takes_enabled=True,
            max_requests_per_writer=3
        )

    ### ---------------- Writer Profile Tests ---------------- ###

    def test_writer_profile_creation(self):
        """Ensure writer profile is created correctly."""
        self.assertEqual(self.writer_profile.user.username, "writer1")
        self.assertEqual(self.writer_profile.registration_id, "W12345")
        self.assertEqual(self.writer_profile.total_earnings, 500.00)

    def test_get_writer_profile(self):
        """Ensure writer profile can be retrieved via API."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/api/writers/{self.writer_profile.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["registration_id"], "W12345")

    ### ---------------- Order Request & Take Tests ---------------- ###

    def test_writer_order_request(self):
        """Test that a writer can request an order."""
        self.client.force_authenticate(user=self.writer_user)
        response = self.client.post("/api/writer-order-requests/", {"writer": self.writer_profile.id, "order": self.order.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WriterOrderRequest.objects.filter(writer=self.writer_profile, order=self.order).exists())

    def test_writer_order_take_limit(self):
        """Test that a writer cannot take more orders than their level allows."""
        self.client.force_authenticate(user=self.writer_user)

        # Take the maximum allowed orders
        for _ in range(self.writer_level.max_orders):
            WriterOrderTake.objects.create(writer=self.writer_profile, order=self.order)

        # Try to take another order
        response = self.client.post("/api/writer-order-takes/", {"writer": self.writer_profile.id, "order": self.order.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("max take limit", str(response.data).lower())

    ### ---------------- Admin Control Tests ---------------- ###

    def test_admin_can_approve_order_request(self):
        """Test that an admin can approve a writer order request."""
        self.client.force_authenticate(user=self.admin_user)
        order_request = WriterOrderRequest.objects.create(writer=self.writer_profile, order=self.order)
        response = self.client.post(f"/api/writer-order-requests/{order_request.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_request.refresh_from_db()
        self.assertTrue(order_request.approved)

    def test_admin_can_enable_disable_takes(self):
        """Test that an admin can enable/disable order takes."""
        self.client.force_authenticate(user=self.admin_user)

        # Disable takes
        response = self.client.patch(f"/api/writer-configs/{self.writer_config.id}/", {"takes_enabled": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.writer_config.refresh_from_db()
        self.assertFalse(self.writer_config.takes_enabled)

    ### ---------------- Payment & Earnings Tests ---------------- ###

    def test_writer_payment_creation(self):
        """Ensure writer payments are created correctly."""
        payment = WriterPayment.objects.create(writer=self.writer_profile, amount=200.00)
        self.assertEqual(payment.amount, 200.00)

    def test_payment_history_logging(self):
        """Ensure that payments are logged in history."""
        payment = PaymentHistory.objects.create(writer=self.writer_profile, amount=150.00)
        self.assertTrue(PaymentHistory.objects.filter(writer=self.writer_profile, amount=150.00).exists())

    ### ---------------- Reward & Penalty Tests ---------------- ###

    def test_writer_earns_reward(self):
        """Ensure a writer can receive a reward."""
        reward = WriterReward.objects.create(writer=self.writer_profile, title="Top Performer", prize="Bonus $50")
        self.assertEqual(reward.prize, "Bonus $50")

    def test_writer_receives_penalty(self):
        """Ensure penalties are assigned correctly."""
        penalty = WriterPenalty.objects.create(writer=self.writer_profile, reason="Late Submission", amount_deducted=20.00)
        self.assertEqual(penalty.amount_deducted, 20.00)

    ### ---------------- Support & Requests ---------------- ###

    def test_writer_creates_support_ticket(self):
        """Test that a writer can create a support ticket."""
        self.client.force_authenticate(user=self.writer_user)
        response = self.client.post("/api/writer-support-tickets/", {"writer": self.writer_profile.id, "category": "Payment Issue", "description": "Payment not received."})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WriterSupportTicket.objects.filter(writer=self.writer_profile, category="Payment Issue").exists())

    def test_writer_requests_deadline_extension(self):
        """Test that a writer can request a deadline extension."""
        self.client.force_authenticate(user=self.writer_user)
        response = self.client.post("/api/writer-deadline-extension-requests/", {"writer": self.writer_profile.id, "order": self.order.id, "old_deadline": now(), "requested_deadline": now(), "reason": "Need more time"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WriterDeadlineExtensionRequest.objects.filter(writer=self.writer_profile, order=self.order).exists())

    ### ---------------- Leave & Suspension Tests ---------------- ###

    def test_admin_can_suspend_writer(self):
        """Ensure an admin can suspend a writer."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post("/api/writer-suspensions/", {"writer": self.writer_profile.id, "reason": "Violation of terms"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WriterSuspension.objects.filter(writer=self.writer_profile).exists())

    def test_admin_can_lift_suspension(self):
        """Ensure an admin can lift a writer's suspension."""
        self.client.force_authenticate(user=self.admin_user)
        suspension = WriterSuspension.objects.create(writer=self.writer_profile, reason="Test suspension")
        response = self.client.patch(f"/api/writer-suspensions/{suspension.id}/", {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        suspension.refresh_from_db()
        self.assertFalse(suspension.is_active)