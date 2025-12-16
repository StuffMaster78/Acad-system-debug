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
    MyNotificationPreferencesViewSet,
    MyEventNotificationPreferenceViewSet,
    NotificationEventPreferenceViewSet,
    RoleNotificationPreferenceViewSet
)
from notifications_system.views.prefs_api import PreferencesViewSet
from notifications_system.views.profiles import (
    NotificationProfileViewSet,
    NotificationGroupProfileViewSet,
    NotificationGroupViewSet
)
from notifications_system.views.broadcasts import BroadcastNotificationViewSet
from notifications_system.views.admin_views import NotificationAdminViewSet
from notifications_system.views.meta import NotificationMetaView
from notifications_system.admin_debug_views import preview_email_template
from notifications_system.views.stream import (
    notification_event_stream,
)
from notifications_system.views.sse import SSEStreamView, SSEStatusView, SSECloseView
from notifications_system.views.polling import poll_notifications
from notifications_system.views.feed_and_status import (
    NotificationFeedViewSet,
    NotificationStatusViewSet
)
from notifications_system.views.webhook_endpoints import (
    NotificationWebhookEndpointViewSet,
)

from notifications_system.views.views_feed import NotificationFeedView
from notifications_system.views.views_actions import (
    NotificationMarkReadView,
    NotificationBulkMarkAllReadView,
)
from notifications_system.views.views_counters import UnreadCountView
from notifications_system.views.views_preview import NotificationTemplatePreviewView
from notifications_system.dashboard.views import (
    PerformanceDashboardView,
    RealTimeMetricsView,
    TemplateAnalyticsView,
    CacheManagementView,
    SystemHealthView,
)

# app_name removed to allow explicit namespaces in main urls.py
# app_name = "notifications_system"

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
# router.register(
#     r"profiles", NotificationProfileViewSet,
#     basename="notification-profiles"
# )
router.register(
    "notification-groups",
    NotificationGroupViewSet,
    basename="notification-groups"
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
router.register(
    r"my/event-preferences",
    MyEventNotificationPreferenceViewSet,
    basename="my-event-preferences"
)
router.register(
    r"webhook-endpoints",
    NotificationWebhookEndpointViewSet,
    basename="notification-webhooks",
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
        "admin/preview-email/<str:priority>/",
        preview_email_template
    ),
    path(
        'notifications/stream/',
        notification_event_stream,
        name='notification_event_stream'
    ),
    path(
        "sse/stream/", SSEStreamView.as_view(), name="sse_stream"
    ),
    path(
        "sse/status/", SSEStatusView.as_view(), name="sse_status"
    ),
    path(
        "sse/close/", SSECloseView.as_view(), name="sse_close"
    ),
    path(
        "poll/", poll_notifications, name="poll_notifications"
    ),
    path(
        "feed/", NotificationFeedView.as_view(), name="notifications-feed"
    ),
    path(
        "notifications/feed/", NotificationFeedViewSet.as_view({'get': 'list'}), name="notifications-feed-viewset"
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
    # Dashboard endpoints
    path("dashboard/", PerformanceDashboardView.as_view(), name="performance_dashboard"),
    path("dashboard/metrics/", RealTimeMetricsView.as_view(), name="realtime_metrics"),
    path("dashboard/templates/", TemplateAnalyticsView.as_view(), name="template_analytics"),
    path("dashboard/cache/", CacheManagementView.as_view(), name="cache_management"),
    path("dashboard/health/", SystemHealthView.as_view(), name="system_health"),

    path("", include(router.urls)),
]