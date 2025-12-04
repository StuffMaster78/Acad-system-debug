"""
API views for editor usage tracking.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from ..models.editor_usage_tracking import EditorSession, EditorAction, EditorProductivityMetrics
from ..services.editor_tracking_service import EditorTrackingService
from ..serializers.editor_tracking_serializers import (
    EditorSessionSerializer,
    EditorActionSerializer,
    EditorProductivityMetricsSerializer
)


class EditorSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing editor sessions.
    """
    queryset = EditorSession.objects.all()
    serializer_class = EditorSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'website', 'is_active']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Users can only see their own sessions unless admin
        if self.request.user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(user=self.request.user)
        return queryset.select_related('user', 'website', 'content_type')
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start a new editor session.
        
        Body:
        {
            "website_id": 123,
            "content_type": "blog_post" | "service_page",
            "content_id": 456
        }
        """
        website_id = request.data.get('website_id')
        content_type_str = request.data.get('content_type')
        content_id = request.data.get('content_id')
        
        if not all([website_id, content_type_str, content_id]):
            return Response(
                {'error': 'website_id, content_type, and content_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from websites.models import Website
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get content object
        if content_type_str == 'blog_post':
            from ..models import BlogPost
            try:
                content = BlogPost.objects.get(id=content_id)
            except BlogPost.DoesNotExist:
                return Response(
                    {'error': 'Blog post not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif content_type_str == 'service_page':
            from service_pages_management.models import ServicePage
            try:
                content = ServicePage.objects.get(id=content_id)
            except ServicePage.DoesNotExist:
                return Response(
                    {'error': 'Service page not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                {'error': 'Invalid content_type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = EditorTrackingService.start_session(
            user=request.user,
            website=website,
            content_object=content
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End an editor session."""
        session = EditorTrackingService.end_session(int(pk))
        if not session:
            return Response(
                {'error': 'Session not found or already ended'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def track_action(self, request, pk=None):
        """
        Track an action in a session.
        
        Body:
        {
            "action_type": "keystroke" | "template_use" | "snippet_use" | etc.,
            "metadata": { ...optional metadata... }
        }
        """
        action_type = request.data.get('action_type')
        metadata = request.data.get('metadata', {})
        
        if not action_type:
            return Response(
                {'error': 'action_type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        action = EditorTrackingService.track_action(
            session_id=int(pk),
            action_type=action_type,
            metadata=metadata
        )
        
        if not action:
            return Response(
                {'error': 'Session not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EditorActionSerializer(action)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EditorProductivityMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for editor productivity metrics.
    """
    queryset = EditorProductivityMetrics.objects.all()
    serializer_class = EditorProductivityMetricsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'website']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Users can only see their own metrics unless admin
        if self.request.user.role not in ['admin', 'superadmin']:
            queryset = queryset.filter(user=self.request.user)
        return queryset.select_related('user', 'website')
    
    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """
        Calculate productivity metrics for a user/website.
        
        Body:
        {
            "website_id": 123,
            "period_start": "2024-01-01" (optional, defaults to 30 days ago),
            "period_end": "2024-01-31" (optional, defaults to today)
        }
        """
        website_id = request.data.get('website_id')
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from websites.models import Website
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        from datetime import datetime
        if period_start:
            period_start = datetime.strptime(period_start, '%Y-%m-%d').date()
        if period_end:
            period_end = datetime.strptime(period_end, '%Y-%m-%d').date()
        
        metrics = EditorTrackingService.calculate_productivity_metrics(
            user=request.user,
            website=website,
            period_start=period_start,
            period_end=period_end
        )
        
        serializer = self.get_serializer(metrics)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def my_metrics(self, request):
        """Get current user's productivity metrics."""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response(
                {'error': 'website_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from websites.models import Website
        try:
            website = Website.objects.get(id=website_id)
        except Website.DoesNotExist:
            return Response(
                {'error': 'Website not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get most recent metrics or calculate
        metrics = EditorProductivityMetrics.objects.filter(
            user=request.user,
            website=website
        ).order_by('-period_end').first()
        
        if not metrics or metrics.period_end < timezone.now().date() - timedelta(days=1):
            # Calculate new metrics
            metrics = EditorTrackingService.calculate_productivity_metrics(
                user=request.user,
                website=website
            )
        
        serializer = self.get_serializer(metrics)
        return Response(serializer.data, status=status.HTTP_200_OK)

