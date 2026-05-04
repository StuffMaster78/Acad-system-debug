from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassOrder


class ClassOrderListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(
        source="client.get_full_name",
        read_only=True,
    )
    assigned_writer_name = serializers.CharField(
        source="assigned_writer.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassOrder
        fields = [
            "id",
            "title",
            "client",
            "client_name",
            "assigned_writer",
            "assigned_writer_name",
            "status",
            "payment_status",
            "institution_name",
            "class_name",
            "class_subject",
            "academic_level",
            "final_amount",
            "paid_amount",
            "balance_amount",
            "currency",
            "is_work_paused",
            "pause_reason",
            "created_at",
            "updated_at",
        ]


class ClassOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassOrder
        fields = [
            "id",
            "website",
            "client",
            "assigned_writer",
            "title",
            "institution_name",
            "institution_state",
            "class_name",
            "class_code",
            "class_subject",
            "academic_level",
            "starts_on",
            "ends_on",
            "status",
            "payment_status",
            "complexity_level",
            "initial_client_notes",
            "writer_visible_notes",
            "admin_internal_notes",
            "quoted_amount",
            "accepted_amount",
            "discount_amount",
            "final_amount",
            "paid_amount",
            "balance_amount",
            "currency",
            "pricing_snapshot",
            "discount_snapshot",
            "is_work_paused",
            "pause_reason",
            "paused_at",
            "submitted_at",
            "accepted_at",
            "completed_at",
            "cancelled_at",
            "archived_at",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "website",
            "status",
            "payment_status",
            "quoted_amount",
            "accepted_amount",
            "discount_amount",
            "final_amount",
            "paid_amount",
            "balance_amount",
            "pricing_snapshot",
            "discount_snapshot",
            "submitted_at",
            "accepted_at",
            "completed_at",
            "cancelled_at",
            "archived_at",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


class ClassOrderCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    institution_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    institution_state = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )
    class_name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    class_code = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )
    class_subject = serializers.CharField(
        max_length=180,
        required=False,
        allow_blank=True,
    )
    academic_level = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )
    starts_on = serializers.DateField(required=False, allow_null=True)
    ends_on = serializers.DateField(required=False, allow_null=True)
    initial_client_notes = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ClassOrderActionSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class ClassOrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField()