"""
Serializers for WriterProfile.

THREE SERIALIZERS
-----------------
WriterProfilePublicSerializer
    Client-facing. Only fields visible to clients during
    preferred writer selection. No performance stats, no earnings.

WriterProfileSummarySerializer
    Admin list view. Key fields for dashboard tables.
    No nested objects — fast to render across many rows.

WriterProfileDetailSerializer
    Admin and writer detail view. Full profile including
    level, capacity, discipline state, onboarding status.
    Read-only for most fields — mutations go through services.

WriterProfileUpdateSerializer
    Writer-editable fields only. Used for PATCH on /me/profile/.
    Validates bio length, timezone format, qualifications schema.
"""

from rest_framework import serializers

from writer_management.models.writer_profile import (
    WriterProfile,
    WriterOnboardingStatus,
    WriterVerificationStatus,
)


class WriterProfilePublicSerializer(serializers.ModelSerializer):
    """
    Public writer card — shown to clients during assignment selection.

    No earnings, no ratings, no internal stats.
    """

    level_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterProfile
        fields = [
            "public_uuid",
            "registration_id",
            "pen_name",
            "bio",
            "qualifications",
            "years_of_experience",
            "timezone",
            "level_name",
            "is_verified",
            "joined_at",
        ]
        read_only_fields = fields

    def get_level_name(self, obj) -> str | None:
        level = obj.writer_level
        return level.name if level is not None else None


class WriterProfileSummarySerializer(serializers.ModelSerializer):
    """
    Compact summary for admin list views.
    No nested objects — flat fields only.
    """

    level_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterProfile
        fields = [
            "id",
            "public_uuid",
            "registration_id",
            "pen_name",
            "full_name",
            "level_name",
            "onboarding_status",
            "verification_status",
            "is_verified",
            "is_deleted",
            "joined_at",
        ]
        read_only_fields = fields

    def get_level_name(self, obj) -> str | None:
        level = obj.writer_level
        return level.name if level is not None else None

    def get_full_name(self, obj) -> str:
        try:
            user = obj.account_profile.user
            return user.get_full_name() or user.email
        except Exception:
            return ""


class WriterProfileDetailSerializer(serializers.ModelSerializer):
    """
    Full writer profile for admin and writer detail views.

    Includes nested capacity and discipline state for
    dashboard display. Mutations go through dedicated
    action endpoints, not this serializer.
    """

    level_name = serializers.SerializerMethodField()
    level_id = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    # Capacity summary (inline — avoids extra request)
    can_take_orders = serializers.SerializerMethodField()
    is_accepting_orders = serializers.SerializerMethodField()
    active_orders_count = serializers.SerializerMethodField()
    # Discipline summary
    is_suspended = serializers.SerializerMethodField()
    is_blacklisted = serializers.SerializerMethodField()
    is_on_probation = serializers.SerializerMethodField()
    active_warning_count = serializers.SerializerMethodField()
    active_strike_count = serializers.SerializerMethodField()

    class Meta:
        model = WriterProfile
        fields = [
            "id",
            "public_uuid",
            "registration_id",
            "pen_name",
            "full_name",
            "email",
            "phone_number",
            "bio",
            "qualifications",
            "years_of_experience",
            "timezone",
            "level_id",
            "level_name",
            "is_verified",
            "verification_status",
            "onboarding_status",
            # Capacity
            "can_take_orders",
            "is_accepting_orders",
            "active_orders_count",
            # Discipline
            "is_suspended",
            "is_blacklisted",
            "is_on_probation",
            "active_warning_count",
            "active_strike_count",
            # Lifecycle
            "is_deleted",
            "deleted_at",
            "joined_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_level_name(self, obj) -> str | None:
        level = obj.writer_level
        return level.name if level is not None else None

    def get_level_id(self, obj) -> int | None:
        return obj.writer_level_id if hasattr(obj, "writer_level_id") else (
            obj.writer_level.pk if obj.writer_level else None
        )

    def get_full_name(self, obj) -> str:
        try:
            return obj.account_profile.user.get_full_name()
        except Exception:
            return ""

    def get_email(self, obj) -> str:
        try:
            return obj.account_profile.user.email
        except Exception:
            return ""

    def get_phone_number(self, obj) -> str | None:
        try:
            return obj.account_profile.user.phone_number or None
        except Exception:
            return None

    def _capacity(self, obj):
        try:
            return obj.capacity
        except Exception:
            return None

    def _discipline(self, obj):
        try:
            return obj.discipline_state
        except Exception:
            return None

    def get_can_take_orders(self, obj) -> bool:
        cap = self._capacity(obj)
        return cap.can_take_orders if cap else False

    def get_is_accepting_orders(self, obj) -> bool:
        cap = self._capacity(obj)
        return cap.is_accepting_orders if cap else False

    def get_active_orders_count(self, obj) -> int:
        cap = self._capacity(obj)
        return cap.active_orders_count if cap else 0

    def get_is_suspended(self, obj) -> bool:
        disc = self._discipline(obj)
        return disc.is_suspended if disc else False

    def get_is_blacklisted(self, obj) -> bool:
        disc = self._discipline(obj)
        return disc.is_blacklisted if disc else False

    def get_is_on_probation(self, obj) -> bool:
        disc = self._discipline(obj)
        return disc.is_on_probation if disc else False

    def get_active_warning_count(self, obj) -> int:
        disc = self._discipline(obj)
        return disc.active_warning_count if disc else 0

    def get_active_strike_count(self, obj) -> int:
        disc = self._discipline(obj)
        return disc.active_strike_count if disc else 0


class WriterProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Writer-editable fields only.
    Used for PATCH /api/writer-management/me/profile/

    Bio capped at 500 characters.
    Timezone validated as IANA string.
    Qualifications validated as list of dicts.
    """

    class Meta:
        model = WriterProfile
        fields = [
            "bio",
            "timezone",
            "qualifications",
            "years_of_experience",
        ]

    def validate_bio(self, value: str) -> str:
        if len(value) > 500:
            raise serializers.ValidationError(
                "Bio cannot exceed 500 characters."
            )
        return value.strip()

    def validate_timezone(self, value: str) -> str:
        import zoneinfo
        try:
            zoneinfo.ZoneInfo(value)
        except Exception:
            raise serializers.ValidationError(
                f"'{value}' is not a valid IANA timezone. "
                "Example: 'Africa/Nairobi', 'America/New_York'."
            )
        return value

    def validate_qualifications(self, value) -> list:
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "qualifications must be a list."
            )
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    f"qualifications[{i}] must be an object."
                )
            if "title" not in item:
                raise serializers.ValidationError(
                    f"qualifications[{i}] must have a 'title' field."
                )
        return value

    def validate_years_of_experience(self, value) -> int | None:
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "years_of_experience cannot be negative."
            )
        return value