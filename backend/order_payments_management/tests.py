from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    OrderPayment, Refund, PaymentDispute, PaymentLog,
    PaymentNotification, PaymentReminderSettings, DiscountUsage
)
from discounts.models import Discount

User = get_user_model()


class TransactionTests(TestCase):
    """Tests for transaction-related operations (payments, refunds, split payments)."""

    def setUp(self):
        """Create test users, orders, payments, and discounts."""
        self.client_user = User.objects.create_user(
            username="client", email="client@example.com", password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.client = APIClient()
        self.admin_client = APIClient()
        self.client.force_authenticate(user=self.client_user)
        self.admin_client.force_authenticate(user=self.admin_user)

        self.discount = Discount.objects.create(
            code="TEST10", discount_type="fixed", value=10, is_active=True
        )

        self.payment = OrderPayment.objects.create(
            client=self.client_user,
            payment_type="standard",
            transaction_id="TXN123",
            original_amount=100,
            discounted_amount=90,
            discount=self.discount,
            status="completed",
            payment_method="credit_card",
            date_processed=timezone.now(),
        )

        self.refund = Refund.objects.create(
            payment=self.payment,
            client=self.client_user,
            amount=50,
            refund_method="wallet",
            status="processed",
            processed_by=self.admin_user,
            processed_at=timezone.now(),
        )

    def test_list_transactions(self):
        """Test if a client can retrieve their transactions."""
        response = self.client.get("/api/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)  # Ensure transactions exist

    def test_admin_can_view_all_transactions(self):
        """Ensure an admin can retrieve all transactions."""
        response = self.admin_client.get("/api/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_client_cannot_see_other_users_transactions(self):
        """Ensure clients only see their own transactions."""
        other_client = User.objects.create_user(
            username="other_client", email="other@example.com", password="password123"
        )
        other_api_client = APIClient()
        other_api_client.force_authenticate(user=other_client)

        response = other_api_client.get("/api/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should be empty

    def test_refund_transaction(self):
        """Test if refunds appear in transaction history."""
        response = self.client.get("/api/transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refund_found = any(tx["transaction_type"] == "refund" for tx in response.data)
        self.assertTrue(refund_found, "Refund should be in transactions.")

    def test_admin_can_issue_refund(self):
        """Ensure admins can create refunds."""
        refund_data = {
            "payment": self.payment.id,
            "amount": 30,
            "refund_method": "wallet",
        }
        response = self.admin_client.post("/api/refunds/", refund_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_client_cannot_issue_refund(self):
        """Clients should NOT be able to create refunds."""
        refund_data = {
            "payment": self.payment.id,
            "amount": 30,
            "refund_method": "wallet",
        }
        response = self.client.post("/api/refunds/", refund_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentDisputeTests(TestCase):
    """Tests for payment dispute functionality."""

    def setUp(self):
        """Create test data for disputes."""
        self.client_user = User.objects.create_user(
            username="client", email="client@example.com", password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.client = APIClient()
        self.admin_client = APIClient()
        self.client.force_authenticate(user=self.client_user)
        self.admin_client.force_authenticate(user=self.admin_user)

        self.payment = OrderPayment.objects.create(
            client=self.client_user,
            payment_type="standard",
            transaction_id="TXN456",
            original_amount=120,
            discounted_amount=110,
            status="completed",
            payment_method="paypal",
            date_processed=timezone.now(),
        )

        self.dispute = PaymentDispute.objects.create(
            payment=self.payment,
            client=self.client_user,
            reason="Unauthorized transaction",
            status="pending",
        )

    def test_client_can_file_dispute(self):
        """Test if a client can create a dispute."""
        dispute_data = {
            "payment": self.payment.id,
            "reason": "Incorrect charge",
        }
        response = self.client.post("/api/payment-disputes/", dispute_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_resolve_dispute(self):
        """Ensure admin can resolve a dispute."""
        response = self.admin_client.patch(
            f"/api/payment-disputes/{self.dispute.id}/", {"status": "resolved"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.dispute.refresh_from_db()
        self.assertEqual(self.dispute.status, "resolved")

    def test_client_cannot_resolve_dispute(self):
        """Clients should not be able to resolve disputes."""
        response = self.client.patch(
            f"/api/payment-disputes/{self.dispute.id}/", {"status": "resolved"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentNotificationTests(TestCase):
    """Tests for payment notifications."""

    def setUp(self):
        """Create test notifications."""
        self.client_user = User.objects.create_user(
            username="client", email="client@example.com", password="password123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.client_user)

        self.payment = OrderPayment.objects.create(
            client=self.client_user,
            payment_type="standard",
            transaction_id="TXN789",
            original_amount=150,
            discounted_amount=140,
            status="completed",
            payment_method="stripe",
            date_processed=timezone.now(),
        )

        self.notification = PaymentNotification.objects.create(
            user=self.client_user,
            payment=self.payment,
            message="Your payment was successful!",
        )

    def test_client_can_retrieve_notifications(self):
        """Test if clients can view their notifications."""
        response = self.client.get("/api/payment-notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_client_can_mark_notification_as_read(self):
        """Test marking notifications as read."""
        response = self.client.patch(
            f"/api/payment-notifications/{self.notification.id}/",
            {"is_read": True},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)


class PaymentReminderSettingsTests(TestCase):
    """Tests for payment reminder settings."""

    def setUp(self):
        """Create test admin and reminder settings."""
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        self.reminder_settings = PaymentReminderSettings.objects.create(
            first_reminder_hours=12, final_reminder_hours=3
        )

    def test_admin_can_update_reminder_settings(self):
        """Ensure admin can modify reminder settings."""
        response = self.admin_client.patch(
            f"/api/payment-reminder-settings/{self.reminder_settings.id}/",
            {"first_reminder_hours": 10},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.reminder_settings.refresh_from_db()
        self.assertEqual(self.reminder_settings.first_reminder_hours, 10)