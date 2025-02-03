from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement,
    SupportMessage, EscalationLog, SupportWorkloadTracker,
    PaymentIssueLog, FAQManagement, SupportDashboard
)

User = get_user_model()


# 🚀 **1️⃣ Base Setup for Test Cases**
class SupportBaseTestCase(APITestCase):
    """Sets up common test users and data for all support-related tests."""

    def setUp(self):
        """Create test users and support profiles."""
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@test.com", password="admin123", role="admin"
        )
        self.support_user = User.objects.create_user(
            username="support", email="support@test.com", password="support123", role="support"
        )
        self.client_user = User.objects.create_user(
            username="client", email="client@test.com", password="client123", role="client"
        )

        self.support_profile = SupportProfile.objects.create(
            user=self.support_user, name="Test Support", email="support@test.com"
        )
        self.client.force_authenticate(user=self.support_user)


# 🚀 **2️⃣ Test Support Profile API**
class SupportProfileTestCase(SupportBaseTestCase):
    """Tests support profile CRUD operations."""

    def test_get_support_profile(self):
        """Ensure support users can retrieve their profile."""
        response = self.client.get("/api/support-profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_access_all_profiles(self):
        """Ensure admin can access all support profiles."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/support-profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 🚀 **3️⃣ Test Support Notifications API**
class SupportNotificationTestCase(SupportBaseTestCase):
    """Tests notifications for support staff."""

    def setUp(self):
        super().setUp()
        self.notification = SupportNotification.objects.create(
            support_staff=self.support_profile,
            message="New support task assigned",
            priority="high"
        )

    def test_get_notifications(self):
        """Ensure support agents can retrieve notifications."""
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_as_read(self):
        """Ensure support agents can mark notifications as read."""
        response = self.client.post("/api/notifications/mark_as_read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 🚀 **4️⃣ Test Order Management API**
class SupportOrderManagementTestCase(SupportBaseTestCase):
    """Tests support managing order statuses."""

    def test_restore_order_to_progress(self):
        """Ensure support agents can restore orders to progress."""
        response = self.client.post("/api/order-management/1/restore_to_progress/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 🚀 **5️⃣ Test Support Messaging API**
class SupportMessageTestCase(SupportBaseTestCase):
    """Tests support messages between clients, writers, and admins."""

    def test_send_message(self):
        """Ensure support agents can send messages."""
        data = {
            "order": 1,
            "sender": self.support_user.id,
            "recipient": self.client_user.id,
            "message": "Hello, how can I assist you?"
        }
        response = self.client.post("/api/messages/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **6️⃣ Test Escalation Log API**
class EscalationLogTestCase(SupportBaseTestCase):
    """Tests support agents escalating cases."""

    def test_escalate_issue(self):
        """Ensure support agents can escalate an issue."""
        data = {
            "escalated_by": self.support_user.id,
            "action_type": "blacklist_client",
            "target_user": self.client_user.id,
            "reason": "Client violated terms"
        }
        response = self.client.post("/api/escalations/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **7️⃣ Test Payment Issue Log API**
class PaymentIssueLogTestCase(SupportBaseTestCase):
    """Tests tracking of payment-related issues."""

    def test_report_payment_issue(self):
        """Ensure support can report a payment issue."""
        data = {
            "order": 1,
            "reported_by": self.support_user.id,
            "issue_type": "unpaid_order",
            "description": "Client hasn't paid yet."
        }
        response = self.client.post("/api/payment-issues/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **8️⃣ Test FAQ Management API**
class FAQManagementTestCase(SupportBaseTestCase):
    """Tests support agents managing FAQs."""

    def test_create_faq(self):
        """Ensure support can create FAQs."""
        data = {
            "category": 1,
            "question": "How do I reset my password?",
            "answer": "Go to settings and click 'Reset Password'.",
            "created_by": self.support_user.id
        }
        response = self.client.post("/api/faqs/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **9️⃣ Test Support Dashboard API**
class SupportDashboardTestCase(SupportBaseTestCase):
    """Tests support agents accessing their dashboard."""

    def test_get_dashboard(self):
        """Ensure support agents can access their dashboard."""
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_dashboard(self):
        """Ensure dashboards can be refreshed."""
        response = self.client.post("/api/dashboard/refresh_dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)