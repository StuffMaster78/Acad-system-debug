from __future__ import annotations

from rest_framework import serializers

from payments_processor.models.gateway_config import PaymentGatewayConfig, PaymentNotificationEmail


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)
    website_slug = serializers.CharField(source="website.slug", read_only=True)
    effective_callback_base_url = serializers.CharField(read_only=True)
    # Whether each env var is actually populated (never expose the value)
    secret_key_configured = serializers.SerializerMethodField()
    webhook_secret_configured = serializers.SerializerMethodField()

    class Meta:
        model = PaymentGatewayConfig
        fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "website_slug",
            "gateway",
            "webhook_endpoint",
            "callback_base_url",
            "effective_callback_base_url",
            "mode",
            "is_active",
            "statement_descriptor",
            "secret_key_env_var",
            "webhook_secret_env_var",
            "secret_key_configured",
            "webhook_secret_configured",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "website_name",
            "website_domain",
            "website_slug",
            "effective_callback_base_url",
            "secret_key_configured",
            "webhook_secret_configured",
            "updated_at",
        ]

    def get_secret_key_configured(self, obj: PaymentGatewayConfig) -> bool:
        return bool(obj.effective_secret_key)

    def get_webhook_secret_configured(self, obj: PaymentGatewayConfig) -> bool:
        return bool(obj.effective_webhook_secret)


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
