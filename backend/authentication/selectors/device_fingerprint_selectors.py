from authentication.models.device_fingerprinting import DeviceFingerprint


def get_fingerprint_by_hash(
    *,
    user,
    website,
    fingerprint_hash: str,
) -> DeviceFingerprint | None:
    """
    Return fingerprint by hash for a user and website.
    """
    return DeviceFingerprint.objects.filter(
        user=user,
        website=website,
        fingerprint_hash=fingerprint_hash,
    ).first()


def list_user_fingerprints(*, user, website):
    """
    Return all fingerprints for a user and website.
    """
    return DeviceFingerprint.objects.filter(
        user=user,
        website=website,
    ).order_by("-last_seen_at")


def list_trusted_fingerprints(*, user, website):
    """
    Return trusted fingerprints for a user and website.
    """
    return DeviceFingerprint.objects.filter(
        user=user,
        website=website,
        is_trusted=True,
    ).order_by("-last_seen_at")


def get_most_recent_fingerprint(*, user, website) -> DeviceFingerprint | None:
    """
    Return the most recently seen fingerprint.
    """
    return DeviceFingerprint.objects.filter(
        user=user,
        website=website,
    ).order_by("-last_seen_at").first()