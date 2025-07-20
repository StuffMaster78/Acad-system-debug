from notifications_system.enums import NotificationPriority


def get_template_for_priority(priority: int) -> str:
        """"Returns the appropriate email template based on notification priority."""
        priority_map = {
            NotificationPriority.EMERGENCY: "notifications/emails/critical.html",
            NotificationPriority.HIGH: "notifications/emails/high.html",
            NotificationPriority.MEDIUM_HIGH: "notifications/emails/normal.html",
            NotificationPriority.NORMAL: "notifications/emails/normal.html",
            NotificationPriority.LOW: "notifications/emails/low.html",
            NotificationPriority.PASSIVE: "notifications/emails/passive.html",
        }
        return priority_map.get(priority, "notifications/emails/normal.html")