from __future__ import annotations
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
