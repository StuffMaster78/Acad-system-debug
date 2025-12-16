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
    Admin view for viewing and tracing all referral codes with comprehensive analytics.
    """
    queryset = ReferralCode.objects.all().select_related(
        'user', 'website'
    ).order_by('-created_at')
    serializer_class = ReferralCodeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['website', 'user__is_active']
    search_fields = ['code', 'user__username', 'user__email', 'user__full_name']
    ordering_fields = ['created_at', 'user__date_joined']
    ordering = ['-created_at']
    pagination_class = ReferralTrackingPagination
    
    @action(detail=True, methods=['get'])
    def trace(self, request, pk=None):
        """
        Comprehensive tracing for a specific referral code.
        Shows all referrals made, conversion details, and abuse flags.
        """
        referral_code = self.get_object()
        
        from referrals.models import Referral
        from orders.models import Order
        
        # Get all referrals using this code
        referrals = Referral.objects.filter(
            referral_code=referral_code.code,
            website=referral_code.website
        ).select_related('referrer', 'referee', 'website').order_by('-created_at')
        
        # Get detailed referral information
        referral_details = []
        for ref in referrals:
            # Get orders placed by this referee
            orders = Order.objects.filter(
                client=ref.referee,
                website=ref.website
            ).order_by('-created_at')
            
            # Get abuse flags if any
            abuse_flags = []
            if hasattr(ref, 'abuse_flags'):
                abuse_flags = [
                    {
                        'type': flag.abuse_type,
                        'reason': flag.reason,
                        'status': flag.status,
                        'detected_at': flag.detected_at
                    }
                    for flag in ref.abuse_flags.all()
                ]
            
            referral_details.append({
                'referral_id': ref.id,
                'referee': {
                    'id': ref.referee.id,
                    'username': ref.referee.username,
                    'email': ref.referee.email,
                    'date_joined': ref.referee.date_joined,
                },
                'created_at': ref.created_at,
                'bonus_awarded': ref.bonus_awarded,
                'is_flagged': ref.is_flagged,
                'is_voided': ref.is_voided,
                'orders_count': orders.count(),
                'orders': [
                    {
                        'id': order.id,
                        'topic': order.topic,
                        'status': order.status,
                        'total_price': str(order.total_price),
                        'created_at': order.created_at,
                    }
                    for order in orders[:5]  # Limit to 5 most recent
                ],
                'abuse_flags': abuse_flags,
            })
        
        # Calculate overall statistics
        total_referrals = referrals.count()
        successful_referrals = referrals.filter(bonus_awarded=True).count()
        flagged_referrals = referrals.filter(is_flagged=True).count()
        voided_referrals = referrals.filter(is_voided=True).count()
        
        # Get all referee IDs
        referee_ids = referrals.values_list('referee_id', flat=True)
        total_orders = Order.objects.filter(
            client_id__in=referee_ids,
            website=referral_code.website
        ).count()
        
        conversion_rate = (successful_referrals / total_referrals * 100) if total_referrals > 0 else 0
        
        return Response({
            'referral_code': {
                'id': referral_code.id,
                'code': referral_code.code,
                'user': {
                    'id': referral_code.user.id,
                    'username': referral_code.user.username,
                    'email': referral_code.user.email,
                    'is_active': referral_code.user.is_active,
                },
                'website': {
                    'id': referral_code.website.id,
                    'name': referral_code.website.name,
                    'domain': referral_code.website.domain,
                },
                'created_at': referral_code.created_at,
                'referral_link': referral_code.get_referral_link(),
            },
            'statistics': {
                'total_referrals': total_referrals,
                'successful_referrals': successful_referrals,
                'flagged_referrals': flagged_referrals,
                'voided_referrals': voided_referrals,
                'total_orders_placed': total_orders,
                'conversion_rate': round(conversion_rate, 2),
            },
            'referrals': referral_details,
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get comprehensive referral code statistics."""
        queryset = self.filter_queryset(self.get_queryset())
        
        from referrals.models import Referral
        from orders.models import Order
        
        # Get codes with most referrals
        top_codes = Referral.objects.values('referral_code').annotate(
            referral_count=Count('id'),
            successful_count=Count('id', filter=Q(bonus_awarded=True))
        ).order_by('-referral_count')[:10]
        
        # Get codes with highest conversion rates
        codes_with_stats = []
        for code_obj in queryset[:100]:  # Limit to avoid performance issues
            referrals = Referral.objects.filter(
                referral_code=code_obj.code,
                website=code_obj.website
            )
            total = referrals.count()
            successful = referrals.filter(bonus_awarded=True).count()
            conversion = (successful / total * 100) if total > 0 else 0
            
            codes_with_stats.append({
                'code': code_obj.code,
                'user': code_obj.user.username,
                'total_referrals': total,
                'successful_referrals': successful,
                'conversion_rate': round(conversion, 2),
            })
        
        # Sort by conversion rate
        codes_with_stats.sort(key=lambda x: x['conversion_rate'], reverse=True)
        
        stats = {
            'total_codes': queryset.count(),
            'active_codes': queryset.filter(user__is_active=True).count(),
            'codes_with_referrals': queryset.filter(
                user__referrals__isnull=False
            ).distinct().count(),
            'top_referral_codes': list(top_codes),
            'top_conversion_codes': codes_with_stats[:10],
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def generate_for_client(self, request):
        """
        Generate referral code for a specific client (admin only).
        Useful for clients who don't have codes yet.
        """
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from users.models import User
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user.role != 'client':
            return Response(
                {'error': 'Only clients can have referral codes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if code already exists
        try:
            existing_code = ReferralCode.objects.get(user=user)
            return Response({
                'message': 'Referral code already exists',
                'code': ReferralCodeSerializer(existing_code).data
            }, status=status.HTTP_200_OK)
        except ReferralCode.DoesNotExist:
            pass
        
        # Generate code
        from referrals.services.referral_service import ReferralService
        website = user.website if hasattr(user, 'website') else None
        
        if not website:
            return Response(
                {'error': 'User must have a website assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        code = ReferralService.generate_unique_code(user, website)
        referral_code = ReferralCode.objects.create(
            user=user,
            website=website,
            code=code
        )
        
        return Response({
            'message': 'Referral code generated successfully',
            'code': ReferralCodeSerializer(referral_code).data
        }, status=status.HTTP_201_CREATED)

