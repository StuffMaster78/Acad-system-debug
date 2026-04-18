from __future__ import annotations

from rest_framework import serializers

from orders.models.legacy_models.unpaid_order_message import UnpaidOrderMessage


class UnpaidOrderMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for unpaid order reminder message configuration.
    """

    class Meta:
        model = UnpaidOrderMessage
        fields = (
            "id",
            "website",
            "name",
            "sequence_number",
            "interval_hours",
            "subject",
            "message",
            "is_active",
            "cancel_order_after_send",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        )

    def validate_interval_hours(self, value: int) -> int:
        """
        Ensure interval hours is greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError(
                "Interval hours must be greater than zero."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Prevent impossible sequencing choices in client input.
        """
        cancel_after_send = attrs.get(
            "cancel_order_after_send",
            getattr(self.instance, "cancel_order_after_send", False),
        )
        is_active = attrs.get(
            "is_active",
            getattr(self.instance, "is_active", True),
        )

        if cancel_after_send and not is_active:
            raise serializers.ValidationError(
                "A final cancellation message must be active."
            )

        return attrs