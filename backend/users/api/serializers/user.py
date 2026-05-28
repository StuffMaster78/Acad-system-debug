from __future__ import annotations

from rest_framework import serializers

from users.models.user import User


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer for the /users/me/ endpoint — returns the AuthUser shape
    expected by the frontend (id, email, role, full_name, avatar_url, ...).
    """

    full_name = serializers.CharField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    timezone = serializers.SerializerMethodField()

    def get_avatar_url(self, obj: User) -> str | None:
        try:
            avatar = obj.profile.avatar
            if avatar:
                request = self.context.get("request")
                return request.build_absolute_uri(avatar.url) if request else avatar.url
        except Exception:
            pass
        return None

    def _profile_attr(self, obj: User, attr: str):
        try:
            return getattr(obj.profile, attr, None) or None
        except Exception:
            return None

    def get_bio(self, obj: User):
        return self._profile_attr(obj, "bio")

    def get_phone(self, obj: User):
        return obj.phone_number or None

    def get_location(self, obj: User):
        return self._profile_attr(obj, "country")

    def get_timezone(self, obj: User):
        return self._profile_attr(obj, "timezone")

    class Meta:
        model = User
        fields = ["id", "email", "role", "full_name", "avatar_url", "bio", "phone", "location", "timezone"]
        read_only_fields = fields


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