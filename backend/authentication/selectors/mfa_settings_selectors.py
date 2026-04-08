from authentication.models.mfa_settings import MFASettings


def get_mfa_settings(*, user, website) -> MFASettings | None:
    """
    Return MFA settings for a user and website.
    """
    return MFASettings.objects.filter(
        user=user,
        website=website,
    ).first()