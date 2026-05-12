class ActivityScoringRules:

    HIGH_PRIORITY = {
        "payment.failed",
        "payment.completed",
        "system.error",
    }

    MEDIUM_PRIORITY = {
        "order.created",
        "order.status_changed",
        "message.sent",
    }

    LOW_PRIORITY = {
        "order.viewed",
        "message.read",
        "system.retry",
    }

    @staticmethod
    def score(event):

        if event.action in ActivityScoringRules.HIGH_PRIORITY:
            return 10

        if event.action in ActivityScoringRules.MEDIUM_PRIORITY:
            return 5

        return 1