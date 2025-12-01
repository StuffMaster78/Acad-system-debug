# Import main views from the parent views.py file
# Need to import from the parent module's views.py directly to avoid circular import
import sys
import os
import importlib.util

# Get the parent directory (admin_management)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
views_py_path = os.path.join(parent_dir, 'views.py')

if os.path.exists(views_py_path):
    spec = importlib.util.spec_from_file_location("admin_management.views_main", views_py_path)
    if spec and spec.loader:
        views_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(views_main)
        # Import all ViewSets from main views.py
        AdminDashboardView = views_main.AdminDashboardView
        UserManagementView = views_main.UserManagementView
        AdminLoginView = views_main.AdminLoginView
        AdminLogoutView = views_main.AdminLogoutView
        BlacklistedUserViewSet = views_main.BlacklistedUserViewSet
        AdminActivityLogViewSet = views_main.AdminActivityLogViewSet
        AdminPromotionRequestViewSet = getattr(views_main, 'AdminPromotionRequestViewSet', None)
        AdminDisputeManagementViewSet = getattr(views_main, 'AdminDisputeManagementViewSet', None)
        AdminRefundManagementViewSet = getattr(views_main, 'AdminRefundManagementViewSet', None)
        AdminReviewModerationViewSet = getattr(views_main, 'AdminReviewModerationViewSet', None)
        AdminOrderManagementViewSet = getattr(views_main, 'AdminOrderManagementViewSet', None)
        AdminSpecialOrdersManagementViewSet = getattr(views_main, 'AdminSpecialOrdersManagementViewSet', None)
        AdminClassBundlesManagementViewSet = getattr(views_main, 'AdminClassBundlesManagementViewSet', None)
        AdminTipManagementViewSet = getattr(views_main, 'AdminTipManagementViewSet', None)
    else:
        raise ImportError("Could not load views.py")
else:
    raise ImportError(f"views.py not found at {views_py_path}")

# Export user management and config management viewsets
from .user_management import ComprehensiveUserManagementViewSet
from .config_management import (
    PricingConfigManagementViewSet,
    WriterConfigManagementViewSet,
    DiscountConfigManagementViewSet,
    NotificationConfigManagementViewSet,
    SystemConfigManagementViewSet,
    ScreenedWordManagementViewSet,
    BlogAuthorPersonaManagementViewSet,
)
from .duplicate_detection import DuplicateAccountDetectionViewSet
from .dashboard_endpoints import (
    AdminDisputeDashboardViewSet,
    AdminRefundDashboardViewSet,
    AdminReviewModerationDashboardViewSet,
    AdminOrderManagementDashboardViewSet,
    AdminSpecialOrdersManagementDashboardViewSet,
    AdminClassManagementDashboardViewSet,
    AdminFinesManagementDashboardViewSet,
    AdminAdvancedAnalyticsDashboardViewSet,
)

__all__ = [
    'AdminDashboardView',
    'UserManagementView',
    'AdminLoginView',
    'AdminLogoutView',
    'BlacklistedUserViewSet',
    'AdminActivityLogViewSet',
    'AdminPromotionRequestViewSet',
    'AdminDisputeManagementViewSet',
    'AdminRefundManagementViewSet',
    'AdminReviewModerationViewSet',
    'AdminOrderManagementViewSet',
    'AdminSpecialOrdersManagementViewSet',
    'AdminClassBundlesManagementViewSet',
    'AdminTipManagementViewSet',
    'ComprehensiveUserManagementViewSet',
    'PricingConfigManagementViewSet',
    'WriterConfigManagementViewSet',
    'DiscountConfigManagementViewSet',
    'NotificationConfigManagementViewSet',
    'SystemConfigManagementViewSet',
    'ScreenedWordManagementViewSet',
    'BlogAuthorPersonaManagementViewSet',
    'DuplicateAccountDetectionViewSet',
    'AdminDisputeDashboardViewSet',
    'AdminRefundDashboardViewSet',
    'AdminReviewModerationDashboardViewSet',
    'AdminOrderManagementDashboardViewSet',
    'AdminSpecialOrdersManagementDashboardViewSet',
    'AdminClassManagementDashboardViewSet',
    'AdminFinesManagementDashboardViewSet',
    'AdminAdvancedAnalyticsDashboardViewSet',
]

