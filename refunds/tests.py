from django.test import TestCase
from django.contrib.auth import get_user_model
from refunds.models import Refund
from order_payments_management.models import OrderPayment
from writer_payments_management.models import WriterPayment
from writer_management.models import WriterLevel
from orders.models import Order
from .services import process_refund
from django.core.exceptions import ValidationError


class RefundTests(TestCase):
    def setUp(self):
        # Create a user (client)
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="password"
        )
        
        # Create an order payment (payment reference)
        self.order_payment = OrderPayment.objects.create(
            order=Order.objects.create(),
            discounted_amount=100.0,
            amount_paid=100.0,
            payment_method="credit_card",
        )
        
        # Create the refund object
        self.refund = Refund.objects.create(
            order_payment=self.order_payment,
            client=self.user,
            wallet_amount=50.0,
            external_amount=20.0,
            refund_method="wallet",
        )

    def test_refund_total_amount(self):
        # Testing total amount of the refund
        self.assertEqual(self.refund.total_amount(), 70.0)

    def test_process_refund(self):
        # Mock the admin user
        admin_user = get_user_model().objects.create_user(
            username="admin", email="admin@example.com", password="adminpassword"
        )

        # Process the refund
        self.refund.status = Refund.PENDING
        self.refund.save()

        process_refund(self.refund, admin_user)

        # Check refund status change
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, Refund.PROCESSED)

        # Check if writer earnings deduction happened
        writer_payment = WriterPayment.objects.first()
        self.assertIsNotNone(writer_payment)
        self.assertTrue(writer_payment.amount_paid < 100.0)

        # Verify logs (you can check whether AdminLog and PaymentLog are created)
        # You would need to mock the logging or inspect the database for logs


        def test_invalid_refund_amount(self):
            # Trying to refund more than the amount paid
            self.refund.wallet_amount = 200.0  # Greater than order_payment.amount_paid
            self.refund.save()

            with self.assertRaises(ValidationError):
                process_refund(self.refund, admin_user)
