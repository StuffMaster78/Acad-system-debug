from celery import shared_task
from django.utils import timezone

from authentication.models.account_deletion_request import (
    AccountDeletionRequest,
)
from authentication.models.account_unlock_request import (
    AccountUnlockRequest,
)
from authentication.models.impersonation_token import ImpersonationToken
from authentication.models.otp_code import OTPCode
from authentication.models.password_reset_request import PasswordResetRequest
from authentication.models.registration_token import RegistrationToken
from authentication.services.account_deletion_service import (
    AccountDeletionService,
)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cleanup_expired_impersonation_tokens_task(self) -> int:
    """
    Delete expired impersonation tokens.
    """
    deleted_count, _ = ImpersonationToken.objects.filter(
        expires_at__lt=timezone.now(),
    ).delete()
    return deleted_count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cleanup_expired_otps_task(self) -> int:
    """
    Delete expired OTP codes.
    """
    deleted_count, _ = OTPCode.objects.filter(
        expires_at__lt=timezone.now(),
    ).delete()
    return deleted_count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cleanup_expired_password_reset_requests_task(self) -> int:
    """
    Delete expired password reset requests.
    """
    deleted_count, _ = PasswordResetRequest.objects.filter(
        expires_at__lt=timezone.now(),
    ).delete()
    return deleted_count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cleanup_expired_registration_tokens_task(self) -> int:
    """
    Delete expired registration tokens.
    """
    deleted_count, _ = RegistrationToken.objects.filter(
        expires_at__lt=timezone.now(),
    ).delete()
    return deleted_count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def cleanup_expired_account_unlock_requests_task(self) -> int:
    """
    Delete expired account unlock requests.
    """
    deleted_count, _ = AccountUnlockRequest.objects.filter(
        expires_at__lt=timezone.now(),
    ).delete()
    return deleted_count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def finalize_scheduled_account_deletions_task(self) -> int:
    """
    Move scheduled deletion requests into retained state after the undo
    window expires.
    """
    count = 0

    requests = AccountDeletionRequest.objects.filter(
        status=AccountDeletionRequest.Status.SCHEDULED,
        scheduled_deletion_at__isnull=False,
        scheduled_deletion_at__lte=timezone.now(),
    ).select_related("user", "website")

    for request_obj in requests:
        service = AccountDeletionService(
            user=request_obj.user,
            website=request_obj.website,
        )
        service.perform_soft_delete(request_obj=request_obj)
        count += 1

    return count


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def purge_retained_account_deletions_task(self) -> int:
    """
    Mark retained deletion requests as purged once retention expires.

    Replace this later with hard delete or anonymization if needed.
    """
    count = 0

    requests = AccountDeletionRequest.objects.filter(
        status=AccountDeletionRequest.Status.RETAINED,
        retained_until__isnull=False,
        retained_until__lte=timezone.now(),
    ).select_related("user", "website")

    for request_obj in requests:
        service = AccountDeletionService(
            user=request_obj.user,
            website=request_obj.website,
        )
        service.mark_purged(request_obj=request_obj)
        count += 1

    return count