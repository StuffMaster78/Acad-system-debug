from authentication.models.password_security import (
    PasswordBreachCheck,
    PasswordExpirationPolicy,
    PasswordHistory,
)


def list_password_history(*, user, website):
    """
    Return password history entries for a user and website.
    """
    return PasswordHistory.objects.filter(
        user=user,
        website=website,
    ).order_by("-created_at")


def get_password_expiration_policy(*, user, website) -> PasswordExpirationPolicy | None:
    """
    Return password expiration policy for a user and website.
    """
    return PasswordExpirationPolicy.objects.filter(
        user=user,
        website=website,
    ).first()


def list_password_breach_checks(*, user, website):
    """
    Return password breach checks for a user and website.
    """
    return PasswordBreachCheck.objects.filter(
        user=user,
        website=website,
    ).order_by("-checked_at")