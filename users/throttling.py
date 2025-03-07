from rest_framework.throttling import AnonRateThrottle

class LoginThrottle(AnonRateThrottle):
    """
    Throttle login attempts to prevent brute force attacks.
    """
    scope = 'login'

class MagicLinkThrottle(AnonRateThrottle):
    """
    Throttle magic link requests to prevent spam.
    """
    scope = 'magic_link'