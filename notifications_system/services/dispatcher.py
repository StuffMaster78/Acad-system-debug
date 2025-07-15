import logging
from notifications_system.services.core import NotificationService
from notifications_system.notification_enums import NotificationType
from notifications_system.tasks import async_send_notification

logger = logging.getLogger(__name__)

def notify_user(
    user,
    subject=None,
    message=None,
    *,
    website=None,
    html_message=None,
    payload=None,
    actor=None,
    channels=None,
    event="generic",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
    template_name=None,
    email_override=None,
):
    """
    Unified dispatcher to send a notification to a single user.

    Args:
        user: Recipient user object
        subject: Title of the notification
        message: Body/message content
        website: Website/multitenancy context
        html_message: Optional HTML for email
        payload: Additional data (order_id, etc)
        actor: Who triggered the event (admin, system, etc.)
        channels: List of channels (e.g., ['email', 'in_app'])
        event: System event type
        category: NotificationCategory (info, error, etc)
        priority: Integer priority (higher = more urgent)
        is_critical: Should bypass normal filters (e.g., always email)
        is_digest: If it should be included in digest
        digest_group: Digest group (e.g., 'daily_summary')
        is_silent: Log but don't deliver
        template_name: If you’re using templates
    """
    logger.info(f"Dispatching notification to {user} | Event: {event} | Channels: {channels}")
    
    payload = payload or {}

    if subject:
        payload.setdefault("title", subject)
    if message:
        payload.setdefault("message", message)

    return NotificationService.send(
        user=user,
        website=website,
        actor=actor,
        event=event,
        context=payload,
        category=category,
        priority=priority,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent,
        channels=channels or [NotificationType.IN_APP],
        template_name=template_name,
        email_override=email_override
    )


def notify_users(
    users,
    subject=None,
    message=None,
    *,
    website=None,
    html_message=None,
    payload=None,
    actor=None,
    channels=None,
    event="generic",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
    template_name=None,
):
    """
    Bulk notify users — forwards to `notify_user` per user.
    """
    notifications = []
    for user in users:
        notif = notify_user(
            user,
            subject=subject,
            message=message,
            website=website,
            html_message=html_message,
            payload=payload,
            actor=actor,
            channels=channels,
            event=event,
            category=category,
            priority=priority,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent,
            template_name=template_name,
        )
        if notif:
            notifications.append(notif)
    return notifications


def notify_user_async(user, **kwargs):
    """
    Asynchronous version of notify_user using Celery.
    """
    async_send_notification.delay(
        user_id=user.id,
        actor_id=kwargs.get("actor").id if kwargs.get("actor") else None,
        website_id=kwargs.get("website").id if kwargs.get("website") else None,
        event=kwargs.get("event", "generic"),
        context=kwargs.get("payload", {}),
        channels=kwargs.get("channels", [NotificationType.IN_APP]),
        category=kwargs.get("category", "info"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False)
    )
    

def notify_admins(
    subject=None,
    message=None,
    *,
    website=None,
    html_message=None,
    payload=None,
    actor=None,
    channels=None,
    event="generic",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
    template_name=None,
):
    """
    Notify all admins with a single call.
    
    Args:
        subject: Title of the notification
        message: Body/message content
        ...
        (other parameters same as notify_user)
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    admins = User.objects.filter(is_staff=True, is_active=True)
    
    return notify_users(
        users=admins,
        subject=subject,
        message=message,
        website=website,
        html_message=html_message,
        payload=payload,
        actor=actor,
        channels=channels or [NotificationType.IN_APP],
        event=event,
        category=category,
        priority=priority,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent,
        template_name=template_name
    )


def notify_error(
    error_message: str,
    *,
    subject="Error Notification",
    website=None,
    payload=None,
    actor=None,
    channels=None,
):
    """
    Notify admins about an error.
    
    Args:
        error_message: The error message to send
        subject: Title of the notification
        website: Website context
        payload: Additional data (if any)
        actor: Who triggered the error (if applicable)
        channels: List of channels to notify (default is in_app)
    """
    return notify_admins(
        subject=subject,
        message=error_message,
        website=website,
        payload=payload,
        actor=actor,
        channels=channels or [NotificationType.IN_APP],
        event="error_notification",
        category="error",
        is_critical=True
    )

def notify_system(
    subject: str,
    message: str,
    *,
    website=None,
    payload=None,
    actor=None,
    channels=None,
    event="system_notification",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
):
    """
    Notify system admins about a system-level event.
    
    Args:
        subject: Title of the notification
        message: Body/message content
        ...
        (other parameters same as notify_user)
    """
    return notify_admins(
        subject=subject,
        message=message,
        website=website,
        payload=payload,
        actor=actor,
        channels=channels or [NotificationType.IN_APP],
        event=event,
        category=category,
        priority=priority,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent
    )


def notify_website(
    subject: str,
    message: str,
    *,
    website=None,
    payload=None,
    actor=None,
    channels=None,
    event="website_notification",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
):
    """
    Notify website users about a website-level event.

    Args:
        subject: Title of the notification
        message: Body/message content
        ...
        (other parameters same as notify_user)
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    website_users = User.objects.filter(is_active=True, website=website)
    return notify_users(
        users=website_users,
        subject=subject,
        message=message,
        website=website,
        payload=payload,
        actor=actor,
        channels=channels or [NotificationType.IN_APP],
        event=event,
        category=category,
        priority=priority,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent
    )

def notify_website_admins(
    subject: str,
    message: str,
    *,
    website=None,
    payload=None,
    actor=None,
    channels=None,
    event="website_admin_notification",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
):
    """
    Notify website admins about a website-level event.

    Args:
        subject: Title of the notification
        message: Body/message content
        ...
        (other parameters same as notify_user)
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    website_admins = User.objects.filter(is_staff=True, is_active=True, website=website)
    
    return notify_users(
        users=website_admins,
        subject=subject,
        message=message,
        website=website,
        payload=payload,
        actor=actor,
        channels=channels or [NotificationType.IN_APP],
        event=event,
        category=category,
        priority=priority,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent
    )

def notify_all_users(
    subject: str,
    message: str,
    *,
    website=None,
    payload=None,
    actor=None,
    channels=None,
    event="global_notification",
    category="info",
    priority=5,
    is_critical=False,
    is_digest=False,
    digest_group=None,
    is_silent=False,
):
    """
    Notify all users across the system.

    Args:
        subject: Title of the notification
        message: Body/message content
        ...
        (other parameters same as notify_user)
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    all_users = User.objects.filter(is_active=True)
    
    return notify_users(
        users=all_users,
        subject=subject,
        message=message,
        website=website,
        payload=payload,
        actor=actor,
        channels=channels or [NotificationType.IN_APP],
        event=event,
        category=category,
        priority=priority,
        is_critical=is_critical,
        is_digest=is_digest,
        digest_group=digest_group,
        is_silent=is_silent
    )

def test_notify(user, channel="in_app"):
    return notify_user(
        user=user,
        subject="Test Notification",
        message="This is a test message.",
        event="test_event",
        category="info",
        channels=[channel],
        is_silent=False
    )
def test_notify_admins(channel="in_app"):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    admins = User.objects.filter(is_staff=True, is_active=True)
    
    return notify_users(
        users=admins,
        subject="Test Admin Notification",
        message="This is a test message for admins.",
        event="test_admin_event",
        category="info",
        channels=[channel],
        is_silent=False
    )


def notify_user_async(user, **kwargs):
    """
    Asynchronous version of notify_user using Celery.
    """
    async_send_notification.delay(
        user_id=user.id,
        actor_id=kwargs.get("actor").id if kwargs.get("actor") else None,
        website_id=kwargs.get("website").id if kwargs.get("website") else None,
        event=kwargs.get("event", "generic"),
        context=kwargs.get("payload", {}),
        channels=kwargs.get("channels", [NotificationType.IN_APP]),
        category=kwargs.get("category", "info"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False)
    )