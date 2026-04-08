from django.utils import timezone

from authentication.models.account_lockout import AccountLockout


def get_active_lockout(
    *,
    user,
    website,
) -> AccountLockout | None:
    """
    Return the current active lockout for a user on a website.
    """
    return AccountLockout.objects.filter(
        user=user,
        website=website,
        is_active=True,
    ).order_by("-locked_at").first()


def is_user_locked(
    *,
    user,
    website,
) -> bool:
    """
    Return whether the user is currently locked out.
    """
    lockout = get_active_lockout(user=user, website=website)

    if lockout is None:
        return False

    locked_until = getattr(lockout, "locked_until", None)
    if locked_until is not None and timezone.now() >= locked_until:
        return False

    return True