from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils import timezone

log = logging.getLogger(__name__)


class ReferralInvitationService:
    """
    Manages pending referral invitations sent to non-users.

    When a user shares their referral link via email, we create a
    PendingReferralInvitation so we can track the conversion when the
    invited person signs up using the referral code.

    Responsibilities:
        1. Create and send a referral invitation email.
        2. Mark an invitation as converted when the referee signs up.
        3. Expire stale invitations.
        4. Query open invitations per referrer.
    """

    EXPIRY_DAYS = 30

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def send_invitation(
        cls,
        *,
        referrer,
        referee_email: str,
        website,
        referral_code: str,
        referral_link: str,
    ):
        """
        Create a pending invitation and send the referral email.

        Args:
            referrer: User sending the invitation.
            referee_email: Email of the person being invited.
            website: Tenant website.
            referral_code: Referral code to embed in the link.
            referral_link: Full referral URL to send.

        Returns:
            PendingReferralInvitation instance.

        Raises:
            ValidationError: If the email is invalid, already a user,
                             or already has a pending invitation.
        """
        from referrals.models import PendingReferralInvitation

        cls._validate_email(referee_email)
        cls._ensure_not_existing_user(referee_email=referee_email, website=website)
        cls._ensure_no_duplicate(
            referrer=referrer,
            referee_email=referee_email,
            website=website,
        )

        invitation = PendingReferralInvitation.objects.create(
            website=website,
            referrer=referrer,
            referee_email=referee_email,
            referral_code=referral_code,
            referral_link=referral_link,
            invitation_sent=False,
            converted=False,
        )

        sent = cls._send_email(
            invitation=invitation,
            referrer=referrer,
        )

        if sent:
            invitation.invitation_sent = True
            invitation.save(update_fields=["invitation_sent"])

        return invitation

    # ------------------------------------------------------------------
    # Convert
    # ------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def mark_converted(cls, *, referee_email: str, website) -> list:
        """
        Mark all pending invitations for this email as converted.

        Called from the signup flow when a new user registers with a
        referral code that matches a pending invitation.

        Returns:
            List of converted PendingReferralInvitation instances.
        """
        from referrals.models import PendingReferralInvitation

        invitations = list(
            PendingReferralInvitation.objects.filter(
                referee_email=referee_email,
                website=website,
                converted=False,
            ).select_for_update()
        )

        now = timezone.now()
        for invitation in invitations:
            invitation.converted = True
            invitation.save(update_fields=["converted"])

        log.info(
            "Marked %d referral invitations as converted for email=%s website=%s",
            len(invitations),
            referee_email,
            getattr(website, "pk", None),
        )

        return invitations

    # ------------------------------------------------------------------
    # Expire
    # ------------------------------------------------------------------

    @classmethod
    def expire_stale(cls, *, website=None) -> int:
        """
        Delete pending invitations older than EXPIRY_DAYS.

        Args:
            website: Optional — restrict to one tenant. None = all tenants.

        Returns:
            Number of invitations deleted.
        """
        from referrals.models import PendingReferralInvitation

        cutoff = timezone.now() - __import__("datetime").timedelta(
            days=cls.EXPIRY_DAYS
        )
        qs = PendingReferralInvitation.objects.filter(
            converted=False,
            sent_at__lt=cutoff,
        )
        if website is not None:
            qs = qs.filter(website=website)

        deleted_count, _ = qs.delete()
        log.info("Expired %d stale referral invitations", deleted_count)
        return deleted_count

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    @staticmethod
    def list_for_referrer(*, referrer, website):
        """Return all pending (non-converted) invitations for a referrer."""
        from referrals.models import PendingReferralInvitation

        return PendingReferralInvitation.objects.filter(
            referrer=referrer,
            website=website,
            converted=False,
        ).order_by("-sent_at")

    @staticmethod
    def get_summary(*, referrer, website) -> dict[str, Any]:
        """Return invitation summary counts for a referrer."""
        from referrals.models import PendingReferralInvitation

        qs = PendingReferralInvitation.objects.filter(
            referrer=referrer, website=website
        )
        return {
            "total_sent": qs.count(),
            "pending": qs.filter(converted=False).count(),
            "converted": qs.filter(converted=True).count(),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_email(email: str) -> None:
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(f"'{email}' is not a valid email address.")

    @staticmethod
    def _ensure_not_existing_user(*, referee_email: str, website) -> None:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(
                email=referee_email,
                website=website,
            ).exists():
                raise ValidationError(
                    f"{referee_email} already has an account. "
                    "Share your referral link directly with them."
                )
        except (ImportError, Exception) as exc:
            if isinstance(exc, ValidationError):
                raise
            log.debug("_ensure_not_existing_user check skipped: %s", exc)

    @staticmethod
    def _ensure_no_duplicate(*, referrer, referee_email: str, website) -> None:
        from referrals.models import PendingReferralInvitation

        if PendingReferralInvitation.objects.filter(
            referrer=referrer,
            referee_email=referee_email,
            website=website,
            converted=False,
        ).exists():
            raise ValidationError(
                f"An invitation has already been sent to {referee_email}."
            )

    @staticmethod
    def _send_email(*, invitation, referrer) -> bool:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key="referral.reward_earned",
                recipient=referrer,
                website=invitation.website,
                context={
                    "referee_email": invitation.referee_email,
                    "referral_code": invitation.referral_code,
                    "referral_link": invitation.referral_link,
                    "referrer_name": getattr(referrer, "first_name", "")
                    or getattr(referrer, "email", ""),
                },
            )
            return True
        except Exception as exc:
            log.warning(
                "ReferralInvitationService._send_email failed "
                "invitation=%s: %s",
                getattr(invitation, "pk", None),
                exc,
            )
            return False
