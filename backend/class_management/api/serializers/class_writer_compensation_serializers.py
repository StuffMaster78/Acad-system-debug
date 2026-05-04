from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassWriterCompensation


class ClassWriterCompensationSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(
        source="writer.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassWriterCompensation
        fields = "__all__"
        read_only_fields = [
            "final_amount",
            "paid_amount",
            "status",
            "wallet_transaction_id",
            "ledger_entry_id",
            "approved_by",
            "posted_by",
            "approved_at",
            "earned_at",
            "posted_at",
            "created_at",
            "updated_at",
        ]


class SetWriterCompensationSerializer(serializers.Serializer):
    writer_id = serializers.IntegerField()
    compensation_type = serializers.ChoiceField(
        choices=[
            ("percentage", "Percentage"),
            ("fixed_amount", "Fixed Amount"),
        ]
    )
    percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    fixed_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    admin_notes = serializers.CharField(required=False, allow_blank=True)