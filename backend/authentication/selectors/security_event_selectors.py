from authentication.models.security_events import SecurityEvent


def list_user_security_events(*, user, website=None):
    """
    Return security events for a user.
    """
    queryset = SecurityEvent.objects.filter(user=user)

    if website is not None:
        queryset = queryset.filter(website=website)

    return queryset.order_by("-created_at")


def list_suspicious_events(*, website=None):
    """
    Return suspicious security events.
    """
    queryset = SecurityEvent.objects.filter(is_suspicious=True)

    if website is not None:
        queryset = queryset.filter(website=website)

    return queryset.order_by("-created_at")


def list_security_events_by_type(*, event_type: str, user=None, website=None):
    """
    Return security events filtered by type.
    """
    queryset = SecurityEvent.objects.filter(event_type=event_type)

    if user is not None:
        queryset = queryset.filter(user=user)

    if website is not None:
        queryset = queryset.filter(website=website)

    return queryset.order_by("-created_at")