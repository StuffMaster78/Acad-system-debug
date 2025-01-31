from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import SuperadminProfile, SuperadminLog
from .serializers import SuperadminProfileSerializer, UserSerializer, SuperadminLogSerializer
from .permissions import IsSuperadmin
from .managers import SuperadminManager
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from .models import SuperadminLog
from orders.models import Order
from notifications_system.models import Notification
# from payments.models import PaymentTransaction, Refund
from orders.models import Dispute, PaymentTransaction, Refund


User = get_user_model()

class SuperadminProfileViewSet(viewsets.ModelViewSet):
    """API for Superadmin Profiles."""
    queryset = SuperadminProfile.objects.all()
    serializer_class = SuperadminProfileSerializer
    permission_classes = [IsSuperadmin]

class UserManagementViewSet(viewsets.ViewSet):
    """API for Superadmins to manage users."""
    permission_classes = [IsSuperadmin]

    def list_users(self, request):
        users = User.objects.all().values("id", "username", "email", "role", "is_suspended", "date_joined")
        return Response(users, status=status.HTTP_200_OK)

    def create_user(self, request):
        """Superadmin creates a user."""
        superadmin = request.user
        result = SuperadminManager.create_user(
            superadmin,
            username=request.data.get("username"),
            email=request.data.get("email"),
            role=request.data.get("role"),
            phone_number=request.data.get("phone_number", ""),
        )
        return Response(result, status=status.HTTP_201_CREATED)

    def suspend_user(self, request):
        """Superadmin suspends a user."""
        user = User.objects.get(pk=request.data.get("user_id"))
        superadmin = request.user
        result = SuperadminManager.suspend_user(superadmin, user, request.data.get("reason", "No reason provided"))
        return Response(result, status=status.HTTP_200_OK)

    def reactivate_user(self, request):
        """Superadmin reactivates a user."""
        user = User.objects.get(pk=request.data.get("user_id"))
        superadmin = request.user
        result = SuperadminManager.reactivate_user(superadmin, user)
        return Response(result, status=status.HTTP_200_OK)

    def change_user_role(self, request):
        """Superadmin changes a user's role."""
        user = User.objects.get(pk=request.data.get("user_id"))
        superadmin = request.user
        result = SuperadminManager.change_user_role(superadmin, user, request.data.get("new_role"))
        return Response(result, status=status.HTTP_200_OK)

class SuperadminLogViewSet(viewsets.ModelViewSet):
    """API for Superadmin logs."""
    queryset = SuperadminLog.objects.all().order_by("-timestamp")
    serializer_class = SuperadminLogSerializer
    permission_classes = [IsSuperadmin]


def superadmin_dashboard(request):
    """Superadmin Dashboard - Displays key system metrics."""

    # User statistics
    total_users = User.objects.count()
    total_admins = User.objects.filter(role="admin").count()
    total_support = User.objects.filter(role="support").count()
    total_editors = User.objects.filter(role="editor").count()
    total_writers = User.objects.filter(role="writer").count()
    total_clients = User.objects.filter(role="client").count()
    suspended_users = User.objects.filter(is_suspended=True).count()
    blacklisted_users = User.objects.filter(is_blacklisted=True).count()

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
    recent_logs = SuperadminLog.objects.order_by("-timestamp")[:10]


    # Fetch all unread notifications for Superadmins
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')

    context = {
        "total_users": total_users,
        "total_admins": total_admins,
        "total_support": total_support,
        "total_editors": total_editors,
        "total_writers": total_writers,
        "total_clients": total_clients,
        "suspended_users": suspended_users,
        "blacklisted_users": blacklisted_users,

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

        "recent_logs": recent_logs,
        "notifications": notifications,
    }

    return render(request, "superadmin_dashboard.html", context)
