import secrets
import hashlib
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError

class EmailVerification(models.Model):
    """
    Stores the email verification token for a user 
    (used in link-based verification).
    Can be used alongside OTP.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="email_verification_website"
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["website", "created_at"]),
            models.Index(fields=["token_hash"]),
            models.Index(fields=["user"]),
            models.Index(fields=["expires_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(used_at__isnull=True),
                name="unique_active_email_verification_per_user",
            )
        ]

    def __str__(self) -> str:
        return f"Email verification for {self.user}"
    
    def clean(self):
        if self.expires_at <= self.created_at:
            raise ValidationError(
                "expires_at must be after created_at"
            )
        
    def matches_token(self, raw_token: str) -> bool:
        import hashlib

        return (
            hashlib.sha256(raw_token.encode()).hexdigest()
            == self.token_hash
        )
        
    @classmethod
    def create_verification(cls, *, user, website, expiry_hours=24):
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        instance = cls.objects.create(
            user=user,
            website=website,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=expiry_hours),
        )

        return instance, raw_token

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired

    def mark_as_used(self) -> None:
        if not self.used_at:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    def verify(self) -> bool:
        if not self.is_valid:
            return False

        self.mark_as_used()
        return True
