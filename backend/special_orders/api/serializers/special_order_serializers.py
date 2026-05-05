from __future__ import annotations

from rest_framework import serializers

from special_orders.models import SpecialOrder


class CreateQuotedSpecialOrderSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    inquiry_details = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    budget = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    duration_days = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
    )
    currency = serializers.CharField(
        required=False,
        default="USD",
        max_length=10,
    )


class CreateFixedSpecialOrderSerializer(serializers.Serializer):
    predefined_config_id = serializers.IntegerField()
    predefined_duration_id = serializers.IntegerField()

    title = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    inquiry_details = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    currency = serializers.CharField(
        required=False,
        default="USD",
        max_length=10,
    )

    platform = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=80,
    )
    writer_level = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=50,
    )
    coupon_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
    )


class SpecialOrderListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.get_full_name",
        read_only=True,
    )
    writer_name = serializers.CharField(
        source="writer.get_full_name",
        read_only=True,
    )
    predefined_config_name = serializers.CharField(
        source="predefined_config.name",
        read_only=True,
    )

    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "title",
            "pricing_mode",
            "status",
            "origin",
            "priority",
            "currency",
            "duration_days",
            "client",
            "client_name",
            "writer",
            "writer_name",
            "predefined_config",
            "predefined_config_name",
            "created_at",
            "updated_at",
        ]


class SpecialOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialOrder
        fields = [
            "id",
            "title",
            "inquiry_details",
            "admin_notes",
            "budget",
            "duration_days",
            "currency",
            "pricing_mode",
            "status",
            "origin",
            "priority",
            "client",
            "writer",
            "predefined_config",
            "predefined_duration",
            "writer_pay_rule",
            "accepted_quote",
            "converted_order",
            "assigned_at",
            "started_at",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]