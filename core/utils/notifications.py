from django.core.mail import send_mail

def send_notification(subject, message, recipient_list, sender="no-reply@example.com"):
    """
    Sends an email notification.

    :param subject: Email subject
    :param message: Email body
    :param recipient_list: List of recipients
    :param sender: Sender email (default: no-reply)
    """
    send_mail(subject, message, sender, recipient_list, fail_silently=False)