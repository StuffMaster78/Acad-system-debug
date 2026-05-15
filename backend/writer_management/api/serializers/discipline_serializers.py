"""
Serializers for discipline models:
    WriterWarning, WriterStrike, WriterSuspension,
    WriterBlacklist, WriterProbation, WriterPenalty,
    WriterDisciplineState
"""

from rest_framework import serializers

from writer_management.models.writer_warning import WriterWarning
from writer_management.models.writer_strike import WriterStrike
from writer_management.models.writer_discipline import (
    WriterSuspension,
    WriterBlacklist,
    WriterProbation,
    WriterPenalty,
)
from writer_management.models.writer_discipline_state import (
    WriterDisciplineState,
)


class WriterWarningSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )
    issued_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterWarning
        fields = [
            "id",
            "writer",
            "category",
            "category_display",
            "reason",
            "is_active",
            "is_voided",
            "expires_at",
            "days_remaining",
            "issued_by",
            "issued_by_name",
            "is_currently_active",
            "created_at",
        ]
        read_only_fields = fields

    def get_issued_by_name(self, obj) -> str:
        user = obj.issued_by
        if user is None:
            return "System"
        return user.get_full_name() or user.email


class IssueWarningSerializer(serializers.Serializer):
    """Input for issuing a warning."""
    reason = serializers.CharField(min_length=10)
    category = serializers.ChoiceField(
        choices=WriterWarning._meta.get_field("category").choices
    )
    expires_days = serializers.IntegerField(
        min_value=1, max_value=365, required=False
    )


class VoidWarningSerializer(serializers.Serializer):
    """Input for voiding a warning."""
    reason = serializers.CharField(min_length=10)


class WriterStrikeSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
    )
    issued_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterStrike
        fields = [
            "id",
            "writer",
            "category",
            "category_display",
            "reason",
            "evidence_notes",
            "is_voided",
            "void_reason",
            "voided_at",
            "writer_notified",
            "issued_by",
            "issued_by_name",
            "counts_toward_threshold",
            "issued_at",
        ]
        read_only_fields = fields

    def get_issued_by_name(self, obj) -> str:
        user = obj.issued_by
        if user is None:
            return "System"
        return user.get_full_name() or user.email


class IssueStrikeSerializer(serializers.Serializer):
    """Input for issuing a strike."""
    reason = serializers.CharField(min_length=10)
    category = serializers.ChoiceField(
        choices=WriterStrike._meta.get_field("category").choices
    )
    evidence_notes = serializers.CharField(required=False, allow_blank=True)


class VoidStrikeSerializer(serializers.Serializer):
    """Input for voiding a strike."""
    reason = serializers.CharField(min_length=10)


class WriterSuspensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterSuspension
        fields = [
            "id",
            "writer",
            "reason",
            "auto_triggered",
            "start_date",
            "end_date",
            "is_active",
            "lifted_at",
            "lift_reason",
        ]
        read_only_fields = fields


class SuspendWriterSerializer(serializers.Serializer):
    """Input for suspending a writer."""
    reason = serializers.CharField(min_length=10)
    duration_days = serializers.IntegerField(
        min_value=1, max_value=365, required=False,
        help_text="Omit for indefinite suspension."
    )


class LiftSuspensionSerializer(serializers.Serializer):
    """Input for lifting a suspension."""
    reason = serializers.CharField(min_length=5)


class WriterBlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterBlacklist
        fields = [
            "id",
            "writer",
            "reason",
            "auto_triggered",
            "blacklisted_at",
            "is_active",
            "lifted_at",
            "lift_reason",
        ]
        read_only_fields = fields


class BlacklistWriterSerializer(serializers.Serializer):
    """Input for blacklisting a writer."""
    reason = serializers.CharField(min_length=10)


class LiftBlacklistSerializer(serializers.Serializer):
    """Input for lifting a blacklist."""
    reason = serializers.CharField(min_length=10)


class WriterProbationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterProbation
        fields = [
            "id",
            "writer",
            "reason",
            "auto_triggered",
            "start_date",
            "end_date",
            "is_active",
            "ended_at",
        ]
        read_only_fields = fields


class PlaceProbationSerializer(serializers.Serializer):
    """Input for placing a writer on probation."""
    reason = serializers.CharField(min_length=10)
    duration_days = serializers.IntegerField(min_value=1, default=30)


class WriterPenaltySerializer(serializers.ModelSerializer):
    reason_display = serializers.CharField(
        source="get_reason_display", read_only=True
    )

    class Meta:
        model = WriterPenalty
        fields = [
            "id",
            "writer",
            "order",
            "reason",
            "reason_display",
            "amount_deducted",
            "notes",
            "created_at",
        ]
        read_only_fields = fields


class ApplyPenaltySerializer(serializers.Serializer):
    """Input for applying a penalty."""
    reason = serializers.ChoiceField(
        choices=WriterPenalty.PenaltyReason.choices
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class WriterDisciplineStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WriterDisciplineState
        fields = [
            "is_suspended",
            "is_blacklisted",
            "is_on_probation",
            "is_restricted",
            "active_strike_count",
            "lifetime_strike_count",
            "active_warning_count",
            "lifetime_warning_count",
            "suspension_ends_at",
            "probation_ends_at",
            "last_discipline_event_at",
            "updated_at",
        ]
        read_only_fields = fields