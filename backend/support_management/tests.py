from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from order_configs.models import PaperType, Subject, TypeOfWork
from orders.models.orders import Order
from websites.models.websites import Website
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement,
    SupportMessage, EscalationLog, SupportWorkloadTracker,
    PaymentIssueLog, FAQManagement, SupportDashboard,
    SupportMessageAccess, SupportPermission, FAQCategory,
)

User = get_user_model()
SUPPORT_API = "/api/v1/support/"


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
        self.website = Website.objects.create(
            name="Support Test",
            domain="https://support.test",
            is_active=True,
        )
        self.client_user.website = self.website
        self.client_user.save(update_fields=["website"])

        self.support_profile = SupportProfile.objects.create(
            user=self.support_user,
            name="Test Support",
            registration_id="SUP-TEST",
            email="support@test.com",
            website=self.website,
        )
        SupportPermission.objects.get_or_create(
            support_staff=self.support_profile,
        )
        SupportMessageAccess.objects.get_or_create(
            support_staff=self.support_user,
        )
        self.faq_category = FAQCategory.objects.create(
            name="General",
            category_type="client",
        )
        self.paper_type = PaperType.objects.create(
            website=self.website,
            name="Research Paper",
        )
        self.subject = Subject.objects.create(
            website=self.website,
            name="Business",
        )
        self.type_of_work = TypeOfWork.objects.create(
            website=self.website,
            name="Essay",
        )
        self.order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic="Support test order",
            status="on_hold",
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            total_price=10,
            client_deadline=timezone.now() + timedelta(days=3),
        )
        self.support_order_action = SupportOrderManagement.objects.create(
            support_staff=self.support_user,
            order=self.order,
            action="restore_in_progress",
            reason="Test restore",
        )
        self.client.force_authenticate(user=self.support_user)


# 🚀 **2️⃣ Test Support Profile API**
class SupportProfileTestCase(SupportBaseTestCase):
    """Tests support profile CRUD operations."""

    def test_get_support_profile(self):
        """Ensure support users can retrieve their profile."""
        response = self.client.get(f"{SUPPORT_API}support-profiles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_access_all_profiles(self):
        """Ensure admin can access all support profiles."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"{SUPPORT_API}support-profiles/")
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
        response = self.client.get(f"{SUPPORT_API}notifications/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_notification_as_read(self):
        """Ensure support agents can mark notifications as read."""
        response = self.client.post(f"{SUPPORT_API}notifications/mark_as_read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 🚀 **4️⃣ Test Order Management API**
class SupportOrderManagementTestCase(SupportBaseTestCase):
    """Tests support managing order statuses."""

    def test_restore_order_to_progress(self):
        """Ensure support agents can restore orders to progress."""
        response = self.client.post(
            f"{SUPPORT_API}order-management/{self.support_order_action.id}/restore_to_progress/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# 🚀 **5️⃣ Test Support Messaging API**
class SupportMessageTestCase(SupportBaseTestCase):
    """Tests support messages between clients, writers, and admins."""

    def test_send_message(self):
        """Ensure support agents can send messages."""
        data = {
            "order": self.order.id,
            "sender": self.support_user.id,
            "recipient": self.client_user.id,
            "message": "Hello, how can I assist you?"
        }
        response = self.client.post(f"{SUPPORT_API}messages/", data)
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
        response = self.client.post(f"{SUPPORT_API}escalations/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **7️⃣ Test Payment Issue Log API**
class PaymentIssueLogTestCase(SupportBaseTestCase):
    """Tests tracking of payment-related issues."""

    def test_report_payment_issue(self):
        """Ensure support can report a payment issue."""
        data = {
            "order": self.order.id,
            "reported_by": self.support_user.id,
            "issue_type": "unpaid_order",
            "description": "Client hasn't paid yet."
        }
        response = self.client.post(f"{SUPPORT_API}payment-issues/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **8️⃣ Test FAQ Management API**
class FAQManagementTestCase(SupportBaseTestCase):
    """Tests support agents managing FAQs."""

    def test_create_faq(self):
        """Ensure support can create FAQs."""
        data = {
            "category": self.faq_category.id,
            "question": "How do I reset my password?",
            "answer": "Go to settings and click 'Reset Password'.",
            "created_by": self.support_user.id
        }
        response = self.client.post(f"{SUPPORT_API}faqs/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# 🚀 **9️⃣ Test Support Dashboard API**
class SupportDashboardTestCase(SupportBaseTestCase):
    """Tests support agents accessing their dashboard."""

    def test_get_dashboard(self):
        """Ensure support agents can access their dashboard."""
        response = self.client.get(f"{SUPPORT_API}dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_dashboard(self):
        """Ensure dashboards can be refreshed."""
        response = self.client.post(f"{SUPPORT_API}dashboard/refresh_dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
