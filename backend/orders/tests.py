from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Order
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from orders.models import Order
from users.models import User
from datetime import timedelta

User = get_user_model()
class OrderDeadlineExtensionTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(email="client@example.com", role="client")
        self.writer_user = User.objects.create_user(email="writer@example.com", role="writer")
        self.support_user = User.objects.create_user(email="support@example.com", role="support")
        
        self.order = Order.objects.create(
            client=self.client_user,
            writer=self.writer_user,
            status="in_progress",
            deadline=timezone.now() + timedelta(days=2)
        )

        self.url = reverse("orders:extend-deadline", kwargs={"pk": self.order.id})

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_deadline_in_past_returns_400(self):
        self.authenticate(self.client_user)
        past_deadline = timezone.now() - timedelta(days=1)
        response = self.client.post(self.url, {"new_deadline": past_deadline.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_deadline", response.data)

    def test_non_owner_cannot_extend_deadline(self):
        self.authenticate(self.writer_user)
        future_deadline = timezone.now() + timedelta(days=3)
        response = self.client.post(self.url, {"new_deadline": future_deadline.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_can_extend_deadline(self):
        self.authenticate(self.support_user)
        new_deadline = timezone.now() + timedelta(days=5)
        response = self.client.post(self.url, {"new_deadline": new_deadline.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertAlmostEqual(self.order.deadline, new_deadline, delta=timedelta(seconds=1))

    def test_client_can_extend_their_own_order(self):
        self.authenticate(self.client_user)
        new_deadline = timezone.now() + timedelta(days=4)
        response = self.client.post(self.url, {"new_deadline": new_deadline.isoformat()})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertAlmostEqual(self.order.deadline, new_deadline, delta=timedelta(seconds=1))

    def test_missing_deadline_returns_400(self):
        self.authenticate(self.client_user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_deadline", response.data)


class OrderModelTest(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(email='client@example.com', password='testpass')
        self.writer_user = User.objects.create_user(email='writer@example.com', password='testpass')

        self.order = Order.objects.create(
            title="Sample Order",
            topic="Mathematics",
            instructions="Detailed instructions for the order",
            academic_level="Undergraduate",
            type_of_work="writing",
            number_of_pages=5,
            client_deadline="2025-02-01 12:00:00",
            client=self.client_user,
            total_price=150.00
        )

    def test_order_creation(self):
        self.assertEqual(self.order.title, "Sample Order")
        self.assertEqual(self.order.topic, "Mathematics")
        self.assertEqual(self.order.client.email, "client@example.com")

    def test_default_values(self):
        self.assertEqual(self.order.status, "pending")
        self.assertFalse(self.order.is_high_value)
        self.assertFalse(self.order.is_urgent)