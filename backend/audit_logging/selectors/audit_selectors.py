from audit_logging.storage.models import AuditEvent


class AuditSelectors:
    """
    Read-only query layer for AuditEvent.

    Purpose:
    - support activity feed generation
    - admin investigation tools
    - debugging and traceability

    Rule:
    No business logic. Only filtering and retrieval.
    """

    # -------------------------
    # Base queries
    # -------------------------
    @staticmethod
    def all():
        return AuditEvent.objects.all()

    # -------------------------
    # Actor-based queries
    # -------------------------
    @staticmethod
    def by_actor(actor_id: int):
        return AuditEvent.objects.filter(actor_id=actor_id)

    @staticmethod
    def by_actor_type(actor_type: str):
        return AuditEvent.objects.filter(actor_type=actor_type)

    # -------------------------
    # Object-based queries
    # -------------------------
    @staticmethod
    def by_object(object_type: str, object_id: str):
        return AuditEvent.objects.filter(
            object_type=object_type,
            object_id=object_id
        )

    # -------------------------
    # Action-based queries
    # -------------------------
    @staticmethod
    def by_action(action: str):
        return AuditEvent.objects.filter(action=action)

    @staticmethod
    def by_actions(actions: list[str]):
        return AuditEvent.objects.filter(action__in=actions)

    # -------------------------
    # Time-based queries
    # -------------------------
    @staticmethod
    def recent(limit: int = 50):
        return AuditEvent.objects.all()[:limit]

    @staticmethod
    def since(timestamp):
        return AuditEvent.objects.filter(timestamp__gte=timestamp)

    @staticmethod
    def between(start, end):
        return AuditEvent.objects.filter(
            timestamp__gte=start,
            timestamp__lte=end
        )

    # -------------------------
    # Request tracing (VERY useful for debugging)
    # -------------------------
    @staticmethod
    def by_request(request_id: str):
        return AuditEvent.objects.filter(request_id=request_id)

    # -------------------------
    # Sensitivity layer (critical for special orders)
    # -------------------------
    @staticmethod
    def sensitive_events():
        return AuditEvent.objects.filter(is_sensitive=True)

    @staticmethod
    def by_sensitivity(level: str):
        return AuditEvent.objects.filter(sensitivity_level=level)

    # -------------------------
    # Activity feed support (this is for your new app)
    # -------------------------
    @staticmethod
    def timeline_for_object(object_type: str, object_id: str):
        return (
            AuditEvent.objects
            .filter(object_type=object_type, object_id=object_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def timeline_for_actor(actor_id: int):
        return (
            AuditEvent.objects
            .filter(actor_id=actor_id)
            .order_by("-timestamp")
        )

    @staticmethod
    def feed(limit: int = 100):
        """
        Generic system-wide feed (for admin/activity dashboards)
        """
        return AuditEvent.objects.all().order_by("-timestamp")[:limit]
    
    @staticmethod
    def get_unprocessed(event_id: str) -> AuditEvent | None:
        try:
            event = AuditEvent.objects.select_for_update().get(event_id=event_id)
        except AuditEvent.DoesNotExist:
            return None

        if event.processed_at is not None:
            return None

        return event