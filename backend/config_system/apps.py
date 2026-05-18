from __future__ import annotations

import logging

from django.apps import AppConfig

from config_system.core.schema import ConfigType
from config_system.registry import CONFIG_REGISTRY


logger = logging.getLogger(__name__)


class ConfigSystemConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "config_system"

    verbose_name = "Runtime Config System"

    def ready(self) -> None:
        """
        Boot-time validation.

        Fail fast if registry integrity is broken.
        """

        self._validate_registry()

        logger.info(
            "Config system initialized successfully."
        )

    # ---------------------------------------------------------
    # Registry Validation
    # ---------------------------------------------------------

    def _validate_registry(self) -> None:

        seen_keys: set[str] = set()

        for key, definition in CONFIG_REGISTRY.items():

            # -------------------------------------------------
            # Duplicate Keys
            # -------------------------------------------------

            if key in seen_keys:
                raise RuntimeError(
                    f"Duplicate config key detected: {key}"
                )

            seen_keys.add(key)

            # -------------------------------------------------
            # Registry Key Integrity
            # -------------------------------------------------

            if definition.key != key:
                raise RuntimeError(
                    (
                        "Registry key mismatch detected. "
                        f"Registry='{key}' "
                        f"Definition='{definition.key}'"
                    )
                )

            # -------------------------------------------------
            # Default Type Validation
            # -------------------------------------------------

            self._validate_default_type(
                key=key,
                config_type=definition.config_type,
                default=definition.default,
            )

            # -------------------------------------------------
            # TTL Validation
            # -------------------------------------------------

            if definition.cache_ttl_seconds < 0:
                raise RuntimeError(
                    (
                        f"{key} has invalid cache TTL: "
                        f"{definition.cache_ttl_seconds}"
                    )
                )

            # -------------------------------------------------
            # Environment Validation
            # -------------------------------------------------

            if not definition.allowed_environments:
                raise RuntimeError(
                    (
                        f"{key} has no allowed environments."
                    )
                )

    # ---------------------------------------------------------
    # Type Safety Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_default_type(
        *,
        key: str,
        config_type: ConfigType,
        default,
    ) -> None:

        if default is None:
            return

        if config_type == ConfigType.BOOL:
            if not isinstance(default, bool):
                raise RuntimeError(
                    f"{key} default must be bool"
                )

        elif config_type == ConfigType.INT:
            if not isinstance(default, int):
                raise RuntimeError(
                    f"{key} default must be int"
                )

        elif config_type == ConfigType.FLOAT:
            if not isinstance(default, (int, float)):
                raise RuntimeError(
                    f"{key} default must be float"
                )

        elif config_type == ConfigType.STRING:
            if not isinstance(default, str):
                raise RuntimeError(
                    f"{key} default must be string"
                )

        elif config_type == ConfigType.LIST:
            if not isinstance(default, list):
                raise RuntimeError(
                    f"{key} default must be list"
                )

        elif config_type == ConfigType.JSON:
            if not isinstance(default, (dict, list)):
                raise RuntimeError(
                    f"{key} default must be json"
                )