"""
Views for advanced analytics.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from ..models.analytics_models import EditorAnalytics, BlogPostAnalytics, ContentPerformanceMetrics
from ..models import BlogPost


class EditorAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for editor analytics."""
    queryset = EditorAnalytics.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'user']
    
    def get_queryset(self):
        """Filter based on permissions."""
        queryset = super().get_queryset().select_related('user', 'website')
        
        # Users can only see their own analytics unless admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate analytics for a user."""
        user_id = request.data.get('user_id', request.user.id)
        website_id = request.data.get('website_id')
        
        from authentication.models import User
        from websites.models import Website
        
        try:
            user = User.objects.get(id=user_id)
            website = Website.objects.get(id=website_id) if website_id else None
        except (User.DoesNotExist, Website.DoesNotExist):
            return Response(
                {'error': 'User or website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        analytics = EditorAnalytics.calculate_for_user(user, website)
        
        from ..serializers.analytics_serializers import EditorAnalyticsSerializer
        serializer = EditorAnalyticsSerializer(analytics)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlogPostAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blog post analytics."""
    queryset = BlogPostAnalytics.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog']
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate analytics for a blog post."""
        blog_id = request.data.get('blog_id')
        
        try:
            blog = BlogPost.objects.get(id=blog_id)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        analytics = BlogPostAnalytics.calculate_for_blog(blog)
        
        from ..serializers.analytics_serializers import BlogPostAnalyticsSerializer
        serializer = BlogPostAnalyticsSerializer(analytics)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics."""
        website_id = request.query_params.get('website_id')
        
        # Get draft completion rate
        total_drafts = BlogPost.objects.filter(
            status='draft',
            website_id=website_id
        ).count() if website_id else BlogPost.objects.filter(status='draft').count()
        
        total_published = BlogPost.objects.filter(
            status='published',
            website_id=website_id
        ).count() if website_id else BlogPost.objects.filter(status='published').count()
        
        draft_completion_rate = (total_published / (total_drafts + total_published) * 100) if (total_drafts + total_published) > 0 else 0
        
        # Get average time to publish
        published_posts = BlogPost.objects.filter(
            status='published',
            publish_date__isnull=False,
            website_id=website_id
        ) if website_id else BlogPost.objects.filter(status='published', publish_date__isnull=False)
        
        avg_time_to_publish = 0
        if published_posts.exists():
            total_hours = 0
            for post in published_posts:
                if post.created_at and post.publish_date:
                    delta = post.publish_date - post.created_at
                    total_hours += delta.total_seconds() / 3600
            avg_time_to_publish = total_hours / published_posts.count()
        
        # Get posts requiring revision
        from ..models.draft_editing import BlogPostRevision
        posts_with_revisions = BlogPost.objects.filter(
            website_id=website_id,
            revisions__revision_number__gt=1
        ).distinct().count() if website_id else BlogPost.objects.filter(
            revisions__revision_number__gt=1
        ).distinct().count()
        
        return Response({
            'draft_completion_rate': round(draft_completion_rate, 2),
            'average_time_to_publish_hours': round(avg_time_to_publish, 2),
            'posts_requiring_revision': posts_with_revisions,
            'total_drafts': total_drafts,
            'total_published': total_published,
        }, status=status.HTTP_200_OK)


class ContentPerformanceMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for content performance metrics."""
    queryset = ContentPerformanceMetrics.objects.all()
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website', 'period_start', 'period_end']

