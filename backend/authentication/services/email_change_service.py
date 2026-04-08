"""
Email change service.

Handle email change request workflows including request creation,
approval, token verification, completion, and cancellation.
"""

import logging
from typing import Optional, Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from authentication.models.email_change_request import (
    EmailChangeRequest,
)
from authentication.services.token_service import TokenService


logger = logging.getLogger(__name__)


class EmailChangeService:
    """
    Manage secure email change request workflows for a user on a
    website.
    """

    DEFAULT_EXPIRY_HOURS = 24

    def __init__(self, user, website):
        """
        Initialize the email change service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for email change."
            )

        self.user = user
        self.website = website

    @transaction.atomic
    def create_request(
        self,
        *,
        new_email: str,
        require_old_email_confirmation: bool = True,
    ) -> tuple[EmailChangeRequest, str, Optional[str]]:
        """
        Create a new email change request.

        Args:
            new_email: New email address requested.
            require_old_email_confirmation: Whether old email
                confirmation is required.

        Returns:
            Tuple of:
                - EmailChangeRequest instance
                - raw new-email verification token
                - raw old-email confirmation token or None

        Raises:
            ValidationError: If the request is invalid.
        """
        self._validate_new_email(new_email=new_email)

        self._cancel_existing_active_requests()

        raw_new_token, new_email_token_hash = (
            TokenService.generate_hashed_token()
        )

        raw_old_token = None
        old_email_token_hash = None

        if require_old_email_confirmation:
            raw_old_token, old_email_token_hash = (
                TokenService.generate_hashed_token()
            )

        request_obj = EmailChangeRequest.objects.create(
            user=self.user,
            website=self.website,
            old_email=self.user.email,
            new_email=new_email,
            new_email_token_hash=new_email_token_hash,
            old_email_token_hash=old_email_token_hash,
            status=EmailChangeRequest.Status.PENDING,
            expires_at=TokenService.build_expiry(
                hours=self.DEFAULT_EXPIRY_HOURS,
            ),
        )

        self._log_security_event(
            event_type="email_change_requested",
            severity="high",
            metadata={
                "old_email": self.user.email,
                "new_email": new_email,
            },
        )

        return request_obj, raw_new_token, raw_old_token

    @transaction.atomic
    def approve_request(
        self,
        *,
        request_obj: EmailChangeRequest,
        approved_by,
    ) -> EmailChangeRequest:
        """
        Approve an email change request.

        Args:
            request_obj: EmailChangeRequest instance.
            approved_by: Admin approving the request.

        Returns:
            Updated EmailChangeRequest instance.

        Raises:
            ValidationError: If the request cannot be approved.
        """
        if request_obj.is_expired:
            request_obj.status = EmailChangeRequest.Status.CANCELLED
            request_obj.save(update_fields=["status"])
            raise ValidationError("Email change request has expired.")

        if request_obj.status != EmailChangeRequest.Status.PENDING:
            raise ValidationError(
                "Only pending email change requests can be approved."
            )

        request_obj.status = EmailChangeRequest.Status.ADMIN_APPROVED
        request_obj.approved_by = approved_by
        request_obj.approved_at = timezone.now()
        request_obj.save(
            update_fields=["status", "approved_by", "approved_at"],
        )

        self._log_security_event(
            event_type="email_change_approved",
            severity="high",
            metadata={
                "old_email": request_obj.old_email,
                "new_email": request_obj.new_email,
                "approved_by": getattr(approved_by, "email", ""),
            },
        )

        return request_obj

    @transaction.atomic
    def reject_request(
        self,
        *,
        request_obj: EmailChangeRequest,
        rejection_reason: str,
    ) -> EmailChangeRequest:
        """
        Reject an email change request.

        Args:
            request_obj: EmailChangeRequest instance.
            rejection_reason: Reason for rejection.

        Returns:
            Updated EmailChangeRequest instance.
        """
        request_obj.status = EmailChangeRequest.Status.REJECTED
        request_obj.rejection_reason = rejection_reason
        request_obj.save(
            update_fields=["status", "rejection_reason"],
        )
        return request_obj

    @transaction.atomic
    def verify_new_email(
        self,
        *,
        raw_token: str,
    ) -> EmailChangeRequest:
        """
        Verify the new email address using the new-email token.

        Args:
            raw_token: Raw verification token.

        Returns:
            Updated EmailChangeRequest instance.

        Raises:
            ValidationError: If the token is invalid or unusable.
        """
        token_hash = TokenService.hash_value(raw_token)

        request_obj = EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            new_email_token_hash=token_hash,
        ).order_by("-created_at").first()

        if request_obj is None:
            raise ValidationError("Invalid verification token.")

        if request_obj.is_expired:
            raise ValidationError("Verification token has expired.")

        if request_obj.status != EmailChangeRequest.Status.ADMIN_APPROVED:
            raise ValidationError(
                "Email change request must be admin-approved first."
            )

        request_obj.status = EmailChangeRequest.Status.NEW_EMAIL_VERIFIED
        request_obj.save(update_fields=["status"])

        if not request_obj.old_email_token_hash:
            self.complete_email_change(request_obj=request_obj)

        return request_obj

    @transaction.atomic
    def confirm_old_email(
        self,
        *,
        raw_token: str,
    ) -> EmailChangeRequest:
        """
        Confirm the old email address using the old-email token.

        Args:
            raw_token: Raw confirmation token.

        Returns:
            Updated EmailChangeRequest instance.

        Raises:
            ValidationError: If the token is invalid or unusable.
        """
        token_hash = TokenService.hash_value(raw_token)

        request_obj = EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            old_email_token_hash=token_hash,
        ).order_by("-created_at").first()

        if request_obj is None:
            raise ValidationError("Invalid confirmation token.")

        if request_obj.is_expired:
            raise ValidationError("Confirmation token has expired.")

        if request_obj.status != EmailChangeRequest.Status.NEW_EMAIL_VERIFIED:
            raise ValidationError(
                "New email must be verified before old email confirmation."
            )

        request_obj.status = EmailChangeRequest.Status.OLD_EMAIL_CONFIRMED
        request_obj.save(update_fields=["status"])

        self.complete_email_change(request_obj=request_obj)

        return request_obj

    @transaction.atomic
    def complete_email_change(
        self,
        *,
        request_obj: EmailChangeRequest,
    ) -> EmailChangeRequest:
        """
        Complete an email change request.

        Args:
            request_obj: EmailChangeRequest instance.

        Returns:
            Updated EmailChangeRequest instance.

        Raises:
            ValidationError: If the request is not ready to complete.
        """
        if request_obj.old_email_token_hash:
            if request_obj.status != EmailChangeRequest.Status.OLD_EMAIL_CONFIRMED:
                raise ValidationError(
                    "Old email confirmation is still required."
                )
        else:
            if request_obj.status != EmailChangeRequest.Status.NEW_EMAIL_VERIFIED:
                raise ValidationError(
                    "New email verification is still required."
                )

        old_email = self.user.email
        self.user.email = request_obj.new_email

        if hasattr(self.user, "email_verified"):
            self.user.email_verified = False
            self.user.save(update_fields=["email", "email_verified"])
        else:
            self.user.save(update_fields=["email"])

        request_obj.status = EmailChangeRequest.Status.COMPLETED
        request_obj.completed_at = timezone.now()
        request_obj.save(update_fields=["status", "completed_at"])

        self._log_security_event(
            event_type="email_changed",
            severity="high",
            metadata={
                "old_email": old_email,
                "new_email": request_obj.new_email,
            },
        )

        return request_obj

    @transaction.atomic
    def cancel_request(
        self,
        *,
        request_obj: EmailChangeRequest,
    ) -> EmailChangeRequest:
        """
        Cancel an email change request.

        Args:
            request_obj: EmailChangeRequest instance.

        Returns:
            Updated EmailChangeRequest instance.
        """
        request_obj.status = EmailChangeRequest.Status.CANCELLED
        request_obj.save(update_fields=["status"])
        return request_obj

    def get_pending_request(self) -> Optional[EmailChangeRequest]:
        """
        Retrieve the most recent active email change request.

        Returns:
            EmailChangeRequest instance or None.
        """
        return EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            status__in=[
                EmailChangeRequest.Status.PENDING,
                EmailChangeRequest.Status.ADMIN_APPROVED,
                EmailChangeRequest.Status.NEW_EMAIL_VERIFIED,
            ],
            expires_at__gt=timezone.now(),
        ).order_by("-created_at").first()

    def get_all_requests(self, status_filter: str | None = None):
        """
        Retrieve email change requests for the website.

        Args:
            status_filter: Optional status filter.

        Returns:
            QuerySet of EmailChangeRequest records.
        """
        queryset = EmailChangeRequest.objects.filter(
            website=self.website,
        )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")

    def _validate_new_email(self, *, new_email: str) -> None:
        """
        Validate a requested new email address.

        Args:
            new_email: New email address.

        Raises:
            ValidationError: If invalid.
        """
        if new_email.lower() == self.user.email.lower():
            raise ValidationError(
                "New email must be different from current email."
            )

        from django.contrib.auth import get_user_model

        User = get_user_model()

        if User.objects.filter(email__iexact=new_email).exclude(
            pk=self.user.pk,
        ).exists():
            raise ValidationError(
                "This email address is already in use."
            )

    def _cancel_existing_active_requests(self) -> int:
        """
        Cancel any existing active requests for the user and website.

        Returns:
            Number of cancelled requests.
        """
        return EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            status__in=[
                EmailChangeRequest.Status.PENDING,
                EmailChangeRequest.Status.ADMIN_APPROVED,
                EmailChangeRequest.Status.NEW_EMAIL_VERIFIED,
            ],
        ).update(status=EmailChangeRequest.Status.CANCELLED)

    def _log_security_event(
        self,
        *,
        event_type: str,
        severity: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Best-effort security event logging.

        Args:
            event_type: Security event type.
            severity: Event severity.
            metadata: Optional event metadata.
        """
        try:
            from authentication.models.security_events import SecurityEvent

            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type=event_type,
                severity=severity,
                is_suspicious=False,
                metadata=metadata or {},
            )
        except Exception as exc:
            logger.warning(
                "Failed to log security event for user=%s website=%s: %s",
                getattr(self.user, "pk", None),
                getattr(self.website, "pk", None),
                exc,
            )