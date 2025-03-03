from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from django.db import models  
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from .models import SuperadminProfile, SuperadminLog, Probation
from .serializers import SuperadminProfileSerializer, UserSerializer, SuperadminLogSerializer
from .permissions import IsSuperadmin
from .managers import SuperadminManager
from .pagination import SuperadminPagination , SuperadminLogCursorPagination
from orders.models import Order, Dispute
from order_payments_management.models import OrderPayment
from notifications_system.models import Notification
from django_filters import rest_framework as filters
from django.core.cache import cache


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

    def suspend_user(self, request):
        """Superadmin suspends a user."""
        user = User.objects.filter(pk=request.data.get("user_id")).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        result = SuperadminManager.suspend_user(request.user, user, request.data.get("reason", "No reason provided"))
        return Response(result, status=status.HTTP_200_OK)

    def reactivate_user(self, request):
        """Superadmin reactivates a user."""
        user = User.objects.filter(pk=request.data.get("user_id")).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        result = SuperadminManager.reactivate_user(request.user, user)
        return Response(result, status=status.HTTP_200_OK)

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

    def get(self, request):
        """Fetch statistics, using caching."""
        cache_key = "superadmin_dashboard_stats"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        data = self.generate_dashboard_data()
        cache.set(cache_key, data, timeout=600)  # Cache for 10 minutes
        return Response(data, status=status.HTTP_200_OK)

    def generate_dashboard_data(self):
        """Generates the dashboard data (expensive query)."""
        return {
            "total_users": User.objects.count(),
            "total_orders": Order.objects.count(),
            "total_revenue": OrderPayment.objects.aggregate(Sum("amount"))["amount__sum"] or 0,
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
            resolved_disputes=Count("id", filter=Q(status="resolved"))
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