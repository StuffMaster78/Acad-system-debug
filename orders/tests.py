from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()

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