from django.conf import settings
from django.db import models


User = settings.AUTH_USER_MODEL


class AuthEventType(models.TextChoices):
    LOGIN_SUCCESS = "login_success", "Login Success"
    LOGIN_FAILED = "login_failed", "Login Failed"
    LOGOUT = "logout", "Logout"
    PASSWORD_CHANGED = "password_changed", "Password Changed"
    PASSWORD_RESET_REQUESTED = (
        "password_reset_requested",
        "Password Reset Requested",
    )
    PASSWORD_RESET_COMPLETED = (
        "password_reset_completed",
        "Password Reset Completed",
    )
    EMAIL_VERIFIED = "email_verified", "Email Verified"
    MFA_ENABLED = "mfa_enabled", "MFA Enabled"
    MFA_DISABLED = "mfa_disabled", "MFA Disabled"
    MFA_RESET = "mfa_reset", "MFA Reset"
    MFA_VERIFIED = "mfa_verified", "MFA Verified"
    MFA_CHALLENGE_REQUESTED = (
        "mfa_challenge_requested",
        "MFA Challenge Requested",
    )
    MFA_CHALLENGE_VERIFIED = (
        "mfa_challenge_verified",
        "MFA Challenge Verified",
    )
    MFA_CHALLENGE_FAILED = (
        "mfa_challenge_failed",
        "MFA Challenge Failed",
    )
    MFA_RECOVERY_REQUESTED = (
        "mfa_recovery_requested",
        "MFA Recovery Requested",
    )
    MFA_RECOVERY_COMPLETED = (
        "mfa_recovery_completed",
        "MFA Recovery Completed",
    )
    MAGIC_LINK_REQUESTED = (
        "magic_link_requested",
        "Magic Link Requested",
    )
    MAGIC_LINK_USED = "magic_link_used", "Magic Link Used"
    ACCOUNT_UPDATED = "account_updated", "Account Updated"
    ACCOUNT_LOCKED = "account_locked", "Account Locked"
    QR_CODE_GENERATED = "qr_code_generated", "QR Code Generated"
    QR_CODE_SCANNED = "qr_code_scanned", "QR Code Scanned"
    DEVICE_DELETED = "device_deleted", "Device Deleted"
    SESSION_REVOKED = "session_revoked", "Session Revoked"
    SUSPICIOUS_LOGIN = "suspicious_login", "Suspicious Login"


class AuthSecurityEvent(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auth_security_events",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="auth_security_events",
    )
    event_type = models.CharField(
        max_length=64,
        choices=AuthEventType.choices,
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
    )
    device = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Auth Security Event"
        verbose_name_plural = "Auth Security Events"
        indexes = [
            models.Index(fields=["website", "event_type"]),
            models.Index(fields=["user", "event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        user_label = (
            getattr(self.user, "email", None)
            or str(self.user)
            or "anonymous"
        )
        return (
            f"{user_label} | {self.event_type} | {self.created_at}"
        )
