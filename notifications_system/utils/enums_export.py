
import json
from notifications_system.enums import (
    NotificationType,
    NotificationCategory,
    NotificationPriority,
    DeliveryStatus
)

def export_notification_enums():
    return {
        "types": [
            NotificationType.IN_APP, NotificationType.EMAIL,
            NotificationType.SMS, NotificationType.WEBSOCKET,
            NotificationType.PUSH
        ],
        "priorities": {k: v for k, v in NotificationPriority.__members__.items()},
        "categories": [
            NotificationCategory.INFO, NotificationCategory.WARNING,
            NotificationCategory.ERROR, NotificationCategory.ANNOUNCEMENT,
            NotificationCategory.NEWS
        ],
        "statuses": [
            DeliveryStatus.PENDING, DeliveryStatus.SENT,
            DeliveryStatus.FAILED, DeliveryStatus.QUEUED,
            DeliveryStatus.RETRY, DeliveryStatus.DELAYED,
            DeliveryStatus.TIMEOUT
        ]
    }
