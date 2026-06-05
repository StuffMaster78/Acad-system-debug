from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassServiceConfig


class ClassServiceConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)
    website_domain = serializers.CharField(source="website.domain", read_only=True)
    created_by_name = serializers.SerializerMethodField()

    def get_created_by_name(self, obj) -> str | None:
        user = getattr(obj, "created_by", None)
        if user is None:
            return None
        full_name = getattr(user, "get_full_name", lambda: "")()
        return full_name or getattr(user, "username", None) or getattr(user, "email", None)

    class Meta:
        model = ClassServiceConfig
        fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "name",
            "slug",
            "description",
            "service_type",
            "pricing_mode",
            "base_price",
            "currency",
            "duration_options",
            "workload_options",
            "task_options",
            "required_fields",
            "requires_portal_access",
            "allow_installments",
            "require_deposit_before_start",
            "deposit_percentage",
            "quote_expiry_hours",
            "is_active",
            "display_order",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "website",
            "website_name",
            "website_domain",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
