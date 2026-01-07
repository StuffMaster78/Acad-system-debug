"""
Admin Dashboard Endpoints

This module contains dashboard aggregation endpoints for admin management.
These endpoints provide comprehensive statistics and analytics for:
- Dispute Management
- Refund Management
- Review Moderation
- Order Management
- Express Classes (single class requests)
- Class Management (Bundles, etc.)
- Special Orders
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404

from admin_management.permissions import IsAdmin
from orders.models import Order, Dispute
from orders.order_enums import OrderStatus
from orders.services.status_transition_service import VALID_TRANSITIONS
from refunds.models import Refund
from reviews_system.models import WebsiteReview, WriterReview, OrderReview
from special_orders.models import SpecialOrder, InstallmentPayment
from class_management.models import ClassBundle, ClassPurchase, ExpressClass
from fines.models import Fine, FineAppeal, FinePolicy, FineStatus, FineType
from tickets.models import Ticket
from users.models import User
from writer_management.models.advance_payment import WriterAdvancePaymentRequest


class AdminDisputeDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for dispute management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get dispute statistics dashboard."""
        # Get all disputes
        # Order model uses 'assigned_writer' not 'writer'
        # Dispute model doesn't have 'resolved_by' field
        all_disputes = Dispute.objects.all().select_related('order', 'order__client', 'order__assigned_writer', 'raised_by')
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_disputes = all_disputes.filter(order__website=website)
        
        # Combined aggregation - reduces from 4+ queries to 1 query
        month_ago = timezone.now() - timedelta(days=30)
        summary_stats = all_disputes.aggregate(
            total_disputes=Count('id'),
            pending_disputes=Count('id', filter=Q(dispute_status='open')),
            resolved_this_month=Count('id', filter=Q(dispute_status='resolved', updated_at__gte=month_ago)),
        )
        
        # Status breakdown - Dispute model uses 'dispute_status' not 'status'
        status_breakdown = all_disputes.values('dispute_status').annotate(
            count=Count('id')
        )
        
        # Pending disputes (open disputes) - only fetch for list
        pending_disputes = all_disputes.filter(dispute_status='open')[:20]
        
        # Disputes by reason
        reason_breakdown = all_disputes.values('reason').annotate(
            count=Count('id')
        )
        
        # Average resolution time - calculate in Python but only for resolved disputes
        # This is acceptable since we're only calculating for a subset
        resolved_with_time = all_disputes.filter(
            dispute_status='resolved',
            updated_at__isnull=False,
            created_at__isnull=False
        ).only('updated_at', 'created_at')  # Only fetch needed fields
        
        avg_resolution_hours = None
        if resolved_with_time.exists():
            # Use values_list for faster iteration
            resolution_times = [
                (row['updated_at'] - row['created_at']).total_seconds() / 3600
                for row in resolved_with_time.values('updated_at', 'created_at')
                if row['updated_at'] and row['created_at']
            ]
            if resolution_times:
                avg_resolution_hours = sum(resolution_times) / len(resolution_times)
        
        return Response({
            'summary': {
                'total_disputes': summary_stats['total_disputes'] or 0,
                'pending_disputes': summary_stats['pending_disputes'] or 0,
                'resolved_this_month': summary_stats['resolved_this_month'] or 0,
                'average_resolution_hours': round(avg_resolution_hours, 2) if avg_resolution_hours else None,
            },
            'status_breakdown': {
                item['dispute_status']: item['count'] for item in status_breakdown
            },
            'reason_breakdown': {
                item['reason']: item['count'] for item in reason_breakdown
            },
            'pending_disputes_list': [
                {
                    'id': dispute.id,
                    'order_id': dispute.order.id if dispute.order else None,
                    'order_topic': dispute.order.topic if dispute.order else None,
                    'reason': dispute.reason,
                    'dispute_status': dispute.dispute_status,
                    'created_at': dispute.created_at.isoformat() if dispute.created_at else None,
                    'client_id': dispute.order.client.id if dispute.order and dispute.order.client else None,
                    'writer_id': dispute.order.assigned_writer.id if dispute.order and dispute.order.assigned_writer else None,
                }
                for dispute in pending_disputes
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get dispute analytics and trends."""
        all_disputes = Dispute.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_disputes = all_disputes.filter(order__website=website)
        
        # Trends by week (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_disputes.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            created=Count('id', filter=Q(dispute_status='open')),
            resolved=Count('id', filter=Q(dispute_status='resolved'))
        ).order_by('week')
        
        # Resolution rate trends - combined aggregation
        month_ago = timezone.now() - timedelta(days=30)
        recent_disputes = all_disputes.filter(created_at__gte=month_ago)
        recent_stats = recent_disputes.aggregate(
            total=Count('id'),
            resolved=Count('id', filter=Q(dispute_status='resolved'))
        )
        total_recent = recent_stats['total'] or 0
        resolved_recent = recent_stats['resolved'] or 0
        resolution_rate = (resolved_recent / total_recent * 100) if total_recent > 0 else 0
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'created': item['created'],
                    'resolved': item['resolved'],
                }
                for item in weekly_trends
            ],
            'resolution_rate_percent': round(resolution_rate, 2),
            'total_this_month': total_recent,
            'resolved_this_month': resolved_recent,
        })
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """Get pending disputes queue."""
        pending_disputes = Dispute.objects.filter(
            dispute_status='open'
        ).select_related('order', 'order__client', 'order__assigned_writer').order_by('-created_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                pending_disputes = pending_disputes.filter(order__website=website)
        
        from orders.serializers_legacy import DisputeSerializer
        serializer = DisputeSerializer(pending_disputes, many=True)
        
        return Response({
            'disputes': serializer.data,
            'count': pending_disputes.count(),
        })


class AdminRefundDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for refund management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get refund statistics dashboard."""
        # Get all refunds
        # Refund model has order_payment, not order directly
        all_refunds = Refund.objects.all().select_related('order_payment', 'order_payment__order', 'order_payment__order__client', 'client', 'processed_by', 'website')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_refunds = all_refunds.filter(website=website)
        
        # Combined aggregations - reduces from 7+ queries to 2 queries
        month_ago = timezone.now() - timedelta(days=30)
        
        # Main summary stats in one query
        summary_stats = all_refunds.aggregate(
            total_refunds=Count('id'),
            pending_refunds=Count('id', filter=Q(status='pending')),
            processed_this_month=Count('id', filter=Q(status='processed', processed_at__gte=month_ago)),
            total_requested=Sum(F('wallet_amount') + F('external_amount')),
            pending_total=Sum(F('wallet_amount') + F('external_amount'), filter=Q(status='pending')),
            avg_refund=Avg(F('wallet_amount') + F('external_amount')),
        )
        
        # Processed this month total
        processed_recent = all_refunds.filter(
            status='processed',
            processed_at__gte=month_ago
        )
        total_processed = processed_recent.aggregate(
            total=Sum(F('wallet_amount') + F('external_amount'))
        )['total'] or 0
        
        # Status breakdown
        status_breakdown = all_refunds.values('status').annotate(
            count=Count('id')
        )
        
        # Pending refunds - only fetch for list
        pending_refunds = all_refunds.filter(status='pending')[:20]
        
        # Refunds by type (refund model doesn't have 'reason', use 'type' instead)
        type_breakdown = all_refunds.values('type').annotate(
            count=Count('id')
        )
        
        return Response({
            'summary': {
                'total_refunds': summary_stats['total_refunds'] or 0,
                'pending_refunds': summary_stats['pending_refunds'] or 0,
                'processed_this_month': summary_stats['processed_this_month'] or 0,
                'total_requested': str(summary_stats['total_requested'] or 0),
                'total_processed_this_month': str(total_processed),
                'pending_total': str(summary_stats['pending_total'] or 0),
                'average_refund_amount': str(summary_stats['avg_refund'] or 0),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'type_breakdown': {
                item['type']: item['count'] for item in type_breakdown
            },
            'pending_refunds_list': [
                {
                    'id': refund.id,
                    'order_id': refund.order_payment.order.id if refund.order_payment and refund.order_payment.order else None,
                    'amount': str((refund.wallet_amount or 0) + (refund.external_amount or 0)),
                    'wallet_amount': str(refund.wallet_amount or 0),
                    'external_amount': str(refund.external_amount or 0),
                    'type': getattr(refund, 'type', None),
                    'status': refund.status,
                    'processed_at': refund.processed_at.isoformat() if refund.processed_at else None,
                    'client_id': refund.client.id if refund.client else (refund.order_payment.order.client.id if refund.order_payment and refund.order_payment.order and refund.order_payment.order.client else None),
                }
                for refund in pending_refunds
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get refund analytics and trends."""
        all_refunds = Refund.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_refunds = all_refunds.filter(order__website=website)
        
        # Trends by week (last 12 weeks)
        # Note: Refund model doesn't have created_at, using processed_at for processed refunds
        # For pending refunds, we'll include them in the current week
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        # Get all refunds and group by processed_at (or use id for approximate timing)
        # Since we don't have created_at, we'll use processed_at for processed refunds
        # and group others by their id (which gives approximate creation order)
        weekly_trends = all_refunds.filter(
            processed_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('processed_at')
        ).values('week').annotate(
            requested=Count('id'),
            processed=Count('id', filter=Q(status='processed')),
            total_amount=Sum(F('wallet_amount') + F('external_amount'))
        ).order_by('week')
        
        # Processing time (average)
        # Refund model doesn't have created_at, use processed_at and id for approximate timing
        processed_with_time = all_refunds.filter(
            status='processed',
            processed_at__isnull=False
        )
        
        avg_processing_hours = None
        if processed_with_time.exists():
            processing_times = []
            for refund in processed_with_time:
                if refund.processed_at and refund.created_at:
                    hours = (refund.processed_at - refund.created_at).total_seconds() / 3600
                    processing_times.append(hours)
            if processing_times:
                avg_processing_hours = sum(processing_times) / len(processing_times)
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'requested': item['requested'],
                    'processed': item['processed'],
                    'total_amount': str(item['total_amount'] or 0),
                }
                for item in weekly_trends
            ],
            'average_processing_hours': round(avg_processing_hours, 2) if avg_processing_hours else None,
        })
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """Get pending refunds queue."""
        pending_refunds = Refund.objects.filter(
            status='pending'
        ).select_related('order', 'order__client').order_by('-created_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                pending_refunds = pending_refunds.filter(order__website=website)
        
        try:
            from refunds.serializers import RefundSerializer
        except ImportError:
            from order_payments_management.serializers import RefundSerializer
        serializer = RefundSerializer(pending_refunds, many=True)
        
        return Response({
            'refunds': serializer.data,
            'count': pending_refunds.count(),
        })
    
    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """Get refund history with filters."""
        all_refunds = Refund.objects.all().select_related('order', 'order__client', 'processed_by')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_refunds = all_refunds.filter(order__website=website)
        
        # Apply filters
        status_filter = request.query_params.get('status', None)
        if status_filter:
            all_refunds = all_refunds.filter(status=status_filter)
        
        date_from = request.query_params.get('date_from', None)
        if date_from:
            all_refunds = all_refunds.filter(created_at__gte=date_from)
        
        date_to = request.query_params.get('date_to', None)
        if date_to:
            all_refunds = all_refunds.filter(created_at__lte=date_to)
        
        # Pagination
        limit = int(request.query_params.get('limit', 50))
        all_refunds = all_refunds[:limit]
        
        from refunds.serializers import RefundSerializer
        serializer = RefundSerializer(all_refunds, many=True)
        
        return Response({
            'refunds': serializer.data,
            'count': len(serializer.data),
        })


class AdminReviewModerationDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for review moderation."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='moderation-queue')
    def moderation_queue(self, request):
        """Get pending reviews for moderation."""
        from reviews_system.serializers import (
            WebsiteReviewSerializer, WriterReviewSerializer, OrderReviewSerializer
        )
        
        # Filter: pending = not approved, not shadowed, or flagged
        pending_filter = Q(is_approved=False) | Q(is_flagged=True) | Q(is_shadowed=True)
        
        # Get pending reviews by type
        pending_reviews = []
        
        # Website reviews
        website_reviews = WebsiteReview.objects.filter(pending_filter).select_related('reviewer', 'website')
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_reviews = website_reviews.filter(website=website)
        
        for review in website_reviews[:50]:
            pending_reviews.append({
                'id': review.id,
                'type': 'website',
                'reviewer': review.reviewer.username if review.reviewer else None,
                'rating': review.rating,
                'comment': review.comment,
                'is_flagged': review.is_flagged,
                'is_approved': review.is_approved,
                'created_at': review.created_at.isoformat() if review.created_at else None,
            })
        
        # Writer reviews
        writer_reviews = WriterReview.objects.filter(pending_filter).select_related('reviewer', 'writer', 'website')
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                writer_reviews = writer_reviews.filter(website=website)
        
        for review in writer_reviews[:50]:
            pending_reviews.append({
                'id': review.id,
                'type': 'writer',
                'reviewer': review.reviewer.username if review.reviewer else None,
                'writer': review.writer.username if review.writer else None,
                'rating': review.rating,
                'comment': review.comment,
                'is_flagged': review.is_flagged,
                'is_approved': review.is_approved,
                'created_at': review.created_at.isoformat() if review.created_at else None,
            })
        
        # Order reviews
        order_reviews = OrderReview.objects.filter(pending_filter).select_related('reviewer', 'order', 'website')
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                order_reviews = order_reviews.filter(website=website)
        
        for review in order_reviews[:50]:
            pending_reviews.append({
                'id': review.id,
                'type': 'order',
                'reviewer': review.reviewer.username if review.reviewer else None,
                'order_id': review.order.id if review.order else None,
                'rating': review.rating,
                'comment': review.comment,
                'is_flagged': review.is_flagged,
                'is_approved': review.is_approved,
                'created_at': review.created_at.isoformat() if review.created_at else None,
            })
        
        # Sort by created_at descending
        pending_reviews.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return Response({
            'reviews': pending_reviews[:100],
            'count': len(pending_reviews),
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get review analytics dashboard."""
        from django.db.models.functions import TruncWeek
        
        # Get all reviews
        all_website_reviews = WebsiteReview.objects.all()
        all_writer_reviews = WriterReview.objects.all()
        all_order_reviews = OrderReview.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_website_reviews = all_website_reviews.filter(website=website)
                all_writer_reviews = all_writer_reviews.filter(website=website)
                all_order_reviews = all_order_reviews.filter(website=website)
        
        # Combined aggregations - reduces from 6 queries to 3 queries
        website_stats = all_website_reviews.aggregate(
            total=Count('id'),
            flagged=Count('id', filter=Q(is_flagged=True))
        )
        writer_stats = all_writer_reviews.aggregate(
            total=Count('id'),
            flagged=Count('id', filter=Q(is_flagged=True))
        )
        order_stats = all_order_reviews.aggregate(
            total=Count('id'),
            flagged=Count('id', filter=Q(is_flagged=True))
        )
        
        total_reviews = (website_stats['total'] or 0) + (writer_stats['total'] or 0) + (order_stats['total'] or 0)
        flagged_reviews = (website_stats['flagged'] or 0) + (writer_stats['flagged'] or 0) + (order_stats['flagged'] or 0)
        
        # Average rating (combine all ratings)
        all_ratings = []
        for review in list(all_website_reviews.values_list('rating', flat=True)) + \
                     list(all_writer_reviews.values_list('rating', flat=True)) + \
                     list(all_order_reviews.values_list('rating', flat=True)):
            if review is not None:
                all_ratings.append(review)
        
        avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
        
        # Rating distribution
        rating_distribution = {}
        for rating in all_ratings:
            rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
        
        # Reviews by week (last 12 weeks) - combine all types
        weeks_ago = timezone.now() - timedelta(weeks=12)
        
        website_weekly = all_website_reviews.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(count=Count('id'))
        
        writer_weekly = all_writer_reviews.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(count=Count('id'))
        
        order_weekly = all_order_reviews.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(count=Count('id'))
        
        # Combine weekly trends
        weekly_dict = {}
        for item in list(website_weekly) + list(writer_weekly) + list(order_weekly):
            week_key = item['week'].isoformat() if item['week'] else None
            if week_key:
                weekly_dict[week_key] = weekly_dict.get(week_key, 0) + item['count']
        
        weekly_trends = [
            {
                'week': week,
                'count': count,
            }
            for week, count in sorted(weekly_dict.items())
        ]
        
        return Response({
            'summary': {
                'total_reviews': total_reviews,
                'website_reviews': website_stats['total'] or 0,
                'writer_reviews': writer_stats['total'] or 0,
                'order_reviews': order_stats['total'] or 0,
                'flagged_reviews': flagged_reviews,
                'average_rating': round(avg_rating, 2),
            },
            'rating_distribution': rating_distribution,
            'weekly_trends': weekly_trends,
        })


class AdminOrderManagementDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for order management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get order statistics dashboard."""
        all_orders = Order.objects.all().select_related('client', 'writer', 'website')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_orders = all_orders.filter(website=website)
        
        # Combined aggregations - reduces from 6+ queries to 2 queries
        week_ago = timezone.now() - timedelta(days=7)
        month_ago = timezone.now() - timedelta(days=30)
        now = timezone.now()
        
        # Main summary stats in one query
        summary_stats = all_orders.aggregate(
            total_orders=Count('id'),
            needs_assignment=Count('id', filter=Q(
                status=OrderStatus.PENDING_ASSIGNMENT.value,
                assigned_writer__isnull=True
            )),
            overdue_orders=Count('id', filter=Q(
                client_deadline__lt=now,
                status__in=[
                    OrderStatus.IN_PROGRESS.value,
                    OrderStatus.UNDER_EDITING.value,
                    OrderStatus.PENDING_REVISION.value
                ]
            )),
            stuck_orders=Count('id', filter=Q(
                status__in=[
                    OrderStatus.IN_PROGRESS.value,
                    OrderStatus.UNDER_EDITING.value,
                ],
                updated_at__lt=week_ago
            )),
            recent_orders=Count('id', filter=Q(created_at__gte=month_ago)),
            total_revenue=Sum('total_price', filter=Q(status=OrderStatus.COMPLETED.value)),
        )
        
        # Status breakdown
        status_breakdown = all_orders.values('status').annotate(
            count=Count('id')
        )
        
        # Orders needing assignment - only fetch for list
        needs_assignment = all_orders.filter(
            status=OrderStatus.PENDING_ASSIGNMENT.value,
            assigned_writer__isnull=True
        )[:20]
        
        # Overdue orders - only fetch for list
        overdue_orders = all_orders.filter(
            client_deadline__lt=now,
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.UNDER_EDITING.value,
                OrderStatus.PENDING_REVISION.value
            ]
        )[:20]
        
        # Calculate transition-based counts - optimized to reduce queries
        # Build all valid source statuses first, then do one query
        target_statuses = [
            'in_progress', 'submitted', 'completed', 'cancelled', 
            'on_hold', 'available', 'revision_requested', 'disputed',
            'under_editing', 'closed', 'reopened'
        ]
        
        # Build a map of source statuses to target statuses
        status_to_targets = {}
        for source, transitions in VALID_TRANSITIONS.items():
            for target in target_statuses:
                if target in transitions:
                    if target not in status_to_targets:
                        status_to_targets[target] = []
                    if source not in status_to_targets[target]:
                        status_to_targets[target].append(source)
        
        # Get counts for all source statuses in one query
        status_counts = dict(all_orders.values('status').annotate(count=Count('id')))
        
        # Calculate transition counts from the status_counts
        transition_counts = {}
        for target_status in target_statuses:
            valid_sources = status_to_targets.get(target_status, [])
            count = sum(status_counts.get(source, 0) for source in valid_sources)
            transition_counts[f'can_transition_to_{target_status}'] = count
        
        return Response({
            'summary': {
                'total_orders': summary_stats['total_orders'] or 0,
                'needs_assignment': summary_stats['needs_assignment'] or 0,
                'overdue_orders': summary_stats['overdue_orders'] or 0,
                'stuck_orders': summary_stats['stuck_orders'] or 0,
                'recent_orders': summary_stats['recent_orders'] or 0,
                'total_revenue': str(summary_stats['total_revenue'] or 0),
                **transition_counts,  # Add transition counts to summary
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'transition_counts': transition_counts,  # Also include as separate field
            'needs_assignment_list': [
                {
                    'id': order.id,
                    'topic': order.topic,
                    'pages': order.number_of_pages,
                    'deadline': order.client_deadline.isoformat() if order.client_deadline else None,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                }
                for order in needs_assignment
            ],
            'overdue_orders_list': [
                {
                    'id': order.id,
                    'topic': order.topic,
                    'pages': order.number_of_pages,
                    'deadline': order.client_deadline.isoformat() if order.client_deadline else None,
                    'status': order.status,
                }
                for order in overdue_orders
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get order analytics and trends."""
        all_orders = Order.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_orders = all_orders.filter(website=website)
        
        # Trends by week (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_orders.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            created=Count('id'),
            completed=Count('id', filter=Q(status=OrderStatus.COMPLETED.value)),
            revenue=Sum('total_price', filter=Q(status=OrderStatus.COMPLETED.value))
        ).order_by('week')
        
        # Service breakdown (using type_of_work)
        service_breakdown = all_orders.values('type_of_work__name').annotate(
            count=Count('id'),
            revenue=Sum('total_price', filter=Q(status=OrderStatus.COMPLETED.value))
        )
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'created': item['created'],
                    'completed': item['completed'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in weekly_trends
            ],
            'service_breakdown': [
                {
                    'service_type': item['type_of_work__name'] or 'Unknown',
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in service_breakdown
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='assignment-queue')
    def assignment_queue(self, request):
        """Get orders needing assignment."""
        needs_assignment = Order.objects.filter(
            status=OrderStatus.PENDING_ASSIGNMENT.value,
            writer__isnull=True
        ).select_related('client', 'website').order_by('-created_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                needs_assignment = needs_assignment.filter(website=website)
        
        try:
            from orders.serializers import OrderSerializer
        except ImportError:
            from orders.serializers_legacy import OrderSerializer
        serializer = OrderSerializer(needs_assignment, many=True)
        
        return Response({
            'orders': serializer.data,
            'count': needs_assignment.count(),
        })
    
    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue(self, request):
        """Get overdue orders."""
        overdue_orders = Order.objects.filter(
            client_deadline__lt=timezone.now(),
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.UNDER_EDITING.value,
                OrderStatus.PENDING_REVISION.value
            ]
        ).select_related('client', 'assigned_writer', 'website').order_by('client_deadline')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                overdue_orders = overdue_orders.filter(website=website)
        
        try:
            from orders.serializers import OrderSerializer
        except ImportError:
            from orders.serializers_legacy import OrderSerializer
        serializer = OrderSerializer(overdue_orders, many=True)
        
        return Response({
            'orders': serializer.data,
            'count': overdue_orders.count(),
        })
    
    @action(detail=False, methods=['get'], url_path='stuck')
    def stuck(self, request):
        """Get stuck orders (no progress)."""
        week_ago = timezone.now() - timedelta(days=7)
        stuck_orders = Order.objects.filter(
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.UNDER_EDITING.value,
            ],
            updated_at__lt=week_ago
        ).select_related('client', 'writer', 'website').order_by('updated_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                stuck_orders = stuck_orders.filter(website=website)
        
        try:
            from orders.serializers import OrderSerializer
        except ImportError:
            from orders.serializers_legacy import OrderSerializer
        serializer = OrderSerializer(stuck_orders, many=True)
        
        return Response({
            'orders': serializer.data,
            'count': stuck_orders.count(),
        })


# ============================================================================
# EXPRESS CLASSES DASHBOARD
# ============================================================================

class AdminExpressClassesDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for express classes management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get express class statistics dashboard."""
        all_express_classes = ExpressClass.objects.all().select_related(
            'client', 'assigned_writer', 'website'
        )
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_express_classes = all_express_classes.filter(website=website)
        
        # Status breakdown
        status_breakdown = all_express_classes.values('status').annotate(
            count=Count('id')
        )
        
        # Pending inquiries
        pending_inquiries = all_express_classes.filter(status='inquiry')
        
        # Scope review queue
        scope_review = all_express_classes.filter(status='scope_review')
        
        # Priced (awaiting assignment)
        priced = all_express_classes.filter(status='priced')
        
        # Assigned/In Progress
        active = all_express_classes.filter(status__in=['assigned', 'in_progress'])
        
        # Completed
        completed = all_express_classes.filter(status='completed')
        
        # Total revenue
        total_revenue = completed.aggregate(
            total=Sum('price')
        )['total'] or 0
        
        return Response({
            'summary': {
                'total_classes': all_express_classes.count(),
                'pending_inquiries': pending_inquiries.count(),
                'scope_review': scope_review.count(),
                'priced': priced.count(),
                'assigned': all_express_classes.filter(status='assigned').count(),
                'in_progress': all_express_classes.filter(status='in_progress').count(),
                'active': active.count(),
                'completed': completed.count(),
                'total_revenue': str(total_revenue),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'pending_inquiries_list': [
                {
                    'id': ec.id,
                    'client_id': ec.client.id if ec.client else None,
                    'client_username': ec.client.username if ec.client else None,
                    'discipline': ec.discipline,
                    'start_date': ec.start_date.isoformat() if ec.start_date else None,
                    'end_date': ec.end_date.isoformat() if ec.end_date else None,
                    'created_at': ec.created_at.isoformat() if ec.created_at else None,
                }
                for ec in pending_inquiries[:20]
            ],
            'scope_review_list': [
                {
                    'id': ec.id,
                    'client_id': ec.client.id if ec.client else None,
                    'client_username': ec.client.username if ec.client else None,
                    'discipline': ec.discipline,
                    'created_at': ec.created_at.isoformat() if ec.created_at else None,
                }
                for ec in scope_review[:20]
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get express class analytics."""
        all_express_classes = ExpressClass.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_express_classes = all_express_classes.filter(website=website)
        
        # Trends by week (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_express_classes.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            created=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            revenue=Sum('price', filter=Q(status='completed'))
        ).order_by('week')
        
        # Discipline breakdown
        discipline_breakdown = all_express_classes.values('discipline').annotate(
            count=Count('id'),
            revenue=Sum('price', filter=Q(status='completed'))
        ).order_by('-count')[:10]
        
        # Average class value
        avg_class_value = all_express_classes.filter(
            status='completed',
            price__isnull=False
        ).aggregate(
            avg=Avg('price')
        )['avg'] or 0
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'created': item['created'],
                    'completed': item['completed'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in weekly_trends
            ],
            'discipline_breakdown': [
                {
                    'discipline': item['discipline'],
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in discipline_breakdown
            ],
            'averages': {
                'avg_class_value': str(avg_class_value),
            },
        })


# ============================================================================
# CLASS MANAGEMENT DASHBOARD (BUNDLES, ETC.)
# ============================================================================

class AdminClassManagementDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for class/bundle management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get class bundle statistics dashboard."""
        all_bundles = ClassBundle.objects.all().select_related('client', 'website')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_bundles = all_bundles.filter(website=website)
        
        # Status breakdown
        status_breakdown = all_bundles.values('status').annotate(
            count=Count('id')
        )
        
        # Pending deposits
        pending_deposits = all_bundles.filter(
            status='pending_deposit',
            deposit_paid=False
        )
        
        # Active bundles
        active_bundles = all_bundles.filter(
            status__in=['active', 'in_progress']
        )
        
        # Total revenue
        total_revenue = all_bundles.filter(
            status='completed'
        ).aggregate(
            total=Sum('total_cost')
        )['total'] or 0
        
        # Installment tracking
        bundles_with_installments = all_bundles.filter(
            payment_plan='installment'
        )
        
        return Response({
            'summary': {
                'total_bundles': all_bundles.count(),
                'pending_deposits': pending_deposits.count(),
                'active_bundles': active_bundles.count(),
                'total_revenue': str(total_revenue),
                'installment_bundles': bundles_with_installments.count(),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'pending_deposits_list': [
                {
                    'id': bundle.id,
                    'client_id': bundle.client.id if bundle.client else None,
                    'total_cost': str(bundle.total_cost),
                    'deposit_amount': str(bundle.deposit_amount),
                    'created_at': bundle.created_at.isoformat() if bundle.created_at else None,
                }
                for bundle in pending_deposits[:20]
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get class bundle analytics."""
        all_bundles = ClassBundle.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_bundles = all_bundles.filter(website=website)
        
        # Trends by week (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_bundles.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            created=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            revenue=Sum('total_cost', filter=Q(status='completed'))
        ).order_by('week')
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'created': item['created'],
                    'completed': item['completed'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in weekly_trends
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='installment-tracking')
    def installment_tracking(self, request):
        """Get installment payment tracking."""
        bundles_with_installments = ClassBundle.objects.filter(
            payment_plan='installment'
        ).select_related('client', 'website')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                bundles_with_installments = bundles_with_installments.filter(website=website)
        
        # Get bundles with pending installments
        pending_installments = []
        for bundle in bundles_with_installments:
            # Check if there are pending installments
            from class_management.models import ClassBundleInstallment
            installments = ClassBundleInstallment.objects.filter(
                bundle=bundle,
                status='pending'
            )
            if installments.exists():
                pending_installments.append({
                    'bundle_id': bundle.id,
                    'client_id': bundle.client.id if bundle.client else None,
                    'total_cost': str(bundle.total_cost),
                    'pending_installments': installments.count(),
                    'next_due_date': installments.order_by('due_date').first().due_date.isoformat() if installments.exists() else None,
                })
        
        return Response({
            'bundles_with_installments': len(bundles_with_installments),
            'pending_installments': pending_installments[:20],
        })


# ============================================================================
# SPECIAL ORDERS DASHBOARD
# ============================================================================

class AdminSpecialOrdersManagementDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for special orders management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get special orders statistics dashboard."""
        all_special_orders = SpecialOrder.objects.all().select_related(
            'client', 'writer', 'website', 'predefined_type'
        )
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_special_orders = all_special_orders.filter(website=website)
        
        # Status breakdown
        status_breakdown = all_special_orders.values('status').annotate(
            count=Count('id')
        )
        
        # Order type breakdown
        type_breakdown = all_special_orders.values('order_type').annotate(
            count=Count('id')
        )
        
        # Pending approvals
        pending_approvals = all_special_orders.filter(
            status='awaiting_approval',
            is_approved=False
        )
        
        # In progress orders
        in_progress = all_special_orders.filter(status='in_progress')
        
        # Total revenue
        total_revenue = all_special_orders.filter(
            status='completed'
        ).aggregate(
            total=Sum('total_cost')
        )['total'] or 0
        
        # Pending deposits
        pending_deposits = all_special_orders.filter(
            status__in=['inquiry', 'awaiting_approval', 'in_progress']
        ).exclude(deposit_required__isnull=True).exclude(deposit_required=0)
        
        # Calculate total pending deposit amount
        total_pending_deposits = pending_deposits.aggregate(
            total=Sum('deposit_required')
        )['total'] or 0
        
        # Orders with pending installments
        orders_with_installments = all_special_orders.filter(
            installments__is_paid=False
        ).distinct()
        
        return Response({
            'summary': {
                'total_orders': all_special_orders.count(),
                'pending_approvals': pending_approvals.count(),
                'in_progress': in_progress.count(),
                'completed': all_special_orders.filter(status='completed').count(),
                'total_revenue': str(total_revenue),
                'total_pending_deposits': str(total_pending_deposits),
                'orders_with_installments': orders_with_installments.count(),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'type_breakdown': {
                item['order_type']: item['count'] for item in type_breakdown
            },
            'pending_approvals_list': [
                {
                    'id': order.id,
                    'client_id': order.client.id if order.client else None,
                    'client_username': order.client.username if order.client else None,
                    'order_type': order.order_type,
                    'total_cost': str(order.total_cost) if order.total_cost else None,
                    'deposit_required': str(order.deposit_required) if order.deposit_required else None,
                    'duration_days': order.duration_days,
                    'inquiry_details': order.inquiry_details[:200] if order.inquiry_details else None,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                }
                for order in pending_approvals[:20]
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get special orders analytics."""
        all_special_orders = SpecialOrder.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_special_orders = all_special_orders.filter(website=website)
        
        # Trends by week (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_special_orders.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            created=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            revenue=Sum('total_cost', filter=Q(status='completed'))
        ).order_by('week')
        
        # Revenue by order type
        revenue_by_type = all_special_orders.filter(
            status='completed'
        ).values('order_type').annotate(
            count=Count('id'),
            revenue=Sum('total_cost')
        )
        
        # Average order value
        avg_order_value = all_special_orders.filter(
            status='completed',
            total_cost__isnull=False
        ).aggregate(
            avg=Avg('total_cost')
        )['avg'] or 0
        
        # Average duration
        avg_duration = all_special_orders.aggregate(
            avg=Avg('duration_days')
        )['avg'] or 0
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'created': item['created'],
                    'completed': item['completed'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in weekly_trends
            ],
            'revenue_by_type': [
                {
                    'order_type': item['order_type'],
                    'count': item['count'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in revenue_by_type
            ],
            'averages': {
                'avg_order_value': str(avg_order_value),
                'avg_duration_days': round(avg_duration, 1) if avg_duration else 0,
            },
        })
    
    @action(detail=False, methods=['get'], url_path='approval-queue')
    def approval_queue(self, request):
        """Get special orders awaiting approval."""
        pending_approvals = SpecialOrder.objects.filter(
            status='awaiting_approval',
            is_approved=False
        ).select_related('client', 'website', 'predefined_type').order_by('-created_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                pending_approvals = pending_approvals.filter(website=website)
        
        try:
            from special_orders.serializers import SpecialOrderSerializer
        except ImportError:
            from rest_framework import serializers
            class SpecialOrderSerializer(serializers.ModelSerializer):
                class Meta:
                    model = SpecialOrder
                    fields = '__all__'
        serializer = SpecialOrderSerializer(pending_approvals, many=True)
        
        return Response({
            'orders': serializer.data,
            'count': pending_approvals.count(),
        })
    
    @action(detail=False, methods=['get'], url_path='installment-tracking')
    def installment_tracking(self, request):
        """Get special orders with pending installments."""
        all_special_orders = SpecialOrder.objects.all().select_related(
            'client', 'website'
        )
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_special_orders = all_special_orders.filter(website=website)
        
        # Get orders with pending installments
        pending_installments = []
        for order in all_special_orders:
            installments = InstallmentPayment.objects.filter(
                special_order=order,
                is_paid=False
            ).order_by('due_date')
            
            if installments.exists():
                next_installment = installments.first()
                total_pending = installments.aggregate(
                    total=Sum('amount_due')
                )['total'] or 0
                
                pending_installments.append({
                    'order_id': order.id,
                    'client_id': order.client.id if order.client else None,
                    'client_username': order.client.username if order.client else None,
                    'total_cost': str(order.total_cost) if order.total_cost else None,
                    'status': order.status,
                    'pending_installments_count': installments.count(),
                    'total_pending_amount': str(total_pending),
                    'next_due_date': next_installment.due_date.isoformat() if next_installment else None,
                    'next_due_amount': str(next_installment.amount_due) if next_installment else None,
                })
        
        # Sort by next due date
        pending_installments.sort(key=lambda x: x['next_due_date'] or '', reverse=False)
        
        return Response({
            'orders_with_pending_installments': len(pending_installments),
            'pending_installments': pending_installments[:50],
        })


class AdminAdvancedAnalyticsDashboardViewSet(viewsets.ViewSet):
    """Advanced analytics dashboard aggregating all admin metrics."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get comprehensive advanced analytics dashboard."""
        from django.db.models.functions import TruncWeek, TruncMonth, TruncDay
        from order_payments_management.models import OrderPayment
        from tickets.models import Ticket
        from writer_management.models.profile import WriterProfile
        
        # Filter by website if needed
        website_filter = None
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_filter = website
        
        # Time range
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # === REVENUE ANALYTICS ===
        revenue_orders = Order.objects.filter(
            created_at__gte=date_from,
            is_paid=True
        )
        if website_filter:
            revenue_orders = revenue_orders.filter(website=website_filter)
        
        total_revenue = revenue_orders.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Revenue by day
        daily_revenue = revenue_orders.annotate(
            day=TruncDay('created_at')
        ).values('day').annotate(
            revenue=Sum('total_price'),
            order_count=Count('id')
        ).order_by('day')
        
        # Revenue by service type (using type_of_work)
        revenue_by_service = revenue_orders.values('type_of_work__name').annotate(
            revenue=Sum('total_price'),
            count=Count('id')
        ).order_by('-revenue')
        
        # === ORDER ANALYTICS ===
        all_orders = Order.objects.filter(created_at__gte=date_from)
        if website_filter:
            all_orders = all_orders.filter(website=website_filter)
        
        # Order conversion funnel
        conversion_funnel = {
            'created': all_orders.count(),
            'paid': all_orders.filter(is_paid=True).count(),
            'assigned': all_orders.filter(assigned_writer__isnull=False).count(),
            'in_progress': all_orders.filter(status=OrderStatus.IN_PROGRESS.value).count(),
            'submitted': all_orders.filter(status=OrderStatus.SUBMITTED.value).count(),
            'completed': all_orders.filter(status=OrderStatus.COMPLETED.value).count(),
        }
        
        # Average order value
        avg_order_value = revenue_orders.aggregate(
            avg=Avg('total_price')
        )['avg'] or 0
        
        # Order completion rate
        completion_rate = (conversion_funnel['completed'] / conversion_funnel['created'] * 100) if conversion_funnel['created'] > 0 else 0
        
        # === WRITER PERFORMANCE ===
        writers = WriterProfile.objects.all()
        if website_filter:
            writers = writers.filter(user__website=website_filter)
        
        # WriterProfile already has 'total_earnings' and 'average_rating' fields
        # Use different annotation name for period earnings to avoid conflict
        writer_performance = writers.annotate(
            completed_orders_count=Count('user__orders_as_writer', filter=Q(
                user__orders_as_writer__status=OrderStatus.COMPLETED.value,
                user__orders_as_writer__created_at__gte=date_from
            )),
            period_total_earnings=Sum('user__orders_as_writer__writer_compensation', filter=Q(
                user__orders_as_writer__status=OrderStatus.COMPLETED.value,
                user__orders_as_writer__created_at__gte=date_from
            ))
        ).filter(completed_orders_count__gt=0).order_by('-completed_orders_count')[:10]
        
        # === CLIENT ANALYTICS ===
        from users.models import User
        clients = User.objects.filter(
            role='client',
            orders_as_client__created_at__gte=date_from
        )
        if website_filter:
            clients = clients.filter(website=website_filter)
        
        client_analytics = clients.annotate(
            order_count=Count('orders_as_client', filter=Q(
                orders_as_client__created_at__gte=date_from
            )),
            total_spent=Sum('orders_as_client__total_price', filter=Q(
                orders_as_client__is_paid=True,
                orders_as_client__created_at__gte=date_from
            ))
        ).filter(order_count__gt=0).order_by('-total_spent')[:10]
        
        # === SUPPORT METRICS ===
        tickets = Ticket.objects.filter(created_at__gte=date_from)
        if website_filter:
            tickets = tickets.filter(website=website_filter)
        
        support_metrics = {
            'total_tickets': tickets.count(),
            'resolved_tickets': tickets.filter(status='closed').count(),
            'avg_resolution_time': None,  # Would need to calculate from ticket timestamps
            'tickets_by_priority': tickets.values('priority').annotate(
                count=Count('id')
            ),
        }
        
        # === DISPUTE METRICS ===
        disputes = Dispute.objects.filter(created_at__gte=date_from)
        if website_filter:
            disputes = disputes.filter(order__website=website_filter)
        
        dispute_metrics = {
            'total_disputes': disputes.count(),
            'resolved': disputes.filter(dispute_status='resolved').count(),
            'pending': disputes.filter(dispute_status='open').count(),
            'resolution_rate': (disputes.filter(dispute_status='resolved').count() / disputes.count() * 100) if disputes.count() > 0 else 0,
        }
        
        # === REFUND METRICS ===
        # Refund model has direct 'website' field, not 'order__website'
        # Refund model doesn't have 'created_at', use processed_at or order_payment creation
        refunds = Refund.objects.all()
        if website_filter:
            refunds = refunds.filter(website=website_filter)
        # Filter by date - use processed_at if available, otherwise order_payment creation
        if date_from:
            refunds = refunds.filter(
                Q(processed_at__gte=date_from) | 
                Q(processed_at__isnull=True, order_payment__created_at__gte=date_from)
            )
        
        refund_metrics = {
            'total_refunds': refunds.count(),
            'total_amount': refunds.aggregate(total=Sum(F('wallet_amount') + F('external_amount')))['total'] or 0,
            'approved': refunds.filter(status='processed').count(),  # Refund status is 'processed' not 'approved'
            'pending': refunds.filter(status='pending').count(),
        }
        
        # === TRENDS ===
        weekly_trends = all_orders.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            orders_created=Count('id'),
            orders_completed=Count('id', filter=Q(status=OrderStatus.COMPLETED.value)),
            revenue=Sum('total_price', filter=Q(is_paid=True))
        ).order_by('week')
        
        return Response({
            'summary': {
                'total_revenue': str(total_revenue),
                'total_orders': conversion_funnel['created'],
                'completed_orders': conversion_funnel['completed'],
                'completion_rate': round(completion_rate, 2),
                'avg_order_value': str(avg_order_value),
                'total_tickets': support_metrics['total_tickets'],
                'total_disputes': dispute_metrics['total_disputes'],
                'total_refunds': refund_metrics['total_refunds'],
            },
            'revenue_analytics': {
                'total': str(total_revenue),
                'daily_breakdown': [
                    {
                        'date': item['day'].isoformat() if item['day'] else None,
                        'revenue': str(item['revenue'] or 0),
                        'order_count': item['order_count'],
                    }
                    for item in daily_revenue
                ],
                'by_service_type': [
                    {
                        'service_type': item['type_of_work__name'] or 'Unknown',
                        'revenue': str(item['revenue'] or 0),
                        'count': item['count'],
                    }
                    for item in revenue_by_service
                ],
            },
            'order_analytics': {
                'conversion_funnel': conversion_funnel,
                'completion_rate': round(completion_rate, 2),
                'avg_order_value': str(avg_order_value),
            },
            'writer_performance': [
                {
                    'writer_id': writer.id,
                    'username': writer.user.username if writer.user else None,
                    'completed_orders': writer.completed_orders_count,  # Use annotation name
                    'total_earnings': str(writer.period_total_earnings or 0),  # Use annotation name
                    'avg_rating': round(float(writer.average_rating), 2) if writer.average_rating else None,  # Use existing field
                }
                for writer in writer_performance
            ],
            'client_analytics': [
                {
                    'client_id': client.id,
                    'username': client.username,
                    'email': client.email,
                    'order_count': client.order_count,
                    'total_spent': str(client.total_spent or 0),
                }
                for client in client_analytics
            ],
            'support_metrics': support_metrics,
            'dispute_metrics': dispute_metrics,
            'refund_metrics': {
                'total_refunds': refund_metrics['total_refunds'],
                'total_amount': str(refund_metrics['total_amount']),
                'approved': refund_metrics['approved'],
                'pending': refund_metrics['pending'],
            },
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'orders_created': item['orders_created'],
                    'orders_completed': item['orders_completed'],
                    'revenue': str(item['revenue'] or 0),
                }
                for item in weekly_trends
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='comparison')
    def comparison(self, request):
        """Compare analytics between two time periods."""
        period1_days = int(request.query_params.get('period1_days', 30))
        period2_days = int(request.query_params.get('period2_days', 30))
        
        now = timezone.now()
        period1_start = now - timedelta(days=period1_days)
        period2_start = now - timedelta(days=period2_days)
        period2_end = now - timedelta(days=period1_days)
        
        # Filter by website if needed
        website_filter = None
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                website_filter = website
        
        # Period 1 metrics
        period1_orders = Order.objects.filter(
            created_at__gte=period1_start,
            created_at__lt=period2_start
        )
        if website_filter:
            period1_orders = period1_orders.filter(website=website_filter)
        
        period1_revenue = period1_orders.filter(is_paid=True).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        period1_completed = period1_orders.filter(status=OrderStatus.COMPLETED.value).count()
        
        # Period 2 metrics
        period2_orders = Order.objects.filter(
            created_at__gte=period2_start,
            created_at__lt=period2_end
        )
        if website_filter:
            period2_orders = period2_orders.filter(website=website_filter)
        
        period2_revenue = period2_orders.filter(is_paid=True).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        period2_completed = period2_orders.filter(status=OrderStatus.COMPLETED.value).count()
        
        # Calculate changes
        revenue_change = ((period1_revenue - period2_revenue) / period2_revenue * 100) if period2_revenue > 0 else 0
        completed_change = ((period1_completed - period2_completed) / period2_completed * 100) if period2_completed > 0 else 0
        
        return Response({
            'period1': {
                'days': period1_days,
                'start_date': period1_start.isoformat(),
                'end_date': period2_start.isoformat(),
                'revenue': str(period1_revenue),
                'completed_orders': period1_completed,
                'total_orders': period1_orders.count(),
            },
            'period2': {
                'days': period2_days,
                'start_date': period2_start.isoformat(),
                'end_date': period2_end.isoformat(),
                'revenue': str(period2_revenue),
                'completed_orders': period2_completed,
                'total_orders': period2_orders.count(),
            },
            'changes': {
                'revenue_change_percent': round(revenue_change, 2),
                'completed_change_percent': round(completed_change, 2),
                'revenue_change_amount': str(period1_revenue - period2_revenue),
            },
        })
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_analytics(self, request):
        """Export analytics data as CSV/JSON."""
        import csv
        import json
        from django.http import HttpResponse
        
        format_type = request.query_params.get('format', 'json')  # json or csv
        analytics_type = request.query_params.get('type', 'dashboard')  # dashboard, orders, reviews, etc.
        
        # Get dashboard data
        dashboard_data = self.dashboard(request)
        data = dashboard_data.data
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="analytics_export_{timezone.now().date()}.csv"'
            
            writer = csv.writer(response)
            
            # Write summary
            if 'summary' in data:
                writer.writerow(['Metric', 'Value'])
                for key, value in data['summary'].items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                writer.writerow([])
            
            # Write revenue analytics
            if 'revenue_analytics' in data and 'daily_breakdown' in data['revenue_analytics']:
                writer.writerow(['Date', 'Revenue', 'Orders'])
                for item in data['revenue_analytics']['daily_breakdown']:
                    writer.writerow([
                        item.get('date', ''),
                        item.get('revenue', 0),
                        item.get('order_count', 0)
                    ])
                writer.writerow([])
            
            # Write weekly trends
            if 'weekly_trends' in data:
                writer.writerow(['Week', 'Orders Created', 'Orders Completed', 'Revenue'])
                for item in data['weekly_trends']:
                    writer.writerow([
                        item.get('week', ''),
                        item.get('orders_created', 0),
                        item.get('orders_completed', 0),
                        item.get('revenue', 0)
                    ])
            
            return response
        else:
            # JSON export
            response = HttpResponse(
                json.dumps(data, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = f'attachment; filename="analytics_export_{timezone.now().date()}.json"'
            return response


class AdminFinesManagementDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for fines management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get fines statistics dashboard."""
        all_fines = Fine.objects.all().select_related(
            'order', 'order__client', 'order__assigned_writer', 'issued_by', 'waived_by'
        )
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_fines = all_fines.filter(order__website=website)
        
        # Status breakdown
        status_breakdown = all_fines.values('status').annotate(
            count=Count('id')
        )
        
        # Fine type breakdown
        type_breakdown = all_fines.values('fine_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Active fines (not waived/voided/resolved)
        active_fines = all_fines.filter(
            status__in=[FineStatus.ISSUED.value, FineStatus.DISPUTED.value]
        )
        
        # Total fine amount
        total_fine_amount = all_fines.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Active fine amount
        active_fine_amount = active_fines.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Waived fines
        waived_fines = all_fines.filter(status=FineStatus.WAIVED.value)
        waived_amount = waived_fines.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Disputed fines
        disputed_fines = all_fines.filter(status=FineStatus.DISPUTED.value)
        
        # Recent fines (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        recent_fines = all_fines.filter(imposed_at__gte=month_ago)
        
        return Response({
            'summary': {
                'total_fines': all_fines.count(),
                'active_fines': active_fines.count(),
                'disputed_fines': disputed_fines.count(),
                'waived_fines': waived_fines.count(),
                'total_fine_amount': str(total_fine_amount),
                'active_fine_amount': str(active_fine_amount),
                'waived_amount': str(waived_amount),
                'recent_fines_30d': recent_fines.count(),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'type_breakdown': [
                {
                    'fine_type': item['fine_type'] or 'Unknown',
                    'count': item['count'],
                    'total_amount': str(item['total_amount'] or 0),
                }
                for item in type_breakdown
            ],
            'disputed_fines_list': [
                {
                    'id': fine.id,
                    'order_id': fine.order.id if fine.order else None,
                    'writer_id': fine.order.assigned_writer.id if fine.order and fine.order.assigned_writer else None,
                    'writer_username': fine.order.assigned_writer.username if fine.order and fine.order.assigned_writer else None,
                    'fine_type': fine.fine_type or 'Unknown',
                    'amount': str(fine.amount),
                    'reason': fine.reason[:200] if fine.reason else None,
                    'imposed_at': fine.imposed_at.isoformat() if fine.imposed_at else None,
                }
                for fine in disputed_fines[:20]
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get fines analytics."""
        all_fines = Fine.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_fines = all_fines.filter(order__website=website)
        
        # Trends by week (last 12 weeks)
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_fines.filter(
            imposed_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('imposed_at')
        ).values('week').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ).order_by('week')
        
        # Fines by type over time
        type_trends = all_fines.filter(
            imposed_at__gte=weeks_ago
        ).values('fine_type').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Average fine amount
        avg_fine_amount = all_fines.aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        # Dispute resolution rate
        total_disputed = all_fines.filter(status=FineStatus.DISPUTED.value).count()
        resolved_disputes = FineAppeal.objects.filter(
            review_decision__in=['accepted', 'rejected']
        ).count()
        dispute_resolution_rate = (resolved_disputes / total_disputed * 100) if total_disputed > 0 else 0
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count'],
                    'total_amount': str(item['total_amount'] or 0),
                }
                for item in weekly_trends
            ],
            'type_trends': [
                {
                    'fine_type': item['fine_type'] or 'Unknown',
                    'count': item['count'],
                    'total_amount': str(item['total_amount'] or 0),
                }
                for item in type_trends
            ],
            'metrics': {
                'avg_fine_amount': str(avg_fine_amount),
                'dispute_resolution_rate': round(dispute_resolution_rate, 2),
            },
        })
    
    @action(detail=False, methods=['get'], url_path='dispute-queue')
    def dispute_queue(self, request):
        """Get fines with active disputes."""
        disputed_fines = Fine.objects.filter(
            status=FineStatus.DISPUTED.value
        ).select_related(
            'order', 'order__client', 'order__assigned_writer'
        ).prefetch_related('fine_appeals').order_by('-imposed_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                disputed_fines = disputed_fines.filter(order__website=website)
        
        # Get associated appeals
        disputed_list = []
        for fine in disputed_fines:
            appeal = FineAppeal.objects.filter(fine=fine).first()
            disputed_list.append({
                'fine_id': fine.id,
                'order_id': fine.order.id if fine.order else None,
                'writer_id': fine.order.assigned_writer.id if fine.order and fine.order.assigned_writer else None,
                'writer_username': fine.order.assigned_writer.username if fine.order and fine.order.assigned_writer else None,
                'fine_type': fine.fine_type or 'Unknown',
                'amount': str(fine.amount),
                'reason': fine.reason[:200] if fine.reason else None,
                'imposed_at': fine.imposed_at.isoformat() if fine.imposed_at else None,
                'appeal_id': appeal.id if appeal else None,
                'appeal_status': appeal.status if appeal else None,
                'appeal_submitted_at': appeal.submitted_at.isoformat() if appeal and appeal.submitted_at else None,
            })
        
        return Response({
            'disputed_fines': disputed_list,
            'count': len(disputed_list),
        })
    
    @action(detail=False, methods=['get'], url_path='active-fines')
    def active_fines(self, request):
        """Get all active fines (not waived/voided)."""
        active_fines = Fine.objects.filter(
            status__in=[FineStatus.ISSUED.value, FineStatus.DISPUTED.value]
        ).select_related(
            'order', 'order__client', 'order__assigned_writer', 'issued_by'
        ).order_by('-imposed_at')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                active_fines = active_fines.filter(order__website=website)
        
        try:
            from fines.serializers import FineSerializer
        except ImportError:
            from rest_framework import serializers
            class FineSerializer(serializers.ModelSerializer):
                class Meta:
                    model = Fine
                    fields = '__all__'
        serializer = FineSerializer(active_fines, many=True)
        
        return Response({
            'fines': serializer.data,
            'count': active_fines.count(),
        })


# ============================================================================
# ADVANCE PAYMENT REQUESTS DASHBOARD
# ============================================================================
class AdminAdvancePaymentsDashboardViewSet(viewsets.ViewSet):
    """Consolidated dashboard endpoints for advance payment requests management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get consolidated advance payment requests statistics dashboard."""
        all_advances = WriterAdvancePaymentRequest.objects.all().select_related(
            'writer', 'writer__user', 'reviewed_by', 'disbursed_by', 'website'
        )
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_advances = all_advances.filter(website=website)
        
        # Combined aggregation - reduces multiple queries to single query
        month_ago = timezone.now() - timedelta(days=30)
        summary_stats = all_advances.aggregate(
            total_requests=Count('id'),
            pending_requests=Count('id', filter=Q(status='pending')),
            approved_requests=Count('id', filter=Q(status='approved')),
            disbursed_requests=Count('id', filter=Q(status='disbursed')),
            rejected_requests=Count('id', filter=Q(status='rejected')),
            repaid_requests=Count('id', filter=Q(status='repaid')),
            recent_requests=Count('id', filter=Q(requested_at__gte=month_ago)),
        )
        
        # Financial aggregations in one query
        financial_stats = all_advances.aggregate(
            total_requested=Sum('requested_amount'),
            total_approved=Sum('approved_amount'),
            total_disbursed=Sum('disbursed_amount'),
            total_repaid=Sum('repaid_amount'),
            pending_requested=Sum('requested_amount', filter=Q(status='pending')),
            approved_but_not_disbursed=Sum('approved_amount', filter=Q(status='approved')),
        )
        
        # Calculate outstanding amount (disbursed - repaid) for all active advances
        outstanding_advances = all_advances.filter(
            status__in=['disbursed', 'approved'],
            disbursed_amount__gt=0
        )
        total_outstanding = sum(
            (adv.disbursed_amount or Decimal('0.00')) - (adv.repaid_amount or Decimal('0.00'))
            for adv in outstanding_advances
        )
        
        # Status breakdown
        status_breakdown = all_advances.values('status').annotate(
            count=Count('id'),
            total_amount=Sum('requested_amount')
        )
        
        # Pending requests (for review queue)
        pending_requests = all_advances.filter(status='pending').order_by('-requested_at')[:20]
        
        # Approved but not disbursed (for disbursement queue)
        approved_not_disbursed = all_advances.filter(
            status='approved',
            disbursed_amount__isnull=True
        ).order_by('-reviewed_at')[:20]
        
        # Recent activity (last 30 days)
        recent_activity = all_advances.filter(
            requested_at__gte=month_ago
        ).order_by('-requested_at')[:20]
        
        return Response({
            'summary': {
                'total_requests': summary_stats['total_requests'] or 0,
                'pending_requests': summary_stats['pending_requests'] or 0,
                'approved_requests': summary_stats['approved_requests'] or 0,
                'disbursed_requests': summary_stats['disbursed_requests'] or 0,
                'rejected_requests': summary_stats['rejected_requests'] or 0,
                'repaid_requests': summary_stats['repaid_requests'] or 0,
                'recent_requests': summary_stats['recent_requests'] or 0,
                'total_requested': str(financial_stats['total_requested'] or Decimal('0.00')),
                'total_approved': str(financial_stats['total_approved'] or Decimal('0.00')),
                'total_disbursed': str(financial_stats['total_disbursed'] or Decimal('0.00')),
                'total_repaid': str(financial_stats['total_repaid'] or Decimal('0.00')),
                'total_outstanding': str(total_outstanding),
                'pending_requested_amount': str(financial_stats['pending_requested'] or Decimal('0.00')),
                'approved_not_disbursed_amount': str(financial_stats['approved_but_not_disbursed'] or Decimal('0.00')),
            },
            'status_breakdown': {
                item['status']: {
                    'count': item['count'],
                    'total_amount': str(item['total_amount'] or Decimal('0.00'))
                }
                for item in status_breakdown
            },
            'pending_requests_list': [
                {
                    'id': req.id,
                    'writer_id': req.writer.id,
                    'writer_username': req.writer.user.username,
                    'requested_amount': str(req.requested_amount),
                    'expected_earnings': str(req.expected_earnings),
                    'max_advance_amount': str(req.max_advance_amount),
                    'reason': req.reason,
                    'requested_at': req.requested_at.isoformat() if req.requested_at else None,
                }
                for req in pending_requests
            ],
            'approved_not_disbursed_list': [
                {
                    'id': req.id,
                    'writer_id': req.writer.id,
                    'writer_username': req.writer.user.username,
                    'requested_amount': str(req.requested_amount),
                    'approved_amount': str(req.approved_amount),
                    'reviewed_by': req.reviewed_by.username if req.reviewed_by else None,
                    'reviewed_at': req.reviewed_at.isoformat() if req.reviewed_at else None,
                    'review_notes': req.review_notes,
                }
                for req in approved_not_disbursed
            ],
            'recent_activity': [
                {
                    'id': req.id,
                    'writer_id': req.writer.id,
                    'writer_username': req.writer.user.username,
                    'status': req.status,
                    'requested_amount': str(req.requested_amount),
                    'approved_amount': str(req.approved_amount) if req.approved_amount else None,
                    'disbursed_amount': str(req.disbursed_amount) if req.disbursed_amount else None,
                    'requested_at': req.requested_at.isoformat() if req.requested_at else None,
                }
                for req in recent_activity
            ],
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get advance payment requests analytics and trends."""
        all_advances = WriterAdvancePaymentRequest.objects.all()
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_advances = all_advances.filter(website=website)
        
        # Time range
        days = int(request.query_params.get('days', 90))
        date_from = timezone.now() - timedelta(days=days)
        
        # Weekly trends
        from django.db.models.functions import TruncWeek
        weekly_trends = all_advances.filter(
            requested_at__gte=date_from
        ).annotate(
            week=TruncWeek('requested_at')
        ).values('week').annotate(
            requested=Count('id'),
            approved=Count('id', filter=Q(status='approved')),
            disbursed=Count('id', filter=Q(status='disbursed')),
            total_requested=Sum('requested_amount'),
            total_disbursed=Sum('disbursed_amount', filter=Q(status='disbursed'))
        ).order_by('week')
        
        # Approval rate
        total_processed = all_advances.filter(
            status__in=['approved', 'rejected'],
            requested_at__gte=date_from
        ).count()
        approved_count = all_advances.filter(
            status='approved',
            requested_at__gte=date_from
        ).count()
        approval_rate = (approved_count / total_processed * 100) if total_processed > 0 else 0
        
        # Average request amounts
        avg_stats = all_advances.filter(
            requested_at__gte=date_from
        ).aggregate(
            avg_requested=Avg('requested_amount'),
            avg_approved=Avg('approved_amount', filter=Q(status='approved')),
            avg_disbursed=Avg('disbursed_amount', filter=Q(status='disbursed'))
        )
        
        # Repayment analytics
        disbursed_advances = all_advances.filter(
            status='disbursed',
            disbursed_at__gte=date_from
        )
        total_disbursed = sum(adv.disbursed_amount or Decimal('0.00') for adv in disbursed_advances)
        total_repaid = sum(adv.repaid_amount or Decimal('0.00') for adv in disbursed_advances)
        repayment_rate = (total_repaid / total_disbursed * 100) if total_disbursed > 0 else 0
        
        return Response({
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'requested': item['requested'],
                    'approved': item['approved'],
                    'disbursed': item['disbursed'],
                    'total_requested': str(item['total_requested'] or Decimal('0.00')),
                    'total_disbursed': str(item['total_disbursed'] or Decimal('0.00')),
                }
                for item in weekly_trends
            ],
            'approval_metrics': {
                'approval_rate': round(approval_rate, 2),
                'total_processed': total_processed,
                'approved_count': approved_count,
            },
            'average_amounts': {
                'avg_requested': str(avg_stats['avg_requested'] or Decimal('0.00')),
                'avg_approved': str(avg_stats['avg_approved'] or Decimal('0.00')),
                'avg_disbursed': str(avg_stats['avg_disbursed'] or Decimal('0.00')),
            },
            'repayment_metrics': {
                'total_disbursed': str(total_disbursed),
                'total_repaid': str(total_repaid),
                'repayment_rate': round(repayment_rate, 2),
            },
        })

