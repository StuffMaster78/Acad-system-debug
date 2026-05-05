from __future__ import annotations

from typing import Any

from rest_framework import serializers

from communications.models.screening_rule import CommunicationScreeningRule
from communications.services.screening_rule_service import (
    CommunicationScreeningRuleService,
)


class CommunicationScreeningRuleSerializer(serializers.ModelSerializer):
    """
    Read serializer for screening rules.
    """

    class Meta:
        model = CommunicationScreeningRule
        fields = [
            "id",
            "website",
            "name",
            "pattern",
            "match_type",
            "action",
            "severity",
            "replacement_text",
            "reason",
            "is_active",
            "is_platform_rule",
            "created_by",
            "updated_by",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CommunicationScreeningRuleCreateSerializer(serializers.Serializer):
    """
    Create or update screening rules.
    """

    website = serializers.PrimaryKeyRelatedField(
        queryset=CommunicationScreeningRule._meta.get_field(
            "website",
        ).remote_field.model.objects.all(),
        required=False,
        allow_null=True,
    )
    name = serializers.CharField(max_length=120)
    pattern = serializers.CharField(max_length=255)
    match_type = serializers.CharField(max_length=20)
    action = serializers.CharField(max_length=30)
    severity = serializers.CharField(max_length=20)
    replacement_text = serializers.CharField(
        max_length=80,
        required=False,
        default="*****",
    )
    reason = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )
    is_platform_rule = serializers.BooleanField(default=False)
    metadata = serializers.DictField(required=False)

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> CommunicationScreeningRule:
        """
        Create screening rule through service.
        """
        request = self.context["request"]

        return CommunicationScreeningRuleService.create_rule(
            website=validated_data.get("website"),
            name=validated_data["name"],
            pattern=validated_data["pattern"],
            match_type=validated_data["match_type"],
            action=validated_data["action"],
            severity=validated_data["severity"],
            replacement_text=validated_data.get("replacement_text", "*****"),
            reason=validated_data.get("reason", ""),
            is_platform_rule=validated_data.get("is_platform_rule", False),
            created_by=request.user,
            metadata=validated_data.get("metadata"),
        )