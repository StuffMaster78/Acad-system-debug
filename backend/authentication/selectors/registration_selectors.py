from django.utils.timezone import now

from authentication.models.registration_token import (
    RegistrationConfirmationLog,
    RegistrationToken,
)


def get_active_registration_token(*, user, website) -> RegistrationToken | None:
    """
    Return most recent unused, unexpired registration token.
    """
    return RegistrationToken.objects.filter(
        user=user,
        website=website,
        used_at__isnull=True,
        expires_at__gt=now(),
    ).order_by("-created_at").first()


def list_registration_tokens(*, user, website):
    """
    Return registration tokens for a user and website.
    """
    return RegistrationToken.objects.filter(
        user=user,
        website=website,
    ).order_by("-created_at")


def list_registration_confirmation_logs(*, user, website):
    """
    Return registration confirmation logs for a user and website.
    """
    return RegistrationConfirmationLog.objects.filter(
        user=user,
        website=website,
    ).order_by("-confirmed_at")