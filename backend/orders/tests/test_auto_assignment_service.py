"""
Tests for AutoAssignmentService
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, WriterAssignmentAcceptance
from orders.services.auto_assignment_service import AutoAssignmentService
from orders.order_enums import OrderStatus
from websites.models import Website
from order_configs.models import PaperType, Subject, TypeOfWork
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel

User = get_user_model()


class AutoAssignmentServiceTestCase(TestCase):
    """Test cases for AutoAssignmentService."""
    
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
            max_orders=5,
            max_requests_per_writer=3
        )
        
        # Create writers with different ratings
        self.writer1 = User.objects.create_user(
            username='writer1',
            email='writer1@test.com',
            role='writer',
            website=self.website
        )
        self.writer1_profile = WriterProfile.objects.create(
            user=self.writer1,
            website=self.website,
            writer_level=self.writer_level,
            is_available_for_auto_assignments=True
        )
        
        self.writer2 = User.objects.create_user(
            username='writer2',
            email='writer2@test.com',
            role='writer',
            website=self.website
        )
        self.writer2_profile = WriterProfile.objects.create(
            user=self.writer2,
            website=self.website,
            writer_level=self.writer_level,
            is_available_for_auto_assignments=True
        )
        
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
        
        # Create an available order
        self.order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Test Order',
            status=OrderStatus.AVAILABLE.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=5,
            total_cost=50.00,
            client_deadline=timezone.now() + timedelta(days=7)
        )
    
    def test_find_best_writer_no_writers(self):
        """Test finding best writer when no writers available."""
        service = AutoAssignmentService(self.order, self.admin_user)
        writer = service.find_best_writer()
        self.assertIsNone(writer)
    
    def test_find_best_writer_with_rating_filter(self):
        """Test finding best writer with minimum rating filter."""
        # Create completed orders to give writer1 a rating
        for i in range(5):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'Completed Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                rating=4.5
            )
        
        service = AutoAssignmentService(self.order, self.admin_user)
        writer = service.find_best_writer(min_rating=4.0)
        self.assertEqual(writer, self.writer1)
    
    def test_find_best_writer_excludes_overloaded(self):
        """Test that writers at capacity are excluded."""
        # Fill writer1's capacity
        for i in range(5):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'Active Order {i}',
                status=OrderStatus.IN_PROGRESS.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00
            )
        
        service = AutoAssignmentService(self.order, self.admin_user)
        writer = service.find_best_writer()
        # Should not return writer1 (at capacity)
        self.assertNotEqual(writer, self.writer1)
    
    def test_auto_assign_success(self):
        """Test successful auto-assignment."""
        # Give writer1 some completed orders for rating
        for i in range(3):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'Completed {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                rating=4.5
            )
        
        service = AutoAssignmentService(self.order, self.admin_user)
        result = service.auto_assign(
            min_rating=4.0,
            max_candidates=10,
            reason='Auto-assigned for testing'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result['assigned_writer'], self.writer1)
        self.assertEqual(result['order'].id, self.order.id)
        
        # Verify order status changed
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.PENDING_WRITER_ASSIGNMENT.value)
        self.assertEqual(self.order.assigned_writer, self.writer1)
        
        # Verify assignment acceptance record created
        acceptance = WriterAssignmentAcceptance.objects.get(order=self.order)
        self.assertEqual(acceptance.writer, self.writer1)
        self.assertEqual(acceptance.status, 'pending')
    
    def test_auto_assign_no_suitable_writer(self):
        """Test auto-assignment when no suitable writer found."""
        service = AutoAssignmentService(self.order, self.admin_user)
        result = service.auto_assign(
            min_rating=5.0,  # Very high rating requirement
            max_candidates=10
        )
        
        self.assertIsNone(result)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, OrderStatus.AVAILABLE.value)
        self.assertIsNone(self.order.assigned_writer)
    
    def test_auto_assign_with_subject_match(self):
        """Test auto-assignment with subject matching requirement."""
        # Give writer1 completed orders in same subject
        for i in range(3):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'History Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,  # Same subject
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                rating=4.5
            )
        
        # Give writer2 completed orders in different subject
        other_subject = Subject.objects.create(
            website=self.website,
            name='Math',
            base_price_multiplier=1.0
        )
        for i in range(3):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer2,
                assigned_writer=self.writer2,
                topic=f'Math Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=other_subject,  # Different subject
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                rating=4.5
            )
        
        service = AutoAssignmentService(self.order, self.admin_user)
        writer = service.find_best_writer(
            require_subject_match=True,
            min_rating=4.0
        )
        
        # Should prefer writer1 (has experience in same subject)
        self.assertEqual(writer, self.writer1)

