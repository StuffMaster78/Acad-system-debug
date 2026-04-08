from django.utils import timezone

from authentication.models.otp_code import OTPCode


def get_active_otp(
    *,
    user,
    website,
    purpose: str,
) -> OTPCode | None:
    """
    Return the most recent active OTP for a user, website, and purpose.
    """
    return OTPCode.objects.filter(
        user=user,
        website=website,
        purpose=purpose,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).order_by("-created_at").first()


def list_otps(
    *,
    user,
    website,
    purpose: str | None = None,
):
    """
    Return OTP records for a user and website.
    """
    queryset = OTPCode.objects.filter(
        user=user,
        website=website,
    )

    if purpose is not None:
        queryset = queryset.filter(purpose=purpose)

    return queryset.order_by("-created_at")


def count_active_otps(
    *,
    user,
    website,
    purpose: str,
) -> int:
    """
    Return count of active OTPs for a purpose.
    """
    return OTPCode.objects.filter(
        user=user,
        website=website,
        purpose=purpose,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).count()