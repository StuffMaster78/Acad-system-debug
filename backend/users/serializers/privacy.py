"""
Serializers for privacy settings and pen names.
"""
from rest_framework import serializers
from users.models.privacy_settings import (
    WriterPrivacySettings,
    ClientPrivacySettings,
    PenName,
)


class PenNameSerializer(serializers.ModelSerializer):
    """Serializer for pen names."""

    class Meta:
        model = PenName
        fields = [
            "id",
            "pen_name",
            "is_active",
            "is_approved",
            "approved_by",
            "approved_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "is_approved",
            "approved_by",
            "approved_at",
            "created_at",
        ]


class WriterPrivacySettingsSerializer(serializers.ModelSerializer):
    """Serializer for writer privacy settings."""

    class Meta:
        model = WriterPrivacySettings
        fields = [
            "id",
            "show_writer_id",
            "show_pen_name",
            "show_completed_orders_count",
            "show_rating",
            "show_workload",
            "show_bio",
            "show_avatar",
            "bio_approved",
            "bio_approved_by",
            "bio_approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "show_writer_id",
            "show_pen_name",
            "show_completed_orders_count",
            "show_rating",
            "show_workload",
            "show_bio",
            "show_avatar",
            "bio_approved",
            "bio_approved_by",
            "bio_approved_at",
            "created_at",
            "updated_at",
        ]


class ClientPrivacySettingsSerializer(serializers.ModelSerializer):
    """Serializer for client privacy settings."""

    class Meta:
        model = ClientPrivacySettings
        fields = [
            "id",
            "show_client_id",
            "show_pen_name",
            "show_real_name",
            "show_email",
            "show_avatar",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "show_client_id",
            "show_pen_name",
            "show_real_name",
            "show_email",
            "show_avatar",
            "created_at",
            "updated_at",
        ]


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

