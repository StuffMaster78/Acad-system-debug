from django.utils import timezone

from authentication.models.mfa_challenge import MFAChallenge


def get_active_mfa_challenge(*, user, website) -> MFAChallenge | None:
    """
    Return the most recent active MFA challenge.
    """
    return MFAChallenge.objects.filter(
        user=user,
        website=website,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
    ).order_by("-created_at").first()


def get_mfa_challenge_by_id(*, challenge_id, user, website) -> MFAChallenge | None:
    """
    Return MFA challenge by ID.
    """
    return MFAChallenge.objects.filter(
        pk=challenge_id,
        user=user,
        website=website,
    ).first()


def list_recent_mfa_challenges(*, user, website):
    """
    Return recent MFA challenges for a user.
    """
    return MFAChallenge.objects.filter(
        user=user,
        website=website,
    ).order_by("-created_at")