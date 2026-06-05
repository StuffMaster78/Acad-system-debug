from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassOrder
from class_management.api.serializers.class_order_serializers import (
    ClassOrderActionContractMixin,
)


class ClientClassOrderDetailSerializer(ClassOrderActionContractMixin, serializers.ModelSerializer):
    class Meta:
        model = ClassOrder
        fields = [
            "id",
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
            "quoted_amount",
            "accepted_amount",
            "discount_code",
            "discount_amount",
            "final_amount",
            "paid_amount",
            "balance_amount",
            "currency",
            "is_work_paused",
            "pause_reason",
            "submitted_at",
            "accepted_at",
            "completed_at",
            "cancelled_at",
            "available_actions",
            "blocked_actions",
            "created_at",
            "updated_at",
        ]


class WriterClassOrderDetailSerializer(ClassOrderActionContractMixin, serializers.ModelSerializer):
    class Meta:
        model = ClassOrder
        fields = [
            "id",
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
            "complexity_level",
            "writer_visible_notes",
            "is_work_paused",
            "pause_reason",
            "submitted_at",
            "completed_at",
            "available_actions",
            "blocked_actions",
            "created_at",
            "updated_at",
        ]
