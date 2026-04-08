from django.utils import timezone
from authentication.models.account_deletion_request import (
    AccountDeletionRequest,
)


def get_active_account_deletion_request(
    *,
    user,
    website,
) -> AccountDeletionRequest | None:
    """
    Return the most recent active account deletion request.
    """
    return AccountDeletionRequest.objects.filter(
        user=user,
        website=website,
        status__in=[
            AccountDeletionRequest.Status.PENDING,
            AccountDeletionRequest.Status.CONFIRMED,
            AccountDeletionRequest.Status.SCHEDULED,
            AccountDeletionRequest.Status.RETAINED,
            AccountDeletionRequest.Status.COMPLETED,
        ],
    ).order_by("-requested_at").first()


def list_account_deletion_requests(*, user, website):
    """
    Return account deletion requests for a user and website.
    """
    return AccountDeletionRequest.objects.filter(
        user=user,
        website=website,
    ).order_by("-requested_at")


def get_access_blocking_deletion_request(
    *,
    user,
    website,
) -> AccountDeletionRequest | None:
    return AccountDeletionRequest.objects.filter(
        user=user,
        website=website,
        status__in=[
            AccountDeletionRequest.Status.SCHEDULED,
            AccountDeletionRequest.Status.RETAINED,
            AccountDeletionRequest.Status.COMPLETED,
        ],
    ).order_by("-requested_at").first()


def list_retention_expired_deletion_requests():
    return AccountDeletionRequest.objects.filter(
        status=AccountDeletionRequest.Status.RETAINED,
        retained_until__isnull=False,
        retained_until__lte=timezone.now(),
    ).order_by("retained_until")