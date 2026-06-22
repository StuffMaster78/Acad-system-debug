"""
Privacy serializer stubs.

WriterPrivacySettings, ClientPrivacySettings, and PenName models were
removed (they had no migrations and no callers). The concrete serializers
below are stubs kept so that any future re-introduction of those models
has a clear place to expand. Only the bottom exports are actively used.
"""
from rest_framework import serializers


# ---------------------------------------------------------------------------
# Compatibility shims for privacy-aware serializers
# ---------------------------------------------------------------------------


class PrivacyAwareWriterSerializer(serializers.Serializer):
    """
    Backwards-compatibility stub for writer privacy-aware serializer.

    Currently this just acts as a pass-through placeholder so that imports
    from `users.serializers.privacy` continue to work. The actual privacy
    masking (if any) is handled by `get_privacy_aware_serializer`.
    """

    # We don't define explicit fields here because this class is not used
    # directly; callers should rely on `get_privacy_aware_serializer`.
    pass


class PrivacyAwareClientSerializer(serializers.Serializer):
    """
    Backwards-compatibility stub for client privacy-aware serializer.

    See notes on `PrivacyAwareWriterSerializer` above.
    """

    pass


def get_privacy_aware_serializer(target_role: str, viewer_role: str, viewer_user):
    """
    Return a serializer class that applies privacy rules based on roles.

    For now this is intentionally conservative and returns ``None`` so that
    the calling code falls back to the default serializer. This keeps the
    system working while avoiding import errors, and can be extended later
    with real masking rules.
    """

    # Placeholder implementation – no extra privacy layer yet.
    return None

