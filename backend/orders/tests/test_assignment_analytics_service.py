"""
Tests for AssignmentAnalyticsService
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from orders.models import Order, WriterAssignmentAcceptance
from orders.services.assignment_analytics_service import AssignmentAnalyticsService
from orders.order_enums import OrderStatus
from websites.models import Website
from order_configs.models import PaperType, Subject, TypeOfWork
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel

User = get_user_model()


class AssignmentAnalyticsServiceTestCase(TestCase):
    """Test cases for AssignmentAnalyticsService."""
    
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
            max_orders=5
        )
        
        # Create writers
        self.writer1 = User.objects.create_user(
            username='writer1',
            email='writer1@test.com',
            role='writer',
            website=self.website
        )
        self.writer1_profile = WriterProfile.objects.create(
            user=self.writer1,
            website=self.website,
            writer_level=self.writer_level
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
            writer_level=self.writer_level
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
        
        # Create orders with assignments
        self.now = timezone.now()
        self.start_date = self.now - timedelta(days=30)
        self.end_date = self.now
    
    def test_get_assignment_success_rates(self):
        """Test getting assignment success rates."""
        # Create orders with different assignment outcomes
        order1 = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Order 1',
            status=OrderStatus.IN_PROGRESS.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=5,
            total_cost=50.00,
            assigned_writer=self.writer1
        )
        
        # Accepted assignment
        WriterAssignmentAcceptance.objects.create(
            website=self.website,
            order=order1,
            writer=self.writer1,
            assigned_by=self.admin_user,
            status='accepted',
            assigned_at=self.now - timedelta(days=5),
            responded_at=self.now - timedelta(days=4)
        )
        
        order2 = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Order 2',
            status=OrderStatus.AVAILABLE.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=5,
            total_cost=50.00,
            assigned_writer=self.writer2
        )
        
        # Rejected assignment
        WriterAssignmentAcceptance.objects.create(
            website=self.website,
            order=order2,
            writer=self.writer2,
            assigned_by=self.admin_user,
            status='rejected',
            assigned_at=self.now - timedelta(days=3),
            responded_at=self.now - timedelta(days=2),
            reason='Too busy'
        )
        
        order3 = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Order 3',
            status=OrderStatus.PENDING_WRITER_ASSIGNMENT.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=5,
            total_cost=50.00,
            assigned_writer=self.writer1
        )
        
        # Pending assignment
        WriterAssignmentAcceptance.objects.create(
            website=self.website,
            order=order3,
            writer=self.writer1,
            assigned_by=self.admin_user,
            status='pending',
            assigned_at=self.now - timedelta(days=1)
        )
        
        service = AssignmentAnalyticsService()
        rates = service.get_assignment_success_rates(
            website=self.website,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self.assertEqual(rates['total_assignments'], 3)
        self.assertEqual(rates['accepted'], 1)
        self.assertEqual(rates['rejected'], 1)
        self.assertEqual(rates['pending'], 1)
        self.assertAlmostEqual(rates['success_rate'], 33.33, places=1)
        self.assertAlmostEqual(rates['rejection_rate'], 33.33, places=1)
    
    def test_get_acceptance_times(self):
        """Test getting acceptance time metrics."""
        order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Order 1',
            status=OrderStatus.IN_PROGRESS.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=5,
            total_cost=50.00,
            assigned_writer=self.writer1
        )
        
        # Create acceptance with known time difference
        assigned_at = self.now - timedelta(hours=5)
        responded_at = self.now - timedelta(hours=2)
        
        WriterAssignmentAcceptance.objects.create(
            website=self.website,
            order=order,
            writer=self.writer1,
            assigned_by=self.admin_user,
            status='accepted',
            assigned_at=assigned_at,
            responded_at=responded_at
        )
        
        service = AssignmentAnalyticsService()
        times = service.get_acceptance_times(
            website=self.website,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self.assertGreater(times['average_hours'], 0)
        self.assertGreater(times['median_hours'], 0)
        self.assertIn('distribution', times)
    
    def test_get_rejection_reasons(self):
        """Test getting rejection reasons."""
        order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='Order 1',
            status=OrderStatus.AVAILABLE.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=5,
            total_cost=50.00,
            assigned_writer=self.writer1
        )
        
        # Create rejections with different reasons
        reasons = ['Too busy', 'Too busy', 'Not my expertise', 'Not available']
        for reason in reasons:
            WriterAssignmentAcceptance.objects.create(
                website=self.website,
                order=order,
                writer=self.writer1,
                assigned_by=self.admin_user,
                status='rejected',
                assigned_at=self.now - timedelta(days=1),
                responded_at=self.now - timedelta(hours=12),
                reason=reason
            )
        
        service = AssignmentAnalyticsService()
        rejection_data = service.get_rejection_reasons(
            website=self.website,
            start_date=self.start_date,
            end_date=self.end_date,
            limit=10
        )
        
        self.assertGreater(len(rejection_data), 0)
        # "Too busy" should appear twice
        too_busy = next((r for r in rejection_data if 'busy' in r['reason'].lower()), None)
        if too_busy:
            self.assertGreaterEqual(too_busy['count'], 2)
    
    def test_get_writer_performance(self):
        """Test getting writer performance metrics."""
        # Create assignments for writer1
        for i in range(5):
            order = Order.objects.create(
                website=self.website,
                client=self.client_user,
                topic=f'Order {i}',
                status=OrderStatus.IN_PROGRESS.value if i < 3 else OrderStatus.AVAILABLE.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                assigned_writer=self.writer1
            )
            
            status = 'accepted' if i < 3 else 'rejected'
            WriterAssignmentAcceptance.objects.create(
                website=self.website,
                order=order,
                writer=self.writer1,
                assigned_by=self.admin_user,
                status=status,
                assigned_at=self.now - timedelta(days=i+1),
                responded_at=self.now - timedelta(days=i) if status == 'accepted' else None
            )
        
        service = AssignmentAnalyticsService()
        performance = service.get_writer_performance(
            writer_id=self.writer1.id,
            website=self.website,
            start_date=self.start_date,
            end_date=self.end_date
        )
        
        self.assertEqual(performance['total_assignments'], 5)
        self.assertEqual(performance['accepted'], 3)
        self.assertEqual(performance['rejected'], 2)
        self.assertAlmostEqual(performance['acceptance_rate'], 60.0, places=1)
    
    def test_get_assignment_trends(self):
        """Test getting assignment trends over time."""
        # Create assignments on different dates
        for i in range(5):
            order = Order.objects.create(
                website=self.website,
                client=self.client_user,
                topic=f'Order {i}',
                status=OrderStatus.IN_PROGRESS.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00,
                assigned_writer=self.writer1
            )
            
            WriterAssignmentAcceptance.objects.create(
                website=self.website,
                order=order,
                writer=self.writer1,
                assigned_by=self.admin_user,
                status='accepted',
                assigned_at=self.now - timedelta(days=i),
                responded_at=self.now - timedelta(days=i-1)
            )
        
        service = AssignmentAnalyticsService()
        trends = service.get_assignment_trends(
            website=self.website,
            start_date=self.start_date,
            end_date=self.end_date,
            group_by='day'
        )
        
        self.assertGreater(len(trends), 0)
        # Each trend entry should have required fields
        for trend in trends:
            self.assertIn('period', trend)
            self.assertIn('total', trend)
            self.assertIn('accepted', trend)
            self.assertIn('rejected', trend)

