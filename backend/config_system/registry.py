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

    # =========================================================
    # ORDERS (additional)
    # =========================================================

    "orders.deadline_min_hours": ConfigDefinition(
        key="orders.deadline_min_hours",
        config_type=ConfigType.INT,
        default=3,
        description="Minimum allowed deadline in hours from now.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "orders.auto_archive_days": ConfigDefinition(
        key="orders.auto_archive_days",
        config_type=ConfigType.INT,
        default=30,
        description="Days after completion before an order is auto-archived.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "orders.allow_guest_checkout": ConfigDefinition(
        key="orders.allow_guest_checkout",
        config_type=ConfigType.BOOL,
        default=False,
        description="Allow unregistered clients to place orders with email only.",
        is_runtime_editable=True,
        enable_rollout=True,
    ),

    "orders.require_payment_before_start": ConfigDefinition(
        key="orders.require_payment_before_start",
        config_type=ConfigType.BOOL,
        default=True,
        description="Block writer from starting until payment is received.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    # =========================================================
    # WRITER
    # =========================================================

    "writer.max_active_orders": ConfigDefinition(
        key="writer.max_active_orders",
        config_type=ConfigType.INT,
        default=5,
        description="Maximum concurrent active orders per writer.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "writer.payout_minimum_amount": ConfigDefinition(
        key="writer.payout_minimum_amount",
        config_type=ConfigType.INT,
        default=20,
        description="Minimum payout request amount in USD.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "writer.allow_self_assignment": ConfigDefinition(
        key="writer.allow_self_assignment",
        config_type=ConfigType.BOOL,
        default=False,
        description="Allow writers to claim available orders without admin assignment.",
        is_runtime_editable=True,
        enable_rollout=True,
    ),

    "writer.bid_window_hours": ConfigDefinition(
        key="writer.bid_window_hours",
        config_type=ConfigType.INT,
        default=2,
        description="Hours a new order is visible in the bid pool before auto-assignment.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    # =========================================================
    # WALLET
    # =========================================================

    "wallet.min_topup_amount": ConfigDefinition(
        key="wallet.min_topup_amount",
        config_type=ConfigType.INT,
        default=10,
        description="Minimum wallet top-up amount in USD.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "wallet.max_balance": ConfigDefinition(
        key="wallet.max_balance",
        config_type=ConfigType.INT,
        default=5000,
        description="Maximum wallet balance allowed per client in USD.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    # =========================================================
    # FEATURES (platform-level feature flags)
    # =========================================================

    "feature.loyalty_enabled": ConfigDefinition(
        key="feature.loyalty_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable the loyalty points and rewards system.",
        is_runtime_editable=True,
        enable_rollout=True,
        cache_ttl_seconds=60,
    ),

    "feature.tips_enabled": ConfigDefinition(
        key="feature.tips_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Allow clients to send tips to writers.",
        is_runtime_editable=True,
        enable_rollout=True,
        cache_ttl_seconds=60,
    ),

    "feature.special_orders_enabled": ConfigDefinition(
        key="feature.special_orders_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable the special/quoted orders workflow.",
        is_runtime_editable=True,
        enable_rollout=True,
        cache_ttl_seconds=60,
    ),

    "feature.class_orders_enabled": ConfigDefinition(
        key="feature.class_orders_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable the class portal orders workflow.",
        is_runtime_editable=True,
        enable_rollout=True,
        cache_ttl_seconds=60,
    ),

    "feature.referrals_enabled": ConfigDefinition(
        key="feature.referrals_enabled",
        config_type=ConfigType.BOOL,
        default=True,
        description="Enable the client referral invitation system.",
        is_runtime_editable=True,
        enable_rollout=True,
        cache_ttl_seconds=60,
    ),

    # =========================================================
    # SECURITY (runtime tunables)
    # =========================================================

    "security.magic_link_ttl_minutes": ConfigDefinition(
        key="security.magic_link_ttl_minutes",
        config_type=ConfigType.INT,
        default=15,
        description="Magic link / passwordless login expiry in minutes.",
        is_runtime_editable=True,
        enable_rollout=False,
    ),

    "security.password_reset_ttl_minutes": ConfigDefinition(
        key="security.password_reset_ttl_minutes",
        config_type=ConfigType.INT,
        default=60,
        description="Password reset link expiry in minutes.",
        is_runtime_editable=True,
        enable_rollout=False,
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