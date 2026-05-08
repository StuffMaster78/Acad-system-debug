from audit_logging.models.audit_dead_letter import AuditDeadLetter


class AuditInsightSelectors:

    @staticmethod
    def dlq_backlog(website=None):
        qs = AuditDeadLetter.objects.filter(is_resolved=False)

        if website:
            qs = qs.filter(website=website)

        return qs

    @staticmethod
    def stuck_events(website=None):
        qs = AuditDeadLetter.objects.filter(
            is_resolved=False,
            retry_count__gte=3,
        )

        if website:
            qs = qs.filter(website=website)

        return qs

    @staticmethod
    def high_risk_failures(website=None):
        qs = AuditDeadLetter.objects.filter(
            is_resolved=False,
        )

        if website:
            qs = qs.filter(website=website)

        # NOTE:
        # Do NOT trust JSON payload for critical filtering at scale.
        # Replace with explicit column later if needed.
        return qs