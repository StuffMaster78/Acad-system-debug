from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    SUPPORT = "support"
    EDITOR = "editor"
    WRITER = "writer"
    CLIENT = "client"