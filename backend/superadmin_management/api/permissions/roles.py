from enum import Enum


class Role(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    SUPPORT = "support"
    EDITOR = "editor"
    VIEWER = "viewer"