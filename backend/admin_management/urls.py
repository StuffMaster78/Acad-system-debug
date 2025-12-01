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
    AdminDisputeManagementViewSet,
    AdminRefundManagementViewSet,
    AdminReviewModerationViewSet,
    AdminOrderManagementViewSet,
    AdminSpecialOrdersManagementViewSet,
    AdminClassBundlesManagementViewSet,
    AdminTipManagementViewSet,
)
from .views_fines import AdminFinesManagementViewSet
from .views_writer_assignment import WriterAssignmentViewSet
from .views.user_management import ComprehensiveUserManagementViewSet
from .views.config_management import (
    PricingConfigManagementViewSet,
    WriterConfigManagementViewSet,
    DiscountConfigManagementViewSet,
    NotificationConfigManagementViewSet,
    SystemConfigManagementViewSet,
    ScreenedWordManagementViewSet,
    BlogAuthorPersonaManagementViewSet,
)
from .views.email_management import (
    MassEmailManagementViewSet,
    EmailDigestManagementViewSet,
    BroadcastMessageManagementViewSet,
)
from .views.financial_overview import FinancialOverviewViewSet
from .views.unified_search import UnifiedSearchViewSet
from .views.exports import ExportViewSet
from .views.duplicate_detection import DuplicateAccountDetectionViewSet
from .views_referrals import (
    AdminReferralTrackingViewSet,
    AdminReferralAbuseViewSet,
    AdminReferralCodeViewSet,
)
from .views_loyalty import AdminLoyaltyTrackingViewSet
from .views_system_health import SystemHealthViewSet
from .views.dashboard_endpoints import (
    AdminDisputeDashboardViewSet,
    AdminRefundDashboardViewSet,
    AdminReviewModerationDashboardViewSet,
    AdminOrderManagementDashboardViewSet,
    AdminSpecialOrdersManagementDashboardViewSet,
    AdminClassManagementDashboardViewSet,
    AdminFinesManagementDashboardViewSet,
    AdminAdvancedAnalyticsDashboardViewSet,
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'dashboard', AdminDashboardView, basename="admin_dashboard")
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
router.register(r'configs/screened-words', ScreenedWordManagementViewSet, basename="screened_words_configs")
router.register(r'configs/blog-authors', BlogAuthorPersonaManagementViewSet, basename="blog_authors_configs")
router.register(r'configs', SystemConfigManagementViewSet, basename="system_configs")

# Email management
router.register(r'emails/mass-emails', MassEmailManagementViewSet, basename="mass_emails")
router.register(r'emails/digests', EmailDigestManagementViewSet, basename="email_digests")
router.register(r'emails/broadcasts', BroadcastMessageManagementViewSet, basename="broadcast_messages")

# Dispute and Refund management
router.register(r'disputes', AdminDisputeManagementViewSet, basename="admin_disputes")
router.register(r'disputes/dashboard', AdminDisputeDashboardViewSet, basename="admin_disputes_dashboard")
router.register(r'refunds', AdminRefundManagementViewSet, basename="admin_refunds")
router.register(r'refunds/dashboard', AdminRefundDashboardViewSet, basename="admin_refunds_dashboard")

# Review Moderation management
router.register(r'reviews', AdminReviewModerationViewSet, basename="admin_reviews")
router.register(r'reviews/dashboard', AdminReviewModerationDashboardViewSet, basename="admin_reviews_dashboard")

# Order Management
router.register(r'orders', AdminOrderManagementViewSet, basename="admin_orders")
router.register(r'orders/dashboard', AdminOrderManagementDashboardViewSet, basename="admin_orders_dashboard")

# Fines Management
router.register(r'fines', AdminFinesManagementViewSet, basename="admin_fines")
router.register(r'fines/dashboard', AdminFinesManagementDashboardViewSet, basename="admin_fines_dashboard")

# Advanced Analytics Dashboard
router.register(r'advanced-analytics', AdminAdvancedAnalyticsDashboardViewSet, basename="admin_advanced_analytics")

# Writer Assignment
router.register(r'writer-assignment', WriterAssignmentViewSet, basename="writer_assignment")

# Special Orders Management
router.register(r'special-orders', AdminSpecialOrdersManagementViewSet, basename="admin_special_orders")
router.register(r'special-orders/dashboard', AdminSpecialOrdersManagementDashboardViewSet, basename="admin_special_orders_dashboard")

# Class Bundles Management
router.register(r'class-bundles', AdminClassBundlesManagementViewSet, basename="admin_class_bundles")
router.register(r'class-bundles/dashboard', AdminClassManagementDashboardViewSet, basename="admin_class_bundles_dashboard")

# Tip Management
router.register(r'tips', AdminTipManagementViewSet, basename="admin_tips")

# Financial Overview
router.register(r'financial-overview', FinancialOverviewViewSet, basename="financial_overview")

# Unified Search
router.register(r'unified-search', UnifiedSearchViewSet, basename="unified_search")

# Exports
router.register(r'exports', ExportViewSet, basename="exports")

# Duplicate Account Detection
router.register(r'duplicate-detection', DuplicateAccountDetectionViewSet, basename="duplicate_detection")

# Referral Tracking and Abuse Management
router.register(r'referrals/tracking', AdminReferralTrackingViewSet, basename="referral_tracking")
router.register(r'referrals/abuse-flags', AdminReferralAbuseViewSet, basename="referral_abuse")
router.register(r'referrals/codes', AdminReferralCodeViewSet, basename="referral_codes")

# Loyalty Points Tracking
router.register(r'loyalty/tracking', AdminLoyaltyTrackingViewSet, basename="loyalty_tracking")

# System Health Monitoring
router.register(r'system-health', SystemHealthViewSet, basename="system_health")

urlpatterns = [
    # Authentication APIs (JWT-Based)
    path("auth/login/", AdminLoginView.as_view(), name="admin_login"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin_logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),

    # Include all registered ViewSets (includes dashboard with all actions)
    path("", include(router.urls)),
]