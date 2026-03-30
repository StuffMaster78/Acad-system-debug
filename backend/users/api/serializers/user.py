from __future__ import annotations

from rest_framework import serializers

from users.models.user import User


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer.
    """

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "phone_number",
            "email_verified",
            "phone_verified",
            "full_name",
            "website",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "email_verified",
            "phone_verified",
            "created_at",
            "updated_at",
        ]