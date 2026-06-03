from __future__ import annotations

from rest_framework import serializers

from websites.models.website_branding import (
    PaymentDisclosureAcknowledgement,
    WebsiteBranding,
)


class PaymentDisclosureConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)
    processor_display_name = serializers.CharField(
        source="payment_processor_name",
        required=False,
        allow_blank=True,
    )
    statement_descriptor = serializers.CharField(
        source="payment_statement_descriptor",
        required=False,
        allow_blank=True,
        max_length=22,
    )
    client_disclosure_text = serializers.CharField(
        source="payment_client_disclosure_text",
        required=False,
        allow_blank=True,
    )
    support_contact = serializers.CharField(
        source="payment_support_contact",
        required=False,
        allow_blank=True,
    )
    requires_acknowledgement = serializers.BooleanField(
        source="payment_requires_acknowledgement",
        required=False,
    )

    class Meta:
        model = WebsiteBranding
        fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "brand_name",
            "processor_display_name",
            "statement_descriptor",
            "client_disclosure_text",
            "support_contact",
            "requires_acknowledgement",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "updated_at",
        ]


class PaymentDisclosureAcknowledgementSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=["shown", "acknowledged"])
    context = serializers.CharField(required=False, allow_blank=True, max_length=80)
    reference_type = serializers.CharField(required=False, allow_blank=True, max_length=80)
    reference_id = serializers.CharField(required=False, allow_blank=True, max_length=80)


class PaymentDisclosureAcknowledgementRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDisclosureAcknowledgement
        fields = [
            "id",
            "website",
            "user",
            "processor_display_name",
            "statement_descriptor",
            "client_disclosure_text",
            "support_contact",
            "context",
            "reference_type",
            "reference_id",
            "shown_at",
            "acknowledged_at",
            "created_at",
        ]
        read_only_fields = fields
