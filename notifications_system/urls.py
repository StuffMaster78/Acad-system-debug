from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notifications_system.views.in_app_notifications import InAppNotificationViewSet
from notifications_system.views.prefs_api import PreferencesViewSet
from notifications_system.views.user_notifications import (
    NotificationViewSet,
    NotificationListView,
    NotificationDetailView,
    MarkNotificationAsReadView,
    UnreadNotificationCountView
)
from notifications_system.views.preferences import (
    NotificationPreferenceViewSet,
    MyNotificationPreferencesView,
    MyEventNotificationPreferenceViewSet,
    NotificationEventPreferenceViewSet,
    RoleNotificationPreferenceViewSet
)
from notifications_system.views.prefs_api import PreferencesViewSet
from notifications_system.views.profiles import (
    NotificationProfileViewSet,
    NotificationGroupProfileViewSet
)
from notifications_system.views.broadcasts import BroadcastNotificationViewSet
from notifications_system.views.admin_views import NotificationAdminViewSet
from notifications_system.views.meta import NotificationMetaView
from notifications_system.views import notification_enum_choices
from notifications_system.admin_debug_views import preview_email_template
from notifications_system.views.stream import (
    notification_event_stream,
)
from notifications_system.views.sse import sse_notifications
from notifications_system.views.polling import poll_notifications
from notifications_system.views.feed_and_status import (
    NotificationFeedViewSet,
    NotificationStatusViewSet
)

from notifications_system.views.views_feed import NotificationFeedView
from notifications_system.views.views_actions import (
    NotificationMarkReadView,
    NotificationBulkMarkAllReadView,
)
from notifications_system.views.views_counters import UnreadCountView
from notifications_system.views.views_preview import NotificationTemplatePreviewView

router = DefaultRouter()
router.register(
    r'notifications',
    NotificationViewSet,
    basename='notifications'
)

router.register(
    r'in-app-notifications',
    InAppNotificationViewSet,
    basename='in-app-notifications'
)

router.register(
    r'notification-preferences',
    NotificationPreferenceViewSet,
    basename='notification-preferences'
)
router.register(
    r"preferences",
    PreferencesViewSet,
    basename="prefs"
)
router.register(
    r"admin/notifications",
    NotificationAdminViewSet,
    basename="admin-notifications"
)
router.register(
    r"notification-profiles",
    NotificationProfileViewSet,
    basename="notification-profiles"
)
router.register(
    r"profiles", NotificationProfileViewSet,
    basename="notification-profiles"
)
router.register(
    "notification-group-profiles",
    NotificationGroupProfileViewSet,
    basename="notification-group-profiles"
)
router.register(
    r'broadcast-notifications',
    BroadcastNotificationViewSet,
    basename="broadcast-notifications"
)
router.register(
    r"event-preferences",
    NotificationEventPreferenceViewSet,
    basename='event-preferences'
)
router.register(
    "role-defaults",
    RoleNotificationPreferenceViewSet,
    basename="role-defaults"
)
router.register(
    r"notifications/feed",
    NotificationFeedViewSet,
    basename="notifications-feed"
)
router.register(
    r"notifications/status",
    NotificationStatusViewSet,
    basename="notifications-status"
)

urlpatterns = [
    path(
        "notifications/meta/",
        NotificationMetaView.as_view(),
        name="notifications-meta"
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
        "notifications/preferences/me/",
        MyNotificationPreferencesView.as_view(),
        name="my-notification-preferences"
    ),
    path(
        "admin/preview-email/<str:priority>/",
        preview_email_template
    ),
    path(
        'notifications/stream/',
        notification_event_stream,
        name='notification_event_stream'
    ),
    path(
        "stream/", sse_notifications, name="sse_notifications"
    ),
    path(
        "poll/", poll_notifications, name="poll_notifications"
    ),
    path(
        "feed/", NotificationFeedView.as_view(), name="notifications-feed"
    ),
    path(
        "mark-read/<int:notification_id>/",
        NotificationMarkReadView.as_view(),
        name="notifications-mark-read"
    ),
    path(
        "mark-all-read/",
        NotificationBulkMarkAllReadView.as_view(),
        name="notifications-mark-all-read"
    ),
    path(
        "unread-count/",
        UnreadCountView.as_view(),
        name="notifications-unread-count"
    ),
    path(
        "templates/preview/",
        NotificationTemplatePreviewView.as_view(),
        name="notifications-template-preview"
    ),

    path("", include(router.urls)),
]