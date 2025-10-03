from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView  # type: ignore
from .views import (
    AdminDashboardView, 
    UserManagementView, 
    AdminLoginView, 
    AdminLogoutView, 
    BlacklistedUserViewSet
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'users', UserManagementView, basename="users")
router.register(r'blacklisted-users', BlacklistedUserViewSet, basename="blacklisted_users")

urlpatterns = [
    # Admin Dashboard
    path("dashboard/", AdminDashboardView.as_view({"get": "get_dashboard_data"}), name="admin_dashboard"),

    # Authentication APIs (JWT-Based)
    path("auth/login/", AdminLoginView.as_view(), name="admin_login"),
    path("auth/logout/", AdminLogoutView.as_view(), name="admin_logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="refresh_token"),

    # Include all registered ViewSets
    path("", include(router.urls)),
]