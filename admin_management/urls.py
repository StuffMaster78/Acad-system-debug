from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView  # type: ignore
from .views import (
    AdminDashboardView, 
    UserManagementView, 
    AdminLoginView, 
    AdminLogoutView, 
    BlacklistedUserViewSet,
    AdminActivityLogViewSet,
)
from .views.user_management import ComprehensiveUserManagementViewSet
from .views.config_management import (
    PricingConfigManagementViewSet,
    WriterConfigManagementViewSet,
    DiscountConfigManagementViewSet,
    NotificationConfigManagementViewSet,
    SystemConfigManagementViewSet,
)
from .views.email_management import (
    MassEmailManagementViewSet,
    EmailDigestManagementViewSet,
    BroadcastMessageManagementViewSet,
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'users', UserManagementView, basename="users")
router.register(r'blacklisted-users', BlacklistedUserViewSet, basename="blacklisted_users")
router.register(r'activity-logs', AdminActivityLogViewSet, basename="activity_logs")

# Comprehensive user management
router.register(r'user-management', ComprehensiveUserManagementViewSet, basename="user_management")

# Configuration management
router.register(r'configs/pricing', PricingConfigManagementViewSet, basename="pricing_configs")
router.register(r'configs/writer', WriterConfigManagementViewSet, basename="writer_configs")
router.register(r'configs/discount', DiscountConfigManagementViewSet, basename="discount_configs")
router.register(r'configs/notifications', NotificationConfigManagementViewSet, basename="notification_configs")
router.register(r'configs', SystemConfigManagementViewSet, basename="system_configs")

# Email management
router.register(r'emails/mass-emails', MassEmailManagementViewSet, basename="mass_emails")
router.register(r'emails/digests', EmailDigestManagementViewSet, basename="email_digests")
router.register(r'emails/broadcasts', BroadcastMessageManagementViewSet, basename="broadcast_messages")

urlpatterns = [
    # Admin Dashboard
    path("dashboard/", AdminDashboardView.as_view({"get": "list"}), name="admin_dashboard"),

    # Authentication APIs (JWT-Based)
    path("auth/login/", AdminLoginView.as_view(), name="admin_login"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin_logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),

    # Include all registered ViewSets
    path("", include(router.urls)),
]