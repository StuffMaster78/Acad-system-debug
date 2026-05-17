from notifications_system.services.notification_service import NotificationService


def handle_user_created(event):
    NotificationService.notify(
        event_key="superadmin.user.created",
        recipient=event.user,
        website=event.website,
        context={
            "role": event.role,
            "temp_password": event.temp_password,
        },
    )