"""
URL configuration for the notification system.
All routes are prefixed with /notifications/ in the main urls.py.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notifications_system.views.notifications import NotificationFeedViewSet
from notifications_system.views.polling import NotificationPollView
from notifications_system.views.preferences import (
    NotificationPreferenceView,
    NotificationEventPreferenceViewSet,
)
from notifications_system.views.broadcasts import BroadcastViewSet
from notifications_system.views.templates import (
    NotificationTemplateViewSet,
    NotificationEventConfigViewSet,
)
from notifications_system.views.admin_views import (
    AdminBroadcastViewSet,
    AdminNotificationProfileViewSet,
    AdminDeliveryLogViewSet,
    AdminNotificationLogViewSet,
)

router = DefaultRouter()

# ── User-facing ────────────────────────────────────────────
router.register(
    r'feed',
    NotificationFeedViewSet,
    basename='notification-feed',
)
router.register(
    r'event-preferences',
    NotificationEventPreferenceViewSet,
    basename='notification-event-preference',
)
router.register(
    r'broadcasts',
    BroadcastViewSet,
    basename='broadcast',
)

# ── Admin ──────────────────────────────────────────────────
router.register(
    r'admin/broadcasts',
    AdminBroadcastViewSet,
    basename='admin-broadcast',
)
router.register(
    r'admin/profiles',
    AdminNotificationProfileViewSet,
    basename='admin-notification-profile',
)
router.register(
    r'admin/deliveries',
    AdminDeliveryLogViewSet,
    basename='admin-delivery-log',
)
router.register(
    r'admin/logs',
    AdminNotificationLogViewSet,
    basename='admin-notification-log',
)

# ── Templates (admin) ──────────────────────────────────────
router.register(
    r'templates',
    NotificationTemplateViewSet,
    basename='notification-template',
)
router.register(
    r'event-configs',
    NotificationEventConfigViewSet,
    basename='notification-event-config',
)

urlpatterns = [
    path('', include(router.urls)),

    # Master preferences (not a viewset — simple get/patch)
    path(
        'preferences/',
        NotificationPreferenceView.as_view(),
        name='notification-preferences',
    ),

    # Poll endpoint (throttled)
    path(
        'poll/',
        NotificationPollView.as_view(),
        name='notification-poll',
    ),
]

## Complete endpoint reference
# ```
# # ── Feed ──────────────────────────────────────────────────────────────────
# GET    /api/v1/notifications/feed/                     Paginated feed (lightweight)
# GET    /api/v1/notifications/feed/{id}/                Full notification detail
# GET    /api/v1/notifications/feed/unread-count/        Cached unread count
# GET    /api/v1/notifications/feed/pinned/              All pinned notifications
# GET    /api/v1/notifications/feed/critical/            Unread critical notifications
# PATCH  /api/v1/notifications/feed/{id}/mark-read/      Mark one read
# PATCH  /api/v1/notifications/feed/mark-all-read/       Mark all read
# PATCH  /api/v1/notifications/feed/{id}/pin/            Pin
# PATCH  /api/v1/notifications/feed/{id}/unpin/          Unpin
# PATCH  /api/v1/notifications/feed/{id}/acknowledge/    Acknowledge

# # Feed query params:
# #   ?category=order|payment|wallet|ticket|account|system
# #   ?is_read=true|false
# #   ?priority=low|normal|high|critical
# #   ?event_key=order.completed

# # ── Poll ──────────────────────────────────────────────────────────────────
# GET    /api/v1/notifications/poll/                     Unread count + latest toast

# # ── Preferences ───────────────────────────────────────────────────────────
# GET    /api/v1/notifications/preferences/              Get master preferences
# # PATCH  /api/v1/notifications/preferences/              Update master preferences

# GET    /api/v1/notifications/event-preferences/        List per-event preferences
# GET    /api/v1/notifications/event-preferences/?group_by=category
# PATCH  /api/v1/notifications/event-preferences/{id}/   Update one event preference
# POST   /api/v1/notifications/event-preferences/reset/  Reset to defaults
# POST   /api/v1/notifications/event-preferences/bulk-update/  Bulk update

# # ── Broadcasts (user-facing) ──────────────────────────────────────────────
# GET    /api/v1/notifications/broadcasts/               Active broadcasts
# GET    /api/v1/notifications/broadcasts/{id}/          Broadcast detail
# GET    /api/v1/notifications/broadcasts/pending/       Pending acknowledgements
# GET    /api/v1/notifications/broadcasts/blocking/      Dashboard gate check
# POST   /api/v1/notifications/broadcasts/{id}/acknowledge/

# # ── Templates (admin) ─────────────────────────────────────────────────────
# GET    /api/v1/notifications/templates/                List templates
# POST   /api/v1/notifications/templates/                Create template
# GET    /api/v1/notifications/templates/{id}/           Get template
# PATCH  /api/v1/notifications/templates/{id}/           Update template
# DELETE /api/v1/notifications/templates/{id}/           Delete template
# POST   /api/v1/notifications/templates/{id}/preview/   Preview with sample context
# GET    /api/v1/notifications/templates/missing/        Events with no template
# GET    /api/v1/notifications/templates/coverage/       Full coverage report

# Templates query params:
#   ?channel=email|in_app
#   ?event_key=order.completed
#   ?scope=global|website

# ── Event configs (admin) ─────────────────────────────────────────────────
# GET    /api/v1/notifications/event-configs/            List all event configs
# GET    /api/v1/notifications/event-configs/{id}/       Get one config

# # ── Admin broadcasts ──────────────────────────────────────────────────────
# POST   /api/v1/notifications/admin/broadcasts/send/        Create + fan out
# POST   /api/v1/notifications/admin/broadcasts/{id}/preview/ Preview to self
# POST   /api/v1/notifications/admin/broadcasts/{id}/cancel/  Cancel scheduled
# GET    /api/v1/notifications/admin/broadcasts/list-all/     All broadcasts + status

# # ── Admin profiles ────────────────────────────────────────────────────────
# GET    /api/v1/notifications/admin/profiles/               List profiles
# POST   /api/v1/notifications/admin/profiles/create-profile/ Create profile
# POST   /api/v1/notifications/admin/profiles/{id}/apply-to-user/
# POST   /api/v1/notifications/admin/profiles/{id}/apply-to-role/
# GET    /api/v1/notifications/admin/profiles/{id}/statistics/

# ── Admin delivery debug (superadmin only) ────────────────────────────────
# GET    /api/v1/notifications/admin/deliveries/         All delivery attempts
# GET    /api/v1/notifications/admin/deliveries/{id}/    One delivery detail
# GET    /api/v1/notifications/admin/logs/               Immutable audit trail
# GET    /api/v1/notifications/admin/logs/{id}/

# Delivery query params:
#   ?user_id=42&channel=email&status=failed&event_key=order.completed