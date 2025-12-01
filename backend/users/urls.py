from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import ( # type: ignore
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

# Import ViewSets from views.py (main file) - use importlib to avoid circular import
import importlib.util
import sys
from pathlib import Path

# Load views.py directly
views_py_path = Path(__file__).parent / 'views.py'
spec = importlib.util.spec_from_file_location("users.views_main", views_py_path)
views_main = importlib.util.module_from_spec(spec)
sys.modules["users.views_main"] = views_main
spec.loader.exec_module(views_main)

UserViewSet = views_main.UserViewSet
AccountDeletionRequestViewSet = views_main.AccountDeletionRequestViewSet
AdminProfileRequestViewSet = views_main.AdminProfileRequestViewSet
AdminUserManagementViewSet = views_main.AdminUserManagementViewSet

# Import AccountManagementViewSet from views package
from users.views.account_management import AccountManagementViewSet
from users.views.privacy_controls import PrivacyControlsViewSet
from users.views.security_activity import SecurityActivityViewSet

# Initialize DRF Router
router = DefaultRouter()

# # Authentication endpoints (Signup, Login, Logout, MFA, Unlock)
# router.register(r'auth', AuthViewSet, basename="auth")
# router.register(r'mfa', MFAViewSet, basename="mfa")
# router.register(r'account-unlock', AccountUnlockViewSet, basename="account-unlock")

# User management (Profiles, Impersonation, Requests)
router.register(r'users', UserViewSet, basename="users")

# Unified Account Management (Password, 2FA, Profile Updates, Security)
router.register(r'account', AccountManagementViewSet, basename="account")

# Privacy Controls (Privacy Settings, Data Access Log, Data Export)
router.register(r'privacy', PrivacyControlsViewSet, basename="privacy")

# GDPR Compliance (All GDPR rights)
from users.views.gdpr_views import GDPRViewSet
router.register(r'gdpr', GDPRViewSet, basename="gdpr")

# Security Activity (Security Events Feed, Activity Summary)
router.register(r'security-activity', SecurityActivityViewSet, basename="security-activity")

# Admin actions (Profile update approvals, Deletions)
router.register(r'admin/profile-requests', AdminProfileRequestViewSet, basename="admin-profile-requests")
router.register(r'admin/user-management', AdminUserManagementViewSet, basename="admin-user-management")

# Account deletion requests (Clients & Writers)
router.register(r'account-deletion', AccountDeletionRequestViewSet, basename="account-deletion")

# Define URL patterns
urlpatterns = [
    path("", include(router.urls)),  # Include all router-based URLs
    # Legacy alias for profile update requests to keep old frontend/tests working:
    # /api/v1/users/users/profile-update-requests/
    path(
        "users/profile-update-requests/",
        AccountManagementViewSet.as_view({"get": "get_profile_update_requests"}),
        name="account-profile-update-requests-legacy",
    ),
    # path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),


    # OpenAPI Schema Endpoints
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),  # Generates OpenAPI schema
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),  # Swagger UI
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),  # ReDoc UI
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)