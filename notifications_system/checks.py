from __future__ import annotations

from django.core.checks import register, Error, Warning
from django.conf import settings

from notifications_system.registry.notification_event_loader import load_event_configs
from notifications_system.registry.main_registry import NOTIFICATION_REGISTRY
from notifications_system.registry.template_registry import (
    autoload_all_templates,
)
from pathlib import Path
# We’ll access the internal dict for a precise check.
# If you prefer, expose a public helper in template_registry instead.
from notifications_system.registry import template_registry as _tpl_mod


@register()
def check_notification_templates(app_configs, **kwargs):
    """
    System checks:
      1) Each configured event has a class-based template registered.
      2) If an event declares channel->template filenames, ensure they exist (name-only check).
    """
    errors = []

    # Ensure registries are populated (AppConfig.ready() should already do this,
    # but running here makes the check self-sufficient).
    try:
        autoload_all_templates()
    except Exception as exc:
        errors.append(Error(
            f"Failed to autoload notification templates: {exc}",
            id="notifications_system.E000",
        ))
        return errors

    try:
        load_event_configs()
    except Exception as exc:
        errors.append(Error(
            f"Failed to load event configs: {exc}",
            id="notifications_system.E000",
        ))
        return errors

    template_classes = getattr(_tpl_mod, "_TEMPLATE_CLASSES", {})  # event_key -> class

    # 1) Every configured event should have a class-based template
    for event_key, cfg in (NOTIFICATION_REGISTRY or {}).items():
        if event_key not in template_classes:
            errors.append(Warning(
                f"No class-based template registered for event '{event_key}'. "
                "Rendering will fall back to BaseNotificationTemplate.",
                id="notifications_system.W001",
            ))

        # 2) Optional: If config declares per-channel template filenames, ensure the mapping exists.
        # (We can only verify the presence of a name, not the file existence here.)
        templates_map = (cfg or {}).get("templates") or {}
        for ch, tpl_name in templates_map.items():
            if not isinstance(tpl_name, str) or not tpl_name.strip():
                errors.append(Warning(
                    f"Event '{event_key}' declares an empty/invalid template name for channel '{ch}'.",
                    id="notifications_system.W002",
                ))

    if not NOTIFICATION_REGISTRY:
        errors.append(Warning(
            "No notification events were loaded into NOTIFICATION_REGISTRY. "
            "Add JSON config files or check NOTIFY_EVENTS_DIR settings.",
            id="notifications_system.W003",
        ))

    return errors


@register()
def check_notifications_redis(app_configs, **kwargs):
    """
    Verifies that Redis is reachable for the notifications system.
    Set NOTIFICATIONS_DISABLE_REDIS_CHECK=True to skip.
    """
    errors = []

    if getattr(settings, "NOTIFICATIONS_DISABLE_REDIS_CHECK", False):
        return errors  # explicitly skipped

    try:
        from .redis_health import check_redis_health
    except Exception as exc:  # very defensive in case of import errors
        errors.append(
            Error(
                "Could not import notifications_system.redis_health module.",
                hint="Ensure redis-py is installed and the module path is correct.",
                obj="notifications_system.redis_health",
                id="notifications_system.E009",
            )
        )
        return errors

    ok = False
    try:
        ok = check_redis_health()
    except Exception as exc:
        errors.append(
            Error(
                "Redis health check raised an exception.",
                hint="Inspect logs for the underlying error and verify REDIS_URL.",
                obj="notifications_system.redis_health.check_redis_health",
                id="notifications_system.E010",
            )
        )
        return errors

    if not ok:
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        errors.append(
            Error(
                "Redis is unreachable for notifications.",
                hint=(
                    "Verify REDIS_URL, the Redis server is running, "
                    "network/firewall allows access, and credentials are correct. "
                    f"Current REDIS_URL: {redis_url}"
                ),
                obj="notifications_system.redis_health",
                id="notifications_system.E011",
            )
        )

    return errors


@register()
def check_notification_config_schemas(app_configs, **kwargs):
    """
    Validates presence and schema correctness of notifications JSON configs:
      - configs/schemas/*.json (schema files)
      - configs/notification_event_config.json        (map/list of events)
      - configs/broadcast_event_config.json           (list)
      - configs/digest_event_config.json              (list)
    """
    errors = []

    try:
        # Local imports to avoid import side-effects during Django app loading
        from notifications_system.registry.validator import (
            SCHEMA_BASE_DIR,
            validate_events_file,
            validate_config_file,
        )
        from notifications_system.registry.notification_event_loader import (
            CONFIGS_DIR as _CONFIGS_DIR,
        )
    except Exception as exc:
        errors.append(
            Error(
                "Could not import validator/loader for notification configs.",
                hint="Check PYTHONPATH and module paths under notifications_system.registry.*",
                obj="notifications_system.registry",
                id="notifications_system.E020",
            )
        )
        return errors

    # Where configs live (you set this up already)
    CONFIGS_DIR = _CONFIGS_DIR  # notifications_system/registry/configs
    SCHEMAS_DIR = SCHEMA_BASE_DIR  # notifications_system/registry/configs/schemas

    # --- 1) Schemas directory must exist ---
    if not SCHEMAS_DIR.exists():
        errors.append(
            Error(
                f"Schema directory not found: {SCHEMAS_DIR}",
                hint="Ensure your schema files are under configs/schemas/ (e.g. event_config_schema.json, broadcast_event.schema.json).",
                obj=str(SCHEMAS_DIR),
                id="notifications_system.E021",
            )
        )
        return errors  # no point continuing without schemas

    # Required schema files
    required_schema_files = {
        "event_config_schema.json",
        "base_event.schema.json",
        "user_event.schema.json",
        "order_event.schema.json",
        "wallet_event.schema.json",
        "broadcast_event.schema.json",
        "digest_event.schema.json",
    }

    missing = [f for f in required_schema_files if not (SCHEMAS_DIR / f).exists()]
    if missing:
        errors.append(
            Error(
                "Missing schema files in configs/schemas/.",
                hint=f"Add the missing files: {', '.join(missing)}",
                obj=str(SCHEMAS_DIR),
                id="notifications_system.E022",
            )
        )

    # Common pitfall: event_config_schema.json accidentally placed in configs/ (root) instead of schemas/
    misplaced_event_schema = (CONFIGS_DIR / "event_config_schema.json")
    if misplaced_event_schema.exists() and not (SCHEMAS_DIR / "event_config_schema.json").exists():
        errors.append(
            Warning(
                "event_config_schema.json is in configs/ but should be in configs/schemas/.",
                hint=f"Move {misplaced_event_schema} → {SCHEMAS_DIR / 'event_config_schema.json'}",
                obj=str(misplaced_event_schema),
                id="notifications_system.W023",
            )
        )

    # --- 2) Validate each config file ---
    notification_cfg = CONFIGS_DIR / "notification_event_config.json"
    broadcast_cfg    = CONFIGS_DIR / "broadcast_event_config.json"
    digest_cfg       = CONFIGS_DIR / "digest_event_config.json"

    # notification_event_config.json (map or list form, uses per-key schemas)
    if notification_cfg.exists():
        try:
            res = validate_events_file(notification_cfg)
            if not res.ok:
                errors.append(
                    Error(
                        f"notification_event_config.json failed validation.",
                        hint="Fix the following:\n- " + "\n- ".join(res.errors[:10]) + ("\n… (truncated)" if len(res.errors) > 10 else ""),
                        obj=str(notification_cfg),
                        id="notifications_system.E024",
                    )
                )
        except Exception as exc:
            errors.append(
                Error(
                    "Exception while validating notification_event_config.json.",
                    hint="Check JSON structure and referenced schemas.",
                    obj=str(notification_cfg),
                    id="notifications_system.E025",
                )
            )
    else:
        errors.append(
            Warning(
                "notification_event_config.json not found.",
                hint=f"Create it at {notification_cfg} (map or list of events).",
                obj=str(CONFIGS_DIR),
                id="notifications_system.W026",
            )
        )

    # broadcast_event_config.json
    if broadcast_cfg.exists():
        try:
            res = validate_config_file(broadcast_cfg, schema_name="broadcast_event.schema")
            if not res.ok:
                errors.append(
                    Error(
                        "broadcast_event_config.json failed validation.",
                        hint="Fix the following:\n- " + "\n- ".join(res.errors[:10]) + ("\n… (truncated)" if len(res.errors) > 10 else ""),
                        obj=str(broadcast_cfg),
                        id="notifications_system.E027",
                    )
                )
        except Exception:
            errors.append(
                Error(
                    "Exception while validating broadcast_event_config.json.",
                    hint="Ensure it is a list of objects matching broadcast_event.schema.",
                    obj=str(broadcast_cfg),
                    id="notifications_system.E028",
                )
            )
    else:
        errors.append(
            Warning(
                "broadcast_event_config.json not found.",
                hint=f"Create it at {broadcast_cfg} if you plan to use broadcast events.",
                obj=str(CONFIGS_DIR),
                id="notifications_system.W029",
            )
        )

    # digest_event_config.json
    if digest_cfg.exists():
        try:
            res = validate_config_file(digest_cfg, schema_name="digest_event.schema")
            if not res.ok:
                errors.append(
                    Error(
                        "digest_event_config.json failed validation.",
                        hint="Fix the following:\n- " + "\n- ".join(res.errors[:10]) + ("\n… (truncated)" if len(res.errors) > 10 else ""),
                        obj=str(digest_cfg),
                        id="notifications_system.E030",
                    )
                )
        except Exception:
            errors.append(
                Error(
                    "Exception while validating digest_event_config.json.",
                    hint="Ensure it is a list of objects matching digest_event.schema.",
                    obj=str(digest_cfg),
                    id="notifications_system.E031",
                )
            )
    else:
        errors.append(
            Warning(
                "digest_event_config.json not found.",
                hint=f"Create it at {digest_cfg} if you plan to use digests.",
                obj=str(CONFIGS_DIR),
                id="notifications_system.W032",
            )
        )

    return errors


@register()
def check_notification_events_loadable(app_configs, **kwargs):
    """
    Dry-runs event config loading and surfaces problems early:
      - JSON parsing / schema validation errors (raised by loader/validator)
      - Duplicate event keys (loader raises)
      - Unknown roles used by events (not registered in role registry)
      - Unknown channels (not in NotificationChannel)
    """
    errors = []

    # Import locally to avoid circulars during Django app init
    try:
        from notifications_system.registry.notification_event_loader import load_event_configs
        from notifications_system.registry.main_registry import NOTIFICATION_REGISTRY
        try:
            # Prefer the richer role registry if present
            from notifications_system.registry.role_registry import ROLE_RESOLVERS as _ROLE_RESOLVERS
            role_source = "role_registry"
        except Exception:
            _ROLE_RESOLVERS = {}
            role_source = None

        from notifications_system.enums import NotificationChannel
    except Exception as exc:
        errors.append(
            Error(
                "Failed to import notification registries/loaders.",
                hint=f"Import error: {exc}",
                obj="notifications_system.registry",
                id="notifications_system.E040",
            )
        )
        return errors

    # 1) Try loading all event configs (central + per-app).
    #    The loader already validates schemas and will raise on duplicates.
    try:
        load_event_configs()
    except Exception as exc:
        errors.append(
            Error(
                "Event config load failed.",
                hint=f"Fix the configuration JSON and schemas. Loader error: {exc}",
                obj="notifications_system.registry.notification_event_loader",
                id="notifications_system.E041",
            )
        )
        return errors  # further checks depend on a loaded registry

    # 2) Sanity-check the loaded entries
    allowed_channels = {c.value for c in NotificationChannel}
    unknown_channel_uses = []
    unknown_roles = []

    for event_key, cfg in (NOTIFICATION_REGISTRY or {}).items():
        # channels (schema should enforce, but we guard anyway)
        for ch in cfg.get("channels", []):
            if ch not in allowed_channels:
                unknown_channel_uses.append((event_key, ch))

        # forced_channels (same)
        for ch in cfg.get("forced_channels", []):
            if ch not in allowed_channels:
                unknown_channel_uses.append((event_key, ch))

        # roles (warn if not in the role registry, when available)
        if _ROLE_RESOLVERS:
            for role in cfg.get("roles", []):
                if role not in _ROLE_RESOLVERS:
                    unknown_roles.append((event_key, role))

    if unknown_channel_uses:
        preview = ", ".join(f"{ek}:{ch}" for ek, ch in unknown_channel_uses[:10])
        errors.append(
            Error(
                "Unknown notification channels referenced in event configs.",
                hint=f"Channels must be one of {sorted(allowed_channels)}. Offenders (first 10): {preview}",
                obj="notifications_system.registry.main_registry.NOTIFICATION_REGISTRY",
                id="notifications_system.E042",
            )
        )

    if unknown_roles:
        # Roles not registered isn’t always fatal; surface as a Warning so you can wire them up.
        preview = ", ".join(f"{ek}:{role}" for ek, role in unknown_roles[:10])
        errors.append(
            Warning(
                "Some event configs reference roles that are not registered.",
                hint=(
                    f"Define resolvers in notifications_system.registry.role_registry "
                    f"or ensure autodiscovery has run. Offenders (first 10): {preview}."
                    + ("" if role_source else " Role registry was not importable; skipping deep role checks.")
                ),
                obj="notifications_system.registry.main_registry.NOTIFICATION_REGISTRY",
                id="notifications_system.W043",
            )
        )

    return errors