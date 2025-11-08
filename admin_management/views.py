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


class AdminActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving admin activity logs.
    """
    serializer_class = AdminLogSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        """Filter logs by website if user has website context."""
        queryset = AdminActivityLog.objects.select_related('admin').order_by('-timestamp')
        website = getattr(self.request.user, 'website', None)
        
        # If user has a website, filter logs by admins from that website
        if website:
            queryset = queryset.filter(admin__website=website)
        
        return queryset


class AdminDashboardView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]

    def list(self, request):
        """Dashboard stats for admin panel"""
        from .services.dashboard_metrics_service import DashboardMetricsService
        
        summary = DashboardMetricsService.get_summary(request.user)
        
        # Get additional user stats
        website = getattr(request.user, 'website', None)
        user_qs = User.objects.all()
        if website:
            user_qs = user_qs.filter(website=website)
        
        total_writers = user_qs.filter(role="writer").count()
        total_editors = user_qs.filter(role="editor").count()
        total_support = user_qs.filter(role="support").count()
        total_clients = user_qs.filter(role="client").count()
        suspended_users = user_qs.filter(is_suspended=True).count()
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
            "recent_logs": [log.action for log in recent_logs],
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
        """Admin endpoint to place an order with optional attribution."""
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
            'created_by_admin': True,
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
