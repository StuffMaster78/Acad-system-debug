from django.db.models import Q
from django.utils.timezone import now

from authentication.models.login_session import LoginSession


def list_active_sessions(*, user, website=None):
    """
    Return active sessions for a user, optionally scoped to website.
    """
    queryset = LoginSession.objects.filter(
        user=user,
        revoked_at__isnull=True,
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=now())
    )

    if website is not None:
        queryset = queryset.filter(website=website)

    return queryset.order_by("-logged_in_at")


def get_session_by_id(*, session_id, user=None, website=None) -> LoginSession | None:
    """
    Return session by primary key with optional scoping.
    """
    queryset = LoginSession.objects.filter(pk=session_id)

    if user is not None:
        queryset = queryset.filter(user=user)

    if website is not None:
        queryset = queryset.filter(website=website)

    return queryset.first()


def get_session_by_token_hash(*, token_hash: str) -> LoginSession | None:
    """
    Return session by token hash.
    """
    return LoginSession.objects.filter(
        token_hash=token_hash,
    ).first()


def count_active_sessions(*, user, website=None) -> int:
    """
    Return active session count for a user.
    """
    return list_active_sessions(user=user, website=website).count()