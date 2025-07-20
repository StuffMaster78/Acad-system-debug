from django.conf import settings


class NotificationSystemConfigurations:
    """
    Centralized configuration for the notification system.
    Extend this as needed for toggles, limits, and defaults.
    """

    # Default notification channels
    DEFAULT_CHANNELS = getattr(
        settings,
        "NOTIFICATION_DEFAULT_CHANNELS",
        ["in_app", "email"]
    )

    # Max retries before failing
    MAX_RETRY_COUNT = getattr(
        settings,
        "NOTIFICATION_MAX_RETRY_COUNT",
        3
    )

    # Enable WebSocket delivery
    ENABLE_WEBSOCKETS = getattr(
        settings,
        "NOTIFICATION_ENABLE_WEBSOCKETS", True)

    # Enable email delivery
    ENABLE_EMAILS = getattr(
        settings,
        "NOTIFICATION_ENABLE_EMAILS", True)

    # Enable SMS delivery
    ENABLE_SMS = getattr(
        settings,
        "NOTIFICATION_ENABLE_SMS", False)

    # Enable digest (daily/weekly summaries)
    ENABLE_DIGESTS = getattr(
        settings,
        "NOTIFICATION_ENABLE_DIGESTS", True)

    # Debug/test mode (log only, no delivery)
    DEBUG_MODE = getattr(
        settings,
        "NOTIFICATION_DEBUG_MODE", False)

    # Notification delivery delays (for async queuing — in seconds)
    DELIVERY_DELAY_SECONDS = getattr(
        settings,
        "NOTIFICATION_DELIVERY_DELAY_SECONDS", 0)

    # Channels with instant priority (override frequency/dnd settings)
    CRITICAL_CHANNELS = getattr(
        settings,
        "NOTIFICATION_CRITICAL_CHANNELS", ["email", "push"])

    @classmethod
    def is_channel_enabled(cls, channel):
        if channel == "email":
            return cls.ENABLE_EMAILS
        if channel == "in_app":
            return True
        if channel == "sms":
            return cls.ENABLE_SMS
        if channel == "push":
            return True
        return False
    

    NOTIFICATION_SEND_RESET_EMAIL = True
