"""
Analytics ViewSets
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from analytics.models import (
    ClientAnalytics,
    ClientAnalyticsSnapshot,
    WriterAnalytics,
    WriterAnalyticsSnapshot,
    ClassAnalytics,
    ClassPerformanceReport,
    ContentEvent,
)
from analytics.serializers import (
    ClientAnalyticsSerializer,
    ClientAnalyticsSnapshotSerializer,
    WriterAnalyticsSerializer,
    WriterAnalyticsSnapshotSerializer,
    ClassAnalyticsSerializer,
    ClassAnalyticsCreateSerializer,
    ClassPerformanceReportSerializer,
    ClassPerformanceReportCreateSerializer,
    ContentEventSerializer,
)
from admin_management.permissions import IsAdmin


class ClientAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for client analytics (read-only).
    """
    queryset = ClientAnalytics.objects.select_related('client', 'website').prefetch_related('analytics_snapshots').all()
    serializer_class = ClientAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter analytics based on user role."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Clients can only see their own analytics
        if user.role == 'client':
            qs = qs.filter(client=user)
        
        # Admins and superadmins can see all
        elif user.role in ['admin', 'superadmin']:
            # Filter by client if provided
            client_id = self.request.query_params.get('client')
            if client_id:
                qs = qs.filter(client_id=client_id)
        
        # Filter by period if provided
        period_start = self.request.query_params.get('period_start')
        period_end = self.request.query_params.get('period_end')
        if period_start:
            qs = qs.filter(period_start__gte=period_start)
        if period_end:
            qs = qs.filter(period_end__lte=period_end)
        
        return qs.order_by('-period_start')
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a specific period."""
        analytics = self.get_object()
        
        # Check permissions
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can recalculate analytics.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        analytics.recalculate()
        
        return Response(
            ClientAnalyticsSerializer(analytics).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def current_period(self, request):
        """Get analytics for current period (last 30 days)."""
        user = request.user
        
        # Determine client
        if user.role == 'client':
            client = user
        else:
            client_id = request.query_params.get('client')
            if not client_id:
                return Response(
                    {'error': 'client parameter required for non-client users.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            from django.contrib.auth import get_user_model
            User = get_user_model()
            client = get_object_or_404(User, id=client_id, role='client')
        
        # Get website
        website = user.website if hasattr(user, 'website') and user.website else None
        
        # Calculate period
        period_end = timezone.now().date()
        period_start = period_end - timedelta(days=30)
        
        # Get or create analytics
        analytics, created = ClientAnalytics.objects.get_or_create(
            client=client,
            website=website or client.website,
            period_start=period_start,
            period_end=period_end,
            defaults={}
        )
        
        # Recalculate if needed
        if created or request.query_params.get('recalculate') == 'true':
            analytics.recalculate()
        
        return Response(ClientAnalyticsSerializer(analytics).data)


class WriterAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for writer analytics (read-only).
    """
    queryset = WriterAnalytics.objects.select_related('writer', 'website').prefetch_related('analytics_snapshots').all()
    serializer_class = WriterAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter analytics based on user role."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Writers can only see their own analytics
        if user.role == 'writer':
            qs = qs.filter(writer=user)
        
        # Admins and superadmins can see all
        elif user.role in ['admin', 'superadmin']:
            # Filter by writer if provided
            writer_id = self.request.query_params.get('writer')
            if writer_id:
                qs = qs.filter(writer_id=writer_id)
        
        # Filter by period if provided
        period_start = self.request.query_params.get('period_start')
        period_end = self.request.query_params.get('period_end')
        if period_start:
            qs = qs.filter(period_start__gte=period_start)
        if period_end:
            qs = qs.filter(period_end__lte=period_end)
        
        return qs.order_by('-period_start')
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate analytics for a specific period."""
        analytics = self.get_object()
        
        # Check permissions
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can recalculate analytics.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        analytics.recalculate()
        
        return Response(
            WriterAnalyticsSerializer(analytics).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def current_period(self, request):
        """Get analytics for current period (last 30 days)."""
        user = request.user
        
        # Determine writer
        if user.role == 'writer':
            writer = user
        else:
            writer_id = request.query_params.get('writer')
            if not writer_id:
                return Response(
                    {'error': 'writer parameter required for non-writer users.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            from django.contrib.auth import get_user_model
            User = get_user_model()
            writer = get_object_or_404(User, id=writer_id, role='writer')
        
        # Get website
        website = user.website if hasattr(user, 'website') and user.website else None
        
        # Calculate period
        period_end = timezone.now().date()
        period_start = period_end - timedelta(days=30)
        
        # Get or create analytics
        analytics, created = WriterAnalytics.objects.get_or_create(
            writer=writer,
            website=website or writer.website,
            period_start=period_start,
            period_end=period_end,
            defaults={}
        )
        
        # Recalculate if needed
        if created or request.query_params.get('recalculate') == 'true':
            analytics.recalculate()
        
        return Response(WriterAnalyticsSerializer(analytics).data)


class ClassAnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for class/bulk order analytics.
    """
    queryset = ClassAnalytics.objects.select_related('website').prefetch_related('reports').all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ClassAnalyticsCreateSerializer
        return ClassAnalyticsSerializer
    
    def get_queryset(self):
        """Filter analytics based on website."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Filter by class name if provided
        class_name = self.request.query_params.get('class_name')
        if class_name:
            qs = qs.filter(class_name=class_name)
        
        # Filter by period if provided
        period_start = self.request.query_params.get('period_start')
        period_end = self.request.query_params.get('period_end')
        if period_start:
            qs = qs.filter(period_start__gte=period_start)
        if period_end:
            qs = qs.filter(period_end__lte=period_end)
        
        return qs.order_by('-period_start')


class ContentEventViewSet(viewsets.ModelViewSet):
    """
    Write-only endpoint for recording generic content engagement events.
    """

    queryset = ContentEvent.objects.all()
    serializer_class = ContentEventSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post', 'head', 'options']

    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate class analytics."""
        analytics = self.get_object()
        analytics.recalculate()
        
        return Response(
            ClassAnalyticsSerializer(analytics).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], serializer_class=ClassPerformanceReportCreateSerializer)
    def generate_report(self, request, pk=None):
        """Generate a performance report for the class."""
        analytics = self.get_object()
        
        serializer = ClassPerformanceReportCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        report = serializer.save(class_analytics=analytics)
        
        return Response(
            ClassPerformanceReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )

