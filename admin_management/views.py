from rest_framework import viewsets, status, views
from rest_framework.response import Response
from django.shortcuts import render
from .models import AdminProfile, AdminLog
from .serializers import (
    AdminProfileSerializer, 
    AdminLogSerializer, 
    BlacklistedUserSerializer, 
    DashboardSerializer, 
    UserSerializer, 
    CreateUserSerializer, 
    SuspendUserSerializer
)
from .managers import AdminManager
from .permissions import IsAdmin, IsSuperAdmin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from .models import AdminProfile, AdminLog, BlacklistedUser
from orders.models import Order, PaymentTransaction, Refund, Dispute
from .serializers import DashboardSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from .models import AdminActivityLog

User = get_user_model()

class AdminDashboardView(viewsets.ViewSet):
    """Admin Dashboard - Provides statistics on users, orders, disputes, and financials."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get_dashboard_data(self, request):
        """Returns dashboard statistics for Admins."""
        
        data = {
            "total_writers": User.objects.filter(role="writer").count(),
            "total_editors": User.objects.filter(role="editor").count(),
            "total_support": User.objects.filter(role="support").count(),
            "total_clients": User.objects.filter(role="client").count(),
            "suspended_users": User.objects.filter(is_suspended=True).count(),
            "total_revenue": PaymentTransaction.objects.aggregate(Sum("amount"))["amount__sum"] or 0,
            "total_refunds": Refund.objects.aggregate(Sum("amount"))["amount__sum"] or 0,
            "pending_payouts": PaymentTransaction.objects.filter(status="pending").aggregate(Sum("amount"))["amount__sum"] or 0,
            "total_orders": Order.objects.count(),
            "orders_in_progress": Order.objects.filter(status="in_progress").count(),
            "completed_orders": Order.objects.filter(status="completed").count(),
            "disputed_orders": Order.objects.filter(status="disputed").count(),
            "canceled_orders": Order.objects.filter(status="canceled").count(),
            "total_disputes": Dispute.objects.count(),
            "resolved_disputes": Dispute.objects.filter(status="resolved").count(),
            "recent_logs": [log.action for log in AdminLog.objects.order_by("-timestamp")[:10]],
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserManagementView(viewsets.ViewSet):
    """Admin manages users (create, suspend, reactivate)."""
    
    permission_classes = [IsAuthenticated, IsAdmin]

    @action(detail=False, methods=["post"])
    def create_user(self, request):
        """Admin creates a new user."""
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def suspend_user(self, request, pk=None):
        """Suspends a user and logs the event."""
        try:
            user = get_object_or_404(User, pk=pk)
            user.is_suspended = True
            user.suspension_reason = request.data.get("reason", "No reason provided")
            user.save()

            # Log suspension
            AdminActivityLog.objects.create(
                admin=request.user,
                action="User Suspension",
                details=f"Admin {request.user.username} suspended {user.username}."
            )

            return Response({"message": f"User {user.username} has been suspended."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperAdmin])
    def blacklist_user(self, request, pk=None):
        """Blacklists a user and logs the event."""
        try:
            user = get_object_or_404(User, pk=pk)
            if user.role == "admin":
                return Response({"error": "You cannot blacklist an admin."}, status=status.HTTP_403_FORBIDDEN)

            BlacklistedUser.objects.create(email=user.email, blacklisted_by=request.user)
            user.is_blacklisted = True
            user.save()

            # Log blacklisting
            AdminActivityLog.objects.create(
                admin=request.user,
                action="User Blacklisted",
                details=f"Admin {request.user.username} blacklisted {user.username}."
            )

            return Response({"message": "User blacklisted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)    
    
    @action(detail=True, methods=["post"])
    def place_probation(self, request, pk=None):
        """Admin places a user on probation."""
        try:
            user = User.objects.get(pk=pk)
            reason = request.data.get("reason", "No reason provided")
            duration = int(request.data.get("duration", 30))

            if user.role == "admin":
                return Response({"error": "Admins cannot be placed on probation."}, status=status.HTTP_403_FORBIDDEN)

            user.place_on_probation(reason, duration)

            return Response({"message": f"User {user.username} is now on probation for {duration} days."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["post"])
    def remove_probation(self, request, pk=None):
        """Admin removes a user from probation."""
        try:
            user = User.objects.get(pk=pk)

            if not user.is_on_probation:
                return Response({"error": "User is not on probation."}, status=status.HTTP_400_BAD_REQUEST)

            user.remove_from_probation()

            return Response({"message": f"User {user.username} is no longer on probation."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        

### 📌 Admin Login API ###
class AdminLoginView(views.APIView):
    """
    Admin Login with JWT Authentication and Activity Logging.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user and user.role in ["admin", "superadmin"]:
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)  # Track last login

            # Log the login activity
            AdminActivityLog.objects.create(
                admin=user,
                action="Admin Login",
                details=f"Admin {user.username} logged in."
            )

            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                },
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid credentials or unauthorized access."}, status=status.HTTP_401_UNAUTHORIZED)


### 📌 Admin Logout API (Blacklists Refresh Token) ###
class AdminLogoutView(views.APIView):
    """
    Logs out an admin and records the event.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Log the logout activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action="Admin Logout",
                details=f"Admin {request.user.username} logged out."
            )

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)


### 📌 Token Refresh API ###
@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh the access token using the refresh token.
    """
    from rest_framework_simplejwt.views import TokenRefreshView
    return TokenRefreshView.as_view()(request)


class BlacklistedUserView(viewsets.ReadOnlyModelViewSet):
    """
    View all blacklisted users.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    queryset = BlacklistedUser.objects.order_by("-blacklisted_at")
    serializer_class = BlacklistedUserSerializer
