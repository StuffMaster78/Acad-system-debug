"""
Admin views for referral tracking and abuse management.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Q, Sum
from django.utils.timezone import now, timedelta
from referrals.models import Referral, ReferralCode, ReferralStats
try:
    from referrals.models import ReferralAbuseFlag
except ImportError:
    ReferralAbuseFlag = None
from referrals.services.abuse_detection import ReferralAbuseDetectionService
from referrals.serializers import (
    ReferralSerializer, ReferralCodeSerializer, ReferralStatsSerializer,
    ReferralAbuseFlagSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination


# ReferralAbuseFlagSerializer is imported from referrals.serializers


class ReferralTrackingPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdminReferralTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin view for tracking all referrals across the system.
    Shows detailed information about referrals, including abuse flags.
    """
    def get_queryset(self):
        """Get queryset, handling case where migration hasn't run yet."""
        queryset = Referral.objects.all().select_related(
            'referrer', 'referee', 'website'
        ).order_by('-created_at')
        
        # Only add these if the fields exist (migration has run)
        try:
            # Test if voided_by field exists by checking model fields
            if 'voided_by' in [f.name for f in Referral._meta.get_fields()]:
                queryset = queryset.select_related('voided_by')
            # Test if abuse_flags relation exists
            if hasattr(Referral, 'abuse_flags'):
                queryset = queryset.prefetch_related('abuse_flags')
        except Exception:
            pass
        
        return queryset
    serializer_class = ReferralSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    def get_filterset_fields(self):
        """Get filterset fields, handling case where migration hasn't run yet."""
        fields = ['website', 'bonus_awarded']
        # Only add abuse fields if they exist
        try:
            if hasattr(Referral, 'is_flagged'):
                fields.append('is_flagged')
            if hasattr(Referral, 'is_voided'):
                fields.append('is_voided')
        except Exception:
            pass
        return fields
    
    filterset_fields = ['website', 'bonus_awarded']  # Base fields, others added dynamically
    search_fields = ['referrer__username', 'referrer__email', 'referee__username', 'referee__email', 'referral_code']
    ordering_fields = ['created_at', 'bonus_awarded']
    ordering = ['-created_at']
    pagination_class = ReferralTrackingPagination
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get overall referral statistics."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Check if new abuse detection fields exist (migration may not have run)
        try:
            # Try to check if fields exist by attempting to access them
            has_abuse_fields = 'is_flagged' in [f.name for f in Referral._meta.get_fields()]
        except Exception:
            has_abuse_fields = False
        
        try:
            # Try to use new fields if they exist
            if has_abuse_fields:
                flagged_count = queryset.filter(is_flagged=True).count()
                voided_count = queryset.filter(is_voided=True).count()
                pending_count = queryset.filter(bonus_awarded=False, is_voided=False).count()
            else:
                flagged_count = 0
                voided_count = 0
                pending_count = queryset.filter(bonus_awarded=False).count()
        except Exception as e:
            # Fallback if fields don't exist yet or query fails
            flagged_count = 0
            voided_count = 0
            pending_count = queryset.filter(bonus_awarded=False).count()
        
        stats = {
            'total_referrals': queryset.count(),
            'successful_referrals': queryset.filter(bonus_awarded=True).count(),
            'flagged_referrals': flagged_count,
            'voided_referrals': voided_count,
            'pending_referrals': pending_count,
            'by_website': queryset.values('website__name').annotate(
                count=Count('id')
            ).values('website__name', 'count'),
            'recent_referrals_24h': queryset.filter(
                created_at__gte=now() - timedelta(days=1)
            ).count(),
            'recent_referrals_7d': queryset.filter(
                created_at__gte=now() - timedelta(days=7)
            ).count(),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def void_referral(self, request, pk=None):
        """Void a referral due to abuse."""
        referral = self.get_object()
        reason = request.data.get('reason', 'Voided by admin')
        
        # Check if abuse detection fields exist
        try:
            has_abuse_fields = 'is_voided' in [f.name for f in Referral._meta.get_fields()]
        except Exception:
            has_abuse_fields = False
        
        if not has_abuse_fields:
            return Response({
                'error': 'Abuse detection features not available. Please run migrations: python manage.py migrate referrals'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        ReferralAbuseDetectionService.void_referral(
            referral,
            request.user,
            reason
        )
        
        return Response({
            'message': 'Referral voided successfully',
            'referral_id': referral.id
        })


class AdminReferralAbuseViewSet(viewsets.ModelViewSet):
    """
    Admin view for managing referral abuse flags.
    """
    def get_queryset(self):
        """Get queryset, handling case where model doesn't exist yet."""
        if ReferralAbuseFlag is None:
            # Try to import it
            try:
                from referrals.models import ReferralAbuseFlag as RAF
                ReferralAbuseFlag = RAF
            except ImportError:
                return ReferralAbuseFlag.objects.none()
        return ReferralAbuseFlag.objects.all().select_related(
            'referral', 'referral__referrer', 'referral__referee', 'reviewed_by'
        ).order_by('-detected_at')
    serializer_class = ReferralAbuseFlagSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'abuse_type', 'referral__website']
    search_fields = ['reason', 'referral__referrer__username', 'referral__referee__username']
    ordering_fields = ['detected_at', 'status']
    ordering = ['-detected_at']
    pagination_class = ReferralTrackingPagination
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get abuse detection statistics."""
        if ReferralAbuseFlag is None:
            try:
                from referrals.models import ReferralAbuseFlag as RAF
                ReferralAbuseFlag = RAF
            except ImportError:
                return Response({
                    'error': 'Abuse detection features not available. Please run migrations: python manage.py migrate referrals',
                    'total_flags': 0,
                    'pending_review': 0,
                    'resolved': 0,
                    'false_positives': 0,
                    'by_type': [],
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        stats = ReferralAbuseDetectionService.get_abuse_statistics()
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Mark an abuse flag as reviewed."""
        flag = self.get_object()
        notes = request.data.get('notes', '')
        action_taken = request.data.get('action_taken', '')
        status_value = request.data.get('status', 'reviewed')
        
        flag.status = status_value
        flag.mark_as_reviewed(request.user, notes, action_taken)
        
        return Response({
            'message': 'Abuse flag reviewed successfully',
            'flag_id': flag.id
        })
    
    @action(detail=True, methods=['post'])
    def mark_false_positive(self, request, pk=None):
        """Mark an abuse flag as false positive."""
        flag = self.get_object()
        flag.status = 'false_positive'
        flag.mark_as_reviewed(request.user, 'Marked as false positive')
        
        return Response({
            'message': 'Abuse flag marked as false positive',
            'flag_id': flag.id
        })


class AdminReferralCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin view for viewing all referral codes.
    """
    queryset = ReferralCode.objects.all().select_related(
        'user', 'website'
    ).order_by('-created_at')
    serializer_class = ReferralCodeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['website']
    search_fields = ['code', 'user__username', 'user__email']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get referral code statistics."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get codes with most referrals
        from referrals.models import Referral
        top_codes = Referral.objects.values('referral_code').annotate(
            referral_count=Count('id')
        ).order_by('-referral_count')[:10]
        
        stats = {
            'total_codes': queryset.count(),
            'active_codes': queryset.filter(
                user__is_active=True
            ).count(),
            'top_referral_codes': list(top_codes),
        }
        
        return Response(stats)

