from __future__ import annotations
from django.contrib.auth import get_user_model
from notifications_system.registry.role_registry import register_role
from notifications_system.roles.common import register_common_roles

# Only put app-specific channel tweaks here.
register_common_roles(
    overrides={
        "client": {"*": {"in_app", "email"}},
        "writer": {"*": {"in_app", "email"}},
        # staff-facing defaults if you want them active for orders
        "support": {"*": {"in_app", "email"}},
        "admin": {"*": {"in_app", "email"}},
        "editor": {"*": {"in_app", "email"}},
        "super_admin": {"*": {"in_app", "email"}},
    }
)

User = get_user_model()


def resolve_writer_pool(ctx):
    order = ctx.get("order")
    website = getattr(order, "website", None) if order else None
    qs = User.objects.filter(role="writer", is_active=True)
    if website and hasattr(User, "website"):
        qs = qs.filter(website=website)
    return qs


register_role(
    "writer_pool",
    resolve_writer_pool,
    {"order.available": {"in_app"}},
)
