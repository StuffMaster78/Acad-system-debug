from django.test import TestCase
from users.models import User
from .models import WriterLevel, PaymentHistory, WriterProgress


class WriterManagementTests(TestCase):
    def setUp(self):
        self.writer_user = User.objects.create_user(
            username="test_writer", email="writer@test.com", password="password123", role="writer"
        )
        self.writer_level = WriterLevel.objects.create(
            name="Intermediate", base_pay_per_page=10.00, max_orders=10, min_rating=4.5
        )

    def test_writer_level_creation(self):
        self.assertEqual(WriterLevel.objects.count(), 1)

    def test_payment_history_creation(self):
        PaymentHistory.objects.create(writer=self.writer_user, amount=100.00, description="Monthly earnings")
        self.assertEqual(self.writer_user.payment_history.count(), 1)

    def test_writer_progress(self):
        progress = WriterProgress.objects.create(writer=self.writer_user, order_id=1, progress=50)
        self.assertEqual(progress.progress, 50)