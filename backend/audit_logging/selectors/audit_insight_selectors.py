from audit_logging.storage.models_dlq import AuditDeadLetter


class AuditInsightSelectors:

    @staticmethod
    def dlq_backlog():
        return AuditDeadLetter.objects.filter(is_resolved=False)

    @staticmethod
    def stuck_events():
        return AuditDeadLetter.objects.filter(
            is_resolved=False,
            retry_count__gte=3
        )

    @staticmethod
    def high_risk_failures():
        return AuditDeadLetter.objects.filter(
            is_resolved=False,
            event_payload__is_sensitive=True
        )