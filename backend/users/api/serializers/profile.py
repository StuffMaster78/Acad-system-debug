from __future__ import annotations

from rest_framework import serializers

from users.models.profile import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for approved user profile data.
    """

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "display_name",
            "bio",
            "avatar",
            "timezone",
            "locale",
            "country",
            "last_seen_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "name_for_display",
            "created_at",
            "updated_at",
        ]