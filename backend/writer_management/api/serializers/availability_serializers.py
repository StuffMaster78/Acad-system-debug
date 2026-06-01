from rest_framework import serializers
from writer_management.models.writer_availability import (
    WriterAvailabilityWindow,
    WriterAvailabilityPreference,
    UnavailabilityReason,
)


class WriterAvailabilityWindowSerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(
        source="get_reason_display", read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)
    is_future = serializers.BooleanField(read_only=True)

    class Meta:
        model = WriterAvailabilityWindow
        fields = [
            "id",
            "reason",
            "reason_display",
            "note",
            "start_at",
            "end_at",
            "is_active",
            "is_future",
            "created_at",
        ]
        read_only_fields = [
            "id", "reason_display", "is_active", "is_future", "created_at"
        ]


class DeclareUnavailableSerializer(serializers.Serializer):
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField(required=False)
    reason = serializers.ChoiceField(
        choices=UnavailabilityReason.choices,
        default=UnavailabilityReason.PERSONAL,
    )
    note = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )

    def validate(self, data):
        end_at = data.get("end_at")
        start_at = data.get("start_at")
        if end_at and end_at <= start_at:
            raise serializers.ValidationError(
                {"end_at": "end_at must be after start_at."}
            )
        return data


class WriterAvailabilityPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterAvailabilityPreference
        fields = [
            "preferred_start_hour",
            "preferred_end_hour",
            "preferred_days",
            "auto_go_offline",
            "auto_offline_after_minutes",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]