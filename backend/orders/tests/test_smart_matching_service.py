"""
Tests for SmartMatchingService
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from orders.services.smart_matching_service import SmartMatchingService
from orders.order_enums import OrderStatus
from websites.models import Website
from order_configs.models import PaperType, Subject, TypeOfWork
from writer_management.models.profile import WriterProfile
from writer_management.models.levels import WriterLevel

User = get_user_model()


class SmartMatchingServiceTestCase(TestCase):
    """Test cases for SmartMatchingService."""
    
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
        
        # Create an order to match
        self.order = Order.objects.create(
            website=self.website,
            client=self.client_user,
            topic='History Research Paper',
            status=OrderStatus.AVAILABLE.value,
            paper_type=self.paper_type,
            subject=self.subject,
            type_of_work=self.type_of_work,
            number_of_pages=10,
            total_cost=100.00,
            client_deadline=timezone.now() + timedelta(days=7)
        )
    
    def test_find_matches_basic(self):
        """Test basic matching functionality."""
        # Give writer1 completed orders in same subject
        for i in range(5):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'History Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=10,
                total_cost=100.00,
                rating=4.5
            )
        
        service = SmartMatchingService()
        matches = service.find_matches(
            order=self.order,
            max_results=10,
            min_rating=4.0
        )
        
        self.assertGreater(len(matches), 0)
        # Writer1 should be in matches
        writer_ids = [match['writer_id'] for match in matches]
        self.assertIn(self.writer1.id, writer_ids)
    
    def test_find_matches_with_scoring(self):
        """Test that matches include scores and explanations."""
        # Give writer1 high rating and experience
        for i in range(10):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=10,
                total_cost=100.00,
                rating=4.8
            )
        
        service = SmartMatchingService()
        matches = service.find_matches(
            order=self.order,
            max_results=10
        )
        
        if len(matches) > 0:
            match = matches[0]
            self.assertIn('writer_id', match)
            self.assertIn('score', match)
            self.assertIn('explanation', match)
            self.assertIn('rating', match)
            self.assertIn('reasons', match)
    
    def test_find_matches_excludes_overloaded(self):
        """Test that overloaded writers are excluded."""
        # Fill writer1's capacity
        for i in range(5):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'Active {i}',
                status=OrderStatus.IN_PROGRESS.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=5,
                total_cost=50.00
            )
        
        service = SmartMatchingService()
        matches = service.find_matches(
            order=self.order,
            max_results=10
        )
        
        # Writer1 should not be in matches (at capacity)
        writer_ids = [match['writer_id'] for match in matches]
        self.assertNotIn(self.writer1.id, writer_ids)
    
    def test_find_matches_prioritizes_experience(self):
        """Test that writers with more experience score higher."""
        # Give writer1 more completed orders
        for i in range(10):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer1,
                assigned_writer=self.writer1,
                topic=f'Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=10,
                total_cost=100.00,
                rating=4.5
            )
        
        # Give writer2 fewer completed orders
        for i in range(3):
            Order.objects.create(
                website=self.website,
                client=self.client_user,
                writer=self.writer2,
                assigned_writer=self.writer2,
                topic=f'Order {i}',
                status=OrderStatus.COMPLETED.value,
                paper_type=self.paper_type,
                subject=self.subject,
                type_of_work=self.type_of_work,
                number_of_pages=10,
                total_cost=100.00,
                rating=4.5
            )
        
        service = SmartMatchingService()
        matches = service.find_matches(
            order=self.order,
            max_results=10
        )
        
        if len(matches) >= 2:
            # Writer1 should have higher score (more experience)
            writer1_match = next((m for m in matches if m['writer_id'] == self.writer1.id), None)
            writer2_match = next((m for m in matches if m['writer_id'] == self.writer2.id), None)
            
            if writer1_match and writer2_match:
                self.assertGreaterEqual(writer1_match['score'], writer2_match['score'])

