from __future__ import annotations


class SpecialOrderPlatform:
    SHADOW_HEALTH = "shadow_health"
    IHUMAN = "ihuman"
    CANVAS = "canvas"
    BLACKBOARD = "blackboard"
    MOODLE = "moodle"
    ATI = "ati"
    ELSEVIER = "elsevier"
    MYLAB = "mylab"
    GOOGLE_CLASSROOM = "google_classroom"
    OTHER = "other"

    CHOICES = [
        (SHADOW_HEALTH, "Shadow Health"),
        (IHUMAN, "iHuman"),
        (CANVAS, "Canvas"),
        (BLACKBOARD, "Blackboard"),
        (MOODLE, "Moodle"),
        (ATI, "ATI"),
        (ELSEVIER, "Elsevier"),
        (MYLAB, "MyLab"),
        (GOOGLE_CLASSROOM, "Google Classroom"),
        (OTHER, "Other"),
    ]


class InstitutionType:
    UNIVERSITY = "university"
    COLLEGE = "college"
    NURSING_SCHOOL = "nursing_school"
    TRAINING_CENTER = "training_center"
    OTHER = "other"

    CHOICES = [
        (UNIVERSITY, "University"),
        (COLLEGE, "College"),
        (NURSING_SCHOOL, "Nursing school"),
        (TRAINING_CENTER, "Training center"),
        (OTHER, "Other"),
    ]


class TwoFactorMethod:
    SMS = "sms"
    EMAIL = "email"
    AUTHENTICATOR = "authenticator"
    APP_PUSH = "app_push"
    CALL = "call"
    WHATSAPP = "whatsapp"
    OTHER = "other"

    CHOICES = [
        (SMS, "SMS"),
        (EMAIL, "Email"),
        (AUTHENTICATOR, "Authenticator"),
        (APP_PUSH, "App push"),
        (CALL, "Call"),
        (WHATSAPP, "WhatsApp"),
        (OTHER, "Other"),
    ]


class SensitiveAccessLevel:
    VIEW_LINK = "view_link"
    VIEW_USERNAME = "view_username"
    REVEAL_PASSWORD = "reveal_password"
    MANAGE_2FA = "manage_2fa"
    FULL = "full"

    CHOICES = [
        (VIEW_LINK, "View link"),
        (VIEW_USERNAME, "View username"),
        (REVEAL_PASSWORD, "Reveal password"),
        (MANAGE_2FA, "Manage 2FA"),
        (FULL, "Full"),
    ]


class SensitiveAccessAction:
    VAULT_CREATED = "vault_created"
    VAULT_UPDATED = "vault_updated"
    OPENED_VAULT = "opened_vault"
    OPENED_LINK = "opened_link"
    VIEWED_USERNAME = "viewed_username"
    REVEALED_PASSWORD = "revealed_password"
    COPIED_PASSWORD = "copied_password"
    GRANT_CREATED = "grant_created"
    GRANT_REVOKED = "grant_revoked"
    TWO_FACTOR_REQUESTED = "two_factor_requested"
    TWO_FACTOR_COMPLETED = "two_factor_completed"

    CHOICES = [
        (VAULT_CREATED, "Vault created"),
        (VAULT_UPDATED, "Vault updated"),
        (OPENED_VAULT, "Opened vault"),
        (OPENED_LINK, "Opened link"),
        (VIEWED_USERNAME, "Viewed username"),
        (REVEALED_PASSWORD, "Revealed password"),
        (COPIED_PASSWORD, "Copied password"),
        (GRANT_CREATED, "Grant created"),
        (GRANT_REVOKED, "Grant revoked"),
        (TWO_FACTOR_REQUESTED, "Two-factor requested"),
        (TWO_FACTOR_COMPLETED, "Two-factor completed"),
    ]


class TwoFactorRequestStatus:
    PENDING = "pending"
    CLIENT_NOTIFIED = "client_notified"
    CODE_RECEIVED = "code_received"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    CHOICES = [
        (PENDING, "Pending"),
        (CLIENT_NOTIFIED, "Client notified"),
        (CODE_RECEIVED, "Code received"),
        (COMPLETED, "Completed"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]