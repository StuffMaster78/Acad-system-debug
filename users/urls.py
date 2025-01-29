from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.viewsets import UserViewSet
from users.views import UserProfileView  # Import only what's needed
from users.views import (
    UserProfileView,
    ImpersonationView,
    UserActivityView,
)
# Create router for ViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),  # Uses ViewSet for user management
    path("profile/", UserProfileView.as_view(), name="user-profile"),  # Get authenticated user's profile
    path("users/impersonate/<int:user_id>/", ImpersonationView.as_view(), name="impersonate-user"),
    path("users/activity/<int:user_id>/", UserActivityView.as_view(), name="user-activity"),
]


# Ensure Django serves media files during development
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)