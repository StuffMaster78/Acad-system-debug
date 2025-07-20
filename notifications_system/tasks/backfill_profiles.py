# notifications/tasks/backfill_profiles.py
from celery import shared_task
from django.contrib.auth import get_user_model
from notifications_system.models.notification_profile import (
    GroupNotificationProfile
)
from notifications_system.models.notification_group import NotificationGroup
from django.db import transaction

User = get_user_model()

@shared_task
def backfill_group_notification_profiles():
    users = User.objects.all().iterator()
    groups = NotificationGroup.objects.all()

    created = 0
    with transaction.atomic():
        for user in users:
            for group in groups:
                obj, was_created = GroupNotificationProfile.objects.get_or_create(
                    user=user,
                    group=group,
                    defaults={
                        "channel": group.default_channel,
                        "priority": group.default_priority,
                        "is_enabled": group.is_enabled_by_default
                    }
                )
                if was_created:
                    created += 1

    return {"profiles_created": created}