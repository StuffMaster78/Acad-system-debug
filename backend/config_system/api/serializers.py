from __future__ import annotations

from rest_framework import serializers

from config_system.registry import (
    CONFIG_REGISTRY,
    require_config_definition,
)
from config_system.core.schema import ConfigType
from config_system.storage.models import ConfigItem


class ConfigItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConfigItem
        fields = (
            "id",
            "key",
            "value",
            "scope",
            "environment",
            "website_id",
            "tenant_id",
            "user_id",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class ConfigUpdateSerializer(serializers.Serializer):

    key = serializers.CharField(max_length=255)

    value = serializers.JSONField()

    scope = serializers.ChoiceField(
        choices=[
            "global",
            "tenant",
            "website",
            "user",
        ],
        default="global",
    )

    environment = serializers.CharField(
        default="prod",
    )

    website_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    tenant_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    user_id = serializers.IntegerField(
        required=False,
        allow_null=True,
    )

    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )

    # ---------------------------------------------------------
    # Key Validation
    # ---------------------------------------------------------

    def validate_key(
        self,
        value: str,
    ) -> str:

        if value not in CONFIG_REGISTRY:
            raise serializers.ValidationError(
                "Unknown config key."
            )

        return value

    # ---------------------------------------------------------
    # Runtime Mutability Validation
    # ---------------------------------------------------------

    def validate(self, attrs):

        key = attrs["key"]

        definition = require_config_definition(key)

        if not definition.is_runtime_editable:
            raise serializers.ValidationError(
                {
                    "key": (
                        "This config cannot "
                        "be edited at runtime."
                    )
                }
            )

        cls = self.__class__

        cls._validate_scope(attrs)

        cls._validate_value_type(
            definition=definition,
            value=attrs["value"],
        )

        cls._validate_rollout_percentage(
            key=key,
            value=attrs["value"],
        )

        return attrs

    # ---------------------------------------------------------
    # Scope Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_scope(attrs) -> None:

        scope = attrs.get("scope")

        if scope == "tenant" and not attrs.get("tenant_id"):
            raise serializers.ValidationError(
                {
                    "tenant_id": (
                        "tenant_id required "
                        "for tenant scope."
                    )
                }
            )

        if scope == "website" and not attrs.get("website_id"):
            raise serializers.ValidationError(
                {
                    "website_id": (
                        "website_id required "
                        "for website scope."
                    )
                }
            )

        if scope == "user" and not attrs.get("user_id"):
            raise serializers.ValidationError(
                {
                    "user_id": (
                        "user_id required "
                        "for user scope."
                    )
                }
            )

    # ---------------------------------------------------------
    # Type Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_value_type(
        *,
        definition,
        value,
    ) -> None:

        config_type = definition.config_type

        if config_type == ConfigType.BOOL:
            if not isinstance(value, bool):
                raise serializers.ValidationError(
                    {"value": "Expected boolean."}
                )

        elif config_type == ConfigType.INT:
            if not isinstance(value, int):
                raise serializers.ValidationError(
                    {"value": "Expected integer."}
                )

        elif config_type == ConfigType.FLOAT:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError(
                    {"value": "Expected float."}
                )

        elif config_type == ConfigType.STRING:
            if not isinstance(value, str):
                raise serializers.ValidationError(
                    {"value": "Expected string."}
                )

        elif config_type == ConfigType.LIST:
            if not isinstance(value, list):
                raise serializers.ValidationError(
                    {"value": "Expected list."}
                )

        elif config_type == ConfigType.JSON:
            if not isinstance(value, (dict, list)):
                raise serializers.ValidationError(
                    {"value": "Expected JSON object/list."}
                )

    # ---------------------------------------------------------
    # Rollout Safety Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_rollout_percentage(
        *,
        key: str,
        value,
    ) -> None:

        if not key.endswith(".rollout_percentage"):
            return

        try:
            percentage = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {
                    "value": (
                        "Rollout percentage "
                        "must be numeric."
                    )
                }
            )

        if percentage < 0 or percentage > 100:
            raise serializers.ValidationError(
                {
                    "value": (
                        "Rollout percentage "
                        "must be between 0 and 100."
                    )
                }
            )