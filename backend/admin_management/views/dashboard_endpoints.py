"""
Admin Dashboard Endpoints

This module contains dashboard aggregation endpoints for admin management.
These endpoints provide comprehensive statistics and analytics for:
- Dispute Management
- Refund Management
- Review Moderation
- Order Management
- Special Orders (already exists, but adding analytics)
- Class Management
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
from refunds.models import Refund
from reviews_system.models import WebsiteReview, WriterReview, OrderReview
from special_orders.models import SpecialOrder, InstallmentPayment
from class_management.models import ClassBundle, ClassPurchase
from fines.models import Fine, FineAppeal, FinePolicy, FineStatus, FineType
from tickets.models import Ticket
from users.models import User


class AdminDisputeDashboardViewSet(viewsets.ViewSet):
    """Dashboard endpoints for dispute management."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get dispute statistics dashboard."""
        # Get all disputes
        all_disputes = Dispute.objects.all().select_related('order', 'order__client', 'order__writer', 'resolved_by')
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_disputes = all_disputes.filter(order__website=website)
        
        # Status breakdown
        status_breakdown = all_disputes.values('status').annotate(
            count=Count('id')
        )
        
        # Pending disputes
        pending_disputes = all_disputes.filter(status='pending')
        
        # Resolved disputes (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        resolved_recent = all_disputes.filter(
            status='resolved',
            resolved_at__gte=month_ago
        )
        
        # Disputes by reason
        reason_breakdown = all_disputes.values('reason').annotate(
            count=Count('id')
        )
        
        # Average resolution time
        resolved_with_time = all_disputes.filter(
            status='resolved',
            resolved_at__isnull=False,
            created_at__isnull=False
        )
        
        avg_resolution_hours = None
        if resolved_with_time.exists():
            resolution_times = []
            for dispute in resolved_with_time:
                if dispute.resolved_at and dispute.created_at:
                    hours = (dispute.resolved_at - dispute.created_at).total_seconds() / 3600
                    resolution_times.append(hours)
            if resolution_times:
                avg_resolution_hours = sum(resolution_times) / len(resolution_times)
        
        return Response({
            'summary': {
                'total_disputes': all_disputes.count(),
                'pending_disputes': pending_disputes.count(),
                'resolved_this_month': resolved_recent.count(),
                'average_resolution_hours': round(avg_resolution_hours, 2) if avg_resolution_hours else None,
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
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
                    'description': dispute.description,
                    'created_at': dispute.created_at.isoformat() if dispute.created_at else None,
                    'client_id': dispute.order.client.id if dispute.order and dispute.order.client else None,
                    'writer_id': dispute.order.writer.id if dispute.order and dispute.order.writer else None,
                }
                for dispute in pending_disputes[:20]
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
            created=Count('id', filter=Q(status='pending')),
            resolved=Count('id', filter=Q(status='resolved'))
        ).order_by('week')
        
        # Resolution rate trends
        month_ago = timezone.now() - timedelta(days=30)
        recent_disputes = all_disputes.filter(created_at__gte=month_ago)
        resolution_rate = (
            recent_disputes.filter(status='resolved').count() / recent_disputes.count() * 100
            if recent_disputes.count() > 0 else 0
        )
        
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
            'total_this_month': recent_disputes.count(),
            'resolved_this_month': recent_disputes.filter(status='resolved').count(),
        })
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """Get pending disputes queue."""
        pending_disputes = Dispute.objects.filter(
            status='pending'
        ).select_related('order', 'order__client', 'order__writer').order_by('-created_at')
        
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
        all_refunds = Refund.objects.all().select_related('order', 'order__client', 'processed_by')
        
        # Filter by website if needed
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_refunds = all_refunds.filter(order__website=website)
        
        # Status breakdown
        status_breakdown = all_refunds.values('status').annotate(
            count=Count('id')
        )
        
        # Pending refunds
        pending_refunds = all_refunds.filter(status='pending')
        
        # Processed refunds (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        processed_recent = all_refunds.filter(
            status='processed',
            processed_at__gte=month_ago
        )
        
        # Total amounts
        total_requested = all_refunds.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_processed = processed_recent.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_total = pending_refunds.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Average refund amount
        avg_refund = all_refunds.aggregate(
            avg=Avg('amount')
        )['avg'] or 0
        
        # Refunds by reason
        reason_breakdown = all_refunds.values('reason').annotate(
            count=Count('id')
        )
        
        return Response({
            'summary': {
                'total_refunds': all_refunds.count(),
                'pending_refunds': pending_refunds.count(),
                'processed_this_month': processed_recent.count(),
                'total_requested': str(total_requested),
                'total_processed_this_month': str(total_processed),
                'pending_total': str(pending_total),
                'average_refund_amount': str(avg_refund),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'reason_breakdown': {
                item['reason']: item['count'] for item in reason_breakdown
            },
            'pending_refunds_list': [
                {
                    'id': refund.id,
                    'order_id': refund.order.id if refund.order else None,
                    'amount': str(refund.amount),
                    'reason': refund.reason,
                    'status': refund.status,
                    'created_at': refund.created_at.isoformat() if refund.created_at else None,
                    'client_id': refund.order.client.id if refund.order and refund.order.client else None,
                }
                for refund in pending_refunds[:20]
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
        weeks_ago = timezone.now() - timedelta(weeks=12)
        from django.db.models.functions import TruncWeek
        
        weekly_trends = all_refunds.filter(
            created_at__gte=weeks_ago
        ).annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            requested=Count('id'),
            processed=Count('id', filter=Q(status='processed')),
            total_amount=Sum('amount')
        ).order_by('week')
        
        # Processing time (average)
        processed_with_time = all_refunds.filter(
            status='processed',
            processed_at__isnull=False,
            created_at__isnull=False
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
        
        # Combine counts
        total_reviews = all_website_reviews.count() + all_writer_reviews.count() + all_order_reviews.count()
        
        # Flagged reviews
        flagged_reviews = (
            all_website_reviews.filter(is_flagged=True).count() +
            all_writer_reviews.filter(is_flagged=True).count() +
            all_order_reviews.filter(is_flagged=True).count()
        )
        
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
                'website_reviews': all_website_reviews.count(),
                'writer_reviews': all_writer_reviews.count(),
                'order_reviews': all_order_reviews.count(),
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
        
        # Status breakdown
        status_breakdown = all_orders.values('status').annotate(
            count=Count('id')
        )
        
        # Orders needing assignment
        needs_assignment = all_orders.filter(
            status=OrderStatus.PENDING_ASSIGNMENT.value,
            writer__isnull=True
        )
        
        # Overdue orders
        overdue_orders = all_orders.filter(
            deadline__lt=timezone.now(),
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.UNDER_EDITING.value,
                OrderStatus.PENDING_REVISION.value
            ]
        )
        
        # Stuck orders (no progress in 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        stuck_orders = all_orders.filter(
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.UNDER_EDITING.value,
            ],
            updated_at__lt=week_ago
        )
        
        # Recent orders (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        recent_orders = all_orders.filter(created_at__gte=month_ago)
        
        # Total revenue
        total_revenue = all_orders.filter(
            status=OrderStatus.COMPLETED.value
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        return Response({
            'summary': {
                'total_orders': all_orders.count(),
                'needs_assignment': needs_assignment.count(),
                'overdue_orders': overdue_orders.count(),
                'stuck_orders': stuck_orders.count(),
                'recent_orders': recent_orders.count(),
                'total_revenue': str(total_revenue),
            },
            'status_breakdown': {
                item['status']: item['count'] for item in status_breakdown
            },
            'needs_assignment_list': [
                {
                    'id': order.id,
                    'topic': order.topic,
                    'pages': order.pages,
                    'deadline': order.deadline.isoformat() if order.deadline else None,
                    'created_at': order.created_at.isoformat() if order.created_at else None,
                }
                for order in needs_assignment[:20]
            ],
            'overdue_orders_list': [
                {
                    'id': order.id,
                    'topic': order.topic,
                    'pages': order.pages,
                    'deadline': order.deadline.isoformat() if order.deadline else None,
                    'status': order.status,
                }
                for order in overdue_orders[:20]
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
            deadline__lt=timezone.now(),
            status__in=[
                OrderStatus.IN_PROGRESS.value,
                OrderStatus.UNDER_EDITING.value,
                OrderStatus.PENDING_REVISION.value
            ]
        ).select_related('client', 'writer', 'website').order_by('deadline')
        
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
        
        writer_performance = writers.annotate(
            completed_orders_count=Count('user__orders_as_writer', filter=Q(
                user__orders_as_writer__status=OrderStatus.COMPLETED.value,
                user__orders_as_writer__created_at__gte=date_from
            )),
            total_earnings=Sum('user__orders_as_writer__writer_compensation', filter=Q(
                user__orders_as_writer__status=OrderStatus.COMPLETED.value,
                user__orders_as_writer__created_at__gte=date_from
            )),
            avg_rating=Avg('user__orders_as_writer__client_rating', filter=Q(
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
        refunds = Refund.objects.filter(created_at__gte=date_from)
        if website_filter:
            refunds = refunds.filter(order__website=website_filter)
        
        refund_metrics = {
            'total_refunds': refunds.count(),
            'total_amount': refunds.aggregate(total=Sum('amount'))['total'] or 0,
            'approved': refunds.filter(status='approved').count(),
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
                    'completed_orders': writer.completed_orders,
                    'total_earnings': str(writer.total_earnings or 0),
                    'avg_rating': round(float(writer.avg_rating), 2) if writer.avg_rating else None,
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

