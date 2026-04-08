from django.utils.timezone import now

from authentication.models.secure_token import SecureToken


def get_active_secure_token(
    *,
    user,
    website,
    purpose: str,
) -> SecureToken | None:
    """
    Return most recent active secure token by purpose.
    """
    return SecureToken.objects.filter(
        user=user,
        website=website,
        purpose=purpose,
        revoked_at__isnull=True,
        expires_at__gt=now(),
    ).order_by("-created_at").first()


def list_secure_tokens(*, user, website, purpose: str | None = None):
    """
    Return secure tokens for a user and website.
    """
    queryset = SecureToken.objects.filter(
        user=user,
        website=website,
    )

    if purpose is not None:
        queryset = queryset.filter(purpose=purpose)

    return queryset.order_by("-created_at")