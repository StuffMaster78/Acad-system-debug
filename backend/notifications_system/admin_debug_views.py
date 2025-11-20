from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from notifications_system.utils.email_renderer import render_notification_email

@staff_member_required
def preview_email_template(request, priority="normal"):
    from notifications_system.enums import NotificationPriority

    test_data = {
        "subject": "This is a Test Notification",
        "message": "You've been assigned a new order. Please take action now.",
        "cta_url": "/orders/123",
        "cta_label": "View Order",
        "website_name": "FocusDesk"
    }

    priority_map = {
        "critical": NotificationPriority.EMERGENCY,
        "high": NotificationPriority.HIGH,
        "normal": NotificationPriority.NORMAL,
        "low": NotificationPriority.LOW,
        "passive": NotificationPriority.PASSIVE,
    }

    priority_enum = priority_map.get(priority, NotificationPriority.NORMAL)

    html = render_notification_email(
        subject=test_data["subject"],
        message=test_data["message"],
        context=test_data,
        priority=priority_enum
    )

    return HttpResponse(html)