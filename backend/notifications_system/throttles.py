"""
Rate limiting for notification endpoints.
Prevents abuse of mark-read and preference update endpoints.
"""
from __future__ import annotations

from rest_framework.throttling import UserRateThrottle


class NotificationMarkReadThrottle(UserRateThrottle):
    """
    Throttle for mark-read endpoint.
    Prevents bots from hammering the read endpoint.
    """
    scope = 'notification_mark_read'
    # Set in settings: THROTTLE_RATES = {'notification_mark_read': '60/minute'}


class NotificationPreferenceUpdateThrottle(UserRateThrottle):
    """
    Throttle for preference update endpoint.
    Prevents rapid preference toggling.
    """
    scope = 'notification_preference_update'
    # Set in settings: THROTTLE_RATES = {'notification_preference_update': '30/minute'}


class NotificationPollThrottle(UserRateThrottle):
    """
    Throttle for the polling endpoint.
    Frontend should poll every 30s — this prevents faster polling.
    """
    scope = 'notification_poll'
    # Set in settings: THROTTLE_RATES = {'notification_poll': '4/minute'}