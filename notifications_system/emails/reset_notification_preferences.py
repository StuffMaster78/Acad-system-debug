from core.utils.email_helpers import send_website_mail
from django.conf import settings

def send_reset_confirmation_email(user, website, use_async=True):
    if use_async and getattr(settings, "USE_CELERY", False):
        from notifications_system.tasks import send_reset_email_task
        send_reset_email_task.delay(user.id, website.id)
    else:
        _send_reset_email_now(user, website)

def _send_reset_email_now(user, website):
    subject = "Your Notification Preferences Have Been Reset"
    message = (
        f"Hi {user.first_name or user.username},\n\n"
        "Your notification preferences have been successfully reset to the default settings.\n"
        "If this wasn't you, please review your preferences or contact support.\n\n"
        f"Regards,\n{website.name} Team"
    )
    html_message = f"""
        <p>Hi {user.first_name or user.username},</p>
        <p>Your <strong>notification preferences</strong> have been successfully reset to the default settings.</p>
        <p>If this wasn't you, please <a href='{website.domain}/dashboard/settings/notifications'>review your preferences</a> or contact support.</p>
        <br>
        <p>Regards,<br>{website.name} Team</p>
    """
    send_website_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        recipient_list=[user.email],
        tenant=website,
    )