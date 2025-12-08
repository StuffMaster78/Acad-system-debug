from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, Q
from django.db import models
from rest_framework import viewsets, status, views
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .services.admin_profile_service import AdminProfileService
from .services.promotion_service import AdminPromotionService

from .models import AdminActivityLog, AdminProfile, BlacklistedUser
from admin_management.serializers import (
    AdminProfileSerializer,
    AdminLogSerializer,
    BlacklistedUserSerializer,
    DashboardSerializer,
    UserSerializer,
    CreateUserSerializer,
    SuspendUserSerializer,
)
from .permissions import IsAdmin, IsSuperAdmin
from orders.models import Order, Dispute
from admin_management.services.blacklist_service import BlacklistService
from admin_management.services.admin_profile_service import  AdminProfileService
from .serializers import (
    BlacklistedUserListSerializer,
    BlacklistedUserDetailSerializer,
    AdminPromotionRequestSerializer,
    AdminPromotionRequestCreateSerializer,
)
from .services.promotion_service import AdminPromotionService
from .models import AdminPromotionRequest, BlacklistedUser  
from rest_framework import mixins
from .serializers import (
    BlacklistedUserListSerializer,
    BlacklistedUserDetailSerializer,
    AdminPromotionRequestSerializer,
    AdminPromotionRequestCreateSerializer,
)

from .serializers import (
    DashboardSerializer,
    CreateUserSerializer,
    BlacklistedUserSerializer,
    BlacklistUserSerializer,
    RemoveBlacklistSerializer,
)
from .models import AdminActivityLog, BlacklistedUser, AdminPromotionRequest
from .permissions import IsAdmin, IsSuperAdmin


User = get_user_model()


class AdminActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving admin activity logs.
    """
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    pagination_class = None  # Disable pagination to return all logs, or use custom pagination
    
    def get_queryset(self):
        """Filter logs by website if user has website context."""
        queryset = AdminActivityLog.objects.select_related('admin').order_by('-timestamp')
        
        # Both superadmin and admin see all activity logs (no website filtering)
        if self.request.user.role not in ['superadmin', 'admin']:
            website = getattr(self.request.user, 'website', None)
            # If user has a website, filter logs by admins from that website
            if website:
                queryset = queryset.filter(admin__website=website)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to ensure all logs are returned or properly paginated."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # If pagination is disabled, return all results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # No pagination - return all logs
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminDashboardView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request):
        """Dashboard stats for admin panel"""
        from .services.dashboard_metrics_service import DashboardMetricsService
        from django.core.cache import cache
        
        # Clear cache on refresh if requested
        if request.query_params.get('refresh') == 'true':
            # Clear all dashboard cache keys for this user
            cache_key = DashboardMetricsService.get_cache_key(request.user, "summary")
            cache.delete(cache_key)
            # Clear other related cache keys by trying common patterns
            website_id = getattr(request.user, 'website_id', None) or 'all'
            role = getattr(request.user, 'role', 'unknown')
            for suffix in ["yearly_", "monthly_", "service_revenue_", "payment_status"]:
                try:
                    pattern_key = f"dashboard_metrics_{role}_{website_id}_{suffix}*"
                    # Django cache doesn't support wildcard deletion, so we clear specific keys
                    # This is a limitation, but we clear the main summary cache which is most important
                except Exception:
                    pass
        
        summary = DashboardMetricsService.get_summary(request.user)
        
        # Get additional user stats - optimized with combined aggregations
        # Both superadmin and admin should see all users
        user_qs = User.objects.all()
        # No website filtering for superadmin and admin - they see all users
        
        # Combined aggregation query - reduces from 5 queries to 1 query
        from django.db.models import Count, Q
        user_stats = user_qs.aggregate(
            total_writers=Count('id', filter=Q(role="writer")),
            total_editors=Count('id', filter=Q(role="editor")),
            total_support=Count('id', filter=Q(role="support")),
            total_clients=Count('id', filter=Q(role="client")),
            suspended_users=Count('id', filter=Q(is_suspended=True))
        )
        
        total_writers = user_stats['total_writers'] or 0
        total_editors = user_stats['total_editors'] or 0
        total_support = user_stats['total_support'] or 0
        total_clients = user_stats['total_clients'] or 0
        suspended_users = user_stats['suspended_users'] or 0
        total_users = total_writers + total_editors + total_support + total_clients
        
        # Get recent activity logs
        recent_logs = AdminActivityLog.objects.order_by("-timestamp")[:10]
        recent_activities = [
            {
                "action": log.action,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "admin": log.admin.username if log.admin else None,
            }
            for log in recent_logs
        ]
        
        # Get payment reminder statistics
        try:
            from order_payments_management.models.payment_reminders import (
                PaymentReminderConfig,
                PaymentReminderSent,
                PaymentReminderDeletionMessage
            )
            
            reminder_configs_qs = PaymentReminderConfig.objects.all()
            deletion_messages_qs = PaymentReminderDeletionMessage.objects.all()
            sent_reminders_qs = PaymentReminderSent.objects.all()
            
            # Both superadmin and admin should see all payment reminders
            # No website filtering for superadmin and admin
            
            # Optimized aggregations - combine queries where possible
            from django.db.models import Count, Q
            reminder_configs_stats = reminder_configs_qs.aggregate(
                total=Count('id'),
                active=Count('id', filter=Q(is_active=True))
            )
            deletion_messages_stats = deletion_messages_qs.aggregate(
                total=Count('id'),
                active=Count('id', filter=Q(is_active=True))
            )
            sent_reminders_total = sent_reminders_qs.count()
            recent_sent_reminders = sent_reminders_qs.order_by("-sent_at")[:5].count()
            
            payment_reminder_stats = {
                "total_reminder_configs": reminder_configs_stats['total'] or 0,
                "active_reminder_configs": reminder_configs_stats['active'] or 0,
                "total_deletion_messages": deletion_messages_stats['total'] or 0,
                "active_deletion_messages": deletion_messages_stats['active'] or 0,
                "total_sent_reminders": sent_reminders_total,
                "recent_sent_reminders": recent_sent_reminders,
            }
        except ImportError:
            payment_reminder_stats = {
                "total_reminder_configs": 0,
                "active_reminder_configs": 0,
                "total_deletion_messages": 0,
                "active_deletion_messages": 0,
                "total_sent_reminders": 0,
                "recent_sent_reminders": 0,
            }
        
        # Build stats object matching DashboardStatsSerializer
        stats_data = {
            "total_users": total_users,
            "active_users": total_users - suspended_users,
            "suspended_users": suspended_users,
            "total_orders": summary.get("total_orders", 0),
            "completed_orders": summary.get("orders_by_status", {}).get("completed", 0),
            "pending_orders": summary.get("orders_by_status", {}).get("pending", 0),
            "total_revenue": summary.get("total_revenue", 0.0),
            "total_disputes": 0,  # Add if you have disputes
            "resolved_disputes": 0,  # Add if you have disputes
            "open_tickets": summary.get("open_tickets_count", 0),
            "closed_tickets": summary.get("closed_tickets_count", 0),
            # Include paid/unpaid counts in stats for consistency
            "paid_orders_count": summary.get("paid_orders_count", 0),
            "unpaid_orders_count": summary.get("unpaid_orders_count", 0),
        }
        
        # Get additional comprehensive metrics
        from django.db.models import Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Recent Orders (last 10)
        recent_orders = Order.objects.select_related('client', 'assigned_writer', 'website').order_by('-created_at')[:10]
        recent_orders_data = [
            {
                "id": order.id,
                "topic": order.topic[:50] + "..." if len(order.topic) > 50 else order.topic,
                "client": order.client.username if order.client else "N/A",
                "writer": order.assigned_writer.username if order.assigned_writer else "Unassigned",
                "status": order.status,
                "total_price": float(order.total_price) if order.total_price else 0.0,
                "is_paid": order.is_paid,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "website": order.website.name if order.website else "N/A",
            }
            for order in recent_orders
        ]
        
        # Top Performing Writers (by completed orders)
        # Query from Order side to avoid conflict with WriterProfile.completed_orders field
        # Note: Order is already imported at the top of the file
        
        # Aggregate from Order model instead of User to avoid annotation conflicts
        top_writers_agg = Order.objects.filter(
            status="completed",
            assigned_writer__role="writer"
        ).values(
            'assigned_writer__id',
            'assigned_writer__username',
            'assigned_writer__email'
        ).annotate(
            completed_orders_count=Count('id'),
            total_earnings=Sum('writer_compensation', default=0)
        ).order_by('-completed_orders_count')[:10]
        
        top_writers_data = [
            {
                "id": item['assigned_writer__id'],
                "username": item['assigned_writer__username'],
                "email": item['assigned_writer__email'],
                "completed_orders": item['completed_orders_count'],
                "total_earnings": float(item['total_earnings']) if item['total_earnings'] else 0.0,
            }
            for item in top_writers_agg
        ]
        
        # Top Spending Clients
        top_clients = User.objects.filter(
            role="client",
            orders_as_client__is_paid=True
        ).annotate(
            total_spent=Sum("orders_as_client__total_price", filter=Q(orders_as_client__is_paid=True), default=0),
            order_count=Count("orders_as_client", filter=Q(orders_as_client__is_paid=True)),
        ).order_by("-total_spent")[:10]
        
        top_clients_data = [
            {
                "id": client.id,
                "username": client.username,
                "email": client.email,
                "total_spent": float(client.total_spent) if client.total_spent else 0.0,
                "order_count": client.order_count,
            }
            for client in top_clients
        ]
        
        # Revenue Trends (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        revenue_trends = Order.objects.filter(
            created_at__gte=thirty_days_ago,
            is_paid=True
        ).extra(
            select={'day': "DATE(created_at)"}
        ).values('day').annotate(
            revenue=Sum("total_price", default=0),
            order_count=Count("id"),
        ).order_by('day')
        
        revenue_trends_data = [
            {
                "date": item["day"].isoformat() if item["day"] else None,
                "revenue": float(item["revenue"]) if item["revenue"] else 0.0,
                "order_count": item["order_count"],
            }
            for item in revenue_trends
        ]
        
        # Order Status Breakdown (detailed)
        all_orders = Order.objects.all()
        order_status_breakdown = all_orders.values('status').annotate(
            count=Count('id'),
            total_revenue=Sum('total_price', filter=Q(is_paid=True), default=0),
        )
        
        status_breakdown_data = {
            item['status']: {
                "count": item['count'],
                "revenue": float(item['total_revenue']) if item['total_revenue'] else 0.0,
            }
            for item in order_status_breakdown
        }
        
        # System Health Metrics
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        system_health = {
            "orders_last_24h": Order.objects.filter(created_at__gte=last_24h).count(),
            "orders_last_7d": Order.objects.filter(created_at__gte=last_7d).count(),
            "new_users_last_24h": User.objects.filter(date_joined__gte=last_24h).count(),
            "new_users_last_7d": User.objects.filter(date_joined__gte=last_7d).count(),
            "overdue_orders": Order.objects.filter(
                client_deadline__lt=now,
                status__in=["in_progress", "pending", "available"]
            ).count(),
            "unassigned_orders": Order.objects.filter(
                assigned_writer__isnull=True,
                status__in=["available", "pending"]
            ).count(),
        }
        
        # Payment Statistics
        try:
            from order_payments_management.models import OrderPayment
            payment_stats = OrderPayment.objects.aggregate(
                total_payments=Count("id"),
                completed_payments=Count("id", filter=Q(status="completed")),
                pending_payments=Count("id", filter=Q(status="pending")),
                failed_payments=Count("id", filter=Q(status="failed")),
                total_amount=Sum("amount", default=0),
            )
        except ImportError:
            payment_stats = {
                "total_payments": 0,
                "completed_payments": 0,
                "pending_payments": 0,
                "failed_payments": 0,
                "total_amount": 0,
            }
        
        # Build response with both serializer format and flat format for compatibility
        data = {
            "stats": stats_data,
            "recent_activities": recent_activities,
            "pending_promotion_requests": [],  # Add if you have promotion requests
            # Also include flat format for easy access
            "total_writers": total_writers,
            "total_editors": total_editors,
            "total_support": total_support,
            "total_clients": total_clients,
            "suspended_users": suspended_users,
            "total_orders": summary.get("total_orders", 0),
            "orders_by_status": summary.get("orders_by_status", {}),
            "total_revenue": summary.get("total_revenue", 0.0),
            "paid_orders_count": summary.get("paid_orders_count", 0),
            "unpaid_orders_count": summary.get("unpaid_orders_count", 0),
            "recent_orders_count": summary.get("recent_orders_count", 0),
            "total_tickets": summary.get("total_tickets", 0),
            "open_tickets_count": summary.get("open_tickets_count", 0),
            "closed_tickets_count": summary.get("closed_tickets_count", 0),
            # New comprehensive metrics
            "orders_in_progress": summary.get("orders_in_progress", 0),
            "orders_on_revision": summary.get("orders_on_revision", 0),
            "disputed_orders": summary.get("disputed_orders", 0),
            "amount_paid_today": summary.get("amount_paid_today", 0.0),
            "income_this_week": summary.get("income_this_week", 0.0),
            "income_2weeks": summary.get("income_2weeks", 0.0),
            "income_monthly": summary.get("income_monthly", 0.0),
            "recent_logs": [log.action for log in recent_logs],
            "payment_reminder_stats": payment_reminder_stats,
            # Additional comprehensive metrics
            "recent_orders": recent_orders_data,
            "top_writers": top_writers_data,
            "top_clients": top_clients_data,
            "revenue_trends": revenue_trends_data,
            "order_status_breakdown": status_breakdown_data,
            "system_health": system_health,
            "payment_stats": {
                "total_payments": payment_stats.get("total_payments", 0),
                "completed_payments": payment_stats.get("completed_payments", 0),
                "pending_payments": payment_stats.get("pending_payments", 0),
                "failed_payments": payment_stats.get("failed_payments", 0),
                "total_amount": float(payment_stats.get("total_amount", 0)) if payment_stats.get("total_amount") else 0.0,
            },
        }
        
        # Try to use serializer, but fallback to direct response if it fails
        try:
            return Response(DashboardSerializer(data).data)
        except Exception as e:
            # If serializer fails, return data directly
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"DashboardSerializer failed, returning raw data: {e}")
            return Response(data)
    
    @action(detail=False, methods=['get'], url_path='analytics/enhanced')
    def get_enhanced_analytics(self, request):
        """Get enhanced analytics and insights."""
        from .services.enhanced_analytics_service import EnhancedAnalyticsService
        
        days = int(request.query_params.get('days', 30))
        analytics = EnhancedAnalyticsService.get_performance_insights(days)
        
        return Response(analytics)
    
    @action(detail=False, methods=['get'], url_path='analytics/compare')
    def get_comparative_analytics(self, request):
        """Get comparative analytics between two periods."""
        from .services.enhanced_analytics_service import EnhancedAnalyticsService
        
        period1_days = int(request.query_params.get('period1_days', 30))
        period2_days = int(request.query_params.get('period2_days', 30))
        
        comparison = EnhancedAnalyticsService.get_comparative_analytics(period1_days, period2_days)
        
        return Response(comparison)
    
    @action(detail=False, methods=['get'], url_path='metrics/summary')
    def get_summary(self, request):
        """Get summary metrics for dashboard."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        summary = DashboardMetricsService.get_summary(request.user)
        return Response(summary)
    
    @action(detail=False, methods=['get'], url_path='metrics/yearly-orders')
    def get_yearly_orders(self, request):
        """Get yearly order counts and revenue."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        year = request.query_params.get('year')
        year = int(year) if year else None
        data = DashboardMetricsService.get_yearly_orders(request.user, year)
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='metrics/yearly-earnings')
    def get_yearly_earnings(self, request):
        """Get yearly earnings breakdown."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        year = request.query_params.get('year')
        year = int(year) if year else None
        data = DashboardMetricsService.get_yearly_earnings(request.user, year)
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='metrics/yearly-comparison')
    def get_yearly_comparison(self, request):
        """Get comprehensive yearly comparison data."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        
        start_year = request.query_params.get('start_year')
        end_year = request.query_params.get('end_year')
        website_id = request.query_params.get('website_id')
        
        start_year = int(start_year) if start_year else None
        end_year = int(end_year) if end_year else None
        website_id = int(website_id) if website_id else None
        
        data = DashboardMetricsService.get_yearly_comparison(
            request.user,
            start_year=start_year,
            end_year=end_year,
            website_id=website_id
        )
        return Response({'results': data})
    
    @action(detail=False, methods=['get'], url_path='metrics/monthly-orders')
    def get_monthly_orders(self, request):
        """Get monthly order breakdown (daily)."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        year = int(year) if year else None
        month = int(month) if month else None
        data = DashboardMetricsService.get_monthly_orders(request.user, year, month)
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='metrics/service-revenue')
    def get_service_revenue(self, request):
        """Get revenue breakdown by service type."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        days = request.query_params.get('days', 30)
        days = int(days) if days else 30
        data = DashboardMetricsService.get_service_revenue(request.user, days)
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='metrics/payment-status')
    def get_payment_status(self, request):
        """Get payment status breakdown."""
        from .services.dashboard_metrics_service import DashboardMetricsService
        data = DashboardMetricsService.get_payment_status_breakdown(request.user)
        return Response(data)
    
    @action(detail=False, methods=['post'], url_path='place-order')
    def place_order(self, request):
        """Admin/Support endpoint to place an order with optional attribution."""
        # Check if user is admin, superadmin, or support
        if request.user.role not in ['admin', 'superadmin', 'support']:
            return Response(
                {"error": "Only admins and support staff can create orders."},
                status=status.HTTP_403_FORBIDDEN
            )
        from .serializers import AdminPlaceOrderSerializer
        from orders.models import Order
        from orders.order_enums import OrderStatus
        from django.db import transaction
        
        serializer = AdminPlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        # Get website from user
        website = getattr(request.user, 'website', None)
        if not website:
            return Response(
                {"error": "User must be associated with a website."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract client and external contact info
        client_id = validated_data.get('client_id')
        external_name = validated_data.get('external_contact_name')
        external_email = validated_data.get('external_contact_email')
        external_phone = validated_data.get('external_contact_phone')
        
        # Get order fields
        order_data = {
            'website': website,
            'topic': validated_data['topic'],
            'paper_type_id': validated_data['paper_type_id'],
            'number_of_pages': validated_data['number_of_pages'],
            'client_deadline': validated_data['client_deadline'],
            'order_instructions': validated_data['order_instructions'],
            'created_by_admin': request.user.role in ['admin', 'superadmin'],  # True for admin, False for support
            'status': OrderStatus.CREATED.value,
            'is_paid': False,  # Orders created by admin start as unpaid
            'allow_unpaid_access': validated_data.get('allow_unpaid_access', False),
        }
        
        # Add optional fields
        if validated_data.get('academic_level_id'):
            order_data['academic_level_id'] = validated_data['academic_level_id']
        if validated_data.get('formatting_style_id'):
            order_data['formatting_style_id'] = validated_data['formatting_style_id']
        if validated_data.get('subject_id'):
            order_data['subject_id'] = validated_data['subject_id']
        if validated_data.get('type_of_work_id'):
            order_data['type_of_work_id'] = validated_data['type_of_work_id']
        if validated_data.get('english_type_id'):
            order_data['english_type_id'] = validated_data['english_type_id']
        if validated_data.get('number_of_slides'):
            order_data['number_of_slides'] = validated_data['number_of_slides']
        if validated_data.get('number_of_refereces'):
            order_data['number_of_refereces'] = validated_data['number_of_refereces']
        if validated_data.get('spacing'):
            order_data['spacing'] = validated_data['spacing']
        if validated_data.get('preferred_writer_id'):
            order_data['preferred_writer_id'] = validated_data['preferred_writer_id']
        
        # Add client if attributed
        if client_id:
            order_data['client_id'] = client_id
        
        # Add external contact if unattributed
        if external_name:
            order_data['external_contact_name'] = external_name
        if external_email:
            order_data['external_contact_email'] = external_email
        if external_phone:
            order_data['external_contact_phone'] = external_phone
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(**order_data)
            
            # Add extra services if provided
            if validated_data.get('extra_services'):
                order.extra_services.set(validated_data['extra_services'])
            
            # Apply discount code if provided
            if validated_data.get('discount_code'):
                from discounts.models import Discount
                try:
                    discount = Discount.objects.get(
                        discount_code=validated_data['discount_code'],
                        website=website,
                        is_active=True
                    )
                    order.discount = discount
                    order.discount_code_used = validated_data['discount_code']
                    order.save()
                except Discount.DoesNotExist:
                    pass  # Ignore invalid discount codes
            
            # Auto-create chat thread for unattributed orders
            if not client_id and (external_name or external_email):
                try:
                    from communications.models import Thread
                    thread = Thread.objects.create(
                        order=order,
                        website=website,
                        # Admin acts as client proxy for unattributed orders
                        created_by=request.user,
                    )
                except Exception:
                    pass  # Don't fail order creation if thread creation fails
        
        # Serialize response
        from orders.serializers import OrderSerializer
        order_serializer = OrderSerializer(order, context={'request': request})
        
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class UserManagementView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=["post"])
    def create_user(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def suspend_user(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_suspended = True
        user.suspension_reason = request.data.get("reason", "No reason provided")
        user.save()

        AdminActivityLog.objects.create(
            admin=request.user,
            action="User Suspension",
            details=f"{request.user.username} suspended {user.username}"
        )
        return Response({"message": f"{user.username} suspended."})

    @action(detail=True, methods=["post"], permission_classes=[IsSuperAdmin])
    def blacklist_user(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if user.role == "admin":
            return Response({"error": "Cannot blacklist another admin."}, status=403)

        BlacklistedUser.objects.create(email=user.email, blacklisted_by=request.user)
        user.is_blacklisted = True
        user.save()

        AdminActivityLog.objects.create(
            admin=request.user,
            action="User Blacklisted",
            details=f"{request.user.username} blacklisted {user.username}"
        )
        return Response({"message": f"{user.username} blacklisted."})

    @action(detail=True, methods=["post"])
    def place_probation(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        reason = request.data.get("reason", "No reason provided")
        duration = int(request.data.get("duration", 30))

        if user.role == "admin":
            return Response({"error": "Cannot place admins on probation."}, status=403)

        user.place_on_probation(reason, duration)
        return Response({"message": f"{user.username} is on probation for {duration} days."})

    @action(detail=True, methods=["post"])
    def remove_probation(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        if not user.is_on_probation:
            return Response({"error": "User is not on probation."}, status=400)

        user.remove_from_probation()
        return Response({"message": f"{user.username} is no longer on probation."})


class AdminLoginView(views.APIView):
    """
    DEPRECATED: Use /api/v1/auth/auth/login/ instead.
    Admin-specific login endpoint (kept for backward compatibility).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Use unified authentication service
        from authentication.services.auth_service import AuthenticationService
        
        email = request.data.get("email") or request.data.get("username")
        password = request.data.get("password")
        
        if not email or not password:
            return Response(
                {"error": "Email/username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = AuthenticationService.login(
                request=request,
                email=email,
                password=password,
                remember_me=request.data.get("remember_me", False)
            )
            
            # Check if user is admin/superadmin
            user_id = result.get("user", {}).get("id")
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                
                if user.role not in ["admin", "superadmin"]:
                    return Response(
                        {"error": "This endpoint is for admin/superadmin users only."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Log admin activity
                AdminActivityLog.objects.create(
                    admin=user,
                    action="Admin Login",
                    details=f"{user.username} logged in."
                )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Admin login error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred during login."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminLogoutView(views.APIView):
    """
    DEPRECATED: Use /api/v1/auth/auth/logout/ instead.
    Admin-specific logout endpoint (kept for backward compatibility).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Use unified authentication service
        from authentication.services.auth_service import AuthenticationService
        from django.core.exceptions import ValidationError
        
        logout_all = request.query_params.get('logout_all', 'false').lower() == 'true'
        
        try:
            result = AuthenticationService.logout(
                request=request,
                user=request.user,
                logout_all=logout_all
            )
            
            # Log admin activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action="Admin Logout",
                details=f"{request.user.username} logged out."
            )
            
            return Response(result, status=status.HTTP_200_OK)
        except (ValidationError, Exception) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Admin logout error: {e}", exc_info=True)
            return Response(
                {"error": "An error occurred during logout."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    return TokenRefreshView.as_view()(request)


class BlacklistedUserViewSet(mixins.ListModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    queryset = BlacklistedUser.objects.select_related(
        "blacklisted_by", "user", "website"
    ).order_by("-blacklisted_at")
    lookup_field = "email"
    lookup_value_regex = r"[\w\.-]+@[\w\.-]+\.\w+"
    pagination_class = None  # Disable pagination for simplicity
    filterset_fields = ["website", "blacklisted_by"]
    search_fields = ["email", "website__name"]
    ordering_fields = ["blacklisted_at", "email"]
    ordering = ["-blacklisted_at"]
    serializer_class = BlacklistedUserListSerializer
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BlacklistedUserDetailSerializer
        return BlacklistedUserListSerializer

    @action(
            detail=False, methods=["post"], url_path="add",
            serializer_class=BlacklistUserSerializer
    )
    def add_to_blacklist(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = blacklist_user(request.user, **serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(
            detail=False, methods=["post"], url_path="remove",
            serializer_class=RemoveBlacklistSerializer
    )
    def remove_from_blacklist(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = remove_from_blacklist(**serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)


class AdminPromotionRequestViewSet(viewsets.ModelViewSet):
    queryset = AdminPromotionRequest.objects.select_related(
        "requested_by", "approved_by", "rejected_by"
    ).order_by("-requested_at")
    serializer_class = AdminPromotionRequestSerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        AdminPromotionService.submit_promotion_request(request=self.request, serializer=serializer)

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        instance = self.get_object()
        AdminPromotionService. approve_promotion_request(instance, approver=request.user)
        return Response({"detail": "Request approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        instance = self.get_object()
        AdminPromotionService.reject_promotion_request(instance, rejector=request.user)
        return Response({"detail": "Request rejected."}, status=status.HTTP_200_OK)


# Admin Dispute Management ViewSet
class AdminDisputeManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for dispute management dashboard."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get dispute statistics dashboard."""
        from orders.models import Dispute
        from orders.order_enums import DisputeStatusEnum
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all disputes
        all_disputes = Dispute.objects.all().select_related('order', 'raised_by', 'website')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_disputes = all_disputes.filter(website=website)
        
        # Status breakdown
        status_breakdown = all_disputes.values('dispute_status').annotate(
            count=Count('id')
        )
        
        # Pending disputes (open)
        pending_disputes = all_disputes.filter(
            dispute_status=DisputeStatusEnum.OPEN.value
        ).count()
        
        # Resolved disputes (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        resolved_recent = all_disputes.filter(
            dispute_status=DisputeStatusEnum.RESOLVED.value,
            updated_at__gte=month_ago
        ).count()
        
        # Disputes by week
        from django.db.models.functions import TruncWeek
        weekly_disputes = all_disputes.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')
        
        # Recent disputes
        recent_disputes = all_disputes.order_by('-created_at')[:10]
        
        # Disputes awaiting response (writer hasn't responded)
        awaiting_response = all_disputes.filter(
            dispute_status=DisputeStatusEnum.OPEN.value,
            writer_responded=False
        ).count()
        
        return Response({
            'summary': {
                'total_disputes': all_disputes.count(),
                'pending_disputes': pending_disputes,
                'resolved_recent': resolved_recent,
                'awaiting_response': awaiting_response,
            },
            'status_breakdown': {
                item['dispute_status']: item['count'] 
                for item in status_breakdown
            },
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count']
                }
                for item in weekly_disputes
            ],
            'recent_disputes': [
                {
                    'id': d.id,
                    'order_id': d.order.id if d.order else None,
                    'order_topic': d.order.topic if d.order else None,
                    'raised_by': d.raised_by.username if d.raised_by else None,
                    'status': d.dispute_status,
                    'created_at': d.created_at.isoformat() if d.created_at else None,
                }
                for d in recent_disputes
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_disputes(self, request):
        """Get pending disputes queue."""
        from orders.models import Dispute
        from orders.order_enums import DisputeStatusEnum
        from orders.serializers import DisputeSerializer
        
        disputes = Dispute.objects.filter(
            dispute_status=DisputeStatusEnum.OPEN.value
        ).select_related('order', 'raised_by', 'website').order_by('-created_at')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            disputes = disputes.filter(website=website)
        
        serializer = DisputeSerializer(disputes, many=True)
        return Response({
            'disputes': serializer.data,
            'count': len(serializer.data)
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get dispute analytics and trends."""
        from orders.models import Dispute
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth
        
        all_disputes = Dispute.objects.all()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_disputes = all_disputes.filter(website=website)
        
        # Monthly trends
        monthly_trends = all_disputes.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            resolved=Count('id', filter=Q(dispute_status='resolved'))
        ).order_by('month')
        
        # Average resolution time (in days)
        resolved_disputes = all_disputes.filter(
            dispute_status='resolved',
            updated_at__isnull=False,
            created_at__isnull=False
        )
        
        resolution_times = []
        for dispute in resolved_disputes:
            if dispute.updated_at and dispute.created_at:
                days = (dispute.updated_at - dispute.created_at).days
                resolution_times.append(days)
        
        avg_resolution_days = sum(resolution_times) / len(resolution_times) if resolution_times else None
        
        # Resolution outcomes breakdown
        outcome_breakdown = all_disputes.filter(
            resolution_outcome__isnull=False
        ).values('resolution_outcome').annotate(
            count=Count('id')
        )
        
        return Response({
            'monthly_trends': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'total': item['count'],
                    'resolved': item['resolved']
                }
                for item in monthly_trends
            ],
            'avg_resolution_days': avg_resolution_days,
            'outcome_breakdown': {
                item['resolution_outcome']: item['count']
                for item in outcome_breakdown
            }
        })


# Admin Refund Management ViewSet
class AdminRefundManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for refund management dashboard."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get refund statistics dashboard."""
        from refunds.models import Refund
        from django.db.models import Count, Sum, Q, F
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all refunds
        all_refunds = Refund.objects.all().select_related('order_payment', 'client')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_refunds = all_refunds.filter(order_payment__website=website)
        
        # Status breakdown - use wallet_amount + external_amount instead of amount
        status_breakdown = all_refunds.values('status').annotate(
            count=Count('id'),
            total_amount=Sum(F('wallet_amount') + F('external_amount'))
        )
        
        # Pending refunds
        pending_refunds = all_refunds.filter(status='pending').count()
        pending_amount = all_refunds.filter(status='pending').aggregate(
            total=Sum(F('wallet_amount') + F('external_amount'))
        )['total'] or 0
        
        # Processed refunds (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        processed_recent = all_refunds.filter(
            status='processed',
            processed_at__gte=month_ago
        ).count()
        processed_amount = all_refunds.filter(
            status='processed',
            processed_at__gte=month_ago
        ).aggregate(total=Sum(F('wallet_amount') + F('external_amount')))['total'] or 0
        
        # Refunds by week
        from django.db.models.functions import TruncWeek
        weekly_refunds = all_refunds.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id'),
            total_amount=Sum(F('wallet_amount') + F('external_amount'))
        ).order_by('week')
        
        # Recent refunds
        recent_refunds = all_refunds.order_by('-created_at')[:10]
        
        return Response({
            'summary': {
                'total_refunds': all_refunds.count(),
                'pending_refunds': pending_refunds,
                'pending_amount': float(pending_amount),
                'processed_recent': processed_recent,
                'processed_amount': float(processed_amount),
            },
            'status_breakdown': {
                item['status']: {
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0)
                }
                for item in status_breakdown
            },
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0)
                }
                for item in weekly_refunds
            ],
            'recent_refunds': [
                {
                    'id': r.id,
                    'order_payment_id': r.order_payment.id if r.order_payment else None,
                    'client': r.client.username if r.client else None,
                    'amount': float(r.total_amount()),  # Use total_amount() method
                    'status': r.status,
                    'refund_method': r.refund_method,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                }
                for r in recent_refunds
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending_refunds(self, request):
        """Get pending refunds queue."""
        from refunds.models import Refund
        from refunds.serializers import RefundSerializer
        
        refunds = Refund.objects.filter(
            status='pending'
        ).select_related('order_payment', 'client').order_by('-created_at')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            refunds = refunds.filter(order_payment__website=website)
        
        serializer = RefundSerializer(refunds, many=True)
        return Response({
            'refunds': serializer.data,
            'count': len(serializer.data)
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get refund analytics and trends."""
        from refunds.models import Refund
        from django.db.models import Count, Sum, Avg, Q, F
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth
        
        all_refunds = Refund.objects.all()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_refunds = all_refunds.filter(order_payment__website=website)
        
        # Monthly trends - use wallet_amount + external_amount instead of amount
        monthly_trends = all_refunds.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            total_amount=Sum(F('wallet_amount') + F('external_amount')),
            processed=Count('id', filter=Q(status='processed'))
        ).order_by('month')
        
        # Average refund amount - use wallet_amount + external_amount
        avg_refund_amount = all_refunds.aggregate(
            avg=Avg(F('wallet_amount') + F('external_amount'))
        )['avg'] or 0
        
        # Refund method breakdown - use wallet_amount + external_amount
        method_breakdown = all_refunds.values('refund_method').annotate(
            count=Count('id'),
            total_amount=Sum(F('wallet_amount') + F('external_amount'))
        )
        
        # Average processing time (for processed refunds)
        processed_refunds = all_refunds.filter(
            status='processed',
            processed_at__isnull=False,
            created_at__isnull=False
        )
        
        processing_times = []
        for refund in processed_refunds:
            if refund.processed_at and refund.created_at:
                days = (refund.processed_at - refund.created_at).days
                processing_times.append(days)
        
        avg_processing_days = sum(processing_times) / len(processing_times) if processing_times else None
        
        return Response({
            'monthly_trends': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0),
                    'processed': item['processed']
                }
                for item in monthly_trends
            ],
            'avg_refund_amount': float(avg_refund_amount),
            'avg_processing_days': avg_processing_days,
            'method_breakdown': {
                item['refund_method']: {
                    'count': item['count'],
                    'total_amount': float(item['total_amount'] or 0)
                }
                for item in method_breakdown
            }
        })


# Admin Review Moderation ViewSet
class AdminReviewModerationViewSet(viewsets.ViewSet):
    """Admin ViewSet for review moderation dashboard."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def _get_review_by_type_and_id(self, review_type: str, review_id: int):
        """Get review instance by type and ID."""
        from reviews_system.models import WebsiteReview, WriterReview, OrderReview
        
        review_map = {
            'website': WebsiteReview,
            'writer': WriterReview,
            'order': OrderReview,
        }
        
        review_class = review_map.get(review_type)
        if not review_class:
            raise ValueError(f"Invalid review type: {review_type}")
        
        return get_object_or_404(review_class, id=review_id)
    
    @action(detail=False, methods=['get'], url_path='moderation-queue')
    def moderation_queue(self, request):
        """Get pending reviews for moderation."""
        from reviews_system.models import WebsiteReview, WriterReview, OrderReview
        from reviews_system.serializers import (
            WebsiteReviewSerializer, WriterReviewSerializer, OrderReviewSerializer
        )
        from django.db.models import Q
        
        # Get query parameters
        review_type = request.query_params.get('type', None)  # website, writer, order
        limit = int(request.query_params.get('limit', 50))
        
        # Filter: pending = not approved, not shadowed, or flagged
        pending_filter = Q(is_approved=False) | Q(is_flagged=True) | Q(is_shadowed=True)
        
        # Get pending reviews by type
        pending_reviews = []
        
        if not review_type or review_type == 'website':
            website_reviews = WebsiteReview.objects.filter(pending_filter).select_related(
                'reviewer', 'website'
            ).order_by('-submitted_at')[:limit]
            for review in website_reviews:
                serializer = WebsiteReviewSerializer(review)
                pending_reviews.append({
                    'type': 'website',
                    'id': review.id,
                    'data': serializer.data
                })
        
        if not review_type or review_type == 'writer':
            writer_reviews = WriterReview.objects.filter(pending_filter).select_related(
                'reviewer', 'writer'
            ).order_by('-submitted_at')[:limit]
            for review in writer_reviews:
                serializer = WriterReviewSerializer(review)
                pending_reviews.append({
                    'type': 'writer',
                    'id': review.id,
                    'data': serializer.data
                })
        
        if not review_type or review_type == 'order':
            order_reviews = OrderReview.objects.filter(pending_filter).select_related(
                'reviewer', 'order', 'writer'
            ).order_by('-submitted_at')[:limit]
            for review in order_reviews:
                serializer = OrderReviewSerializer(review)
                pending_reviews.append({
                    'type': 'order',
                    'id': review.id,
                    'data': serializer.data
                })
        
        # Sort by submitted_at descending
        pending_reviews.sort(key=lambda x: x['data'].get('submitted_at', ''), reverse=True)
        
        return Response({
            'reviews': pending_reviews[:limit],
            'count': len(pending_reviews),
            'counts_by_type': {
                'website': WebsiteReview.objects.filter(pending_filter).count(),
                'writer': WriterReview.objects.filter(pending_filter).count(),
                'order': OrderReview.objects.filter(pending_filter).count(),
            }
        })
    
    @action(detail=False, methods=['post'], url_path='approve')
    def approve_review(self, request):
        """Approve a review."""
        from reviews_system.services.review_moderation_service import ReviewModerationService
        
        review_type = request.data.get('review_type')  # website, writer, order
        review_id = request.data.get('review_id')
        moderation_notes = request.data.get('moderation_notes', '')
        
        if not review_type or not review_id:
            return Response(
                {"detail": "review_type and review_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            review = self._get_review_by_type_and_id(review_type, review_id)
            ReviewModerationService.moderate_review(review, {
                'is_approved': True,
                'is_shadowed': False,
                'moderation_notes': moderation_notes
            })
            
            return Response({
                "detail": "Review approved successfully.",
                "review_id": review.id,
                "review_type": review_type
            })
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error approving review: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='reject')
    def reject_review(self, request):
        """Reject (shadow) a review."""
        from reviews_system.services.review_moderation_service import ReviewModerationService
        
        review_type = request.data.get('review_type')
        review_id = request.data.get('review_id')
        reason = request.data.get('reason', 'Review rejected by admin')
        moderation_notes = request.data.get('moderation_notes', '')
        
        if not review_type or not review_id:
            return Response(
                {"detail": "review_type and review_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            review = self._get_review_by_type_and_id(review_type, review_id)
            ReviewModerationService.moderate_review(review, {
                'is_approved': False,
                'is_shadowed': True,
                'flag_reason': reason,
                'moderation_notes': moderation_notes
            })
            
            return Response({
                "detail": "Review rejected successfully.",
                "review_id": review.id,
                "review_type": review_type
            })
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error rejecting review: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='flag')
    def flag_review(self, request):
        """Flag a review for further investigation."""
        from reviews_system.services.review_moderation_service import ReviewModerationService
        
        review_type = request.data.get('review_type')
        review_id = request.data.get('review_id')
        reason = request.data.get('reason', '')
        moderation_notes = request.data.get('moderation_notes', '')
        
        if not review_type or not review_id:
            return Response(
                {"detail": "review_type and review_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reason:
            return Response(
                {"detail": "reason is required for flagging a review."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            review = self._get_review_by_type_and_id(review_type, review_id)
            ReviewModerationService.moderate_review(review, {
                'is_flagged': True,
                'flag_reason': reason,
                'moderation_notes': moderation_notes
            })
            
            return Response({
                "detail": "Review flagged successfully.",
                "review_id": review.id,
                "review_type": review_type
            })
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error flagging review: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='shadow')
    def shadow_review(self, request):
        """Shadow hide a review."""
        from reviews_system.services.review_moderation_service import ReviewModerationService
        
        review_type = request.data.get('review_type')
        review_id = request.data.get('review_id')
        reason = request.data.get('reason', 'Review shadowed by admin')
        moderation_notes = request.data.get('moderation_notes', '')
        
        if not review_type or not review_id:
            return Response(
                {"detail": "review_type and review_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            review = self._get_review_by_type_and_id(review_type, review_id)
            ReviewModerationService.shadow_review(review, reason)
            if moderation_notes:
                review.moderation_notes = moderation_notes
                review.save(update_fields=['moderation_notes'])
            
            return Response({
                "detail": "Review shadowed successfully.",
                "review_id": review.id,
                "review_type": review_type
            })
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error shadowing review: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get review analytics dashboard."""
        from reviews_system.models import WebsiteReview, WriterReview, OrderReview
        from django.db.models import Count, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth
        
        # Get all reviews
        all_website_reviews = WebsiteReview.objects.all()
        all_writer_reviews = WriterReview.objects.all()
        all_order_reviews = OrderReview.objects.all()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_website_reviews = all_website_reviews.filter(website=website)
            all_writer_reviews = all_writer_reviews.filter(website=website)
            all_order_reviews = all_order_reviews.filter(website=website)
        
        # Status breakdown
        website_status = all_website_reviews.values('is_approved', 'is_shadowed', 'is_flagged').annotate(
            count=Count('id')
        )
        writer_status = all_writer_reviews.values('is_approved', 'is_shadowed', 'is_flagged').annotate(
            count=Count('id')
        )
        order_status = all_order_reviews.values('is_approved', 'is_shadowed', 'is_flagged').annotate(
            count=Count('id')
        )
        
        # Pending reviews (not approved, shadowed, or flagged)
        pending_filter = Q(is_approved=False) | Q(is_shadowed=True) | Q(is_flagged=True)
        pending_website = all_website_reviews.filter(pending_filter).count()
        pending_writer = all_writer_reviews.filter(pending_filter).count()
        pending_order = all_order_reviews.filter(pending_filter).count()
        
        # Approved reviews
        approved_website = all_website_reviews.filter(is_approved=True, is_shadowed=False).count()
        approved_writer = all_writer_reviews.filter(is_approved=True, is_shadowed=False).count()
        approved_order = all_order_reviews.filter(is_approved=True, is_shadowed=False).count()
        
        # Flagged reviews
        flagged_website = all_website_reviews.filter(is_flagged=True).count()
        flagged_writer = all_writer_reviews.filter(is_flagged=True).count()
        flagged_order = all_order_reviews.filter(is_flagged=True).count()
        
        # Average ratings
        avg_rating_website = all_website_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        avg_rating_writer = all_writer_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        avg_rating_order = all_order_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Monthly trends (last 12 months)
        month_ago = timezone.now() - timedelta(days=365)
        monthly_website = all_website_reviews.filter(
            submitted_at__gte=month_ago
        ).annotate(
            month=TruncMonth('submitted_at')
        ).values('month').annotate(
            count=Count('id'),
            approved=Count('id', filter=Q(is_approved=True, is_shadowed=False))
        ).order_by('month')
        
        monthly_writer = all_writer_reviews.filter(
            submitted_at__gte=month_ago
        ).annotate(
            month=TruncMonth('submitted_at')
        ).values('month').annotate(
            count=Count('id'),
            approved=Count('id', filter=Q(is_approved=True, is_shadowed=False))
        ).order_by('month')
        
        monthly_order = all_order_reviews.filter(
            submitted_at__gte=month_ago
        ).annotate(
            month=TruncMonth('submitted_at')
        ).values('month').annotate(
            count=Count('id'),
            approved=Count('id', filter=Q(is_approved=True, is_shadowed=False))
        ).order_by('month')
        
        return Response({
            'summary': {
                'total_reviews': {
                    'website': all_website_reviews.count(),
                    'writer': all_writer_reviews.count(),
                    'order': all_order_reviews.count(),
                },
                'pending_reviews': {
                    'website': pending_website,
                    'writer': pending_writer,
                    'order': pending_order,
                    'total': pending_website + pending_writer + pending_order,
                },
                'approved_reviews': {
                    'website': approved_website,
                    'writer': approved_writer,
                    'order': approved_order,
                    'total': approved_website + approved_writer + approved_order,
                },
                'flagged_reviews': {
                    'website': flagged_website,
                    'writer': flagged_writer,
                    'order': flagged_order,
                    'total': flagged_website + flagged_writer + flagged_order,
                },
                'average_ratings': {
                    'website': float(avg_rating_website),
                    'writer': float(avg_rating_writer),
                    'order': float(avg_rating_order),
                }
            },
            'monthly_trends': {
                'website': [
                    {
                        'month': item['month'].isoformat() if item['month'] else None,
                        'count': item['count'],
                        'approved': item['approved']
                    }
                    for item in monthly_website
                ],
                'writer': [
                    {
                        'month': item['month'].isoformat() if item['month'] else None,
                        'count': item['count'],
                        'approved': item['approved']
                    }
                    for item in monthly_writer
                ],
                'order': [
                    {
                        'month': item['month'].isoformat() if item['month'] else None,
                        'count': item['count'],
                        'approved': item['approved']
                    }
                    for item in monthly_order
                ]
            }
        })
    
    @action(detail=False, methods=['get'], url_path='spam-detection')
    def spam_detection(self, request):
        """Get spam detection alerts for reviews."""
        from reviews_system.models import WebsiteReview, WriterReview, OrderReview
        from django.db.models import Count, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get reviews from last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        
        # Get recent reviews
        recent_website = WebsiteReview.objects.filter(submitted_at__gte=week_ago)
        recent_writer = WriterReview.objects.filter(submitted_at__gte=week_ago)
        recent_order = OrderReview.objects.filter(submitted_at__gte=week_ago)
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            recent_website = recent_website.filter(website=website)
            recent_writer = recent_writer.filter(website=website)
            recent_order = recent_order.filter(website=website)
        
        # Find users with multiple reviews in short time (potential spam)
        # Users with 3+ reviews in last 7 days
        website_spam_users = recent_website.values('reviewer').annotate(
            count=Count('id')
        ).filter(count__gte=3)
        
        writer_spam_users = recent_writer.values('reviewer').annotate(
            count=Count('id')
        ).filter(count__gte=3)
        
        order_spam_users = recent_order.values('reviewer').annotate(
            count=Count('id')
        ).filter(count__gte=3)
        
        # Reviews with very short comments (potential spam)
        # Note: We'll filter in Python since Django ORM doesn't support length directly
        short_comment_threshold = 10
        website_short = sum(1 for r in recent_website if not r.comment or len(r.comment) < short_comment_threshold)
        writer_short = sum(1 for r in recent_writer if not r.comment or len(r.comment) < short_comment_threshold)
        order_short = sum(1 for r in recent_order if not r.comment or len(r.comment) < short_comment_threshold)
        
        # All 5-star reviews (potential fake reviews)
        website_five_star = recent_website.filter(rating=5).count()
        writer_five_star = recent_writer.filter(rating=5).count()
        order_five_star = recent_order.filter(rating=5).count()
        
        return Response({
            'alerts': {
                'multiple_reviews_users': {
                    'website': list(website_spam_users),
                    'writer': list(writer_spam_users),
                    'order': list(order_spam_users),
                },
                'short_comments': {
                    'website': website_short,
                    'writer': writer_short,
                    'order': order_short,
                    'total': website_short + writer_short + order_short,
                },
                'all_five_star': {
                    'website': website_five_star,
                    'writer': writer_five_star,
                    'order': order_five_star,
                    'total': website_five_star + writer_five_star + order_five_star,
                }
            },
            'summary': {
                'total_recent_reviews': (
                    recent_website.count() + recent_writer.count() + recent_order.count()
                ),
                'potential_spam_count': (
                    len(website_spam_users) + len(writer_spam_users) + len(order_spam_users)
                )
            }
        })


# Admin Order Management ViewSet
class AdminOrderManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for order management dashboard."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get order statistics dashboard."""
        from orders.models import Order
        from orders.order_enums import OrderStatus
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all orders
        all_orders = Order.objects.all().select_related('client', 'assigned_writer', 'website')
        
        # Both superadmin and admin should see all orders (no website filtering)
        # No website filtering for superadmin and admin
        
        # Status breakdown
        status_breakdown = all_orders.values('status').annotate(
            count=Count('id')
        )
        
        # Orders by status
        pending_orders = all_orders.filter(status__in=['pending', 'available', 'unpaid']).count()
        in_progress_orders = all_orders.filter(status__in=['in_progress', 'assigned', 'on_revision']).count()
        completed_orders = all_orders.filter(status__in=['completed', 'reviewed', 'closed']).count()
        cancelled_orders = all_orders.filter(status__in=['cancelled', 'refunded']).count()
        
        # Orders needing assignment (available, pending, unpaid)
        needs_assignment = all_orders.filter(
            status__in=['available', 'pending', 'unpaid'],
            assigned_writer__isnull=True
        ).count()
        
        # Overdue orders
        now = timezone.now()
        overdue_orders = all_orders.filter(
            Q(client_deadline__lt=now) | Q(writer_deadline__lt=now),
            status__in=['in_progress', 'assigned', 'on_revision', 'pending']
        ).count()
        
        # Recent orders (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        recent_orders = all_orders.filter(created_at__gte=month_ago).count()
        
        # Orders by week
        from django.db.models.functions import TruncWeek
        weekly_orders = all_orders.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id')
        ).order_by('week')
        
        # Average order value
        avg_order_value = all_orders.aggregate(
            avg=Avg('total_price')
        )['avg'] or 0
        
        # Total revenue (completed orders)
        total_revenue = all_orders.filter(
            status__in=['completed', 'reviewed', 'closed']
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        return Response({
            'summary': {
                'total_orders': all_orders.count(),
                'pending_orders': pending_orders,
                'in_progress_orders': in_progress_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'needs_assignment': needs_assignment,
                'overdue_orders': overdue_orders,
                'recent_orders': recent_orders,
                'avg_order_value': float(avg_order_value),
                'total_revenue': float(total_revenue),
            },
            'status_breakdown': {
                item['status']: item['count']
                for item in status_breakdown
            },
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count']
                }
                for item in weekly_orders
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get order analytics and trends."""
        from orders.models import Order
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth, TruncWeek
        
        all_orders = Order.objects.all()
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_orders = all_orders.filter(website=website)
        
        # Get query parameters
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Filter orders by date range
        orders = all_orders.filter(created_at__gte=date_from)
        
        # Monthly trends
        monthly_trends = orders.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'reviewed', 'closed'])),
            total_revenue=Sum('total_price', filter=Q(status__in=['completed', 'reviewed', 'closed']))
        ).order_by('month')
        
        # Weekly trends
        weekly_trends = orders.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(status__in=['completed', 'reviewed', 'closed']))
        ).order_by('week')
        
        # Service type breakdown
        service_breakdown = orders.values('paper_type__name').annotate(
            count=Count('id'),
            total_revenue=Sum('total_price', filter=Q(status__in=['completed', 'reviewed', 'closed']))
        ).order_by('-count')
        
        # Status trends over time
        status_trends = orders.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Average completion time
        completed_orders = orders.filter(
            status__in=['completed', 'reviewed', 'closed']
        )
        
        completion_times = []
        for order in completed_orders:
            # Try to find completion time from transitions or updated_at
            completed_at = getattr(order, 'completed_at', None) or order.updated_at
            if completed_at and order.created_at:
                days = (completed_at - order.created_at).days
                if days >= 0:
                    completion_times.append(days)
        
        avg_completion_days = sum(completion_times) / len(completion_times) if completion_times else None
        
        # Conversion rate (orders that reach completed status)
        total_orders_count = orders.count()
        completed_count = orders.filter(status__in=['completed', 'reviewed', 'closed']).count()
        conversion_rate = (completed_count / total_orders_count * 100) if total_orders_count > 0 else 0
        
        return Response({
            'monthly_trends': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'count': item['count'],
                    'completed': item['completed'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in monthly_trends
            ],
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count'],
                    'completed': item['completed']
                }
                for item in weekly_trends
            ],
            'service_breakdown': [
                {
                    'service_type': item['paper_type__name'] or 'Unknown',
                    'count': item['count'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in service_breakdown
            ],
            'status_trends': {
                item['status']: item['count']
                for item in status_trends
            },
            'avg_completion_days': avg_completion_days,
            'conversion_rate': conversion_rate,
        })
    
    @action(detail=False, methods=['get'], url_path='assignment-queue')
    def assignment_queue(self, request):
        """Get orders needing assignment."""
        from orders.models import Order
        from orders.serializers import OrderSerializer
        from orders.order_enums import OrderStatus
        
        # Orders that need assignment
        orders = Order.objects.filter(
            status__in=[OrderStatus.AVAILABLE.value, OrderStatus.PENDING.value, OrderStatus.UNPAID.value],
            assigned_writer__isnull=True
        ).select_related('client', 'website', 'paper_type').order_by('-created_at')
        
        # Both superadmin and admin should see all orders (no website filtering)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        status_filter = request.query_params.get('status', None)
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        orders = orders[:limit]
        
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'orders': serializer.data,
            'count': len(serializer.data),
            'total_needing_assignment': Order.objects.filter(
                status__in=[OrderStatus.AVAILABLE.value, OrderStatus.PENDING.value, OrderStatus.UNPAID.value],
                assigned_writer__isnull=True
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='overdue')
    def overdue_orders(self, request):
        """Get overdue orders."""
        from orders.models import Order
        from orders.serializers import OrderSerializer
        from django.utils import timezone
        
        now = timezone.now()
        
        # Overdue orders (deadline passed but not completed)
        overdue = Order.objects.filter(
            Q(client_deadline__lt=now) | Q(writer_deadline__lt=now),
            status__in=['in_progress', 'assigned', 'on_revision', 'pending', 'available']
        ).select_related('client', 'assigned_writer', 'website').order_by('client_deadline', 'writer_deadline')
        
        # Both superadmin and admin should see all orders (no website filtering)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        overdue = overdue[:limit]
        
        serializer = OrderSerializer(overdue, many=True)
        return Response({
            'orders': serializer.data,
            'count': len(serializer.data),
            'total_overdue': Order.objects.filter(
                Q(client_deadline__lt=now) | Q(writer_deadline__lt=now),
                status__in=['in_progress', 'assigned', 'on_revision', 'pending', 'available']
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='stuck')
    def stuck_orders(self, request):
        """Get stuck orders (no progress for extended period)."""
        from orders.models import Order
        from orders.serializers import OrderSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        # Orders that haven't been updated in last 7 days and are in progress
        stuck_threshold = timezone.now() - timedelta(days=7)
        
        stuck = Order.objects.filter(
            updated_at__lt=stuck_threshold,
            status__in=['in_progress', 'assigned', 'on_revision', 'pending']
        ).select_related('client', 'assigned_writer', 'website').order_by('updated_at')
        
        # Both superadmin and admin should see all orders (no website filtering)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        days = int(request.query_params.get('days', 7))
        
        # Recalculate with custom days if provided
        if days != 7:
            stuck_threshold = timezone.now() - timedelta(days=days)
            stuck = Order.objects.filter(
                updated_at__lt=stuck_threshold,
                status__in=['in_progress', 'assigned', 'on_revision', 'pending']
            ).select_related('client', 'assigned_writer', 'website').order_by('updated_at')
            # Both superadmin and admin should see all orders (no website filtering)
        
        stuck = stuck[:limit]
        
        serializer = OrderSerializer(stuck, many=True)
        return Response({
            'orders': serializer.data,
            'count': len(serializer.data),
            'total_stuck': Order.objects.filter(
                updated_at__lt=stuck_threshold,
                status__in=['in_progress', 'assigned', 'on_revision', 'pending']
            ).count()
        })
    
    @action(detail=False, methods=['post'], url_path='bulk-assign')
    def bulk_assign(self, request):
        """Bulk assign orders to writers."""
        from orders.models import Order
        from orders.services.assignment import OrderAssignmentService
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ValidationError
        
        User = get_user_model()
        
        order_ids = request.data.get('order_ids', [])
        writer_id = request.data.get('writer_id')
        reason = request.data.get('reason', 'Bulk assignment by admin')
        
        if not order_ids or not writer_id:
            return Response(
                {"detail": "order_ids and writer_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            writer = User.objects.get(id=writer_id, role='writer', is_active=True)
        except User.DoesNotExist:
            return Response(
                {"detail": "Writer not found or not active."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        results = {
            'success': [],
            'failed': []
        }
        
        for order_id in order_ids:
            try:
                order = Order.objects.get(id=order_id)
                assignment_service = OrderAssignmentService(order)
                assignment_service.actor = request.user
                assignment_service.assign_writer(writer.id, reason)
                results['success'].append(order_id)
            except ValidationError as e:
                results['failed'].append({
                    'order_id': order_id,
                    'error': str(e)
                })
            except Exception as e:
                results['failed'].append({
                    'order_id': order_id,
                    'error': str(e)
                })
        
        return Response({
            'detail': f"Bulk assignment completed. {len(results['success'])} succeeded, {len(results['failed'])} failed.",
            'results': results
        })
    
    @action(detail=False, methods=['post'], url_path='bulk-action')
    def bulk_action(self, request):
        """Perform bulk actions on orders."""
        from orders.models import Order
        from orders.order_enums import OrderStatus
        
        order_ids = request.data.get('order_ids', [])
        action = request.data.get('action')  # cancel, refund, archive, etc.
        notes = request.data.get('notes', '')
        
        if not order_ids or not action:
            return Response(
                {"detail": "order_ids and action are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'success': [],
            'failed': []
        }
        
        for order_id in order_ids:
            try:
                order = Order.objects.get(id=order_id)
                
                if action == 'cancel':
                    order.status = OrderStatus.CANCELLED.value
                    order.save(update_fields=['status'])
                elif action == 'refund':
                    order.status = OrderStatus.REFUNDED.value
                    order.save(update_fields=['status'])
                elif action == 'archive':
                    order.status = OrderStatus.ARCHIVED.value
                    order.save(update_fields=['status'])
                elif action == 'on_hold':
                    order.status = OrderStatus.ON_HOLD.value
                    order.save(update_fields=['status'])
                else:
                    results['failed'].append({
                        'order_id': order_id,
                        'error': f"Unknown action: {action}"
                    })
                    continue
                
                results['success'].append(order_id)
            except Exception as e:
                results['failed'].append({
                    'order_id': order_id,
                    'error': str(e)
                })
        
        return Response({
            'detail': f"Bulk action '{action}' completed. {len(results['success'])} succeeded, {len(results['failed'])} failed.",
            'results': results
        })
    
    @action(detail=True, methods=['get'], url_path='timeline')
    def order_timeline(self, request, pk=None):
        """Get order timeline/history."""
        from orders.models import Order, OrderTransitionLog, WriterReassignmentLog
        from orders.serializers import OrderSerializer
        
        order = get_object_or_404(Order, id=pk)
        
        # Get order details
        order_serializer = OrderSerializer(order)
        
        # Get transition logs
        transitions = OrderTransitionLog.objects.filter(
            order=order
        ).select_related('user').order_by('-timestamp')
        
        # Get reassignment logs
        reassignments = WriterReassignmentLog.objects.filter(
            order=order
        ).select_related('previous_writer', 'new_writer', 'reassigned_by').order_by('-reassigned_at')
        
        # Combine into timeline
        timeline = []
        
        # Add transitions
        for transition in transitions:
            timeline.append({
                'type': 'status_change',
                'timestamp': transition.timestamp.isoformat() if transition.timestamp else None,
                'user': transition.user.username if transition.user else 'System',
                'old_status': transition.old_status,
                'new_status': transition.new_status,
                'action': transition.action,
                'is_automatic': transition.is_automatic,
                'meta': transition.meta
            })
        
        # Add reassignments
        for reassignment in reassignments:
            timeline.append({
                'type': 'reassignment',
                'timestamp': reassignment.reassigned_at.isoformat() if reassignment.reassigned_at else None,
                'user': reassignment.reassigned_by.username if reassignment.reassigned_by else 'System',
                'previous_writer': reassignment.previous_writer.username if reassignment.previous_writer else None,
                'new_writer': reassignment.new_writer.username if reassignment.new_writer else None,
                'reason': reassignment.reason
            })
        
        # Sort by timestamp descending
        timeline.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        return Response({
            'order': order_serializer.data,
            'timeline': timeline,
            'total_events': len(timeline)
        })


# Admin Special Orders Management ViewSet
class AdminSpecialOrdersManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for special orders management dashboard."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get special order statistics dashboard."""
        from special_orders.models import SpecialOrder
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all special orders
        all_orders = SpecialOrder.objects.all().select_related('client', 'writer', 'website', 'predefined_type')
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_orders = all_orders.filter(website=website)
        
        # Status breakdown
        status_breakdown = all_orders.values('status').annotate(
            count=Count('id')
        )
        
        # Order type breakdown
        type_breakdown = all_orders.values('order_type').annotate(
            count=Count('id')
        )
        
        # Combined aggregations - reduces from 8 queries to 2 queries
        month_ago = timezone.now() - timedelta(days=30)
        
        # Status and approval counts in one query
        status_counts = all_orders.aggregate(
            inquiry_orders=Count('id', filter=Q(status='inquiry')),
            awaiting_approval=Count('id', filter=Q(status='awaiting_approval')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            completed=Count('id', filter=Q(status='completed')),
            needs_approval=Count('id', filter=Q(status__in=['inquiry', 'awaiting_approval'], is_approved=False)),
            needs_estimation=Count('id', filter=Q(order_type='estimated', total_cost__isnull=True, status__in=['inquiry', 'awaiting_approval'])),
            recent_orders=Count('id', filter=Q(created_at__gte=month_ago))
        )
        
        inquiry_orders = status_counts['inquiry_orders'] or 0
        awaiting_approval = status_counts['awaiting_approval'] or 0
        in_progress = status_counts['in_progress'] or 0
        completed = status_counts['completed'] or 0
        needs_approval = status_counts['needs_approval'] or 0
        needs_estimation = status_counts['needs_estimation'] or 0
        recent_orders = status_counts['recent_orders'] or 0
        
        # Revenue aggregations in one query
        revenue_stats = all_orders.aggregate(
            total_revenue=Sum('total_cost', filter=Q(status='completed')),
            avg_order_value=Avg('total_cost')
        )
        
        total_revenue = revenue_stats['total_revenue'] or 0
        avg_order_value = revenue_stats['avg_order_value'] or 0
        
        # Pending installments
        from special_orders.models import InstallmentPayment
        pending_installments = InstallmentPayment.objects.filter(
            is_paid=False,
            special_order__status__in=['in_progress', 'completed']
        ).count()
        
        return Response({
            'summary': {
                'total_orders': all_orders.count(),
                'inquiry_orders': inquiry_orders,
                'awaiting_approval': awaiting_approval,
                'in_progress': in_progress,
                'completed': completed,
                'needs_approval': needs_approval,
                'needs_estimation': needs_estimation,
                'recent_orders': recent_orders,
                'total_revenue': float(total_revenue),
                'avg_order_value': float(avg_order_value),
                'pending_installments': pending_installments,
            },
            'status_breakdown': {
                item['status']: item['count']
                for item in status_breakdown
            },
            'type_breakdown': {
                item['order_type']: item['count']
                for item in type_breakdown
            }
        })
    
    @action(detail=False, methods=['get'], url_path='approval-queue')
    def approval_queue(self, request):
        """Get orders awaiting approval."""
        from special_orders.models import SpecialOrder
        from special_orders.serializers import SpecialOrderSerializer
        
        # Orders awaiting approval
        orders = SpecialOrder.objects.filter(
            status__in=['inquiry', 'awaiting_approval'],
            is_approved=False
        ).select_related('client', 'writer', 'website', 'predefined_type').order_by('-created_at')
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                orders = orders.filter(website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        status_filter = request.query_params.get('status', None)
        order_type_filter = request.query_params.get('order_type', None)
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        if order_type_filter:
            orders = orders.filter(order_type=order_type_filter)
        
        orders = orders[:limit]
        
        serializer = SpecialOrderSerializer(orders, many=True)
        return Response({
            'orders': serializer.data,
            'count': len(serializer.data),
            'total_awaiting_approval': SpecialOrder.objects.filter(
                status__in=['inquiry', 'awaiting_approval'],
                is_approved=False
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='estimated-queue')
    def estimated_queue(self, request):
        """Get orders needing cost estimation."""
        from special_orders.models import SpecialOrder
        from special_orders.serializers import SpecialOrderSerializer
        
        # Orders needing cost estimation
        orders = SpecialOrder.objects.filter(
            order_type='estimated',
            total_cost__isnull=True,
            status__in=['inquiry', 'awaiting_approval']
        ).select_related('client', 'website').order_by('-created_at')
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                orders = orders.filter(website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        orders = orders[:limit]
        
        serializer = SpecialOrderSerializer(orders, many=True)
        return Response({
            'orders': serializer.data,
            'count': len(serializer.data),
            'total_needing_estimation': SpecialOrder.objects.filter(
                order_type='estimated',
                total_cost__isnull=True,
                status__in=['inquiry', 'awaiting_approval']
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='installment-tracking')
    def installment_tracking(self, request):
        """Get installment payment tracking."""
        from special_orders.models import InstallmentPayment, SpecialOrder
        from special_orders.serializers import InstallmentPaymentSerializer
        from django.utils import timezone
        from django.db.models import Q, Sum
        
        now = timezone.now().date()
        
        # Get all installments
        installments = InstallmentPayment.objects.filter(
            special_order__status__in=['in_progress', 'completed']
        ).select_related('special_order', 'special_order__client', 'payment_record').order_by('due_date')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            installments = installments.filter(special_order__website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        status_filter = request.query_params.get('status', None)  # paid, unpaid, overdue
        
        if status_filter == 'paid':
            installments = installments.filter(is_paid=True)
        elif status_filter == 'unpaid':
            installments = installments.filter(is_paid=False, due_date__gte=now)
        elif status_filter == 'overdue':
            installments = installments.filter(is_paid=False, due_date__lt=now)
        
        installments = installments[:limit]
        
        serializer = InstallmentPaymentSerializer(installments, many=True)
        
        # Calculate statistics
        total_installments = InstallmentPayment.objects.filter(
            special_order__status__in=['in_progress', 'completed']
        )
        if website:
            total_installments = total_installments.filter(special_order__website=website)
        
        paid_count = total_installments.filter(is_paid=True).count()
        unpaid_count = total_installments.filter(is_paid=False, due_date__gte=now).count()
        overdue_count = total_installments.filter(is_paid=False, due_date__lt=now).count()
        
        total_due = total_installments.filter(is_paid=False).aggregate(
            total=Sum('amount_due')
        )['total'] or 0
        
        return Response({
            'installments': serializer.data,
            'count': len(serializer.data),
            'statistics': {
                'total_installments': total_installments.count(),
                'paid': paid_count,
                'unpaid': unpaid_count,
                'overdue': overdue_count,
                'total_due': float(total_due)
            }
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get special order analytics and trends."""
        from special_orders.models import SpecialOrder
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth, TruncWeek
        
        all_orders = SpecialOrder.objects.all()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_orders = all_orders.filter(website=website)
        
        # Get query parameters
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Filter orders by date range
        orders = all_orders.filter(created_at__gte=date_from)
        
        # Monthly trends
        monthly_trends = orders.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            total_revenue=Sum('total_cost', filter=Q(status='completed'))
        ).order_by('month')
        
        # Weekly trends
        weekly_trends = orders.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(status='completed'))
        ).order_by('week')
        
        # Order type breakdown
        type_breakdown = orders.values('order_type').annotate(
            count=Count('id'),
            total_revenue=Sum('total_cost', filter=Q(status='completed'))
        ).order_by('-count')
        
        # Status trends over time
        status_trends = orders.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Predefined type breakdown
        predefined_breakdown = orders.filter(
            order_type='predefined'
        ).values('predefined_type__name').annotate(
            count=Count('id'),
            total_revenue=Sum('total_cost', filter=Q(status='completed'))
        ).order_by('-count')
        
        # Average completion time
        completed_orders = orders.filter(status='completed')
        
        completion_times = []
        for order in completed_orders:
            if order.updated_at and order.created_at:
                days = (order.updated_at - order.created_at).days
                if days >= 0:
                    completion_times.append(days)
        
        avg_completion_days = sum(completion_times) / len(completion_times) if completion_times else None
        
        # Conversion rate (orders that reach completed status)
        total_orders_count = orders.count()
        completed_count = orders.filter(status='completed').count()
        conversion_rate = (completed_count / total_orders_count * 100) if total_orders_count > 0 else 0
        
        return Response({
            'monthly_trends': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'count': item['count'],
                    'completed': item['completed'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in monthly_trends
            ],
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count'],
                    'completed': item['completed']
                }
                for item in weekly_trends
            ],
            'type_breakdown': [
                {
                    'order_type': item['order_type'],
                    'count': item['count'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in type_breakdown
            ],
            'status_trends': {
                item['status']: item['count']
                for item in status_trends
            },
            'predefined_breakdown': [
                {
                    'predefined_type': item['predefined_type__name'] or 'Unknown',
                    'count': item['count'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in predefined_breakdown
            ],
            'avg_completion_days': avg_completion_days,
            'conversion_rate': conversion_rate,
        })
    
    @action(detail=False, methods=['get', 'post'], url_path='configs')
    def configs(self, request):
        """Get or create/update predefined order configs."""
        from special_orders.models import PredefinedSpecialOrderConfig, PredefinedSpecialOrderDuration
        from special_orders.serializers import (
            PredefinedSpecialOrderConfigSerializer,
            PredefinedSpecialOrderDurationSerializer
        )
        
        if request.method == 'GET':
            # Get all configs
            configs = PredefinedSpecialOrderConfig.objects.all().select_related('website').prefetch_related('durations')
            
            # Filter by website if user has website context
            website = getattr(request.user, 'website', None)
            if website:
                configs = configs.filter(website=website)
            
            serializer = PredefinedSpecialOrderConfigSerializer(configs, many=True)
            return Response({
                'configs': serializer.data,
                'count': len(serializer.data)
            })
        
        elif request.method == 'POST':
            # Create or update config
            config_id = request.data.get('id', None)
            name = request.data.get('name')
            description = request.data.get('description', '')
            website_id = request.data.get('website')
            is_active = request.data.get('is_active', True)
            durations = request.data.get('durations', [])  # List of {duration_days, price}
            
            if not name or not website_id:
                return Response(
                    {"detail": "name and website are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                from websites.models import Website
                website = Website.objects.get(id=website_id)
            except Website.DoesNotExist:
                return Response(
                    {"detail": "Website not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if config_id:
                # Update existing config
                try:
                    config = PredefinedSpecialOrderConfig.objects.get(id=config_id)
                    config.name = name
                    config.description = description
                    config.is_active = is_active
                    config.save()
                except PredefinedSpecialOrderConfig.DoesNotExist:
                    return Response(
                        {"detail": "Config not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Create new config
                config = PredefinedSpecialOrderConfig.objects.create(
                    name=name,
                    description=description,
                    website=website,
                    is_active=is_active
                )
            
            # Update durations
            if durations:
                # Delete existing durations
                PredefinedSpecialOrderDuration.objects.filter(predefined_order=config).delete()
                
                # Create new durations
                for duration_data in durations:
                    PredefinedSpecialOrderDuration.objects.create(
                        predefined_order=config,
                        website=website,
                        duration_days=duration_data.get('duration_days'),
                        price=duration_data.get('price')
                    )
            
            serializer = PredefinedSpecialOrderConfigSerializer(config)
            return Response({
                'detail': 'Config created/updated successfully.',
                'config': serializer.data
            })


# Admin Class Bundles Management ViewSet
class AdminClassBundlesManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for class bundles management dashboard."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get class bundle statistics dashboard."""
        from class_management.models import ClassBundle
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all class bundles
        all_bundles = ClassBundle.objects.all().select_related('client', 'assigned_writer', 'website', 'config')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_bundles = all_bundles.filter(website=website)
        
        # Status breakdown
        status_breakdown = all_bundles.values('status').annotate(
            count=Count('id')
        )
        
        # Level breakdown
        level_breakdown = all_bundles.values('level').annotate(
            count=Count('id')
        )
        
        # Bundles by status
        not_started = all_bundles.filter(status='not_started').count()
        in_progress = all_bundles.filter(status='in_progress').count()
        exhausted = all_bundles.filter(status='exhausted').count()
        completed = all_bundles.filter(status='completed').count()
        
        # Bundles with installments enabled
        with_installments = all_bundles.filter(installments_enabled=True).count()
        
        # Recent bundles (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        recent_bundles = all_bundles.filter(created_at__gte=month_ago).count()
        
        # Total revenue (completed bundles)
        total_revenue = all_bundles.filter(
            status='completed'
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Average bundle value
        avg_bundle_value = all_bundles.aggregate(
            avg=Avg('total_price')
        )['avg'] or 0
        
        # Pending installments
        from class_management.models import ClassInstallment
        pending_installments = ClassInstallment.objects.filter(
            is_paid=False,
            class_bundle__status__in=['in_progress', 'completed']
        ).count()
        
        # Pending deposits
        pending_deposits = all_bundles.filter(
            deposit_required__gt=0,
            deposit_paid__lt=models.F('deposit_required'),
            status__in=['not_started', 'in_progress']
        ).count()
        
        return Response({
            'summary': {
                'total_bundles': all_bundles.count(),
                'not_started': not_started,
                'in_progress': in_progress,
                'exhausted': exhausted,
                'completed': completed,
                'with_installments': with_installments,
                'recent_bundles': recent_bundles,
                'total_revenue': float(total_revenue),
                'avg_bundle_value': float(avg_bundle_value),
                'pending_installments': pending_installments,
                'pending_deposits': pending_deposits,
            },
            'status_breakdown': {
                item['status']: item['count']
                for item in status_breakdown
            },
            'level_breakdown': {
                item['level'] or 'Unknown': item['count']
                for item in level_breakdown
            }
        })
    
    @action(detail=False, methods=['get'], url_path='installment-tracking')
    def installment_tracking(self, request):
        """Get installment payment tracking."""
        from class_management.models import ClassInstallment, ClassBundle
        from class_management.serializers import ClassInstallmentSerializer
        from django.utils import timezone
        from django.db.models import Q, Sum
        
        now = timezone.now().date()
        
        # Get all installments
        installments = ClassInstallment.objects.filter(
            class_bundle__status__in=['in_progress', 'completed']
        ).select_related('class_bundle', 'class_bundle__client', 'payment_record').order_by('due_date')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            installments = installments.filter(class_bundle__website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        status_filter = request.query_params.get('status', None)  # paid, unpaid, overdue
        
        if status_filter == 'paid':
            installments = installments.filter(is_paid=True)
        elif status_filter == 'unpaid':
            installments = installments.filter(is_paid=False, due_date__gte=now)
        elif status_filter == 'overdue':
            installments = installments.filter(is_paid=False, due_date__lt=now)
        
        installments = installments[:limit]
        
        serializer = ClassInstallmentSerializer(installments, many=True)
        
        # Calculate statistics
        total_installments = ClassInstallment.objects.filter(
            class_bundle__status__in=['in_progress', 'completed']
        )
        if website:
            total_installments = total_installments.filter(class_bundle__website=website)
        
        paid_count = total_installments.filter(is_paid=True).count()
        unpaid_count = total_installments.filter(is_paid=False, due_date__gte=now).count()
        overdue_count = total_installments.filter(is_paid=False, due_date__lt=now).count()
        
        total_due = total_installments.filter(is_paid=False).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'installments': serializer.data,
            'count': len(serializer.data),
            'statistics': {
                'total_installments': total_installments.count(),
                'paid': paid_count,
                'unpaid': unpaid_count,
                'overdue': overdue_count,
                'total_due': float(total_due)
            }
        })
    
    @action(detail=False, methods=['get'], url_path='deposit-pending')
    def deposit_pending(self, request):
        """Get bundles with pending deposits."""
        from class_management.models import ClassBundle
        from class_management.serializers import ClassBundleSerializer
        
        # Bundles with pending deposits
        bundles = ClassBundle.objects.filter(
            deposit_required__gt=0,
            deposit_paid__lt=models.F('deposit_required'),
            status__in=['not_started', 'in_progress']
        ).select_related('client', 'website', 'config').order_by('-created_at')
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            bundles = bundles.filter(website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        bundles = bundles[:limit]
        
        serializer = ClassBundleSerializer(bundles, many=True)
        return Response({
            'bundles': serializer.data,
            'count': len(serializer.data),
            'total_pending_deposits': ClassBundle.objects.filter(
                deposit_required__gt=0,
                deposit_paid__lt=models.F('deposit_required'),
                status__in=['not_started', 'in_progress']
            ).count()
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get class bundle analytics and trends."""
        from class_management.models import ClassBundle
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth, TruncWeek
        
        all_bundles = ClassBundle.objects.all()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_bundles = all_bundles.filter(website=website)
        
        # Get query parameters
        days = int(request.query_params.get('days', 30))
        date_from = timezone.now() - timedelta(days=days)
        
        # Filter bundles by date range
        bundles = all_bundles.filter(created_at__gte=date_from)
        
        # Monthly trends
        monthly_trends = bundles.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            total_revenue=Sum('total_price', filter=Q(status='completed'))
        ).order_by('month')
        
        # Weekly trends
        weekly_trends = bundles.annotate(
            week=TruncWeek('created_at')
        ).values('week').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(status='completed'))
        ).order_by('week')
        
        # Level breakdown
        level_breakdown = bundles.values('level').annotate(
            count=Count('id'),
            total_revenue=Sum('total_price', filter=Q(status='completed'))
        ).order_by('-count')
        
        # Status trends over time
        status_trends = bundles.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Pricing source breakdown
        pricing_breakdown = bundles.values('pricing_source').annotate(
            count=Count('id'),
            total_revenue=Sum('total_price', filter=Q(status='completed'))
        ).order_by('-count')
        
        # Average completion time
        completed_bundles = bundles.filter(status='completed')
        
        completion_times = []
        for bundle in completed_bundles:
            if bundle.completed_at and bundle.created_at:
                days = (bundle.completed_at - bundle.created_at).days
                if days >= 0:
                    completion_times.append(days)
        
        avg_completion_days = sum(completion_times) / len(completion_times) if completion_times else None
        
        # Conversion rate (bundles that reach completed status)
        total_bundles_count = bundles.count()
        completed_count = bundles.filter(status='completed').count()
        conversion_rate = (completed_count / total_bundles_count * 100) if total_bundles_count > 0 else 0
        
        return Response({
            'monthly_trends': [
                {
                    'month': item['month'].isoformat() if item['month'] else None,
                    'count': item['count'],
                    'completed': item['completed'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in monthly_trends
            ],
            'weekly_trends': [
                {
                    'week': item['week'].isoformat() if item['week'] else None,
                    'count': item['count'],
                    'completed': item['completed']
                }
                for item in weekly_trends
            ],
            'level_breakdown': [
                {
                    'level': item['level'] or 'Unknown',
                    'count': item['count'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in level_breakdown
            ],
            'status_trends': {
                item['status']: item['count']
                for item in status_trends
            },
            'pricing_breakdown': [
                {
                    'pricing_source': item['pricing_source'],
                    'count': item['count'],
                    'total_revenue': float(item['total_revenue'] or 0)
                }
                for item in pricing_breakdown
            ],
            'avg_completion_days': avg_completion_days,
            'conversion_rate': conversion_rate,
        })
    
    @action(detail=False, methods=['get', 'post'], url_path='configs')
    def configs(self, request):
        """Get or create/update bundle configs."""
        from class_management.models import ClassBundleConfig, ClassDurationOption
        from class_management.serializers import ClassBundleConfigSerializer
        
        if request.method == 'GET':
            # Get all configs
            configs = ClassBundleConfig.objects.all().select_related('website', 'duration')
            
            # Filter by website if user has website context
            website = getattr(request.user, 'website', None)
            if website:
                configs = configs.filter(website=website)
            
            serializer = ClassBundleConfigSerializer(configs, many=True)
            return Response({
                'configs': serializer.data,
                'count': len(serializer.data)
            })
        
        elif request.method == 'POST':
            # Create or update config
            config_id = request.data.get('id', None)
            website_id = request.data.get('website')
            duration_id = request.data.get('duration')
            level = request.data.get('level')
            bundle_size = request.data.get('bundle_size')
            price_per_class = request.data.get('price_per_class')
            is_active = request.data.get('is_active', True)
            
            if not website_id or not duration_id or not level or not bundle_size or not price_per_class:
                return Response(
                    {"detail": "website, duration, level, bundle_size, and price_per_class are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                from websites.models import Website
                website = Website.objects.get(id=website_id)
                duration = ClassDurationOption.objects.get(id=duration_id)
            except Website.DoesNotExist:
                return Response(
                    {"detail": "Website not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except ClassDurationOption.DoesNotExist:
                return Response(
                    {"detail": "Duration option not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if config_id:
                # Update existing config
                try:
                    config = ClassBundleConfig.objects.get(id=config_id)
                    config.website = website
                    config.duration = duration
                    config.level = level
                    config.bundle_size = bundle_size
                    config.price_per_class = price_per_class
                    config.is_active = is_active
                    config.save()
                except ClassBundleConfig.DoesNotExist:
                    return Response(
                        {"detail": "Config not found."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Create new config
                config = ClassBundleConfig.objects.create(
                    website=website,
                    duration=duration,
                    level=level,
                    bundle_size=bundle_size,
                    price_per_class=price_per_class,
                    is_active=is_active
                )
            
            serializer = ClassBundleConfigSerializer(config)
            return Response({
                'detail': 'Config created/updated successfully.',
                'config': serializer.data
            })
    
    @action(detail=False, methods=['get'], url_path='communication-threads')
    def communication_threads(self, request):
        """Get communication threads for class bundles."""
        from class_management.models import ClassBundle
        from communications.models import CommunicationThread
        from communications.serializers import CommunicationThreadSerializer
        
        # Get all bundles with threads
        bundles = ClassBundle.objects.filter(
            message_threads__isnull=False
        ).select_related('client', 'website').prefetch_related('message_threads').distinct()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            bundles = bundles.filter(website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        bundle_id = request.query_params.get('bundle_id', None)
        
        if bundle_id:
            bundles = bundles.filter(id=bundle_id)
        
        bundles = bundles[:limit]
        
        # Collect all threads
        threads = []
        for bundle in bundles:
            bundle_threads = bundle.message_threads.all()
            for thread in bundle_threads:
                serializer = CommunicationThreadSerializer(thread)
                threads.append({
                    'bundle_id': bundle.id,
                    'bundle_client': bundle.client.username if bundle.client else None,
                    'thread': serializer.data
                })
        
        return Response({
            'threads': threads,
            'count': len(threads)
        })
    
    @action(detail=False, methods=['get'], url_path='support-tickets')
    def support_tickets(self, request):
        """Get support tickets for class bundles."""
        from class_management.models import ClassBundle
        from tickets.models import Ticket
        from tickets.serializers import TicketSerializer
        
        # Get all bundles with tickets
        bundles = ClassBundle.objects.filter(
            support_tickets__isnull=False
        ).select_related('client', 'website').prefetch_related('support_tickets').distinct()
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            bundles = bundles.filter(website=website)
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 50))
        bundle_id = request.query_params.get('bundle_id', None)
        status_filter = request.query_params.get('status', None)
        
        if bundle_id:
            bundles = bundles.filter(id=bundle_id)
        
        bundles = bundles[:limit]
        
        # Collect all tickets
        tickets = []
        for bundle in bundles:
            bundle_tickets = bundle.support_tickets.all()
            if status_filter:
                bundle_tickets = bundle_tickets.filter(status=status_filter)
            
            for ticket in bundle_tickets:
                serializer = TicketSerializer(ticket)
                tickets.append({
                    'bundle_id': bundle.id,
                    'bundle_client': bundle.client.username if bundle.client else None,
                    'ticket': serializer.data
                })
        
        return Response({
            'tickets': tickets,
            'count': len(tickets)
        })


# Admin Tip Management ViewSet
class AdminTipManagementViewSet(viewsets.ViewSet):
    """Admin ViewSet for tip management and earnings tracking."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get tip statistics dashboard with earnings breakdown."""
        from writer_management.models.tipping import Tip
        from django.db.models import Count, Sum, Avg, Q
        from django.utils import timezone
        from datetime import timedelta
        from django.core.cache import cache
        import hashlib
        import json
        
        # Build cache key
        cache_params = {
            'user_id': request.user.id,
            'user_role': getattr(request.user, 'role', None),
            'website_id': getattr(request.user, 'website_id', None) if hasattr(request.user, 'website_id') else None,
            'days': request.query_params.get('days', '30'),
        }
        cache_key = f"tip_dashboard:{hashlib.md5(json.dumps(cache_params, sort_keys=True).encode()).hexdigest()}"
        
        # Try cache first (5 minute TTL)
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result)
        
        # Get all tips
        all_tips = Tip.objects.all().select_related(
            'client', 'writer', 'order', 'writer_level', 'website', 'payment'
        )
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                all_tips = all_tips.filter(website=website)
        
        # Date range filter with validation
        try:
            days = max(1, min(int(request.query_params.get('days', 30)), 365))
        except (ValueError, TypeError):
            days = 30
        date_from = timezone.now() - timedelta(days=days)
        recent_tips = all_tips.filter(sent_at__gte=date_from)
        
        # Total statistics - combined into single query
        total_stats = all_tips.aggregate(
            total_tips=Count('id'),
            total_tip_amount=Sum('tip_amount'),
            total_writer_earnings=Sum('writer_earning'),
            total_platform_profit=Sum('platform_profit'),
            avg_tip_amount=Avg('tip_amount'),
            avg_writer_percentage=Avg('writer_percentage')
        )
        
        # Recent statistics (last N days) - combined into single query
        recent_stats = recent_tips.aggregate(
            total_tips=Count('id'),
            total_tip_amount=Sum('tip_amount'),
            total_writer_earnings=Sum('writer_earning'),
            total_platform_profit=Sum('platform_profit')
        )
        
        # Tip type breakdown
        type_breakdown = all_tips.values('tip_type').annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit')
        )
        
        # Payment status breakdown
        payment_status_breakdown = all_tips.values('payment_status').annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount')
        )
        
        # Writer level breakdown
        level_breakdown = all_tips.filter(writer_level__isnull=False).values(
            'writer_level__name'
        ).annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit'),
            avg_percentage=Avg('writer_percentage')
        )
        
        # Payment status counts - combined into single query
        payment_status_counts = all_tips.values('payment_status').annotate(
            count=Count('id')
        )
        payment_status_dict = {item['payment_status']: item['count'] for item in payment_status_counts}
        
        response_data = {
            'summary': {
                'total_tips': total_stats['total_tips'] or 0,
                'total_tip_amount': float(total_stats['total_tip_amount'] or 0),
                'total_writer_earnings': float(total_stats['total_writer_earnings'] or 0),
                'total_platform_profit': float(total_stats['total_platform_profit'] or 0),
                'avg_tip_amount': float(total_stats['avg_tip_amount'] or 0),
                'avg_writer_percentage': float(total_stats['avg_writer_percentage'] or 0),
            },
            'recent_summary': {
                'days': days,
                'total_tips': recent_stats['total_tips'] or 0,
                'total_tip_amount': float(recent_stats['total_tip_amount'] or 0),
                'total_writer_earnings': float(recent_stats['total_writer_earnings'] or 0),
                'total_platform_profit': float(recent_stats['total_platform_profit'] or 0),
            },
            'payment_status': {
                'completed': payment_status_dict.get('completed', 0),
                'pending': payment_status_dict.get('pending', 0),
                'processing': payment_status_dict.get('processing', 0),
                'failed': payment_status_dict.get('failed', 0),
            },
            'type_breakdown': list(type_breakdown),
            'payment_status_breakdown': list(payment_status_breakdown),
            'level_breakdown': list(level_breakdown),
        }
        
        # Cache the result for 5 minutes
        cache.set(cache_key, response_data, 300)
        
        return Response(response_data)
    
    @action(detail=False, methods=['get'])
    def list_tips(self, request):
        """List all tips with earnings breakdown."""
        from writer_management.models.tipping import Tip
        from writer_management.serializers import TipDetailSerializer
        from django.db.models import Q, Sum, Count
        
        queryset = Tip.objects.all().select_related(
            'client', 'writer', 'order', 'writer_level', 'website', 'payment'
        )
        
        # Filter by website if user has website context and is not superadmin
        if request.user.role != 'superadmin':
            website = getattr(request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Filter by tip type
        tip_type = request.query_params.get('tip_type')
        if tip_type:
            queryset = queryset.filter(tip_type=tip_type)
        
        # Filter by payment status
        payment_status = request.query_params.get('payment_status')
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)
        
        # Filter by writer
        writer_id = request.query_params.get('writer_id')
        if writer_id:
            queryset = queryset.filter(writer_id=writer_id)
        
        # Filter by client
        client_id = request.query_params.get('client_id')
        if client_id:
            queryset = queryset.filter(client_id=client_id)
        
        # Filter by date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(sent_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(sent_at__lte=date_to)
        
        # Order by most recent first
        queryset = queryset.order_by('-sent_at')
        
        # Pagination with validation and max limit
        try:
            limit = min(max(1, int(request.query_params.get('limit', 50))), 1000)
        except (ValueError, TypeError):
            limit = 50
        try:
            offset = max(0, int(request.query_params.get('offset', 0)))
        except (ValueError, TypeError):
            offset = 0
        
        # Get summary statistics before pagination (combined query)
        summary = queryset.aggregate(
            total_count=Count('id'),
            total_tip_amount=Sum('tip_amount'),
            total_writer_earnings=Sum('writer_earning'),
            total_platform_profit=Sum('platform_profit')
        )
        
        # Apply pagination
        tips = queryset[offset:offset + limit]
        
        serializer = TipDetailSerializer(tips, many=True, context={'request': request})
        
        return Response({
            'count': summary['total_count'] or 0,
            'results': serializer.data,
            'summary': {
                'total_tip_amount': float(summary['total_tip_amount'] or 0),
                'total_writer_earnings': float(summary['total_writer_earnings'] or 0),
                'total_platform_profit': float(summary['total_platform_profit'] or 0),
            }
        })
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        """Get tip analytics with trends and breakdowns."""
        from writer_management.models.tipping import Tip
        from django.db.models import Count, Sum, Avg
        from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all tips
        all_tips = Tip.objects.all().select_related(
            'client', 'writer', 'order', 'writer_level', 'website'
        )
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_tips = all_tips.filter(website=website)
        
        # Date range with validation
        try:
            days = max(1, min(int(request.query_params.get('days', 90)), 365))
        except (ValueError, TypeError):
            days = 90
        date_from = timezone.now() - timedelta(days=days)
        filtered_tips = all_tips.filter(sent_at__gte=date_from)
        
        # Monthly trends
        monthly_trends = filtered_tips.annotate(
            month=TruncMonth('sent_at')
        ).values('month').annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit')
        ).order_by('month')
        
        # Weekly trends
        weekly_trends = filtered_tips.annotate(
            week=TruncWeek('sent_at')
        ).values('week').annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit')
        ).order_by('-week')[:12]  # Last 12 weeks
        
        # Daily trends (last 30 days)
        daily_trends = filtered_tips.filter(
            sent_at__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            day=TruncDay('sent_at')
        ).values('day').annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit')
        ).order_by('-day')[:30]
        
        # Tip type breakdown
        type_breakdown = filtered_tips.values('tip_type').annotate(
            count=Count('id'),
            total_amount=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit'),
            avg_amount=Avg('tip_amount')
        )
        
        # Top writers by tips received
        top_writers = filtered_tips.values(
            'writer__id', 'writer__username', 'writer__email'
        ).annotate(
            tip_count=Count('id'),
            total_received=Sum('writer_earning'),
            avg_tip=Avg('writer_earning')
        ).order_by('-total_received')[:10]
        
        # Top clients by tips sent
        top_clients = filtered_tips.values(
            'client__id', 'client__username', 'client__email'
        ).annotate(
            tip_count=Count('id'),
            total_sent=Sum('tip_amount')
        ).order_by('-total_sent')[:10]
        
        # Writer level performance
        level_performance = filtered_tips.filter(
            writer_level__isnull=False
        ).values('writer_level__name').annotate(
            tip_count=Count('id'),
            total_tips=Sum('tip_amount'),
            total_writer_earnings=Sum('writer_earning'),
            total_platform_profit=Sum('platform_profit'),
            avg_percentage=Avg('writer_percentage')
        ).order_by('-total_tips')
        
        return Response({
            'period': {
                'days': days,
                'date_from': date_from,
            },
            'trends': {
                'monthly': list(monthly_trends),
                'weekly': list(weekly_trends),
                'daily': list(daily_trends),
            },
            'breakdowns': {
                'by_type': list(type_breakdown),
                'by_level': list(level_performance),
            },
            'top_performers': {
                'writers': list(top_writers),
                'clients': list(top_clients),
            },
        })
    
    @action(detail=False, methods=['get'], url_path='earnings')
    def earnings(self, request):
        """Get detailed earnings breakdown."""
        from writer_management.models.tipping import Tip
        from django.db.models import Sum, Avg, Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Get all tips
        all_tips = Tip.objects.all().select_related(
            'client', 'writer', 'writer_level', 'website'
        )
        
        # Filter by website if user has website context
        website = getattr(request.user, 'website', None)
        if website:
            all_tips = all_tips.filter(website=website)
        
        # Date range filter
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            all_tips = all_tips.filter(sent_at__gte=date_from)
        if date_to:
            all_tips = all_tips.filter(sent_at__lte=date_to)
        
        # Only completed tips for earnings
        completed_tips = all_tips.filter(payment_status='completed')
        
        # Overall earnings
        overall = completed_tips.aggregate(
            total_tips=Count('id'),
            total_tip_amount=Sum('tip_amount'),
            total_writer_earnings=Sum('writer_earning'),
            total_platform_profit=Sum('platform_profit'),
            avg_tip_amount=Avg('tip_amount'),
            avg_writer_percentage=Avg('writer_percentage')
        )
        
        # Earnings by writer level
        earnings_by_level = completed_tips.filter(
            writer_level__isnull=False
        ).values('writer_level__name').annotate(
            tip_count=Count('id'),
            total_tips=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit'),
            avg_percentage=Avg('writer_percentage')
        ).order_by('-total_tips')
        
        # Earnings by tip type
        earnings_by_type = completed_tips.values('tip_type').annotate(
            tip_count=Count('id'),
            total_tips=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit')
        )
        
        # Monthly earnings (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        monthly_earnings = completed_tips.filter(
            sent_at__gte=twelve_months_ago
        ).extra(
            select={'month': "DATE_TRUNC('month', sent_at)"}
        ).values('month').annotate(
            tip_count=Count('id'),
            total_tips=Sum('tip_amount'),
            writer_earnings=Sum('writer_earning'),
            platform_profit=Sum('platform_profit')
        ).order_by('-month')[:12]
        
        return Response({
            'overall': {
                'total_tips': overall['total_tips'] or 0,
                'total_tip_amount': float(overall['total_tip_amount'] or 0),
                'total_writer_earnings': float(overall['total_writer_earnings'] or 0),
                'total_platform_profit': float(overall['total_platform_profit'] or 0),
                'avg_tip_amount': float(overall['avg_tip_amount'] or 0),
                'avg_writer_percentage': float(overall['avg_writer_percentage'] or 0),
                'platform_profit_percentage': float(
                    (overall['total_platform_profit'] or 0) / (overall['total_tip_amount'] or 1) * 100
                ) if overall['total_tip_amount'] else 0,
            },
            'by_level': list(earnings_by_level),
            'by_type': list(earnings_by_type),
            'monthly': list(monthly_earnings),
        })
