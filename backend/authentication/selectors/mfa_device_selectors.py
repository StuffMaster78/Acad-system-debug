from authentication.models.mfa_device import MFADevice


def list_user_mfa_devices(*, user, website):
    """
    Return MFA devices for a user and website.
    """
    return MFADevice.objects.filter(
        user=user,
        website=website,
    ).order_by("-created_at")


def list_active_mfa_devices(*, user, website):
    """
    Return active MFA devices for a user and website.
    """
    return MFADevice.objects.filter(
        user=user,
        website=website,
        is_active=True,
    ).order_by("-created_at")


def get_mfa_device_by_id(*, device_id, user, website) -> MFADevice | None:
    """
    Return MFA device by ID.
    """
    return MFADevice.objects.filter(
        pk=device_id,
        user=user,
        website=website,
    ).first()