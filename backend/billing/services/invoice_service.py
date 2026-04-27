from __future__ import annotations

import secrets
from datetime import timedelta
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from billing.constants import InvoicePurpose, InvoiceStatus
from billing.models.invoice import (
    Invoice,
)


class InvoiceService:
    """
    Service layer for invoice write operations and lifecycle transitions.

    This service owns business rules for creating, updating, issuing,
    expiring, cancelling, and settling invoices.

    Design goals:
        1. Keep the Invoice model dumb.
        2. Centralize all invoice write logic in one place.
        3. Enforce tenant and workflow consistency.
        4. Prevent invalid state transitions.
        5. Be safe for future integration with payments_processor and ledger.

    Notes:
        1. This service does not process payments directly.
        2. This service does not post to the ledger directly.
        3. Payment collection should happen through payments_processor.
        4. Financial recording should happen through ledger after confirmed settlement.
    """

    TERMINAL_STATUSES = {
        InvoiceStatus.PAID,
        InvoiceStatus.CANCELLED,
        InvoiceStatus.EXPIRED,
    }

    @staticmethod
    def _generate_payment_token() -> str:
        """
        Generate a secure token for invoice payment links.

        Returns:
            str: A URL safe random token.
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def _validate_amount(*, amount: Decimal) -> None:
        """
        Validate that the invoice amount is greater than zero.

        Args:
            amount: Invoice amount to validate.

        Raises:
            ValidationError: If the amount is zero or negative.
        """
        if amount <= Decimal("0"):
            raise ValidationError("Invoice amount must be greater than zero.")

    @staticmethod
    def _validate_recipient(
        *,
        client,
        recipient_email: str,
    ) -> None:
        """
        Validate that the invoice has a resolvable recipient.

        Args:
            client: Linked user object or None.
            recipient_email: Fallback recipient email.

        Raises:
            ValidationError: If neither a client nor recipient email is provided.
        """
        if client is None and not recipient_email:
            raise ValidationError(
                "Either client or recipient_email must be provided."
            )

    @staticmethod
    def _validate_related_objects(
        *,
        order_id,
        special_order_id,
        class_purchase_id,
    ) -> None:
        """
        Validate that the invoice points to at most one billable object.

        Args:
            order_id: Optional linked order id.
            special_order_id: Optional linked special order id.
            class_purchase_id: Optional linked class purchase id.

        Raises:
            ValidationError: If more than one billable object is linked.
        """
        linked_count = sum(
            1
            for value in (order_id, special_order_id, class_purchase_id)
            if value
        )
        if linked_count > 1:
            raise ValidationError(
                "An invoice can reference only one billable object."
            )

    @staticmethod
    def _validate_due_at(
        *,
        due_at,
        issued_at=None,
    ) -> None:
        """
        Validate invoice timing fields.

        Args:
            due_at: Payment due timestamp.
            issued_at: Optional issued timestamp.

        Raises:
            ValidationError: If due_at is missing or earlier than issued_at.
        """
        if due_at is None:
            raise ValidationError("due_at is required.")

        if issued_at is not None and due_at < issued_at:
            raise ValidationError("due_at cannot be earlier than issued_at.")

    @staticmethod
    def _validate_client_tenancy(
        *,
        website,
        client,
    ) -> None:
        """
        Validate that the client belongs to the same tenant when applicable.

        Args:
            website: Website tenant for the invoice.
            client: Linked user object or None.

        Raises:
            ValidationError: If the client appears to belong to another tenant.
        """
        if client is None:
            return

        client_website_id = getattr(client, "website_id", None)
        if client_website_id and client_website_id != website.id:
            raise ValidationError(
                "Client must belong to the same website as the invoice."
            )

    @classmethod
    def validate_invoice_payload(
        cls,
        *,
        website,
        amount: Decimal,
        due_at,
        client=None,
        recipient_email: str = "",
        order_id=None,
        special_order_id=None,
        class_purchase_id=None,
        issued_at=None,
    ) -> None:
        """
        Validate invoice payload before create or update operations.

        Args:
            website: Tenant website.
            amount: Monetary amount to charge.
            due_at: Due timestamp.
            client: Optional system user recipient.
            recipient_email: Optional external recipient email.
            order_id: Optional linked order id.
            special_order_id: Optional linked special order id.
            class_purchase_id: Optional linked class purchase id.
            issued_at: Optional issued timestamp.

        Raises:
            ValidationError: If any business rule is violated.
        """
        cls._validate_amount(amount=amount)
        cls._validate_recipient(
            client=client,
            recipient_email=recipient_email,
        )
        cls._validate_related_objects(
            order_id=order_id,
            special_order_id=special_order_id,
            class_purchase_id=class_purchase_id,
        )
        cls._validate_due_at(due_at=due_at, issued_at=issued_at)
        cls._validate_client_tenancy(website=website, client=client)

    @classmethod
    def create_invoice(
        cls,
        *,
        website,
        title: str,
        amount: Decimal,
        due_at,
        issued_by=None,
        purpose: str = InvoicePurpose.OTHER,
        description: str = "",
        client=None,
        recipient_email: str = "",
        recipient_name: str = "",
        order=None,
        special_order=None,
        class_purchase=None,
        order_number: str = "",
        currency: str = "",
        custom_payment_link: str = "",
    ) -> Invoice:
        """
        Create a new draft invoice after validating the payload.

        Args:
            website: Tenant website that owns the invoice.
            title: Human readable invoice title.
            amount: Amount owed.
            due_at: Payment deadline.
            issued_by: User creating the invoice.
            purpose: Structured invoice purpose.
            description: Optional invoice description.
            client: Optional linked recipient user.
            recipient_email: Optional external recipient email.
            recipient_name: Optional recipient display name.
            order: Optional linked order.
            special_order: Optional linked special order.
            class_purchase: Optional linked class purchase.
            order_number: Optional display reference.
            currency: Optional currency code.
            custom_payment_link: Optional override payment link.

        Returns:
            Invoice: Newly created draft invoice.

        Raises:
            ValidationError: If validation fails.
        """
        cls.validate_invoice_payload(
            website=website,
            amount=amount,
            due_at=due_at,
            client=client,
            recipient_email=recipient_email,
            order_id=getattr(order, "id", None),
            special_order_id=getattr(special_order, "id", None),
            class_purchase_id=getattr(class_purchase, "id", None),
        )

        return Invoice.objects.create(
            website=website,
            title=title,
            amount=amount,
            due_at=due_at,
            issued_by=issued_by,
            purpose=purpose,
            description=description,
            client=client,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
            order_number=order_number,
            currency=currency,
            custom_payment_link=custom_payment_link,
            status=InvoiceStatus.DRAFT,
        )

    @staticmethod
    def _get_locked_invoice(*, invoice_id: int) -> Invoice:
        """
        Retrieve and lock an invoice row for safe state mutation.

        Args:
            invoice_id: Primary key of the invoice to lock.

        Returns:
            Invoice: Locked invoice instance.
        """
        return Invoice.objects.select_for_update().get(id=invoice_id)

    @classmethod
    @transaction.atomic
    def issue_invoice(cls, *, invoice: Invoice) -> Invoice:
        """
        Transition a draft invoice to issued state.

        Args:
            invoice: Invoice instance to issue.

        Returns:
            Invoice: Updated issued invoice.

        Raises:
            ValidationError: If the invoice is not in draft state.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)

        if locked_invoice.status != InvoiceStatus.DRAFT:
            raise ValidationError("Only draft invoices can be issued.")

        cls._validate_due_at(
            due_at=locked_invoice.due_at,
            issued_at=timezone.now(),
        )

        locked_invoice.status = InvoiceStatus.ISSUED
        locked_invoice.issued_at = timezone.now()
        locked_invoice.save(
            update_fields=[
                "status",
                "issued_at",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def cancel_invoice(cls, *, invoice: Invoice) -> Invoice:
        """
        Cancel an invoice that has not been fully paid.

        Args:
            invoice: Invoice instance to cancel.

        Returns:
            Invoice: Updated cancelled invoice.

        Raises:
            ValidationError: If the invoice is already paid or already terminal.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)

        if locked_invoice.status == InvoiceStatus.PAID:
            raise ValidationError("Paid invoices cannot be cancelled.")

        if locked_invoice.status in {
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED,
        }:
            raise ValidationError(
                "Invoice is already in a terminal non payable state."
            )

        locked_invoice.status = InvoiceStatus.CANCELLED
        locked_invoice.cancelled_at = timezone.now()
        locked_invoice.save(
            update_fields=[
                "status",
                "cancelled_at",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def expire_invoice(cls, *, invoice: Invoice) -> Invoice:
        """
        Mark an invoice as expired when it is no longer payable.

        Args:
            invoice: Invoice instance to expire.

        Returns:
            Invoice: Updated expired invoice.

        Raises:
            ValidationError: If the invoice is already paid or already terminal.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)

        if locked_invoice.status == InvoiceStatus.PAID:
            raise ValidationError("Paid invoices cannot be expired.")

        if locked_invoice.status in {
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED,
        }:
            raise ValidationError(
                "Invoice is already in a terminal non payable state."
            )

        locked_invoice.status = InvoiceStatus.EXPIRED
        locked_invoice.expired_at = timezone.now()
        locked_invoice.save(
            update_fields=[
                "status",
                "expired_at",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def mark_partially_paid(
        cls,
        *,
        invoice: Invoice,
    ) -> Invoice:
        """
        Mark an invoice as partially paid.

        Args:
            invoice: Invoice instance to update.

        Returns:
            Invoice: Updated invoice.

        Raises:
            ValidationError: If the invoice is already terminal.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)

        if locked_invoice.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal invoices cannot be marked partially paid."
            )

        locked_invoice.status = InvoiceStatus.PARTIALLY_PAID
        locked_invoice.save(update_fields=["status", "updated_at"])
        return locked_invoice

    @classmethod
    @transaction.atomic
    def mark_paid(
        cls,
        *,
        invoice: Invoice,
        paid_at=None,
    ) -> Invoice:
        """
        Mark an invoice as fully paid.

        Args:
            invoice: Invoice instance to update.
            paid_at: Optional explicit settlement timestamp.

        Returns:
            Invoice: Updated paid invoice.

        Raises:
            ValidationError: If the invoice is cancelled or expired.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)

        if locked_invoice.status in {
            InvoiceStatus.CANCELLED,
            InvoiceStatus.EXPIRED,
        }:
            raise ValidationError(
                "Cancelled or expired invoices cannot be marked paid."
            )

        locked_invoice.status = InvoiceStatus.PAID
        locked_invoice.paid_at = paid_at or timezone.now()
        locked_invoice.save(
            update_fields=[
                "status",
                "paid_at",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def attach_payment_intent_reference(
        cls,
        *,
        invoice: Invoice,
        payment_intent_reference: str,
    ) -> Invoice:
        """
        Attach a payment intent reference from payments_processor.

        Args:
            invoice: Invoice instance to update.
            payment_intent_reference: External or internal payment intent reference.

        Returns:
            Invoice: Updated invoice.

        Raises:
            ValidationError: If the reference is empty.
        """
        if not payment_intent_reference:
            raise ValidationError(
                "payment_intent_reference is required."
            )

        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)
        locked_invoice.payment_intent_reference = payment_intent_reference
        locked_invoice.save(
            update_fields=[
                "payment_intent_reference",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def ensure_payment_token(
        cls,
        *,
        invoice: Invoice,
        expiry_hours: int = 72,
        force_refresh: bool = False,
    ) -> Invoice:
        """
        Ensure that the invoice has a valid payment token.

        Args:
            invoice: Invoice instance to update.
            expiry_hours: Number of hours before the token expires.
            force_refresh: Whether to forcibly regenerate the token.

        Returns:
            Invoice: Updated invoice containing a valid token.

        Raises:
            ValidationError: If expiry_hours is invalid.
        """
        if expiry_hours <= 0:
            raise ValidationError("expiry_hours must be greater than zero.")

        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)
        now = timezone.now()

        token_still_valid = (
            locked_invoice.payment_token
            and locked_invoice.token_expires_at
            and locked_invoice.token_expires_at > now
        )

        if token_still_valid and not force_refresh:
            return locked_invoice

        locked_invoice.payment_token = cls._generate_payment_token()
        locked_invoice.token_expires_at = now + timedelta(hours=expiry_hours)
        locked_invoice.save(
            update_fields=[
                "payment_token",
                "token_expires_at",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def mark_email_sent(
        cls,
        *,
        invoice: Invoice,
        sent_at=None,
    ) -> Invoice:
        """
        Update invoice email delivery tracking.

        Args:
            invoice: Invoice instance to update.
            sent_at: Optional timestamp for delivery.

        Returns:
            Invoice: Updated invoice with email tracking fields incremented.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)
        locked_invoice.email_sent_at = sent_at or timezone.now()
        locked_invoice.email_sent_count += 1
        locked_invoice.save(
            update_fields=[
                "email_sent_at",
                "email_sent_count",
                "updated_at",
            ]
        )
        return locked_invoice

    @classmethod
    @transaction.atomic
    def update_invoice_metadata(
        cls,
        *,
        invoice: Invoice,
        title: Optional[str] = None,
        description: Optional[str] = None,
        recipient_name: Optional[str] = None,
        recipient_email: Optional[str] = None,
        due_at=None,
        purpose: Optional[str] = None,
        custom_payment_link: Optional[str] = None,
        order_number: Optional[str] = None,
    ) -> Invoice:
        """
        Update editable invoice metadata for non terminal invoices.

        Args:
            invoice: Invoice instance to update.
            title: Optional new title.
            description: Optional new description.
            recipient_name: Optional new recipient name.
            recipient_email: Optional new recipient email.
            due_at: Optional new due timestamp.
            purpose: Optional new purpose.
            custom_payment_link: Optional new payment link override.
            order_number: Optional new display reference.

        Returns:
            Invoice: Updated invoice.

        Raises:
            ValidationError: If the invoice is paid, cancelled, or expired.
        """
        locked_invoice = cls._get_locked_invoice(invoice_id=invoice.pk)

        if locked_invoice.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal invoices cannot be edited."
            )

        if title is not None:
            locked_invoice.title = title

        if description is not None:
            locked_invoice.description = description

        if recipient_name is not None:
            locked_invoice.recipient_name = recipient_name

        if recipient_email is not None:
            locked_invoice.recipient_email = recipient_email

        if due_at is not None:
            locked_invoice.due_at = due_at

        if purpose is not None:
            locked_invoice.purpose = purpose

        if custom_payment_link is not None:
            locked_invoice.custom_payment_link = custom_payment_link

        if order_number is not None:
            locked_invoice.order_number = order_number


        cls.validate_invoice_payload(
            website=locked_invoice.website,
            amount=locked_invoice.amount,
            due_at=locked_invoice.due_at,
            client=locked_invoice.client,
            recipient_email=locked_invoice.recipient_email,
            order_id=getattr(locked_invoice.order, "pk", None),
            special_order_id=getattr(
                locked_invoice.special_order,
                "pk",
                None,
            ),
            class_purchase_id=getattr(
                locked_invoice.class_purchase,
                "pk",
                None,
            ),
            issued_at=locked_invoice.issued_at,
        )

        locked_invoice.save(
            update_fields=[
                "title",
                "description",
                "recipient_name",
                "recipient_email",
                "due_at",
                "purpose",
                "custom_payment_link",
                "order_number",
                "updated_at",
            ]
        )
        return locked_invoice