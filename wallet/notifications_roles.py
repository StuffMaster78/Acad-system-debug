from __future__ import annotations
from notifications_system.roles.common import register_common_roles

register_common_roles(
    overrides={
        "client": {
            "*": {"in_app", "email"},
            "wallet.balance_low": {"in_app", "email"},
        },
        "admin": {"*": {"email", "in_app"}},
        "support": {"*": {"email", "in_app"}},
        "super_admin": {"*": {"email", "in_app"}},
    }
)
 
#  # wallet/notifications_roles.py
# from __future__ import annotations

# """Role resolvers and default channel policies for wallet events.

# Resolves recipients based on the event context. Expects emitters to
# populate context with a key ``wallet`` pointing to a wallet-like model
# that exposes an ``owner`` (client user).

# Channel defaults are per-role and can be overridden by project settings
# (NOTIFICATION_ROLE_DEFAULTS) or per-role registration here.
# """

# from typing import Any, Mapping, Optional
# from django.contrib.auth import get_user_model
# from notifications_system.registry.role_registry import register_role


# User = get_user_model()


# def _wallet(ctx: Mapping[str, Any]):
#     """Return wallet object from context."""
#     return ctx.get("wallet")


# def resolve_client(ctx: Mapping[str, Any]) -> Optional[User]:
#     """Resolve the wallet owner (client).

#     Args:
#         ctx: Event context mapping.

#     Returns:
#         User or None.
#     """
#     w = _wallet(ctx)
#     return getattr(w, "owner", None) if w else None


# def resolve_support(ctx: Mapping[str, Any]) -> Optional[User]:
#     """Resolve a support/staff fallback.

#     Args:
#         ctx: Event context mapping.

#     Returns:
#         First staff user, if any.
#     """
#     return User.objects.filter(is_staff=True).order_by("id").first()


# def resolve_admin(ctx: Mapping[str, Any]) -> Optional[User]:
#     """Resolve an admin.

#     Args:
#         ctx: Event context mapping.

#     Returns:
#         First staff user, if any.
#     """
#     return User.objects.filter(is_staff=True).order_by("id").first()


# def resolve_super_admin(ctx: Mapping[str, Any]) -> Optional[User]:
#     """Resolve a superuser.

#     Args:
#         ctx: Event context mapping.

#     Returns:
#         First superuser, if any.
#     """
#     return User.objects.filter(is_superuser=True).order_by("id").first()


# # -- Channel defaults per role ----------------------------------------------

# register_role(
#     "client",
#     resolver=resolve_client,
#     channels={"*": {"in_app", "email"}},
# )

# register_role(
#     "support",
#     resolver=resolve_support,
#     channels={"*": {"email", "in_app"}},
# )

# register_role(
#     "admin",
#     resolver=resolve_admin,
#     channels={"*": {"email", "in_app"}},
# )

# register_role(
#     "super_admin",
#     resolver=resolve_super_admin,
#     channels={"*": {"email", "in_app"}},
# )