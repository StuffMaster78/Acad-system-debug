from notifications_system.services.dispatcher import (
    BaseNotificationHandler, register_handler,
)


@register_handler("special_order.created")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.updated")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.deleted")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.on_hold")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.completed")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.cancelled")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.reopened")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.archived")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.rated")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.reviewed")


@register_handler("special_order.price_set")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.approved")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )


@register_handler("special_order.assigned")
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )
def handle(self, *, user, event, payload=None, **kwargs):
    from notifications_system.services.core import NotificationService
    NotificationService.send_notification(
        user=user,
        event=event,
        payload=payload or {},
        website=kwargs.get("website"),
        actor=kwargs.get("actor"),
        channels=kwargs.get("channels"),
        category=kwargs.get("category"),
        template_name=kwargs.get("template_name"),
        priority=kwargs.get("priority", 5),
        is_critical=kwargs.get("is_critical", False),
        is_digest=kwargs.get("is_digest", False),
        digest_group=kwargs.get("digest_group"),
        is_silent=kwargs.get("is_silent", False),
    )