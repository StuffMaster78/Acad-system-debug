from .models import SupportNotification

def send_support_notification(support_staff, message):
    """
    Create a notification for a support staff member.
    """
    SupportNotification.objects.create(
        support_staff=support_staff,
        message=message,
    )