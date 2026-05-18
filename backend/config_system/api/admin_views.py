from __future__ import annotations

from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config_system.api.serializers import (
    ConfigItemSerializer,
    ConfigUpdateSerializer,
)
from config_system.core.engine import FeatureEngine
from config_system.registry import CONFIG_REGISTRY, get_config_definition
from config_system.services.evaluator import ConfigEvaluator
from config_system.services.updater import ConfigUpdateError, ConfigUpdater
from config_system.storage.models import ConfigItem


# ============================================================
# Permissions
# ============================================================

class IsConfigAdmin(permissions.BasePermission):
    message = "You do not have permission to manage runtime configs."

    def has_permission( # type: ignore[reportOptionalMemberAccess]
            self,
            request: Request,
            view: Any
        ) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


# ============================================================
# Helpers (fix all Pylance nonsense at the boundary)
# ============================================================

def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_bool_str(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("1", "true", "yes", "on")
    return bool(value)


# ============================================================
# Config List
# ============================================================

class ConfigListView(APIView):
    permission_classes = [IsConfigAdmin]

    def get(self, request: Request) -> Response:
        queryset = ConfigItem.objects.filter(is_active=True).order_by("key")

        serializer = ConfigItemSerializer(queryset, many=True)
        return Response(serializer.data)


# ============================================================
# Config Detail
# ============================================================

class ConfigDetailView(APIView):
    permission_classes = [IsConfigAdmin]

    def get(self, request: Request, key: str) -> Response:
        definition = get_config_definition(key)

        if definition is None:
            return Response(
                {"detail": "Unknown config key."},
                status=status.HTTP_404_NOT_FOUND,
            )

        value = ConfigEvaluator.get(key)

        return Response(
            {
                "key": key,
                "value": value,
                "definition": {
                    "description": definition.description,
                    "config_type": definition.config_type.value,
                    "default": definition.default,
                    "is_runtime_editable": definition.is_runtime_editable,
                    "requires_restart": definition.requires_restart,
                    "enable_rollout": definition.enable_rollout,
                    "cache_ttl_seconds": definition.cache_ttl_seconds,
                },
            }
        )


# ============================================================
# Update Config
# ============================================================

class ConfigUpdateView(APIView):
    permission_classes = [IsConfigAdmin]

    def post(self, request: Request) -> Response:
        serializer = ConfigUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        key = cast(str, data.get("key"))
        value = data.get("value")

        if not key:
            return Response(
                {"detail": "key is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            obj = ConfigUpdater.set(
                key=key,
                value=value,
                actor=request.user,
                scope=cast(str, data.get("scope", "global")),
                environment=cast(str, data.get("environment", "prod")),
                website_id=_as_int(data.get("website_id")),
                tenant_id=_as_int(data.get("tenant_id")),
                user_id=_as_int(data.get("user_id")),
                reason=cast(str, data.get("reason", "")),
            )

        except ConfigUpdateError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(ConfigItemSerializer(obj).data, status=status.HTTP_200_OK)


# ============================================================
# Delete Config
# ============================================================

class ConfigDeleteView(APIView):
    permission_classes = [IsConfigAdmin]

    def delete(self, request: Request, key: str) -> Response:
        params = cast(dict[str, Any], request.query_params)

        try:
            ConfigUpdater.delete(
                key=key,
                actor=request.user,
                scope=cast(str, params.get("scope", "global")),
                website_id=_as_int(params.get("website_id")),
                tenant_id=_as_int(params.get("tenant_id")),
                user_id=_as_int(params.get("user_id")),
                reason=cast(str, params.get("reason", "")),
            )

        except ConfigUpdateError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Config deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )


# ============================================================
# Feature Check
# ============================================================

class FeatureCheckView(APIView):
    permission_classes = [IsConfigAdmin]

    def post(self, request: Request) -> Response:
        data = cast(dict[str, Any], request.data)

        key = cast(str, data.get("key"))

        if not key:
            return Response(
                {"detail": "key is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enabled = FeatureEngine.is_enabled(key=key)

        return Response({"key": key, "enabled": enabled})


# ============================================================
# Registry
# ============================================================

class ConfigRegistryView(APIView):
    permission_classes = [IsConfigAdmin]

    def get(self, request: Request) -> Response:
        payload: list[dict[str, Any]] = []

        for key, definition in CONFIG_REGISTRY.items():
            payload.append(
                {
                    "key": key,
                    "config_type": definition.config_type.value,
                    "default": definition.default,
                    "description": definition.description,
                    "is_runtime_editable": definition.is_runtime_editable,
                    "requires_restart": definition.requires_restart,
                    "enable_rollout": definition.enable_rollout,
                    "cache_ttl_seconds": definition.cache_ttl_seconds,
                }
            )

        return Response(payload)