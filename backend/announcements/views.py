"""
Views for announcements app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Prefetch
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from authentication.permissions import IsSuperadminOrAdmin
from .models import Announcement, AnnouncementView
from .serializers import (
    AnnouncementSerializer,
    AnnouncementCreateSerializer,
    AnnouncementUpdateSerializer,
    AnnouncementViewSerializer,
    AnnouncementAnalyticsSerializer
)
from .services.engagement import EngagementTrackingService
from .services.analytics import AnnouncementAnalyticsService


class AnnouncementPagination(PageNumberPagination):
    """Pagination for announcements list."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for announcements.
    Public users can list and retrieve.
    Admins can create, update, delete.
    """
    queryset = Announcement.objects.select_related(
        'broadcast', 'broadcast__website', 'broadcast__created_by'
    )
    permission_classes = [IsAuthenticated]
    pagination_class = AnnouncementPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'broadcast__pinned', 'broadcast__is_active']
    search_fields = ['broadcast__title', 'broadcast__message']
    ordering_fields = ['created_at', 'view_count', 'broadcast__pinned']
    ordering = ['-broadcast__pinned', '-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return AnnouncementCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AnnouncementUpdateSerializer
        return AnnouncementSerializer

    def get_queryset(self):
        """Filter announcements based on user role and permissions."""
        user = self.request.user
        queryset = super().get_queryset()

        # Optimize: Always prefetch related to avoid N+1 queries
        queryset = queryset.select_related('broadcast', 'broadcast__website', 'broadcast__created_by')

        # Filter by website if not superadmin/admin
        # Admins and superadmins can see all announcements
        if user.role not in ['admin', 'superadmin']:
            website = getattr(user, 'website', None)
            if website:
                queryset = queryset.filter(broadcast__website=website)

        # For public users, only show active announcements
        # Admins and superadmins can see all (active and inactive)
        if user.role not in ['admin', 'superadmin']:
            now = timezone.now()
            queryset = queryset.filter(
                broadcast__is_active=True
            ).filter(
                Q(broadcast__expires_at__isnull=True) |
                Q(broadcast__expires_at__gte=now)
            )

            # Filter by user's role - only show announcements where:
            # 1. User's role is in target_roles, OR
            # 2. show_to_all is True (for system-wide announcements)
            user_role = getattr(user, 'role', None)
            if user_role:
                # Use exact role matching - user's role must be in target_roles array
                queryset = queryset.filter(
                    Q(broadcast__target_roles__contains=[user_role]) |
                    Q(broadcast__show_to_all=True)
                )
            else:
                # If no role, only show announcements with show_to_all=True
                queryset = queryset.filter(broadcast__show_to_all=True)

        # Additional filtering
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        pinned = self.request.query_params.get('pinned')
        if pinned == 'true':
            queryset = queryset.filter(broadcast__pinned=True)

        unread = self.request.query_params.get('unread')
        if unread == 'true' and user.is_authenticated:
            from django.db.models import Exists, OuterRef
            viewed_subquery = AnnouncementView.objects.filter(
                user=user,
                announcement=OuterRef('pk')
            )
            queryset = queryset.exclude(Exists(viewed_subquery))

        # Optimize: Prefetch user's views to avoid N+1 queries in serializer
        # Only prefetch if we're not filtering by unread (to avoid double query)
        if user.is_authenticated and unread != 'true':
            queryset = queryset.prefetch_related(
                Prefetch(
                    'views',
                    queryset=AnnouncementView.objects.filter(user=user).only('id', 'acknowledged', 'viewed_at'),
                    to_attr='user_views'
                )
            )

        return queryset

    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperadminOrAdmin()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Track when a user views an announcement."""
        announcement = self.get_object()
        time_spent = request.data.get('time_spent')

        EngagementTrackingService.track_view(
            user=request.user,
            announcement=announcement,
            time_spent=time_spent
        )

        return Response({
            'message': 'View tracked',
            'is_read': True
        })

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Mark an announcement as acknowledged by the user."""
        announcement = self.get_object()

        EngagementTrackingService.acknowledge(
            user=request.user,
            announcement=announcement
        )

        return Response({
            'message': 'Announcement acknowledged',
            'acknowledged': True
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread announcements for current user."""
        user = request.user
        website = getattr(user, 'website', None) if user.role not in ['admin', 'superadmin'] else None
        
        try:
            count = EngagementTrackingService.get_user_unread_count(
                user=user,
                website=website
            )
        except Exception as e:
            # Log error but return 0 to prevent breaking the UI
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting unread count: {e}", exc_info=True)
            count = 0
        
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin an announcement (admin only)."""
        announcement = self.get_object()
        announcement.broadcast.pinned = True
        announcement.broadcast.save(update_fields=['pinned'])
        return Response({'message': 'Announcement pinned'})

    @action(detail=True, methods=['post'])
    def unpin(self, request, pk=None):
        """Unpin an announcement (admin only)."""
        announcement = self.get_object()
        announcement.broadcast.pinned = False
        announcement.broadcast.save(update_fields=['pinned'])
        return Response({'message': 'Announcement unpinned'})

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get engagement analytics for an announcement (admin only)."""
        announcement = self.get_object()
        stats = AnnouncementAnalyticsService.get_engagement_stats(announcement)

        # Serialize readers
        from .serializers import AnnouncementViewSerializer
        readers_data = AnnouncementViewSerializer(
            stats['readers'],
            many=True,
            context={'request': request}
        ).data

        return Response({
            'total_views': stats['total_views'],
            'unique_viewers': stats['unique_viewers'],
            'acknowledged_count': stats['acknowledged_count'],
            'engagement_rate': stats['engagement_rate'],
            'views_by_role': stats['views_by_role'],
            'views_over_time': stats['views_over_time'],
            'readers': readers_data,
            'non_readers_count': stats['non_readers_count']
        })

    @action(detail=True, methods=['get'])
    def readers(self, request, pk=None):
        """Get list of readers and non-readers (admin only)."""
        announcement = self.get_object()
        read_status = AnnouncementAnalyticsService.get_user_read_status(announcement)

        from .serializers import AnnouncementViewSerializer
        readers_data = AnnouncementViewSerializer(
            read_status['readers'],
            many=True,
            context={'request': request}
        ).data

        # Serialize non-readers (simple format)
        non_readers_data = [
            {
                'id': user.id,
                'email': user.email,
                'name': user.get_full_name() or user.username,
                'role': getattr(user, 'role', 'unknown')
            }
            for user in read_status['non_readers']
        ]

        return Response({
            'readers': readers_data,
            'non_readers': non_readers_data,
            'readers_count': read_status['readers_count'],
            'non_readers_count': read_status['non_readers_count']
        })

    @action(detail=True, methods=['get'])
    def export_analytics(self, request, pk=None):
        """Export analytics data as CSV (admin only)."""
        from django.http import HttpResponse
        import csv
        from io import StringIO

        announcement = self.get_object()
        stats = AnnouncementAnalyticsService.get_engagement_stats(announcement)

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['User Email', 'User Name', 'Viewed At', 'Time Spent (seconds)', 'Acknowledged', 'Acknowledged At'])

        # Write reader data
        for reader in stats['readers']:
            writer.writerow([
                getattr(reader.user, 'email', ''),
                reader.user.get_full_name() or getattr(reader.user, 'username', ''),
                reader.viewed_at.isoformat() if reader.viewed_at else '',
                reader.time_spent or '',
                'Yes' if reader.acknowledged else 'No',
                reader.acknowledged_at.isoformat() if reader.acknowledged_at else ''
            ])

        # Create HTTP response
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="announcement-{announcement.id}-analytics.csv"'
        return response


