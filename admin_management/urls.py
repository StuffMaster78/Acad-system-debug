from django.urls import path
from .views import (
    AdminDashboardView,
    UserManagementView,
)

urlpatterns = [
    # Admin Dashboard API
    path("dashboard/", AdminDashboardView.as_view({"get": "get_dashboard_data"}), name="admin_dashboard"),

    # User Management APIs
    path("users/create/", UserManagementView.as_view({"post": "create_user"}), name="create_user"),
    path("users/suspend/", UserManagementView.as_view({"post": "suspend_user"}), name="suspend_user"),
]
