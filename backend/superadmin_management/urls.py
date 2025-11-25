from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SuperadminProfileViewSet,
    UserManagementViewSet,
    SuperadminLogViewSet,
    SuperadminDashboardViewSet,
    AppealViewSet,
)

# Create router instance
router = DefaultRouter()

# Register ViewSets
router.register(r"superadmin-profile", SuperadminProfileViewSet, basename="superadmin-profile")
router.register(r"users", UserManagementViewSet, basename="users")
router.register(r"logs", SuperadminLogViewSet, basename="logs")
router.register(r"dashboard", SuperadminDashboardViewSet, basename="superadmin-dashboard")
router.register(r"appeals", AppealViewSet, basename="appeals")

# Define urlpatterns
urlpatterns = [
    path("", include(router.urls)),  # Include all router-generated routes
]
