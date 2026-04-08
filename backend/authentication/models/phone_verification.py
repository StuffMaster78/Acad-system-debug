from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from websites.models.websites import Website


class PhoneVerification(models.Model):
    """
    Represents a phone number verification request.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='phone_verifications',
        help_text=_("User whose phone is being verified")
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='phone_verifications',
        help_text=_("Website context")
    )
    phone_number = models.CharField(
        max_length=20,
        help_text=_("Phone number to verify (E.164 format)")
    )
    code_hash = models.CharField(
        max_length=6,
        help_text=_("6-digit verification code")
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Whether phone number is verified")
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When phone was verified")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When verification was initiated")
    )
    expires_at = models.DateTimeField(
        help_text=_("When verification code expires")
    )
    attempts = models.IntegerField(
        default=0,
        help_text=_("Number of verification attempts")
    )
    max_attempts = models.IntegerField(
        default=3,
        help_text=_("Maximum verification attempts allowed")
    )
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website", "phone_number"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_expired(self) -> bool:
        """
        Return whether the verification has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_exhausted(self) -> bool:
        """
        Return whether the verification has exhausted attempts.
        """
        return self.attempts >= self.max_attempts

    @property
    def is_valid(self) -> bool:
        """
        Return whether this verification can still be used.
        """
        return (
            not self.is_verified
            and not self.is_expired
            and not self.is_exhausted
        )
    
    def __str__(self):
        status = "Verified" if self.is_verified else "Pending"
        return f"Phone verification for {self.user.email}: {self.phone_number} ({status})"
