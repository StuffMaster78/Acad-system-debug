from django.conf import settings
from celery import shared_task # type: ignore
from notifications_system.utils.email_helpers import send_website_mail
from notifications_system.utils.sms_helpers import send_sms_notification
from notifications_system.utils.push_helpers import send_push_notification
from notifications_system.services.core import NotificationService

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


def process_outbox(outbox_id: int):
    from notifications_system.models.outbox import Outbox
    ob = Outbox.objects.filter(id=outbox_id).first()
    if not ob:
        return
    p = dict(ob.payload or {})
    # ensure we don't re-enqueue
    old_async = getattr(settings, "ASYNC_NOTIFICATIONS", True)
    try:
        setattr(settings, "ASYNC_NOTIFICATIONS", False)
        NotificationService.send_notification(
            user=ob.user,
            event=ob.event_key,
            payload=p,
            website=ob.website,
            actor=None,
            channels=p.get("channels"),
            category=p.get("category"),
            template_name=p.get("template_name"),
            priority=p.get("priority", 5),
            is_critical=p.get("is_critical", False),
            is_digest=p.get("is_digest", False),
            digest_group=p.get("digest_group"),
            is_silent=p.get("is_silent", False),
            email_override=p.get("email_override"),
            global_broadcast=p.get("global_broadcast", False),
            groups=p.get("groups"),
            role=p.get("role"),
        )
    finally:
        setattr(settings, "ASYNC_NOTIFICATIONS", old_async)