# authentication/constants.py
ROLE_CLIENT = 'client'
ROLE_WRITER = 'writer'
ROLE_SUPPORT = 'support'
ROLE_EDITOR = 'editor'
ROLE_ADMIN = 'admin'
ROLE_SUPERADMIN = 'superadmin'

ROLE_HIERARCHY = {
    ROLE_CLIENT: 0,
    ROLE_WRITER: 1,
    ROLE_SUPPORT: 2,
    ROLE_EDITOR: 3,
    ROLE_ADMIN: 4,
    ROLE_SUPERADMIN: 5,
}


AUTH_EVENT_KEYS = {
    "registration_requested": "auth.registration_verification_requested",
    "password_reset_requested": "auth.password_reset_requested",
    "account_unlock_requested": "auth.account_unlock_requested",
    "account_unlocked": "auth.account_unlocked",
    "mfa_challenge_requested": "auth.mfa_challenge_requested",
    "suspicious_login_detected": "auth.suspicious_login_detected",
    "account_deletion_scheduled": "auth.account_deletion_scheduled",
    "account_deletion_cancelled": "auth.account_deletion_cancelled",
    "account_deletion_completed": "auth.account_deletion_completed",
}

DEFAULTS = {
    "session_idle_timeout_seconds": 30 * 60,
    "impersonation_idle_timeout_seconds": 15 * 60,
    "session_warning_seconds": 5 * 60,
    "registration_token_expiry_minutes": 10,
    "unlock_token_expiry_minutes": 30,
}