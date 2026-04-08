from django.conf import settings
from django.db import models
from django.utils import timezone


class OTPCode(models.Model):
    """
    Store a hashed one time verification code for a user and website.
    """

    class Purpose(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        PASSWORD_RESET = "password_reset", "Password Reset"
        EMAIL_CHANGE = "email_change", "Email Change"
        ACCOUNT_UNLOCK = "account_unlock", "Account Unlock"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_codes",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="otp_codes",
    )
    purpose = models.CharField(
        max_length=50,
        choices=Purpose.choices,
    )
    code_hash = models.CharField(
        max_length=255,
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    attempts = models.PositiveIntegerField(
        default=0,
    )
    max_attempts = models.PositiveIntegerField(
        default=5,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website", "purpose"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        return (
            self.used_at is None
            and not self.is_expired
            and self.attempts < self.max_attempts
        )

    def mark_as_used(self) -> None:
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    def record_attempt(self) -> None:
        self.attempts += 1
        self.save(update_fields=["attempts"])