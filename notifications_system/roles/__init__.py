# notifications_system/roles/__init__.py
from .common import (  # noqa: F401
    register_common_roles,
    resolve_client,
    resolve_writer,
    resolve_support,
    resolve_admin,
    resolve_super_admin,
    resolve_editor,
)