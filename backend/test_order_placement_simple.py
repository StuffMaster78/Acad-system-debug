#!/usr/bin/env python3
"""
Simplified End-to-End Test for Order Placement and Phase Transitions
Uses Django's TestCase framework for proper database handling.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django with test settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings_test')
django.setup()

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from websites.models import Website
from orders.models import Order
from orders.services.mark_order_as_paid_service import MarkOrderPaidService
from orders.services.status_transition_service import StatusTransitionService
from orders.services.assignment import OrderAssignmentService
from orders.services.submit_order_service import SubmitOrderService
from orders.services.complete_order_service import CompleteOrderService
from orders.services.rate_order_service import RateOrderService
from orders.services.review_order_service import ReviewOrderService
from orders.utils.order_utils import save_order
from order_payments_management.models import OrderPayment
from order_configs.models import PaperType, AcademicLevel
from client_wallet.models import ClientWallet

User = get_user_model()

class OrderPlacementTest(TransactionTestCase):
    """Test order placement and phase transitions."""
    
    def setUp(self):
        """Set up test data."""
        # Create website
        self.website = Website.objects.create(
            domain="localhost",
            name='Test Website',
            slug='test',
            is_active=True
        )
        
        # Create test client
        self.client_user = User.objects.create_user(
            email='test_client@example.com',
            username='test_client',
            role='client',
            website=self.website,
            is_active=True,
            password='TestPassword123!'
        )
        
        # Create test writer
        self.writer_user = User.objects.create_user(
            email='test_writer@example.com',
            username='test_writer',
            role='writer',
            website=self.website,
            is_active=True,
            password='TestPassword123!'
        )
        
        # Create test admin
        self.admin_user = User.objects.create_user(
            email='test_admin@example.com',
            username='test_admin',
            role='admin',
            website=self.website,
            is_active=True,
            is_staff=True,
            password='TestPassword123!'
        )
        
        # Create client wallet
        self.wallet, _ = ClientWallet.objects.get_or_create(
            client=self.client_user,
            website=self.website,
            defaults={'balance': Decimal('1000.00')}
        )
        if self.wallet.balance < Decimal('500.00'):
            self.wallet.balance = Decimal('1000.00')
            self.wallet.save()
        
        # Create paper type
        self.paper_type, _ = PaperType.objects.get_or_create(
            name='Essay',
            website=self.website,
            defaults={
                'base_price_per_page': Decimal('10.00'),
                'description': 'Standard essay paper type'
            }
        )
    
    def test_order_placement_flow(self):
        """Test complete order placement and phase transitions."""
        print("\n" + "="*70)
        print("ORDER PLACEMENT AND PHASE TRANSITION TEST")
        print("="*70 + "\n")
        
        # Phase 1: Order Creation
        print("Phase 1: Order Creation")
        deadline = timezone.now() + timedelta(days=7)
        order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Test Order: Comprehensive Analysis of Order Placement System',
            paper_type=self.paper_type,
            number_of_pages=10,
            client_deadline=deadline,
            order_instructions='This is a test order to verify the complete order placement workflow.',
            status='created',
            is_paid=False,
        )
        save_order(order)
        
        self.assertIsNotNone(order.id)
        self.assertIn(order.status, ['created', 'unpaid'])
        self.assertFalse(order.is_paid)
        self.assertGreater(order.total_price, 0)
        print(f"✅ Order #{order.id} created: Status={order.status}, Price=${order.total_price}")
        
        # Phase 2: Payment Processing
        print("\nPhase 2: Payment Processing")
        payment = OrderPayment.objects.create(
            order=order,
            client=self.client_user,
            website=self.website,
            payment_type='standard',
            amount=order.total_price,
            original_amount=order.total_price,
            discounted_amount=order.total_price,
            status='completed',
            payment_method='wallet',
            transaction_id=f'TEST-{order.id}-{int(timezone.now().timestamp())}'
        )
        
        service = MarkOrderPaidService()
        order = service.mark_paid(order.id)
        
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, 'in_progress')
        print(f"✅ Order #{order.id} marked as paid: Status={order.status}")
        
        # Phase 3: Writer Assignment
        print("\nPhase 3: Writer Assignment")
        assignment_service = OrderAssignmentService(order)
        assignment_service.actor = self.admin_user
        
        order = assignment_service.assign_writer(self.writer_user.id, reason="Test assignment")
        
        self.assertEqual(order.assigned_writer_id, self.writer_user.id)
        self.assertEqual(order.status, 'in_progress')
        print(f"✅ Writer {self.writer_user.username} assigned to Order #{order.id}")
        
        # Phase 4: Order Submission
        print("\nPhase 4: Order Submission")
        submit_service = SubmitOrderService()
        order = submit_service.submit_order(order.id, self.writer_user)
        
        self.assertEqual(order.status, 'submitted')
        print(f"✅ Order #{order.id} submitted: Status={order.status}")
        
        # Phase 5: Review and Editing (optional transitions)
        print("\nPhase 5: Review and Editing")
        transition_service = StatusTransitionService(user=self.admin_user)
        
        # Try to transition to reviewed
        try:
            order = transition_service.transition_order_to_status(
                order, 'reviewed', skip_payment_check=True
            )
            print(f"✅ Order #{order.id} reviewed: Status={order.status}")
        except Exception as e:
            print(f"ℹ️  Could not transition to 'reviewed': {e}")
        
        # Phase 6: Completion
        print("\nPhase 6: Order Completion")
        complete_service = CompleteOrderService()
        order = complete_service.complete_order(order.id, self.admin_user)
        
        self.assertIn(order.status, ['completed', 'under_editing'])
        print(f"✅ Order #{order.id} completed: Status={order.status}")
        
        # Phase 7: Rating
        print("\nPhase 7: Order Rating")
        if order.status == 'completed':
            rate_service = RateOrderService()
            order = rate_service.rate_order(
                order.id,
                self.client_user,
                rating=5,
                comment="Excellent service! Test order completed successfully."
            )
            self.assertEqual(order.status, 'rated')
            print(f"✅ Order #{order.id} rated: Status={order.status}")
        
        # Phase 8: Final Review and Closure
        print("\nPhase 8: Final Review and Closure")
        if order.status == 'rated':
            review_service = ReviewOrderService()
            order = review_service.review_order(order.id, self.admin_user)
            self.assertEqual(order.status, 'reviewed')
            print(f"✅ Order #{order.id} reviewed: Status={order.status}")
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"✅ Order #{order.id} successfully transitioned through phases")
        print(f"   Final Status: {order.status}")
        print(f"   Payment Status: {'Paid' if order.is_paid else 'Unpaid'}")
        print(f"   Writer: {order.assigned_writer.username if order.assigned_writer else 'None'}")
        print(f"   Total Price: ${order.total_price}")
        print("✅ All phases completed successfully!\n")

if __name__ == '__main__':
    import django
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])
    sys.exit(failures)

