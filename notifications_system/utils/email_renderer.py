from django.template.loader import render_to_string
from notifications_system.enums import NotificationPriority

TEMPLATE_MAP = {
    NotificationPriority.EMERGENCY: "notifications/emails/critical.html",
    NotificationPriority.HIGH: "notifications/emails/high.html",
    NotificationPriority.MEDIUM_HIGH: "notifications/emails/high.html",
    NotificationPriority.NORMAL: "notifications/emails/normal.html",
    NotificationPriority.LOW: "notifications/emails/low.html",
    NotificationPriority.PASSIVE: "notifications/emails/passive.html",
}

DEFAULT_TEMPLATE = "notifications/emails/normal.html"

def render_notification_email(
        subject,
        message,
        *, context=None,
        priority=NotificationPriority.NORMAL,
        template_name=None
):
    context = context or {}
    context.update({
        "subject": subject,
        "message": message,
    })

    template = template_name or TEMPLATE_MAP.get(
        priority, DEFAULT_TEMPLATE
    )
    return render_to_string(template, context)