from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from django.db import models  
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from .models import SuperadminProfile, SuperadminLog, Probation, Appeal
from .serializers import SuperadminProfileSerializer, UserSerializer, SuperadminLogSerializer, AppealSerializer
from .permissions import IsSuperadmin
from .managers import SuperadminManager
from .pagination import SuperadminPagination , SuperadminLogCursorPagination
from orders.models import Order, Dispute
from order_payments_management.models import OrderPayment
from notifications_system.models.notifications import Notification
from django_filters import rest_framework as filters
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from websites.models import Website
from tickets.models import Ticket
from writer_management.models.tipping import Tip


User = get_user_model()

### 🔹 1️⃣ Superadmin-Only View
class SuperadminOnlyView(APIView):
    """An example view that only Superadmins can access."""
    permission_classes = [IsAuthenticated, IsSuperadmin]

    def get(self, request):
        return Response({"message": "Welcome, Superadmin!"})

class UserFilter(filters.FilterSet):
    """Custom filtering for users."""
    is_active = filters.BooleanFilter(field_name="is_active")
    is_suspended = filters.BooleanFilter(field_name="is_suspended")

    class Meta:
        model = User
        fields = ["role", "is_suspended", "is_active", "date_joined"]

### 🔹 2️⃣ Superadmin Profile API
class SuperadminProfileViewSet(viewsets.ModelViewSet):
    """API for managing Superadmin Profiles with pagination."""
    queryset = SuperadminProfile.objects.all().order_by("-created_at")
    serializer_class = SuperadminProfileSerializer
    permission_classes = [IsSuperadmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter  # Custom filtering
    filterset_fields = ['user__username', 'user__email', 'role', 'email', 'created_at']
    pagination_class = SuperadminPagination  # Enable pagination


### 🔹 3️⃣ User Management API (Now Uses `ReadOnlyModelViewSet`)
class UserManagementViewSet(viewsets.ReadOnlyModelViewSet):
    """API for Superadmins to manage users with pagination."""
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsSuperadmin]
    pagination_class = SuperadminPagination  # Enable pagination
    filter_backends = [DjangoFilterBackend, SearchFilter]  # Added search filter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["role", "is_suspended", "date_joined"]
    search_fields = ["username", "email", "role"]  # Search enabled

    @action(detail=False, methods=['post'], url_path='create_user')
    def create_user(self, request):
        """Superadmin creates a user."""
        result = SuperadminManager.create_user(
            request.user,
            username=request.data.get("username"),
            email=request.data.get("email"),
            role=request.data.get("role"),
            phone_number=request.data.get("phone_number", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='suspend_user')
    def suspend_user(self, request):
        """Superadmin suspends a user."""
        user = User.objects.filter(pk=request.data.get("user_id")).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        result = SuperadminManager.suspend_user(request.user, user, request.data.get("reason", "No reason provided"))
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='reactivate_user')
    def reactivate_user(self, request):
        """Superadmin reactivates a user."""
        user = User.objects.filter(pk=request.data.get("user_id")).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        result = SuperadminManager.reactivate_user(request.user, user)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='change_user_role')
    def change_user_role(self, request):
        """Superadmin changes a user's role."""
        user = User.objects.filter(pk=request.data.get("user_id")).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        result = SuperadminManager.change_user_role(request.user, user, request.data.get("new_role"))
        return Response(result, status=status.HTTP_200_OK)


### 🔹 4️⃣ Superadmin Logs API (Now Paginated)
class SuperadminLogViewSet(viewsets.ModelViewSet):
    """API for retrieving Superadmin logs with pagination."""
    queryset = SuperadminLog.objects.all().order_by("-timestamp")
    serializer_class = SuperadminLogSerializer
    permission_classes = [IsSuperadmin]
    pagination_class = SuperadminLogCursorPagination  # Now uses CursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["action_type", "timestamp", "superadmin__username"]


### 🔹 5️⃣ Superadmin Dashboard (Web Interface)

class SuperadminDashboardViewSet(viewsets.ViewSet):
    """API view for Superadmin Dashboard statistics."""
    permission_classes = [IsSuperadmin]

    def list(self, request):
        """Fetch statistics, using caching."""
        cache_key = "superadmin_dashboard_stats"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        data = self.generate_dashboard_data()
        cache.set(cache_key, data, timeout=600)  # Cache for 10 minutes
        return Response(data, status=status.HTTP_200_OK)

    def generate_dashboard_data(self):
        """Generates comprehensive dashboard data."""
        from django.db.models import Avg, Max, Min
        
        # User Statistics
        user_stats = User.objects.aggregate(
            total_users=Count("id"),
            total_admins=Count("id", filter=Q(role="admin")),
            total_support=Count("id", filter=Q(role="support")),
            total_editors=Count("id", filter=Q(role="editor")),
            total_writers=Count("id", filter=Q(role="writer")),
            total_clients=Count("id", filter=Q(role="client")),
            suspended_users=Count("id", filter=Q(is_suspended=True)),
            active_users=Count("id", filter=Q(is_active=True)),
        )
        
        # Financial Statistics
        financial_stats = OrderPayment.objects.aggregate(
            total_revenue=Sum("amount", default=0),
            pending_payouts=Sum("amount", filter=Q(status="pending"), default=0),
            completed_payments=Sum("amount", filter=Q(status="completed"), default=0),
            failed_payments=Count("id", filter=Q(status="failed")),
        )
        
        total_refunds = OrderPayment.objects.filter(status="refunded").aggregate(Sum("amount"))["amount__sum"] or 0
        
        # Order Statistics
        order_stats = Order.objects.aggregate(
            total_orders=Count("id"),
            in_progress=Count("id", filter=Q(status="in_progress")),
            completed=Count("id", filter=Q(status="completed")),
            disputed=Count("id", filter=Q(status="disputed")),
            canceled=Count("id", filter=Q(status="canceled")),
            pending=Count("id", filter=Q(status="pending")),
            submitted=Count("id", filter=Q(status="submitted")),
            available=Count("id", filter=Q(status="available")),
            avg_order_value=Avg("total_price", filter=Q(is_paid=True)),
            total_revenue_orders=Sum("total_price", filter=Q(is_paid=True), default=0),
        )
        
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
        top_writers = User.objects.filter(
            role="writer",
            orders_as_writer__status="completed"
        ).annotate(
            completed_orders_count=Count("orders_as_writer", filter=Q(orders_as_writer__status="completed")),
            total_earnings=Sum("orders_as_writer__writer_compensation", filter=Q(orders_as_writer__status="completed"), default=0),
        ).order_by("-completed_orders_count")[:10]
        
        top_writers_data = [
            {
                "id": writer.id,
                "username": writer.username,
                "email": writer.email,
                "completed_orders": writer.completed_orders_count,
                "total_earnings": float(writer.total_earnings) if writer.total_earnings else 0.0,
            }
            for writer in top_writers
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
        
        # Website Statistics
        website_stats = Website.objects.annotate(
            order_count=Count("order"),
            user_count=Count("website_users"),
            total_revenue=Sum("order__total_price", filter=Q(order__is_paid=True), default=0),
        ).values("id", "name", "domain", "is_active", "order_count", "user_count", "total_revenue")[:10]
        
        website_stats_data = [
            {
                "id": ws["id"],
                "name": ws["name"],
                "domain": ws["domain"],
                "is_active": ws["is_active"],
                "order_count": ws["order_count"],
                "user_count": ws["user_count"],
                "total_revenue": float(ws["total_revenue"]) if ws["total_revenue"] else 0.0,
            }
            for ws in website_stats
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
        
        # Dispute Statistics
        dispute_stats = Dispute.objects.aggregate(
            total_disputes=Count("id"),
            resolved_disputes=Count("id", filter=Q(dispute_status="resolved")),
            pending_disputes=Count("id", filter=Q(dispute_status="open")),
            in_progress_disputes=Count("id", filter=Q(dispute_status="in_review")),
        )
        
        # Ticket Statistics
        ticket_stats = Ticket.objects.aggregate(
            total_tickets=Count("id"),
            open_tickets=Count("id", filter=Q(status__in=["open", "pending"])),
            closed_tickets=Count("id", filter=Q(status="closed")),
        )
        
        # Tip Statistics
        tip_stats = Tip.objects.aggregate(
            total_tips=Count("id"),
            total_tip_amount=Sum("tip_amount", default=0),
            completed_tips=Count("id", filter=Q(payment_status="completed")),
        )
        
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
        
        return {
            **user_stats,
            **financial_stats,
            "total_refunds": float(total_refunds),
            **order_stats,
            **dispute_stats,
            **ticket_stats,
            "tip_stats": {
                "total_tips": tip_stats["total_tips"],
                "total_tip_amount": float(tip_stats["total_tip_amount"]) if tip_stats["total_tip_amount"] else 0.0,
                "completed_tips": tip_stats["completed_tips"],
            },
            "recent_orders": recent_orders_data,
            "top_writers": top_writers_data,
            "top_clients": top_clients_data,
            "website_stats": website_stats_data,
            "revenue_trends": revenue_trends_data,
            "system_health": system_health,
        }



    def superadmin_dashboard(request):
        """Superadmin Dashboard - Displays key system metrics."""
        
        user_stats = User.objects.aggregate(
            total_users=Count("id"),
            total_admins=Count("id", filter=Q(role="admin")),
            total_support=Count("id", filter=Q(role="support")),
            total_editors=Count("id", filter=Q(role="editor")),
            total_writers=Count("id", filter=Q(role="writer")),
            total_clients=Count("id", filter=Q(role="client")),
            suspended_users=Count("id", filter=Q(is_suspended=True)),
        )

        financial_stats = OrderPayment.objects.aggregate(
            total_revenue=Sum("amount", default=0),
            pending_payouts=Sum("amount", filter=Q(status="pending"), default=0)
        )
        
        total_refunds = OrderPayment.objects.filter(status="refunded").aggregate(Sum("amount"))["amount__sum"] or 0


        order_stats = Order.objects.aggregate(
            total_orders=Count("id"),
            in_progress=Count("id", filter=Q(status="in_progress")),
            completed=Count("id", filter=Q(status="completed")),
            disputed=Count("id", filter=Q(status="disputed")),
            canceled=Count("id", filter=Q(status="canceled"))
        )

        dispute_stats = Dispute.objects.aggregate(
            total_disputes=Count("id"),
            resolved_disputes=Count("id", filter=Q(dispute_status="resolved"))
        )

        # Fetch all unread notifications for Superadmins
        notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')

        context = {
            **user_stats,
            **financial_stats,
            "total_refunds": total_refunds,
            **order_stats,
            **dispute_stats,
            "recent_logs": SuperadminLog.objects.order_by("-timestamp")[:10],
            "notifications": notifications,
        }

        return render(request, "superadmin_dashboard.html", context)


### 🔹 6️⃣ Appeal Management ViewSet
class AppealViewSet(viewsets.ModelViewSet):
    """API for managing user appeals (probation, blacklist, suspension)."""
    queryset = Appeal.objects.all().select_related(
        'user', 'reviewed_by'
    ).order_by('-submitted_at')
    serializer_class = AppealSerializer
    permission_classes = [IsSuperadmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'appeal_type', 'user']
    search_fields = ['user__username', 'user__email', 'reason']
    ordering_fields = ['submitted_at', 'status']
    ordering = ['-submitted_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve an appeal."""
        appeal = self.get_object()
        
        if appeal.status != 'pending':
            return Response(
                {"error": "Appeal has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appeal.status = 'approved'
        appeal.reviewed_by = request.user
        appeal.save()
        
        # Handle appeal type-specific actions
        if appeal.appeal_type == 'probation':
            # Remove from probation
            from writer_management.models.discipline import Probation
            Probation.objects.filter(
                writer__user=appeal.user,
                is_active=True
            ).update(is_active=False)
        elif appeal.appeal_type == 'blacklist':
            # Remove from blacklist
            from writer_management.models.discipline import WriterBlacklist
            WriterBlacklist.objects.filter(
                writer__user=appeal.user,
                is_active=True
            ).update(is_active=False)
        elif appeal.appeal_type == 'suspension':
            # Lift suspension
            from writer_management.models.discipline import WriterSuspension
            WriterSuspension.objects.filter(
                writer__user=appeal.user,
                is_active=True
            ).update(is_active=False)
        
        # Log the action
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="Appeal Approved",
            action_details=f"Approved {appeal.appeal_type} appeal for {appeal.user.username}"
        )
        
        return Response(
            {"message": "Appeal approved successfully."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject an appeal."""
        appeal = self.get_object()
        
        if appeal.status != 'pending':
            return Response(
                {"error": "Appeal has already been reviewed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appeal.status = 'rejected'
        appeal.reviewed_by = request.user
        appeal.save()
        
        # Log the action
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="Appeal Rejected",
            action_details=f"Rejected {appeal.appeal_type} appeal for {appeal.user.username}"
        )
        
        return Response(
            {"message": "Appeal rejected."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending appeals."""
        appeals = self.queryset.filter(status='pending')
        serializer = self.get_serializer(appeals, many=True)
        return Response(serializer.data)