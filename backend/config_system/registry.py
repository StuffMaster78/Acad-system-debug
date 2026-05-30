from __future__ import annotations

from config_system.core.schema import (
    ConfigDefinition,
    ConfigType,
)


CONFIG_REGISTRY: dict[str, ConfigDefinition] = {

    # =========================================================
    # SYSTEM
    # =========================================================

    "system.debug": ConfigDefinition(
        key="system.debug",
        config_type=ConfigType.BOOL,
        default=False,
        description="Enable global debug behaviors.",
        is_runtime_editable=False,
        requires_restart=True,
        enable_rollout=False,
        cache_ttl_seconds=60,
    ),

    "system.maintenance_mode": ConfigDefinition(
        key="system.maintenance_mode",
        config_type=ConfigType.BOOL,
        default=False,
        description="Global maintenance mode kill switch.",
        is_runtime_editable=True,
        requires_restart=False,
        enable_rollout=False,
        cache_ttl_seconds=10,
    ),

    "system.readonly_mode": ConfigDefinition(
        key="system.readonly_mode",
        config_type=ConfigType.BOOL,
        default=False,
        description="Disable all write operations globally.",
        is_runtime_editable=True,
        requires_restart=False,
        enable_rollout=False,
        cache_ttl_seconds=15,
    ),

    # =========================================================
    # AUTH
    # =========================================================

    "auth.enable_mfa": ConfigDefinition(
        key="auth.enable_mfa",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable multi-factor authentication.",
        enable_rollout=True,
    ),

    "auth.session_timeout_seconds": ConfigDefinition(
        key="auth.session_timeout_seconds",
        config_type=ConfigType.INT,
        default=28800,
        description="Session idle timeout in seconds.",
        enable_rollout=False,
    ),

    "auth.max_login_attempts": ConfigDefinition(
        key="auth.max_login_attempts",
        config_type=ConfigType.INT,
        default=5,
        description="Maximum login attempts before temporary lock.",
        enable_rollout=False,
    ),

    # =========================================================
    # NOTIFICATIONS
    # =========================================================

    "notifications.enabled": ConfigDefinition(
        key="notifications.enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Master notification switch.",
        enable_rollout=True,
    ),

    "notifications.email_enabled": ConfigDefinition(
        key="notifications.email_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable email notifications.",
        enable_rollout=True,
    ),

    "notifications.sms_enabled": ConfigDefinition(
        key="notifications.sms_enabled",
        config_type=ConfigType.BOOL,
        default=False,
        description="Enable SMS notifications.",
        enable_rollout=True,
    ),

    "notifications.dedupe_window_seconds": ConfigDefinition(
        key="notifications.dedupe_window_seconds",
        config_type=ConfigType.INT,
        default=45,
        description="Notification dedupe window.",
        enable_rollout=False,
    ),

    # =========================================================
    # PAYMENTS
    # =========================================================

    "payments.enable_split_payments": ConfigDefinition(
        key="payments.enable_split_payments",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable wallet + gateway split payments.",
        enable_rollout=True,
    ),

    "payments.retry_failed_transactions": ConfigDefinition(
        key="payments.retry_failed_transactions",
        config_type=ConfigType.BOOL,
        default=True,
        description="Retry failed transactions automatically.",
        enable_rollout=True,
    ),

    "payments.max_retry_attempts": ConfigDefinition(
        key="payments.max_retry_attempts",
        config_type=ConfigType.INT,
        default=3,
        description="Maximum retry attempts for payment processing.",
        enable_rollout=False,
    ),

    # =========================================================
    # ORDERS
    # =========================================================

    "orders.auto_archive_enabled": ConfigDefinition(
        key="orders.auto_archive_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Auto archive completed orders.",
        enable_rollout=True,
    ),

    "orders.max_active_orders_per_user": ConfigDefinition(
        key="orders.max_active_orders_per_user",
        config_type=ConfigType.INT,
        default=10,
        description="Maximum active orders allowed per user.",
        enable_rollout=False,
    ),

    # =========================================================
    # CACHE
    # =========================================================

    "cache.enabled": ConfigDefinition(
        key="cache.enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Global cache enable switch.",
        enable_rollout=True,
    ),

    "cache.default_ttl_seconds": ConfigDefinition(
        key="cache.default_ttl_seconds",
        config_type=ConfigType.INT,
        default=300,
        description="Default cache TTL.",
        enable_rollout=False,
    ),

    # =========================================================
    # OBSERVABILITY
    # =========================================================

    "observability.metrics.enabled": ConfigDefinition(
        key="observability.metrics.enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable metrics collection.",
        enable_rollout=False,
    ),

    "observability.tracing.enabled": ConfigDefinition(
        key="observability.tracing.enabled",
        config_type=ConfigType.BOOL,
        default=False,
        description="Enable distributed tracing.",
        enable_rollout=False,
    ),

    # =========================================================
    # FILES
    # =========================================================

    "files.delivery_guard_enabled": ConfigDefinition(
        key="files.delivery_guard_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Gate final file downloads behind payment + scan + submission checks.",
        is_runtime_editable=True,
        enable_rollout=True,
        cache_ttl_seconds=30,
    ),

    "files.signed_url_expiry_seconds": ConfigDefinition(
        key="files.signed_url_expiry_seconds",
        config_type=ConfigType.INT,
        default=900,
        description="Signed download URL lifetime in seconds (default 15 min).",
        is_runtime_editable=True,
        enable_rollout=False,
        cache_ttl_seconds=60,
    ),

    "files.max_upload_size_mb": ConfigDefinition(
        key="files.max_upload_size_mb",
        config_type=ConfigType.INT,
        default=25,
        description="Global default maximum upload size in megabytes.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    # =========================================================
    # REFERRALS
    # =========================================================

    "referrals.invitation_expiry_days": ConfigDefinition(
        key="referrals.invitation_expiry_days",
        config_type=ConfigType.INT,
        default=30,
        description="Days before a pending referral invitation expires.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "referrals.invitations_enabled": ConfigDefinition(
        key="referrals.invitations_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Allow clients to send referral invitations by email.",
        is_runtime_editable=True,
        enable_rollout=True,
    ),

    # =========================================================
    # NOTIFICATIONS (additional runtime tunables)
    # =========================================================

    "notifications.rate_limit_max": ConfigDefinition(
        key="notifications.rate_limit_max",
        config_type=ConfigType.INT,
        default=10,
        description="Maximum notifications sent to one recipient per rate-limit window.",
        is_runtime_editable=True,
        enable_rollout=False,
        cache_ttl_seconds=60,
    ),

    "notifications.rate_limit_window_seconds": ConfigDefinition(
        key="notifications.rate_limit_window_seconds",
        config_type=ConfigType.INT,
        default=300,
        description="Rate-limit window duration in seconds.",
        is_runtime_editable=True,
        enable_rollout=False,
        cache_ttl_seconds=60,
    ),
}


# =============================================================
# Registry Helpers
# =============================================================

def get_config_definition(
    key: str,
) -> ConfigDefinition | None:
    """
    Safe config definition lookup.
    """

    return CONFIG_REGISTRY.get(key)


def require_config_definition(
    key: str,
) -> ConfigDefinition:
    """
    Strict config definition lookup.
    Raises if missing.
    """

    definition = CONFIG_REGISTRY.get(key)

    if definition is None:
        raise KeyError(
            f"Unknown config key: {key}"
        )

    return definition


def list_config_keys() -> list[str]:
    """
    Useful for admin panels,
    introspection,
    validation,
    autocomplete,
    observability tooling.
    """

    return sorted(CONFIG_REGISTRY.keys())