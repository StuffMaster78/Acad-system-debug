from celery import shared_task # type: ignore
from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.utils.sms_helpers import send_sms_notification
from notifications_system.utils.push_helpers import send_push_notification
from notifications_system.utils.ws_helpers import send_ws_notification

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=5, max_retries=3)
def async_send_website_mail(self, user_id, subject, message, html_message=None):
    from users.models import User  # Or wherever user model lives
    user = User.objects.get(pk=user_id)
    send_website_mail(user, subject, message, html_message)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=3, max_retries=3)
def async_send_sms_notification(self, user_id, message):
    from users.models import User
    user = User.objects.get(pk=user_id)
    send_sms_notification(user, message)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=3, max_retries=3)
def async_send_push_notification(self, user_id, title, message):
    from users.models import User
    user = User.objects.get(pk=user_id)
    send_push_notification(user, title, message)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=3, max_retries=3)
def async_send_ws_notification(self, user_id, payload):
    from users.models import User
    user = User.objects.get(pk=user_id)
    send_ws_notification(user, payload)
