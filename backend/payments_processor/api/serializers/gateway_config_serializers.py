from __future__ import annotations

from rest_framework import serializers

from payments_processor.models.gateway_config import PaymentGatewayConfig, PaymentNotificationEmail


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)
    effective_callback_base_url = serializers.CharField(read_only=True)

    class Meta:
        model = PaymentGatewayConfig
        fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "gateway",
            "webhook_endpoint",
            "callback_base_url",
            "effective_callback_base_url",
            "mode",
            "is_active",
            "updated_at",
        ]
        read_only_fields = ["id", "website_name", "website_domain", "effective_callback_base_url", "updated_at"]


class PaymentNotificationEmailSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)

    class Meta:
        model = PaymentNotificationEmail
        fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "email",
            "label",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "website_name", "website_domain", "created_at"]
