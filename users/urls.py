from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.viewsets import UserViewSet
from users.views import (
    UserProfileView,
    ImpersonationView,
    UserActivityView,
)

# Create router for UserViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")

urlpatterns = [
    # ViewSet for User Management (Search, Filter, List, Retrieve, Update)
    path("", include(router.urls)),

    # Get authenticated user's profile
    path("profile/", UserProfileView.as_view(), name="user-profile"),

    # Impersonation (Admins & Superadmins)
    path("users/impersonate/<int:user_id>/", ImpersonationView.as_view(), name="impersonate-user"),

    # User Activity Tracking
    path("users/activity/<int:user_id>/", UserActivityView.as_view(), name="user-activity"),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
