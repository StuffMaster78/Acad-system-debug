# notifications_system/serializers/__init__.py
"""
Re-exports all serializers so existing imports keep working.

Views import from here:
    from notifications_system.serializers import NotificationSerializer

Individual modules import directly:
    from notifications_system.serializers.notifications import NotificationSerializer
"""

# Notifications
from notifications_system.serializers.notifications import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationsUserStatusSerializer,
    UserNotificationMetaSerializer,
)

# Preferences
from notifications_system.serializers.preferences import (
    NotificationPreferenceSerializer,
    NotificationEventPreferenceSerializer,
    NotificationPreferenceProfileSerializer,
    RoleNotificationPreferenceSerializer,
)

# Broadcasts
from notifications_system.serializers.broadcasts import (
    BroadcastNotificationSerializer,
    BroadcastAcknowledgementSerializer,
    BroadcastOverrideSerializer,
)

# Templates
from notifications_system.serializers.templates import (
    NotificationEventSerializer,
    NotificationTemplateSerializer,
    NotificationTemplateCreateSerializer,
    NotificationEventConfigSerializer,
    NotificationEventOverrideSerializer,
)

# Delivery + log
from notifications_system.serializers.delivery import (
    DeliverySerializer,
    NotificationLogSerializer,
)

# Digest
from notifications_system.serializers.digest import (
    NotificationDigestSerializer,
)

__all__ = [
    # Notifications
    'NotificationSerializer',
    'NotificationListSerializer',
    'NotificationsUserStatusSerializer',
    'UserNotificationMetaSerializer',
    # Preferences
    'NotificationPreferenceSerializer',
    'NotificationEventPreferenceSerializer',
    'NotificationPreferenceProfileSerializer',
    'RoleNotificationPreferenceSerializer',
    # Broadcasts
    'BroadcastNotificationSerializer',
    'BroadcastAcknowledgementSerializer',
    'BroadcastOverrideSerializer',
    # Templates
    'NotificationEventSerializer',
    'NotificationTemplateSerializer',
    'NotificationTemplateCreateSerializer',
    'NotificationEventConfigSerializer',
    'NotificationEventOverrideSerializer',
    # Delivery
    'DeliverySerializer',
    'NotificationLogSerializer',
    # Digest
    'NotificationDigestSerializer',
]

## Updated file tree
""""
notifications_system/serializers/
├── __init__.py          re-exports everything — existing imports unchanged
├── notifications.py     NotificationSerializer, NotificationListSerializer,
│                        NotificationsUserStatusSerializer, UserNotificationMetaSerializer
├── preferences.py       NotificationPreferenceSerializer,
│                        NotificationEventPreferenceSerializer,
│                        NotificationPreferenceProfileSerializer,
│                        RoleNotificationPreferenceSerializer
├── broadcasts.py        BroadcastNotificationSerializer,
│                        BroadcastAcknowledgementSerializer,
│                        BroadcastOverrideSerializer
├── templates.py         NotificationEventSerializer,
│                        NotificationTemplateSerializer,
│                        NotificationTemplateCreateSerializer,
│                        NotificationEventConfigSerializer,
│                        NotificationEventOverrideSerializer
├── delivery.py          DeliverySerializer,
│                        NotificationLogSerializer
└── digest.py            NotificationDigestSerializer
"""