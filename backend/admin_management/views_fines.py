"""
Admin Fines Management Dashboard ViewSet
Provides comprehensive fine management endpoints for admins.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from fines.models import Fine, FineAppeal, FineStatus, FinePolicy
from fines.serializers import FineSerializer, FineAppealSerializer
from fines.services.fine_services import FineService
from authentication.permissions import IsAdminOrSuperAdmin


class AdminFinesManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for fines management dashboard."""
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get fine statistics dashboard."""
        # Get all fines
        all_fines = Fine.objects.select_related(
            'order', 'order__assigned_writer', 'issued_by', 'waived_by'
        )
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_fines = all_fines.filter(order__website=website)
        
        # Status breakdown
        status_breakdown = all_fines.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Total statistics
        total_fines = all_fines.count()
        total_amount = all_fines.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        # FineStatus doesn't have PENDING, use ISSUED for active/pending fines
        pending_fines = all_fines.filter(status=FineStatus.ISSUED).count()
        resolved_fines = all_fines.filter(status=FineStatus.RESOLVED).count()
        waived_fines = all_fines.filter(status=FineStatus.WAIVED).count()
        voided_fines = all_fines.filter(status=FineStatus.VOIDED).count()
        
        # Fines with appeals
        fines_with_appeals = all_fines.filter(appeal__isnull=False).distinct().count()
        pending_appeals = FineAppeal.objects.filter(status='pending').count()
        
        # Recent fines (last 30 days)
        # Fine model uses 'imposed_at' not 'issued_at'
        month_ago = timezone.now() - timedelta(days=30)
        recent_fines = all_fines.filter(imposed_at__gte=month_ago).count()
        recent_amount = all_fines.filter(
            imposed_at__gte=month_ago
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        
        # Monthly trends
        monthly_trends = all_fines.filter(
            imposed_at__gte=timezone.now() - timedelta(days=90)
        ).annotate(
            month=TruncMonth('imposed_at')
        ).values('month').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('month')
        
        # Top writers by fines
        top_writers = all_fines.values(
            'order__assigned_writer__username',
            'order__assigned_writer__id'
        ).annotate(
            fine_count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-fine_count')[:10]
        
        return Response({
            'summary': {
                'total_fines': total_fines,
                'total_amount': float(total_amount),
                'pending_fines': pending_fines,
                'resolved_fines': resolved_fines,
                'waived_fines': waived_fines,
                'voided_fines': voided_fines,
                'fines_with_appeals': fines_with_appeals,
                'pending_appeals': pending_appeals,
            },
            'recent': {
                'count': recent_fines,
                'amount': float(recent_amount),
            },
            'status_breakdown': list(status_breakdown),
            'monthly_trends': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0),
                }
                for item in monthly_trends
            ],
            'top_writers': [
                {
                    'writer_id': item['order__assigned_writer__id'],
                    'writer_username': item['order__assigned_writer__username'],
                    'fine_count': item['fine_count'],
                    'total_amount': float(item['total_amount'] or 0),
                }
                for item in top_writers
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_fines(self, request):
        """Get pending fines queue."""
        # FineStatus doesn't have PENDING, use ISSUED for active/pending fines
        fines = Fine.objects.filter(
            status=FineStatus.ISSUED
        ).select_related(
            'order', 'order__assigned_writer', 'issued_by'
        ).order_by('-imposed_at')
        
        # Filter by website if applicable
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                fines = fines.filter(order__website=website)
        
        serializer = FineSerializer(fines, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='appeals')
    def appeals_queue(self, request):
        """Get fine appeals queue."""
        appeals = FineAppeal.objects.filter(
            status='pending'
        ).select_related(
            'fine', 'fine__order', 'appealed_by', 'reviewed_by'
        ).order_by('-submitted_at')
        
        # Filter by website if applicable
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                appeals = appeals.filter(fine__order__website=website)
        
        serializer = FineAppealSerializer(appeals, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get fine analytics."""
        all_fines = Fine.objects.select_related('order', 'order__assigned_writer')
        
        # Filter by website if applicable
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_fines = all_fines.filter(order__website=website)
        
        # Get query parameters
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Filter by date range - Fine model uses 'imposed_at' not 'issued_at'
        fines = all_fines.filter(imposed_at__gte=date_from)
        
        # Daily trends
        daily_trends = fines.annotate(
            date=TruncDate('imposed_at')
        ).values('date').annotate(
            count=Count('id'),
            total_amount=Sum('amount'),
            resolved_count=Count('id', filter=Q(status=FineStatus.RESOLVED)),
            waived_count=Count('id', filter=Q(status=FineStatus.WAIVED)),
        ).order_by('date')
        
        # Fine type breakdown (if fine_type field exists)
        type_breakdown = fines.values('fine_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('-count')
        
        # Appeal rate
        total_fines = fines.count()
        appealed_fines = fines.filter(appeal__isnull=False).distinct().count()
        appeal_rate = (appealed_fines / total_fines * 100) if total_fines > 0 else 0
        
        # Resolution time (average days to resolve)
        resolved_fines = fines.filter(
            status=FineStatus.RESOLVED,
            resolved_at__isnull=False
        )
        resolution_times = []
        for fine in resolved_fines:
            # Fine model uses 'imposed_at' not 'issued_at'
            if fine.resolved_at and fine.imposed_at:
                days_to_resolve = (fine.resolved_at - fine.imposed_at).days
                resolution_times.append(days_to_resolve)
        
        avg_resolution_days = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return Response({
            'daily_trends': [
                {
                    'date': item['date'].isoformat() if item['date'] else None,
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0),
                    'resolved_count': item['resolved_count'],
                    'waived_count': item['waived_count'],
                }
                for item in daily_trends
            ],
            'type_breakdown': [
                {
                    'fine_type': item['fine_type'] or 'unknown',
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0),
                }
                for item in type_breakdown
            ],
            'metrics': {
                'total_fines': total_fines,
                'appealed_fines': appealed_fines,
                'appeal_rate': round(appeal_rate, 2),
                'avg_resolution_days': round(avg_resolution_days, 1),
            },
        })
    
    @action(detail=True, methods=['post'], url_path='waive')
    def waive_fine(self, request, pk=None):
        """Waive a fine (admin action)."""
        fine = Fine.objects.get(pk=pk)
        reason = request.data.get('reason', '')
        
        waived = FineService.waive_fine(fine, request.user, reason)
        serializer = FineSerializer(waived)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='void')
    def void_fine(self, request, pk=None):
        """Void a fine (admin action)."""
        fine = Fine.objects.get(pk=pk)
        reason = request.data.get('reason', 'Fine voided by admin')
        
        voided = FineService.void_fine(fine, request.user, reason)
        serializer = FineSerializer(voided)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='appeals/approve')
    def approve_appeal(self, request, pk=None):
        """Approve a fine appeal."""
        from fines.services.fine_appeal_service import FineAppealService
        
        appeal = FineAppeal.objects.get(pk=pk)
        notes = request.data.get('notes', '')
        
        reviewed = FineAppealService.review_appeal(
            appeal,
            request.user,
            decision='approved',
            notes=notes
        )
        serializer = FineAppealSerializer(reviewed)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='appeals/reject')
    def reject_appeal(self, request, pk=None):
        """Reject a fine appeal."""
        from fines.services.fine_appeal_service import FineAppealService
        
        appeal = FineAppeal.objects.get(pk=pk)
        notes = request.data.get('notes', '')
        
        reviewed = FineAppealService.review_appeal(
            appeal,
            request.user,
            decision='rejected',
            notes=notes
        )
        serializer = FineAppealSerializer(reviewed)
        return Response(serializer.data, status=status.HTTP_200_OK)

