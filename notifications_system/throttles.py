from rest_framework.throttling import UserRateThrottle


class NotificationThrottle(UserRateThrottle):
    """
    Prevents users from hammering notification endpoints.
    """
    rate = "60/min"


class NotificationWriteBurstThrottle(UserRateThrottle):
    scope = "notifications_write_burst"   # e.g. 20/min

class NotificationWriteSustainedThrottle(UserRateThrottle):
    scope = "notifications_write_sustained"  # e.g. 200/day