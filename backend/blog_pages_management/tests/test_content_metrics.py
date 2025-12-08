"""
Tests for Content Metrics Service.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from websites.models import Website
from analytics.models import ContentEvent
from blog_pages_management.models import BlogPost
from blog_pages_management.services.content_metrics_service import ContentMetricsService

User = get_user_model()


class ContentMetricsServiceTestCase(TestCase):
    """Test cases for ContentMetricsService."""
    
    def setUp(self):
        """Set up test data."""
        self.website = Website.objects.create(
            name='Test Website',
            domain='https://test.com',
            is_active=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.blog_post = BlogPost.objects.create(
            website=self.website,
            title='Test Blog Post',
            slug='test-blog-post',
            content='Test content',
            is_published=True
        )
        self.content_type = ContentType.objects.get_for_model(BlogPost)
    
    def test_aggregate_for_blog_post_no_events(self):
        """Test aggregation when there are no events."""
        metrics = ContentMetricsService.aggregate_for_blog_post(self.blog_post)
        
        self.assertEqual(metrics['view_count'], 0)
        self.assertEqual(metrics['like_count'], 0)
        self.assertEqual(metrics['dislike_count'], 0)
        self.assertEqual(metrics['avg_scroll_percent'], 0.0)
        self.assertEqual(metrics['primary_cta_clicks'], 0)
    
    def test_aggregate_for_blog_post_with_events(self):
        """Test aggregation with various event types."""
        # Create view events
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.VIEW
        )
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.VIEW
        )
        
        # Create like event
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.LIKE
        )
        
        # Create scroll events
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.SCROLL,
            metadata={'scroll_percent': 50}
        )
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.SCROLL,
            metadata={'scroll_percent': 75}
        )
        
        # Create CTA click
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.CTA
        )
        
        metrics = ContentMetricsService.aggregate_for_blog_post(self.blog_post)
        
        self.assertEqual(metrics['view_count'], 2)
        self.assertEqual(metrics['like_count'], 1)
        self.assertEqual(metrics['dislike_count'], 0)
        self.assertEqual(metrics['avg_scroll_percent'], 62.5)  # (50 + 75) / 2
        self.assertEqual(metrics['primary_cta_clicks'], 1)
    
    def test_update_blog_post_metrics(self):
        """Test updating blog post metrics."""
        # Create some events
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.VIEW
        )
        ContentEvent.objects.create(
            website=self.website,
            content_type=self.content_type,
            object_id=self.blog_post.id,
            event_type=ContentEvent.EventType.LIKE
        )
        
        # Update metrics
        updated_post = ContentMetricsService.update_blog_post_metrics(self.blog_post)
        
        # Refresh from database
        updated_post.refresh_from_db()
        
        self.assertEqual(updated_post.view_count, 1)
        self.assertEqual(updated_post.like_count, 1)
        self.assertEqual(updated_post.dislike_count, 0)
        self.assertEqual(updated_post.primary_cta_clicks, 0)

