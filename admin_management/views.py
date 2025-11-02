from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.shortcuts import get_object_or_404
from django.db.models import Sum
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


class AdminDashboardView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request):
        """Dashboard stats for admin panel"""
        data = {
            "total_writers": User.objects.filter(role="writer").count(),
            "total_editors": User.objects.filter(role="editor").count(),
            "total_support": User.objects.filter(role="support").count(),
            "total_clients": User.objects.filter(role="client").count(),
            "suspended_users": User.objects.filter(is_suspended=True).count(),
            "total_orders": Order.objects.count(),
            "orders_in_progress": Order.objects.filter(status="in_progress").count(),
            "completed_orders": Order.objects.filter(status="completed").count(),
            "disputed_orders": Order.objects.filter(status="disputed").count(),
            "canceled_orders": Order.objects.filter(status="canceled").count(),
            "total_disputes": Dispute.objects.count(),
            "resolved_disputes": Dispute.objects.filter(status="resolved").count(),
            "recent_logs": [log.action for log in AdminActivityLog.objects.order_by("-timestamp")[:10]],
        }
        return Response(DashboardSerializer(data).data)


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
