from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Import ViewSets
from users.views import (
    AuthViewSet,
    UserViewSet,
    MFAViewSet,
    AccountUnlockViewSet,
    AccountDeletionRequestViewSet,
    AdminProfileRequestViewSet,
    AdminUserManagementViewSet,
    CustomTokenRefreshView
)

# Initialize DRF Router
router = DefaultRouter()

# Authentication endpoints (Signup, Login, Logout, MFA, Unlock)
router.register(r'auth', AuthViewSet, basename="auth")
router.register(r'mfa', MFAViewSet, basename="mfa")
router.register(r'account-unlock', AccountUnlockViewSet, basename="account-unlock")

# User management (Profiles, Impersonation, Requests)
router.register(r'users', UserViewSet, basename="users")

# Admin actions (Profile update approvals, Deletions)
router.register(r'admin/profile-requests', AdminProfileRequestViewSet, basename="admin-profile-requests")
router.register(r'admin/user-management', AdminUserManagementViewSet, basename="admin-user-management")

# Account deletion requests (Clients & Writers)
router.register(r'account-deletion', AccountDeletionRequestViewSet, basename="account-deletion")

# Define URL patterns
urlpatterns = [
    path("", include(router.urls)),  # Include all router-based URLs
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
