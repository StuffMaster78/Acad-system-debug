from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications_system.views import (
    NotificationViewSet, NotificationPreferenceViewSet,
    NotificationMetaView
)

router = DefaultRouter()
router.register(
    r'notifications',
    NotificationViewSet,
    basename='notifications'
)
router.register(
    r'notification-preferences',
    NotificationPreferenceViewSet,
    basename='notification-preferences'
)

urlpatterns = [
    path("meta/", NotificationMetaView.as_view(), name="notifications-meta"),
    path("", include(router.urls)),
]