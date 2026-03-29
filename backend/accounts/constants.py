"""Static constants for the accounts app"""

DEFAULT_CLIENT_ROLE = "client"
DEFAULT_WRITER_ROLE = "writer"

DEFAULT_STAFF_ROLES = [
    "admin",
    "editor",
    "support",
]

# To prevent deletion or modification
SYSTEM_ROLE_KEYS = {
    "super_admin",
    "admin,"
}

# Onboarding Config
DEFAULT_ONBOARDING_METADATA = {}

ONBOARDING_SESSION_EXPIRY_HOURS = 72


# Audit defaults

DEFAULT_AUDIT_ACTOR = None