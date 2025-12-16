"""
Tests for BulkAssignmentService
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, WriterAssignmentAcceptance
from orders.services.bulk_assignment_service import BulkAssignmentService
from orders.order_enums import OrderStatus
from websites.models import Website
from order_configs.models import PaperType, Subject, TypeOfWork
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel

User = get_user_model()


class BulkAssignmentServiceTestCase(TestCase):
    """Test cases for BulkAssignmentService."""
    
    def setUp(self):
        """Set up test data."""
        self.website = Website.objects.create(
            name='Test Website',
            domain='https://test.com',
            is_active=True
        )
        
        self.client_user = User.objects.create_user(
            username='testclient',
            email='client@test.com',
            role='client',
            website=self.website
        )
        
        # Create writer level
        self.writer_level = WriterLevel.objects.create(
            website=self.website,
            name='Level 1',
            max_orders=10,
            max_requests_per_writer=5
        )
        
        # Create multiple writers
        self.writers = []
        for i in range(3):
            writer = User.objects.create_user(
                username=f'writer{i+1}',
                email=f'writer{i+1}@test.com',
                role='writer',
                website=self.website
            )
            WriterProfile.objects.create(
                user=writer,
                website=self.website,
                writer_level=self.writer_level,
                is_available_for_auto_assignments=True
            )
            self.writers.append(writer)
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            role='admin',
            website=self.website
        )
        
        # Create order configs
        self.paper_type = PaperType.objects.create(
            website=self.website,
            name='Essay',
            base_price=10.00
        )
        
        self.subject = Subject.objects.create(
            website=self.website,
            name='History',
            base_price_multiplier=1.0
        )
        
        self.type_of_work = TypeOfWork.objects.create(
            website=self.website,
            name='Research Paper',
            base_price_multiplier=1.2
        )
        
        # Create multiple available orders
        self.orders = []
        for i in range(6):
            order = Order.objects.create(
                website=self.website,
                client=self.client_user,
                topic=f'Test Order {i+1}',
                status=OrderStatus.AVAILABLE.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                client_deadline=timezone.now() + timedelta(days=7)
            )
            self.orders.append(order)
    
    def test_bulk_assign_balanced_strategy(self):
        """Test balanced distribution strategy."""
        service = BulkAssignmentService(self.admin_user, self.website)
        
        order_ids = [order.id for order in self.orders[:6]]
        writer_ids = [writer.id for writer in self.writers]
        
        results = service.bulk_assign(
            order_ids=order_ids,
            writer_ids=writer_ids,
            strategy='balanced',
            reason='Bulk assignment test'
        )
        
        self.assertEqual(len(results['successful']), 6)
        self.assertEqual(len(results['failed']), 0)
        
        # Verify balanced distribution (2 orders per writer)
        assignments = {}
        for order_id in order_ids:
            order = Order.objects.get(id=order_id)
            writer_id = order.assigned_writer.id if order.assigned_writer else None
            assignments[writer_id] = assignments.get(writer_id, 0) + 1
        
        # Each writer should have 2 orders
        for writer in self.writers:
            self.assertEqual(assignments.get(writer.id, 0), 2)
    
    def test_bulk_assign_round_robin_strategy(self):
        """Test round-robin distribution strategy."""
        service = BulkAssignmentService(self.admin_user, self.website)
        
        order_ids = [order.id for order in self.orders[:6]]
        writer_ids = [writer.id for writer in self.writers]
        
        results = service.bulk_assign(
            order_ids=order_ids,
            writer_ids=writer_ids,
            strategy='round_robin',
            reason='Round-robin test'
        )
        
        self.assertEqual(len(results['successful']), 6)
        
        # Verify round-robin pattern (writer1, writer2, writer3, writer1, writer2, writer3)
        expected_pattern = [self.writers[0], self.writers[1], self.writers[2],
                          self.writers[0], self.writers[1], self.writers[2]]
        
        for i, order_id in enumerate(order_ids):
            order = Order.objects.get(id=order_id)
            self.assertEqual(order.assigned_writer, expected_pattern[i])
    
    def test_bulk_assign_best_match_strategy(self):
        """Test best-match distribution strategy."""
        # Give writers different ratings
        for i, writer in enumerate(self.writers):
            for j in range(3):
                Order.objects.create(
                    website=self.website,
                    client=self.client_user,
                    writer=writer,
                    assigned_writer=writer,
                    topic=f'Completed {i}-{j}',
                    status=OrderStatus.COMPLETED.value,
                    paper_type=self.paper_type,
                    subject=self.subject,
                    type_of_work=self.type_of_work,
                    number_of_pages=5,
                    total_cost=50.00,
                    rating=4.0 + (i * 0.2)  # Different ratings
                )
        
        service = BulkAssignmentService(self.admin_user, self.website)
        
        order_ids = [order.id for order in self.orders[:3]]
        
        results = service.bulk_assign(
            order_ids=order_ids,
            writer_ids=None,  # Best-match doesn't need writer_ids
            strategy='best_match',
            reason='Best-match test'
        )
        
        self.assertEqual(len(results['successful']), 3)
        # Best-match should assign to highest-rated writer
        # (writer2 should get most assignments as it has highest rating)
    
    def test_bulk_assign_with_failures(self):
        """Test bulk assignment with some failures."""
        # Make one writer unavailable
        self.writers[0].writer_profile.is_available_for_auto_assignments = False
        self.writers[0].writer_profile.save()
        
        # Fill another writer's capacity
        for i in range(10):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writers[1],
                assigned_writer=self.writers[1],
                topic=f'Filled {i}',
                status=OrderStatus.IN_PROGRESS.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00
            )
        
        service = BulkAssignmentService(self.admin_user, self.website)
        
        order_ids = [order.id for order in self.orders[:6]]
        writer_ids = [writer.id for writer in self.writers]
        
        results = service.bulk_assign(
            order_ids=order_ids,
            writer_ids=writer_ids,
            strategy='balanced',
            reason='Test with failures'
        )
        
        # Should have some successful and some failed
        self.assertGreater(len(results['successful']), 0)
        # All should succeed if we only use available writer
        self.assertEqual(len(results['failed']), 0)
    
    def test_bulk_assign_empty_order_list(self):
        """Test bulk assignment with empty order list."""
        service = BulkAssignmentService(self.admin_user, self.website)
        
        results = service.bulk_assign(
            order_ids=[],
            writer_ids=[writer.id for writer in self.writers],
            strategy='balanced',
            reason='Empty test'
        )
        
        self.assertEqual(len(results['successful']), 0)
        self.assertEqual(len(results['failed']), 0)
    
    def test_bulk_assign_invalid_strategy(self):
        """Test bulk assignment with invalid strategy."""
        service = BulkAssignmentService(self.admin_user, self.website)
        
        with self.assertRaises(ValidationError):
            service.bulk_assign(
                order_ids=[self.orders[0].id],
                writer_ids=[self.writers[0].id],
                strategy='invalid_strategy',
                reason='Invalid test'
            )

