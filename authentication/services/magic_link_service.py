import uuid
from datetime import timedelta
from django.utils.timezone import now
from django.core.exceptions import ValidationError, PermissionDenied

from authentication.models.magic_links import MagicLink
from authentication.models.audit import AuditLog
from users.models import User


class MagicLinkService:
    """
    Service layer for creating, validating, and consuming magic links.
    """

    def __init__(self, website):
        self.website = website

    def create_magic_link(
            self, user, expires_in_minutes=15,
            ip=None, user_agent=None
        ):
        """
        Generates a new magic link token.
        Revokes any active ones first.
        """
        MagicLink.objects.filter(
            user=user, website=self.website,
            used_at__isnull=True,
            expires_at__gt=now()
        ).delete()

        token = uuid.uuid4()
        expires_at = now() + timedelta(
            minutes=expires_in_minutes
        )

        link = MagicLink.objects.create(
            user=user,
            website=self.website,
            token=token,
            expires_at=expires_at,
            ip_address=ip,
            user_agent=user_agent,
        )

        AuditLog.objects.create(
            user=user,
            website=self.website,
            event="magic_link_created",
            ip_address=ip,
            device=user_agent,
        )

        return link

    def validate_token(self, token: str):
        """
        Validates the token and returns the matching MagicLink.
        """
        try:
            link = MagicLink.objects.get(token=token, website=self.website)
        except MagicLink.DoesNotExist:
            raise ValidationError("Invalid or expired token.")

        if not link.is_valid():
            raise PermissionDenied("Magic link has expired or already been used.")

        return link

    def consume_token(self, token: str):
        """
        Validates and consumes a magic link (marks it as used).
        """
        link = self.validate_token(token)
        link.mark_used()

        AuditLog.objects.create(
            user=link.user,
            website=self.website,
            event="magic_link_used",
            ip_address=link.ip_address or "N/A",
            device=link.user_agent or "N/A"
        )

        return link.user