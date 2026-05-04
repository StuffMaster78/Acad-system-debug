from __future__ import annotations

from rest_framework import serializers

from class_management.models import (
    ClassPriceCounterOffer,
    ClassPriceProposal,
)


class ClassPriceProposalSerializer(serializers.ModelSerializer):
    proposed_by_name = serializers.CharField(
        source="proposed_by.get_full_name",
        read_only=True,
    )
    accepted_by_name = serializers.CharField(
        source="accepted_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassPriceProposal
        fields = "__all__"
        read_only_fields = [
            "final_amount",
            "status",
            "sent_at",
            "accepted_at",
            "rejected_at",
            "proposed_by",
            "accepted_by",
            "created_at",
            "updated_at",
        ]


class CreatePriceProposalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    discount_code = serializers.CharField(required=False, allow_blank=True)
    message_to_client = serializers.CharField(required=False, allow_blank=True)
    internal_notes = serializers.CharField(required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    send_now = serializers.BooleanField(default=False)


class ClassPriceCounterOfferSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassPriceCounterOffer
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class CreateCounterOfferSerializer(serializers.Serializer):
    offered_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    message = serializers.CharField(required=False, allow_blank=True)


class RejectProposalSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)