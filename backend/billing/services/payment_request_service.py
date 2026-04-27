from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError

import secrets
from django.db import transaction
from datetime import timedelta
from django.utils import timezone

from billing.constants import PaymentRequestStatus
from billing.models.payment_request import PaymentRequest


class PaymentRequestService:
    """
    Own payment request write operations and lifecycle transitions.
    """

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate payment request amount.

        Args:
            amount:
                Amount to validate.

        Raises:
            ValidationError:
                Raised when the amount is not greater than zero.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                "Payment request amount must be greater than zero."
            )

    @staticmethod
    def _validate_recipient(
        *,
        client,
        recipient_email: str,
    ) -> None:
        """
        Validate payment request recipient information.

        Args:
            client:
                Linked user recipient, if any.
            recipient_email:
                Fallback recipient email.

        Raises:
            ValidationError:
                Raised when no recipient path exists.
        """
        if client is None and not recipient_email:
            raise ValidationError(
                "Either client or recipient_email is required."
            )

    @classmethod
    def create_payment_request(
        cls,
        *,
        website,
        title: str,
        amount: Decimal,
        requested_by=None,
        purpose: str,
        description: str = "",
        client=None,
        recipient_email: str = "",
        recipient_name: str = "",
        order=None,
        special_order=None,
        class_purchase=None,
        due_at=None,
        currency: str = "",
    ) -> PaymentRequest:
        """
        Create a draft payment request.

        Returns:
            PaymentRequest: Newly created draft payment request.
        """
        cls._validate_amount(amount=amount)
        cls._validate_recipient(
            client=client,
            recipient_email=recipient_email,
        )

        return PaymentRequest.objects.create(
            website=website,
            title=title,
            amount=amount,
            requested_by=requested_by,
            purpose=purpose,
            description=description,
            client=client,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
            due_at=due_at,
            currency=currency,
            status=PaymentRequestStatus.DRAFT,
        )

    @staticmethod
    def _get_locked_payment_request(
        *,
        payment_request_id: int,
    ) -> PaymentRequest:
        """
        Retrieve and lock a payment request for safe mutation.

        Args:
            payment_request_id:
                Payment request primary key.

        Returns:
            PaymentRequest: Locked payment request instance.
        """
        return PaymentRequest.objects.select_for_update().get(
            pk=payment_request_id
        )

    @classmethod
    @transaction.atomic
    def issue_payment_request(
        cls,
        *,
        payment_request: PaymentRequest,
    ) -> PaymentRequest:
        """
        Mark a draft payment request as issued.

        Args:
            payment_request:
                Payment request to update.

        Returns:
            PaymentRequest: Updated payment request.
        """
        locked_request = cls._get_locked_payment_request(
            payment_request_id=payment_request.pk
        )
        locked_request.status = PaymentRequestStatus.ISSUED
        locked_request.issued_at = timezone.now()
        locked_request.save(
            update_fields=["status", "issued_at", "updated_at"]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def mark_partially_paid(
        cls,
        *,
        payment_request: PaymentRequest,
    ) -> PaymentRequest:
        """
        Mark a payment request as partially paid.

        Args:
            payment_request:
                Payment request to update.

        Returns:
            PaymentRequest: Updated payment request.
        """
        locked_request = cls._get_locked_payment_request(
            payment_request_id=payment_request.pk
        )
        locked_request.status = PaymentRequestStatus.PARTIALLY_PAID
        locked_request.save(update_fields=["status", "updated_at"])
        return locked_request

    @classmethod
    @transaction.atomic
    def mark_paid(
        cls,
        *,
        payment_request: PaymentRequest,
    ) -> PaymentRequest:
        """
        Mark a payment request as fully paid.

        Args:
            payment_request:
                Payment request to update.

        Returns:
            PaymentRequest: Updated payment request.
        """
        locked_request = cls._get_locked_payment_request(
            payment_request_id=payment_request.pk
        )
        locked_request.status = PaymentRequestStatus.PAID
        locked_request.paid_at = timezone.now()
        locked_request.save(
            update_fields=["status", "paid_at", "updated_at"]
        )
        return locked_request
    

    @staticmethod
    def _generate_payment_token() -> str:
        """
        Generate a secure token for payment request payment links.

        Returns:
            str:
                URL-safe random token.
        """
        return secrets.token_urlsafe(32)


    @classmethod
    @transaction.atomic
    def ensure_payment_token(
        cls,
        *,
        payment_request: PaymentRequest,
        expiry_hours: int = 72,
        force_refresh: bool = False,
    ) -> PaymentRequest:
        """
        Ensure that the payment request has a valid payment token.

        Args:
            payment_request:
                Payment request instance to update.
            expiry_hours:
                Number of hours before token expires.
            force_refresh:
                Whether to forcibly regenerate token.

        Returns:
            PaymentRequest:
                Updated payment request containing a valid token.

        Raises:
            ValidationError:
                Raised when expiry_hours is invalid.
        """
        if expiry_hours <= 0:
            raise ValidationError(
                "expiry_hours must be greater than zero."
            )

        locked_request = cls._get_locked_payment_request(
            payment_request_id=payment_request.pk
        )
        now = timezone.now()

        token_still_valid = (
            locked_request.payment_token
            and locked_request.token_expires_at
            and locked_request.token_expires_at > now
        )

        if token_still_valid and not force_refresh:
            return locked_request

        locked_request.payment_token = cls._generate_payment_token()
        locked_request.token_expires_at = now + timedelta(
            hours=expiry_hours
        )
        locked_request.save(
            update_fields=[
                "payment_token",
                "token_expires_at",
                "updated_at",
            ]
        )
        return locked_request