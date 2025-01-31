from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import render
from .models import AdminProfile, AdminLog
from .serializers import AdminProfileSerializer, AdminLogSerializer
from .managers import AdminManager
from .permissions import IsAdmin
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from .models import AdminProfile, AdminLog
from orders.models import Order
from client_management.models import PaymentTransaction, Refund
from orders.models import Dispute
from .serializers import DashboardSerializer


User = get_user_model()
class AdminDashboardView(viewsets.ViewSet):
    """Admin Dashboard - Displays key statistics."""

    permission_classes = [IsAdmin]

    def dashboard(self, request):
        """Returns dashboard data for Admins."""
        total_writers = AdminProfile.objects.filter(can_manage_writers=True).count()
        total_editors = AdminProfile.objects.filter(can_manage_editors=True).count()
        total_support = AdminProfile.objects.filter(can_manage_support=True).count()

        logs = AdminLog.objects.order_by("-timestamp")[:10]

        return Response({
            "total_writers": total_writers,
            "total_editors": total_editors,
            "total_support": total_support,
            "recent_logs": [log.action for log in logs]
        }, status=status.HTTP_200_OK)

class UserManagementView(viewsets.ViewSet):
    """Admin manages users (create, suspend, reactivate)."""
    
    permission_classes = [IsAdmin]

    def create_user(self, request):
        """Admin creates a new user."""
        admin = request.user
        result = AdminManager.create_user(
            admin,
            username=request.data.get("username"),
            email=request.data.get("email"),
            role=request.data.get("role"),
            phone_number=request.data.get("phone_number", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)

    def suspend_user(self, request):
        """Admin suspends a user."""
        admin = request.user
        user = User.objects.get(pk=request.data.get("user_id"))
        result = AdminManager.suspend_user(admin, user, request.data.get("reason", "No reason provided"))
        return Response(result, status=status.HTTP_200_OK)
    

class AdminDashboardView(viewsets.ViewSet):
    """
    Admin Dashboard - Provides statistics on users, orders, disputes, and financials.
    """

    permission_classes = [IsAdmin]

    def get_dashboard_data(self, request):
        """Returns dashboard statistics for Admins."""

        # User statistics
        total_writers = User.objects.filter(role="writer").count()
        total_editors = User.objects.filter(role="editor").count()
        total_support = User.objects.filter(role="support").count()
        total_clients = User.objects.filter(role="client").count()
        suspended_users = User.objects.filter(is_suspended=True).count()

        # Financial statistics
        total_revenue = PaymentTransaction.objects.aggregate(Sum("amount"))["amount__sum"] or 0
        total_refunds = Refund.objects.aggregate(Sum("amount"))["amount__sum"] or 0
        pending_payouts = PaymentTransaction.objects.filter(status="pending").aggregate(Sum("amount"))["amount__sum"] or 0

        # Order statistics
        total_orders = Order.objects.count()
        orders_in_progress = Order.objects.filter(status="in_progress").count()
        completed_orders = Order.objects.filter(status="completed").count()
        disputed_orders = Order.objects.filter(status="disputed").count()
        canceled_orders = Order.objects.filter(status="canceled").count()

        # Dispute statistics
        total_disputes = Dispute.objects.count()
        resolved_disputes = Dispute.objects.filter(status="resolved").count()

        # Recent logs
        recent_logs = AdminLog.objects.order_by("-timestamp")[:10]

        dashboard_data = {
            "total_writers": total_writers,
            "total_editors": total_editors,
            "total_support": total_support,
            "total_clients": total_clients,
            "suspended_users": suspended_users,
            "total_revenue": total_revenue,
            "total_refunds": total_refunds,
            "pending_payouts": pending_payouts,
            "total_orders": total_orders,
            "orders_in_progress": orders_in_progress,
            "completed_orders": completed_orders,
            "disputed_orders": disputed_orders,
            "canceled_orders": canceled_orders,
            "total_disputes": total_disputes,
            "resolved_disputes": resolved_disputes,
            "recent_logs": [log.action for log in recent_logs]
        }

        serializer = DashboardSerializer(dashboard_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
