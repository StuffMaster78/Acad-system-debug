import os


class FeatureFlags:
    """
    Environment-variable-backed feature flags.

    Set FF_<FLAG>=true in your environment to enable a flag.
    All flags default to False unless explicitly enabled.

    These are coarse on/off switches. For gradual rollouts, percentage
    targeting, or per-tenant overrides use the config_system registry
    with FeatureEngine.is_enabled().
    """

    def __init__(self):
        self.flags = {
            # File system
            "DELIVERY_GUARD": _flag("FF_DELIVERY_GUARD", True),

            # Payments
            "WALLET_ORDER_PAYMENT": _flag("FF_WALLET_ORDER_PAYMENT", True),
            "STRIPE_CHECKOUT": _flag("FF_STRIPE_CHECKOUT", False),

            # Referrals
            "REFERRAL_INVITATIONS": _flag("FF_REFERRAL_INVITATIONS", True),

            # Discounts
            "SPECIAL_ORDER_DISCOUNT": _flag("FF_SPECIAL_ORDER_DISCOUNT", True),
            "ORDER_CHECKOUT_DISCOUNT": _flag("FF_ORDER_CHECKOUT_DISCOUNT", True),

            # Communications
            "COMMS_MODERATION": _flag("FF_COMMS_MODERATION", True),
            "COMMS_LINK_REVIEW": _flag("FF_COMMS_LINK_REVIEW", True),

            # Observability
            "ACTIVITY_FEED": _flag("FF_ACTIVITY_FEED", True),
            "AUDIT_LOGGING": _flag("FF_AUDIT_LOGGING", True),
        }

    def is_enabled(self, flag: str) -> bool:
        return self.flags.get(flag, False)


def _flag(key: str, default: bool = False) -> bool:
    val = os.getenv(key, "").strip().lower()
    if val in ("1", "true", "yes"):
        return True
    if val in ("0", "false", "no"):
        return False
    return default


feature_flags = FeatureFlags()


def feature(flag: str) -> bool:
    return feature_flags.is_enabled(flag)
