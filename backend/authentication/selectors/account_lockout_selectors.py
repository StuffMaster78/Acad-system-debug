from authentication.models.account_lockout import AccountLockout


def get_active_lockout(*, user, website) -> AccountLockout | None:
    """
    Return the user's current active lockout, if any.
    """
    return AccountLockout.objects.filter(
        user=user,
        website=website,
        is_active=True,
    ).order_by("-locked_at").first()


def list_active_lockouts_for_website(*, website):
    """
    Return active lockouts for a website.
    """
    return AccountLockout.objects.filter(
        website=website,
        is_active=True,
    ).order_by("-locked_at")


def list_user_lockouts(*, user, website):
    """
    Return all lockouts for a user on a website.
    """
    return AccountLockout.objects.filter(
        user=user,
        website=website,
    ).order_by("-locked_at")