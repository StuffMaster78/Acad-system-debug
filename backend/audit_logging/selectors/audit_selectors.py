from django.db import transaction
from audit_logging.models.audit_event import AuditEvent


class AuditSelectors:
    """
    Read-only query layer for AuditEvent.

    Rules:
    - no business logic
    - no mutations
    - tenant-safe filtering only
    """

    # -------------------------
    # BASE
    # -------------------------
    @staticmethod
    def all():
        return AuditEvent.objects.all()

    @staticmethod
    def for_website(website_id: str):
        return AuditEvent.objects.filter(website_id=website_id)

    # -------------------------
    # ACTOR
    # -------------------------
    @staticmethod
    def by_actor(actor_id: int):
        return AuditEvent.objects.filter(actor_id=actor_id)

    @staticmethod
    def by_actor_type(actor_type: str):
        return AuditEvent.objects.filter(actor_type=actor_type)

    # -------------------------
    # OBJECT
    # -------------------------
    @staticmethod
    def by_object(object_type: str, object_id: str):
        return AuditEvent.objects.filter(
            object_type=object_type,
            object_id=object_id,
        )

    # -------------------------
    # ACTION
    # -------------------------
    @staticmethod
    def by_action(action: str):
        return AuditEvent.objects.filter(action=action)

    @staticmethod
    def by_actions(actions: list[str]):
        return AuditEvent.objects.filter(action__in=actions)

    # -------------------------
    # TIME (FIXED FIELD NAME)
    # -------------------------
    @staticmethod
    def recent(limit: int = 50):
        return AuditEvent.objects.order_by("-occurred_at")[:limit]

    @staticmethod
    def since(timestamp):
        return AuditEvent.objects.filter(occurred_at__gte=timestamp)

    @staticmethod
    def between(start, end):
        return AuditEvent.objects.filter(
            occurred_at__gte=start,
            occurred_at__lte=end,
        )

    # -------------------------
    # FEED (TENANT SAFE)
    # -------------------------
    @staticmethod
    def feed(website_id: str, limit: int = 100):
        return (
            AuditEvent.objects
            .filter(website_id=website_id)
            .order_by("-occurred_at")[:limit]
        )

    # -------------------------
    # SENSITIVITY
    # -------------------------
    @staticmethod
    def sensitive_events():
        return AuditEvent.objects.filter(is_sensitive=True)

    @staticmethod
    def by_sensitivity(level: str):
        return AuditEvent.objects.filter(sensitivity_level=level)

    # -------------------------
    # TRACE DEBUGGING
    # -------------------------
    @staticmethod
    def by_request(request_id: str):
        return AuditEvent.objects.filter(session_id=request_id)

    # -------------------------
    # IDEMPOTENCY / PROCESSING
    # -------------------------
    @staticmethod
    def claim_unprocessed_event(event_id: str) -> AuditEvent | None:
        with transaction.atomic():
            try:
                event = (
                    AuditEvent.objects
                    .select_for_update(skip_locked=True)
                    .filter(
                        id=event_id,
                        processed_at__isnull=True,
                        status="pending",
                    )
                    .first()
                )

                if not event:
                    return None

                event.status = "processing"
                event.save(update_fields=["status"])
                return event
            except AuditEvent.DoesNotExist:
                return None