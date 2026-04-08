from authentication.models.session_limits import SessionLimitPolicy


def get_session_limit_policy(*, user, website) -> SessionLimitPolicy | None:
    """
    Return session limit policy for a user and website.
    """
    return SessionLimitPolicy.objects.filter(
        user=user,
        website=website,
    ).first()