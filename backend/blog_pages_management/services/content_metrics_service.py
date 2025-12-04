"""
Service to aggregate ContentEvent data into cached metrics on BlogPost.
"""
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Avg, Q
from analytics.models import ContentEvent
from blog_pages_management._legacy_models import BlogPost


class ContentMetricsService:
    """
    Aggregates ContentEvent data and updates cached metrics on BlogPost.
    """
    
    @staticmethod
    def aggregate_for_blog_post(blog_post: BlogPost) -> dict:
        """
        Calculate metrics from ContentEvent for a specific BlogPost.
        
        Returns:
            dict with keys: view_count, like_count, dislike_count, 
            avg_scroll_percent, primary_cta_clicks
        """
        content_type = ContentType.objects.get_for_model(BlogPost)
        
        events = ContentEvent.objects.filter(
            website=blog_post.website,
            content_type=content_type,
            object_id=blog_post.id
        )
        
        # Count views
        view_count = events.filter(event_type=ContentEvent.EventType.VIEW).count()
        
        # Count likes
        like_count = events.filter(event_type=ContentEvent.EventType.LIKE).count()
        
        # Count dislikes
        dislike_count = events.filter(event_type=ContentEvent.EventType.DISLIKE).count()
        
        # Calculate average scroll depth
        scroll_events = events.filter(event_type=ContentEvent.EventType.SCROLL)
        scroll_percents = [
            event.metadata.get('scroll_percent', 0)
            for event in scroll_events
            if isinstance(event.metadata.get('scroll_percent'), (int, float))
        ]
        avg_scroll_percent = sum(scroll_percents) / len(scroll_percents) if scroll_percents else 0.0
        
        # Count CTA clicks
        primary_cta_clicks = events.filter(event_type=ContentEvent.EventType.CTA).count()
        
        return {
            'view_count': view_count,
            'like_count': like_count,
            'dislike_count': dislike_count,
            'avg_scroll_percent': round(avg_scroll_percent, 2),
            'primary_cta_clicks': primary_cta_clicks,
        }
    
    @staticmethod
    def update_blog_post_metrics(blog_post: BlogPost) -> BlogPost:
        """
        Update cached metrics on a BlogPost instance from ContentEvent data.
        
        Returns:
            Updated BlogPost instance
        """
        metrics = ContentMetricsService.aggregate_for_blog_post(blog_post)
        
        blog_post.view_count = metrics['view_count']
        blog_post.like_count = metrics['like_count']
        blog_post.dislike_count = metrics['dislike_count']
        blog_post.avg_scroll_percent = metrics['avg_scroll_percent']
        blog_post.primary_cta_clicks = metrics['primary_cta_clicks']
        
        blog_post.save(update_fields=[
            'view_count', 'like_count', 'dislike_count',
            'avg_scroll_percent', 'primary_cta_clicks'
        ])
        
        return blog_post
    
    @staticmethod
    def update_all_blog_posts(website=None):
        """
        Update metrics for all published BlogPosts (optionally filtered by website).
        
        Args:
            website: Optional Website instance to filter by
        """
        queryset = BlogPost.objects.filter(is_published=True, is_deleted=False)
        if website:
            queryset = queryset.filter(website=website)
        
        for blog_post in queryset:
            ContentMetricsService.update_blog_post_metrics(blog_post)

