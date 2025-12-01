from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import F, Q, Count
from .models import (
    SupportProfile, SupportNotification, SupportOrderManagement,
    SupportMessage, SupportGlobalAccess, SupportPermission,
    DisputeResolutionLog, SupportActionLog, EscalationLog, 
    SupportAvailability, SupportActivityLog, PaymentIssueLog,
    SupportOrderFileManagement, WriterPerformanceLog,
    SupportWorkloadTracker, OrderDisputeSLA, FAQCategory, FAQManagement,
    SupportDashboard
)
from .serializers import (
    SupportProfileSerializer, SupportNotificationSerializer, 
    SupportOrderManagementSerializer, SupportMessageSerializer, 
    SupportGlobalAccessSerializer, SupportPermissionSerializer, 
    DisputeResolutionLogSerializer, SupportActionLogSerializer, 
    EscalationLogSerializer, SupportAvailabilitySerializer, 
    SupportActivityLogSerializer, PaymentIssueLogSerializer,
    SupportOrderFileManagementSerializer, WriterPerformanceLogSerializer, 
    SupportWorkloadTrackerSerializer, OrderDisputeSLASerializer, 
    FAQCategorySerializer, FAQManagementSerializer, 
    SupportDashboardSerializer
)
from .permissions import (
    IsSupportAgent, IsAdminOrSuperAdmin, CanManageOrders, 
    CanHandleDisputes, CanRecommendBlacklist, CanModerateMessages, 
    CanManageWriterPerformance, CanEscalateIssues, CanAccessSupportDashboard
)

# 🚀 **1️⃣ Support Profile ViewSet**
class SupportProfileViewSet(viewsets.ModelViewSet):
    queryset = SupportProfile.objects.all()
    serializer_class = SupportProfileSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        """Admins can view all support profiles, support can view their own."""
        if self.request.user.role == "support":
            return SupportProfile.objects.filter(user=self.request.user)
        return super().get_queryset()


# 🚀 **2️⃣ Support Notifications ViewSet**
class SupportNotificationViewSet(viewsets.ModelViewSet):
    queryset = SupportNotification.objects.all()
    serializer_class = SupportNotificationSerializer
    permission_classes = [IsSupportAgent]

    def get_queryset(self):
        return SupportNotification.objects.filter(support_staff=self.request.user.support_profile)

    @action(detail=False, methods=["post"])
    def mark_as_read(self, request):
        """Marks all notifications as read for the current support agent."""
        notifications = self.get_queryset()
        notifications.update(is_read=True)
        return Response({"message": "Notifications marked as read."}, status=status.HTTP_200_OK)


# 🚀 **3️⃣ Support Order Management ViewSet**
class SupportOrderManagementViewSet(viewsets.ModelViewSet):
    queryset = SupportOrderManagement.objects.all()
    serializer_class = SupportOrderManagementSerializer
    permission_classes = [CanManageOrders]

    @action(detail=True, methods=["post"])
    def restore_to_progress(self, request, pk=None):
        """Restores an order back to progress."""
        instance = self.get_object()
        instance.restore_order_progress()
        return Response({"message": "Order restored to progress."}, status=status.HTTP_200_OK)


# 🚀 **4️⃣ Support Messages ViewSet**
class SupportMessageViewSet(viewsets.ModelViewSet):
    queryset = SupportMessage.objects.all()
    serializer_class = SupportMessageSerializer
    permission_classes = [CanModerateMessages]

    def get_queryset(self):
        """Support can see only their messages or those they moderate."""
        return SupportMessage.objects.filter(sender=self.request.user) | \
               SupportMessage.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=["post"])
    def flag_message(self, request, pk=None):
        """Flags a message as inappropriate."""
        instance = self.get_object()
        instance.flag_message()
        return Response({"message": "Message flagged for review."}, status=status.HTTP_200_OK)


# 🚀 **5️⃣ Escalation Log ViewSet**
class EscalationLogViewSet(viewsets.ModelViewSet):
    queryset = EscalationLog.objects.all()
    serializer_class = EscalationLogSerializer
    permission_classes = [CanEscalateIssues]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approves an escalation request."""
        instance = self.get_object()
        if request.user.role in ["admin", "superadmin"]:
            instance.approve(admin=request.user)
            return Response({"message": "Escalation approved."}, status=status.HTTP_200_OK)
        return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


# 🚀 **6️⃣ Support Workload Tracker ViewSet**
class SupportWorkloadTrackerViewSet(viewsets.ModelViewSet):
    queryset = SupportWorkloadTracker.objects.all()
    serializer_class = SupportWorkloadTrackerSerializer
    permission_classes = [IsAdminOrSuperAdmin]


# 🚀 **7️⃣ Payment Issue Log ViewSet**
class PaymentIssueLogViewSet(viewsets.ModelViewSet):
    queryset = PaymentIssueLog.objects.all()
    serializer_class = PaymentIssueLogSerializer
    permission_classes = [IsSupportAgent]

    @action(detail=True, methods=["post"])
    def escalate_issue(self, request, pk=None):
        """Escalates a payment issue to an admin."""
        instance = self.get_object()
        instance.escalate_issue(admin=request.user)
        return Response({"message": "Payment issue escalated."}, status=status.HTTP_200_OK)


# 🚀 **8️⃣ FAQ Management ViewSet**
class FAQManagementViewSet(viewsets.ModelViewSet):
    queryset = FAQManagement.objects.all()
    serializer_class = FAQManagementSerializer
    permission_classes = [IsSupportAgent]


# 🚀 **9️⃣ Support Dashboard ViewSet**
class SupportDashboardViewSet(viewsets.ModelViewSet):
    queryset = SupportDashboard.objects.all()
    serializer_class = SupportDashboardSerializer
    permission_classes = [CanAccessSupportDashboard]

    @action(detail=False, methods=["post"])
    def refresh_dashboard(self, request):
        """Refreshes all support dashboards."""
        SupportDashboard.refresh_all_dashboards()
        return Response({"message": "Support dashboards refreshed."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["get"], url_path="tickets")
    def dashboard_tickets(self, request):
        """Get recent and active tickets for support dashboard."""
        from tickets.models import Ticket
        from tickets.serializers import TicketSerializer
        from django.utils import timezone
        from datetime import timedelta
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get query parameters
        limit = int(request.query_params.get('limit', 20))
        status_filter = request.query_params.get('status', None)
        priority_filter = request.query_params.get('priority', None)
        
        # Get tickets
        if request.user.role == "support":
            # Support can see assigned tickets and unassigned tickets
            tickets = Ticket.objects.filter(
                Q(assigned_to=request.user) | Q(assigned_to__isnull=True)
            ).select_related('created_by', 'assigned_to', 'website').order_by('-created_at')
        else:
            # Admins can see all tickets
            tickets = Ticket.objects.all().select_related('created_by', 'assigned_to', 'website').order_by('-created_at')
        
        # Filter by status if provided
        if status_filter:
            tickets = tickets.filter(status=status_filter)
        
        # Filter by priority if provided
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter)
        
        # Limit results
        tickets = tickets[:limit]
        
        serializer = TicketSerializer(tickets, many=True)
        return Response({
            'tickets': serializer.data,
            'count': len(serializer.data),
            'total_open': Ticket.objects.filter(status__in=['open', 'in_progress']).count(),
            'total_assigned_to_me': Ticket.objects.filter(assigned_to=request.user).count() if request.user.role == "support" else None,
        })
    
    @action(detail=False, methods=["get"], url_path="queue")
    def dashboard_queue(self, request):
        """Get ticket queue with filters for support dashboard."""
        from tickets.models import Ticket
        from tickets.serializers import TicketSerializer
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get unassigned tickets
        unassigned = Ticket.objects.filter(
            assigned_to__isnull=True,
            status__in=['open', 'in_progress']
        ).select_related('created_by', 'website').order_by('-priority', '-created_at')
        
        # Get my assigned tickets
        my_assigned = Ticket.objects.filter(
            assigned_to=request.user,
            status__in=['open', 'in_progress']
        ).select_related('created_by', 'website').order_by('-priority', '-created_at')
        
        # Get high priority tickets
        high_priority = Ticket.objects.filter(
            priority__in=['high', 'critical'],
            status__in=['open', 'in_progress']
        ).select_related('created_by', 'assigned_to', 'website').order_by('-priority', '-created_at')
        
        # Get overdue tickets (open for more than 24 hours)
        from django.utils import timezone
        from datetime import timedelta
        overdue_threshold = timezone.now() - timedelta(hours=24)
        overdue = Ticket.objects.filter(
            status__in=['open', 'in_progress'],
            created_at__lt=overdue_threshold
        ).select_related('created_by', 'assigned_to', 'website').order_by('-created_at')
        
        return Response({
            'unassigned_tickets': TicketSerializer(unassigned[:20], many=True).data,
            'my_assigned_tickets': TicketSerializer(my_assigned[:20], many=True).data,
            'high_priority_tickets': TicketSerializer(high_priority[:20], many=True).data,
            'overdue_tickets': TicketSerializer(overdue[:20], many=True).data,
            'counts': {
                'unassigned': unassigned.count(),
                'my_assigned': my_assigned.count(),
                'high_priority': high_priority.count(),
                'overdue': overdue.count(),
            }
        })
    
    @action(detail=False, methods=["get"], url_path="workload")
    def dashboard_workload(self, request):
        """Get workload tracking for support dashboard."""
        from tickets.models import Ticket, TicketMessage
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Avg, Count, Q
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or create workload tracker
        workload_tracker, _ = SupportWorkloadTracker.objects.get_or_create(
            support_staff=request.user
        )
        
        # Get current ticket load
        current_tickets = Ticket.objects.filter(
            assigned_to=request.user,
            status__in=['open', 'in_progress']
        )
        
        # Calculate average response time (time to first response)
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        recent_tickets = Ticket.objects.filter(
            assigned_to=request.user,
            created_at__gte=week_ago
        )
        
        # Get tickets with messages to calculate response time
        tickets_with_messages = recent_tickets.filter(messages__isnull=False).distinct()
        
        response_times = []
        for ticket in tickets_with_messages:
            first_message = ticket.messages.filter(sender=request.user).order_by('created_at').first()
            if first_message and ticket.created_at:
                response_time = (first_message.created_at - ticket.created_at).total_seconds() / 3600  # hours
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else None
        
        # Resolution rate (last 30 days)
        month_ago = timezone.now() - timedelta(days=30)
        resolved_tickets = Ticket.objects.filter(
            assigned_to=request.user,
            status='closed',
            updated_at__gte=month_ago
        ).count()
        
        total_tickets = Ticket.objects.filter(
            assigned_to=request.user,
            created_at__gte=month_ago
        ).count()
        
        resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
        
        # Tickets resolved today
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        resolved_today = Ticket.objects.filter(
            assigned_to=request.user,
            status='closed',
            updated_at__gte=today_start
        ).count()
        
        # SLA compliance (tickets resolved within 24 hours)
        sla_compliant = Ticket.objects.filter(
            assigned_to=request.user,
            status='closed',
            created_at__gte=month_ago
        ).annotate(
            resolution_time=timezone.now() - F('created_at')
        ).filter(
            resolution_time__lte=timedelta(hours=24)
        ).count()
        
        sla_compliance_rate = (sla_compliant / resolved_tickets * 100) if resolved_tickets > 0 else 0
        
        return Response({
            'current_ticket_load': current_tickets.count(),
            'average_response_time_hours': avg_response_time,
            'resolution_rate_percent': resolution_rate,
            'tickets_resolved_today': resolved_today,
            'tickets_resolved_this_week': Ticket.objects.filter(
                assigned_to=request.user,
                status='closed',
                updated_at__gte=week_ago
            ).count(),
            'tickets_resolved_this_month': resolved_tickets,
            'sla_compliance_rate_percent': sla_compliance_rate,
            'workload_tracker': {
                'tickets_handled': workload_tracker.tickets_handled,
                'disputes_handled': workload_tracker.disputes_handled,
                'orders_managed': workload_tracker.orders_managed,
                'last_activity': workload_tracker.last_activity.isoformat() if workload_tracker.last_activity else None,
            }
        })
    
    @action(detail=False, methods=["get"], url_path="analytics/performance")
    def analytics_performance(self, request):
        """Get performance analytics for support team or individual agent."""
        from .services.analytics_service import SupportAnalyticsService
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        support_user = request.user if request.user.role == "support" else None
        
        service = SupportAnalyticsService(support_user=support_user, days=days)
        analytics = service.get_performance_analytics()
        
        return Response(analytics)
    
    @action(detail=False, methods=["get"], url_path="analytics/trends")
    def analytics_trends(self, request):
        """Get trend analytics (weekly breakdown)."""
        from .services.analytics_service import SupportAnalyticsService
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        support_user = request.user if request.user.role == "support" else None
        
        service = SupportAnalyticsService(support_user=support_user, days=days)
        trends = service.get_trend_analytics()
        
        return Response({'trends': trends})
    
    @action(detail=False, methods=["get"], url_path="analytics/comparison")
    def analytics_comparison(self, request):
        """Compare performance across all support agents."""
        from .services.analytics_service import SupportAnalyticsService
        
        if request.user.role not in ["admin", "superadmin"]:
            return Response(
                {"detail": "Only admins can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        service = SupportAnalyticsService(days=days)
        comparison = service.get_agent_comparison()
        
        return Response({'comparison': comparison})
    
    @action(detail=False, methods=["get"], url_path="analytics/sla")
    def analytics_sla(self, request):
        """Get SLA compliance analytics."""
        from .services.analytics_service import SupportAnalyticsService
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        support_user = request.user if request.user.role == "support" else None
        
        service = SupportAnalyticsService(support_user=support_user, days=days)
        sla_analytics = service.get_sla_analytics()
        
        return Response(sla_analytics)
    
    @action(detail=False, methods=["get"], url_path="analytics/workload")
    def analytics_workload(self, request):
        """Get workload distribution across support team."""
        from .services.analytics_service import SupportAnalyticsService
        
        if request.user.role not in ["admin", "superadmin"]:
            return Response(
                {"detail": "Only admins can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        service = SupportAnalyticsService(days=days)
        distribution = service.get_workload_distribution()
        
        return Response({'distribution': distribution})
    
    @action(detail=False, methods=["get"], url_path="performance/metrics")
    def performance_metrics(self, request):
        """Get performance metrics for current support agent."""
        from .services.performance_service import SupportPerformanceService
        
        if request.user.role != "support":
            return Response(
                {"detail": "Only support agents can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        service = SupportPerformanceService(support_user=request.user, days=days)
        metrics = service.get_performance_metrics()
        
        return Response(metrics)
    
    @action(detail=False, methods=["get"], url_path="performance/trends")
    def performance_trends(self, request):
        """Get performance trends for current support agent."""
        from .services.performance_service import SupportPerformanceService
        
        if request.user.role != "support":
            return Response(
                {"detail": "Only support agents can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        days = int(request.query_params.get('days', 30))
        service = SupportPerformanceService(support_user=request.user, days=days)
        trends = service.get_performance_trends()
        
        return Response({'trends': trends})
    
    @action(detail=False, methods=["get"], url_path="sla/breaches")
    def sla_breaches(self, request):
        """Get all SLA breaches."""
        from .models import OrderDisputeSLA
        from .serializers import OrderDisputeSLASerializer
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filter by assigned agent if support, show all if admin
        if request.user.role == "support":
            breaches = OrderDisputeSLA.objects.filter(
                assigned_to=request.user,
                sla_breached=True,
                actual_resolution_time__isnull=True
            )
        else:
            breaches = OrderDisputeSLA.objects.filter(
                sla_breached=True,
                actual_resolution_time__isnull=True
            )
        
        serializer = OrderDisputeSLASerializer(breaches, many=True)
        return Response({
            'breaches': serializer.data,
            'count': breaches.count()
        })
    
    @action(detail=False, methods=["get"], url_path="orders")
    def dashboard_orders(self, request):
        """Get order management dashboard for support."""
        from orders.models import Order
        from orders.order_enums import OrderStatus
        from orders.serializers import OrderSerializer
        from refunds.models import Refund
        from django.db.models import Q, Count
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Orders requiring support attention
        disputed_orders = Order.objects.filter(
            status=OrderStatus.DISPUTED.value
        ).select_related('client', 'writer', 'website')
        
        # Payment issues
        payment_issue_orders = Order.objects.filter(
            Q(payment_status='failed') | Q(payment_status='pending'),
            status__in=[OrderStatus.PENDING_PAYMENT.value, OrderStatus.PAYMENT_FAILED.value]
        ).select_related('client', 'writer', 'website')
        
        # Refund requests
        pending_refunds = Refund.objects.filter(
            status='pending'
        ).select_related('order', 'order__client')
        
        # Orders with support tickets
        from tickets.models import Ticket
        orders_with_tickets = Order.objects.filter(
            tickets__isnull=False
        ).distinct().select_related('client', 'writer', 'website')
        
        return Response({
            'disputed_orders': {
                'count': disputed_orders.count(),
                'orders': OrderSerializer(disputed_orders[:10], many=True).data,
            },
            'payment_issue_orders': {
                'count': payment_issue_orders.count(),
                'orders': OrderSerializer(payment_issue_orders[:10], many=True).data,
            },
            'pending_refunds': {
                'count': pending_refunds.count(),
                'refunds': [
                    {
                        'id': refund.id,
                        'order_id': refund.order.id if refund.order else None,
                        'amount': str(refund.amount),
                        'reason': refund.reason,
                        'status': refund.status,
                        'created_at': refund.created_at.isoformat() if refund.created_at else None,
                    }
                    for refund in pending_refunds[:10]
                ],
            },
            'orders_with_tickets': {
                'count': orders_with_tickets.count(),
                'orders': OrderSerializer(orders_with_tickets[:10], many=True).data,
            },
            'summary': {
                'total_requiring_attention': (
                    disputed_orders.count() + 
                    payment_issue_orders.count() + 
                    pending_refunds.count()
                ),
            }
        })
    
    @action(detail=False, methods=["get"], url_path="escalations")
    def dashboard_escalations(self, request):
        """Get escalation management for support dashboard."""
        from .models import EscalationLog
        from .serializers import EscalationLogSerializer
        from django.db.models import Q
        
        if request.user.role not in ["support", "admin", "superadmin"]:
            return Response(
                {"detail": "Only support staff can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get escalated tickets
        if request.user.role == "support":
            escalations = EscalationLog.objects.filter(
                Q(escalated_to=request.user) | Q(escalated_by=request.user)
            ).select_related('ticket', 'escalated_by', 'escalated_to', 'resolved_by')
        else:
            escalations = EscalationLog.objects.all().select_related(
                'ticket', 'escalated_by', 'escalated_to', 'resolved_by'
            )
        
        # Filter by status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            escalations = escalations.filter(status=status_filter)
        
        # Get unresolved escalations
        unresolved = escalations.filter(status='pending')
        
        # Get resolved escalations
        resolved = escalations.filter(status='resolved')
        
        # Get escalation reasons breakdown
        reasons_breakdown = escalations.values('escalation_reason').annotate(
            count=Count('id')
        )
        
        return Response({
            'escalations': EscalationLogSerializer(escalations[:50], many=True).data,
            'unresolved_escalations': EscalationLogSerializer(unresolved[:20], many=True).data,
            'resolved_escalations': EscalationLogSerializer(resolved[:20], many=True).data,
            'counts': {
                'total': escalations.count(),
                'unresolved': unresolved.count(),
                'resolved': resolved.count(),
            },
            'reasons_breakdown': {
                item['escalation_reason']: item['count'] 
                for item in reasons_breakdown
            },
        })