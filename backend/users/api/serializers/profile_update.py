from __future__ import annotations

from rest_framework import serializers

from users.models.profile import ProfileUpdateRequest


class ProfileUpdateRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for profile update requests.
    """

    class Meta:
        model = ProfileUpdateRequest
        fields = [
            "id",
            "user",
            "profile",
            "website",
            "requested_changes",
            "status",
            "submitted_note",
            "reviewed_by",
            "reviewed_at",
            "review_note",
            "applied_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "profile",
            "website",
            "status",
            "reviewed_by",
            "reviewed_at",
            "review_note",
            "applied_at",
            "created_at",
            "updated_at",
        ]


class SubmitProfileUpdateRequestSerializer(serializers.Serializer):
    """
    Serializer for submitting profile updates.
    """

    requested_changes = serializers.JSONField()
    submitted_note = serializers.CharField(required=False, allow_blank=True)