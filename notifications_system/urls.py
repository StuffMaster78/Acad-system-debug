from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications_system.views import (
    NotificationEventPreferenceViewSet, NotificationViewSet, NotificationPreferenceViewSet,
    NotificationMetaView, RoleNotificationPreferenceViewSet, UnreadNotificationCountView,
    NotificationListView, NotificationDetailView,
    MarkNotificationAsReadView, NotificationAdminViewSet,
    NotificationProfileViewSet, MyNotificationPreferencesView,
    MyEventNotificationPreferenceViewSet,
    NotificationGroupProfileViewSet, BroadcastNotificationViewSet
)
from notifications_system.views import notification_enum_choices
from notifications_system.admin_debug_views import preview_email_template

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
router.register(
    r"admin/notifications", NotificationAdminViewSet,
    basename="admin-notifications"
)
router.register(
    r"notification-profiles", NotificationProfileViewSet,
    basename="notification-profiles"
)
router.register(
    "preferences", MyEventNotificationPreferenceViewSet,
    basename="notification-preferences"
)
router.register(
    r"profiles", NotificationProfileViewSet,
    basename="notification-profiles"
)
router.register(
    "notification-group-profiles", NotificationGroupProfileViewSet,
    basename="notification-group-profiles"
)
router.register(
    "broadcasts", BroadcastNotificationViewSet,
    basename="broadcast-notifications"
)
router.register(
    r"event-preferences",
    NotificationEventPreferenceViewSet,
    basename='event-preferences'
)
router.register(
    "role-defaults", RoleNotificationPreferenceViewSet,
    basename="role-defaults"
)

urlpatterns = [
    path(
        "notifications/meta/", NotificationMetaView.as_view(),
        name="notifications-meta"
    ),
    path(
        "notifications/metadata/", 
        NotificationMetaView.as_view(),
        name="notifications-metadata"
    ),
    path(
        "notifications/",
        NotificationListView.as_view(),
        name="notifications-list"
    ),
    path(
        "notifications/<int:pk>/",
        NotificationDetailView.as_view(),
        name="notifications-detail"
    ),
    path(
        "notifications/<int:pk>/mark-read/",
        MarkNotificationAsReadView.as_view(),
        name="notifications-mark-read"
    ),
    path(
        "notifications/unread-count/",
        UnreadNotificationCountView.as_view(),
        name="notifications-unread-count"
    ),
    path(
        "admin/notifications/enums/",
        notification_enum_choices
    ),
    path(
        "notifications/preferences/me/",
        MyNotificationPreferencesView.as_view(),
        name="my-notification-preferences"
    ),
    path(
        "admin/preview-email/<str:priority>/",
        preview_email_template
    ),

    path("", include(router.urls)),
]