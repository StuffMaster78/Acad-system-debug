from django.core.mail import EmailMultiAlternatives
from notifications_system.utils.email_renderer import render_notification_email

def send_rich_notification_email(
        subject, message, recipient_list, *,
        website=None, context=None, priority=None,
        template_name=None
):
    """
    Sends a rich HTML email notification to a list of recipients.
    This function uses the provided subject, message, and context
    to render an HTML email template. It supports optional parameters
    like website for branding, context for dynamic content,
    and priority for notification importance. 
    """
    html_message = render_notification_email(
        subject,
        message,
        context=context or {"website_name": getattr(website, "name", None)},
        priority=priority,
        template_name=template_name
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=getattr(website, "email_from", "no-reply@example.com"),
        to=recipient_list
    )
    email.attach_alternative(html_message, "text/html")
    return email.send()
