from rest_framework.throttling import UserRateThrottle


class NotificationThrottle(UserRateThrottle):
    """
    Prevents users from hammering notification endpoints.
    """
    rate = "60/min"
