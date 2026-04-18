from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from orders.models.legacy_models.order_adjustment_request import (
    OrderAdjustmentRequest,
    OrderAdjustmentStatus,
)


class OrderAdjustmentRequestService:
    """
    Own write operations and lifecycle transitions for order adjustment
    requests.

    This service manages the negotiation and funding lifecycle for
    order-side commercial adjustments such as:

        1. page increases
        2. slide increases
        3. deadline decreases
        4. extra services
        5. other out-of-scope paid changes

    Architectural boundaries:
        1. orders owns negotiation and decision workflow
        2. billing owns the receivable created after acceptance
        3. payments_processor collects payment
        4. ledger records actual money movement

    This service does not create payment intents, collect payment, or
    post to ledger directly.
    """

    ACTIVE_STATUSES = {
        OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
        OrderAdjustmentStatus.CLIENT_COUNTERED,
        OrderAdjustmentStatus.ACCEPTED,
        OrderAdjustmentStatus.FUNDING_PENDING,
    }

    TERMINAL_STATUSES = {
        OrderAdjustmentStatus.DECLINED,
        OrderAdjustmentStatus.CANCELLED,
        OrderAdjustmentStatus.FUNDED,
        OrderAdjustmentStatus.EXPIRED,
    }

    @staticmethod
    def _validate_amount(
        *,
        amount: Decimal,
        field_name: str,
    ) -> None:
        """
        Validate that a monetary amount is greater than zero.

        Args:
            amount:
                Amount to validate.
            field_name:
                Human-readable field name used in the error message.

        Raises:
            ValidationError:
                Raised when the amount is zero or negative.
        """
        if amount <= Decimal("0"):
            raise ValidationError(
                f"{field_name} must be greater than zero."
            )

    @staticmethod
    def _get_locked_adjustment_request(
        *,
        adjustment_request_id: int,
    ) -> OrderAdjustmentRequest:
        """
        Retrieve and lock an order adjustment request for safe mutation.

        Args:
            adjustment_request_id:
                Primary key of the adjustment request.

        Returns:
            OrderAdjustmentRequest:
                Locked adjustment request instance.
        """
        return OrderAdjustmentRequest.objects.select_for_update().get(
            pk=adjustment_request_id
        )

    @classmethod
    def create_adjustment_request(
        cls,
        *,
        website,
        order,
        adjustment_type: str,
        title: str,
        requested_amount: Decimal,
        requested_by=None,
        description: str = "",
        writer_justification: str = "",
        expires_at=None,
    ) -> OrderAdjustmentRequest:
        """
        Create a new order adjustment request.

        Args:
            website:
                Tenant website that owns the request.
            order:
                Order affected by the requested adjustment.
            adjustment_type:
                Structured adjustment type.
            title:
                Short title describing the request.
            requested_amount:
                Initial amount requested for the adjustment.
            requested_by:
                Actor who initiated the request.
            description:
                Optional customer-facing description.
            writer_justification:
                Optional internal or semi-internal reason for the request.
            expires_at:
                Optional timestamp after which the request is stale.

        Returns:
            OrderAdjustmentRequest:
                Newly created adjustment request.

        Raises:
            ValidationError:
                Raised when the requested amount is invalid.
        """
        cls._validate_amount(
            amount=requested_amount,
            field_name="requested_amount",
        )

        return OrderAdjustmentRequest.objects.create(
            website=website,
            order=order,
            requested_by=requested_by,
            adjustment_type=adjustment_type,
            title=title,
            description=description,
            writer_justification=writer_justification,
            requested_amount=requested_amount,
            status=OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
            expires_at=expires_at,
        )

    @classmethod
    @transaction.atomic
    def client_accept_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        reviewed_by=None,
        accepted_amount: Optional[Decimal] = None,
    ) -> OrderAdjustmentRequest:
        """
        Mark an adjustment request as accepted by the client.

        This method finalizes the agreed amount and prepares the request
        for downstream billing handoff.

        Args:
            adjustment_request:
                Adjustment request to update.
            reviewed_by:
                Actor finalizing or reviewing the acceptance.
            accepted_amount:
                Optional explicit agreed amount. When omitted, the service
                uses the client counter amount if present, otherwise the
                original requested amount.

        Returns:
            OrderAdjustmentRequest:
                Updated accepted adjustment request.

        Raises:
            ValidationError:
                Raised when the request is in a terminal state or when the
                final amount is invalid.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal adjustment requests cannot be accepted."
            )

        final_amount = accepted_amount
        if final_amount is None:
            if locked_request.client_counter_amount is not None:
                final_amount = locked_request.client_counter_amount
            else:
                final_amount = locked_request.requested_amount

        cls._validate_amount(
            amount=final_amount,
            field_name="final_amount",
        )

        locked_request.final_amount = final_amount
        locked_request.status = OrderAdjustmentStatus.ACCEPTED
        locked_request.accepted_at = timezone.now()
        locked_request.reviewed_by = reviewed_by
        locked_request.save(
            update_fields=[
                "final_amount",
                "status",
                "accepted_at",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def client_counter_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        counter_amount: Decimal,
        counter_reason: str = "",
        reviewed_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Record a client counter-offer for an adjustment request.

        Args:
            adjustment_request:
                Adjustment request to update.
            counter_amount:
                Amount proposed by the client.
            counter_reason:
                Optional explanation for the counter-offer.
            reviewed_by:
                Optional actor recording the counter.

        Returns:
            OrderAdjustmentRequest:
                Updated countered adjustment request.

        Raises:
            ValidationError:
                Raised when the request is terminal or the counter amount
                is invalid.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal adjustment requests cannot be countered."
            )

        cls._validate_amount(
            amount=counter_amount,
            field_name="counter_amount",
        )

        locked_request.client_counter_amount = counter_amount
        locked_request.client_counter_reason = counter_reason
        locked_request.status = OrderAdjustmentStatus.CLIENT_COUNTERED
        locked_request.countered_at = timezone.now()
        locked_request.reviewed_by = reviewed_by
        locked_request.save(
            update_fields=[
                "client_counter_amount",
                "client_counter_reason",
                "status",
                "countered_at",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def client_decline_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        reviewed_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Mark an adjustment request as declined by the client.

        Args:
            adjustment_request:
                Adjustment request to update.
            reviewed_by:
                Optional actor recording the decline.

        Returns:
            OrderAdjustmentRequest:
                Updated declined adjustment request.

        Raises:
            ValidationError:
                Raised when the request is already terminal.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal adjustment requests cannot be declined."
            )

        locked_request.status = OrderAdjustmentStatus.DECLINED
        locked_request.declined_at = timezone.now()
        locked_request.reviewed_by = reviewed_by
        locked_request.save(
            update_fields=[
                "status",
                "declined_at",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def cancel_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        reviewed_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Cancel an adjustment request.

        Args:
            adjustment_request:
                Adjustment request to update.
            reviewed_by:
                Optional actor performing the cancellation.

        Returns:
            OrderAdjustmentRequest:
                Updated cancelled adjustment request.

        Raises:
            ValidationError:
                Raised when the request is already funded or already in a
                terminal non-cancellable state.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status == OrderAdjustmentStatus.FUNDED:
            raise ValidationError(
                "Funded adjustment requests cannot be cancelled."
            )

        if locked_request.status in {
            OrderAdjustmentStatus.CANCELLED,
            OrderAdjustmentStatus.DECLINED,
            OrderAdjustmentStatus.EXPIRED,
        }:
            raise ValidationError(
                "Adjustment request is already terminal."
            )

        locked_request.status = OrderAdjustmentStatus.CANCELLED
        locked_request.reviewed_by = reviewed_by
        locked_request.save(
            update_fields=[
                "status",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def expire_request(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> OrderAdjustmentRequest:
        """
        Expire an adjustment request.

        Args:
            adjustment_request:
                Adjustment request to update.

        Returns:
            OrderAdjustmentRequest:
                Updated expired adjustment request.

        Raises:
            ValidationError:
                Raised when the request is already terminal.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal adjustment requests cannot be expired."
            )

        locked_request.status = OrderAdjustmentStatus.EXPIRED
        locked_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def mark_funding_pending(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        billing_payment_request=None,
        invoice=None,
        reviewed_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Mark an accepted adjustment request as awaiting settlement.

        This should be called after billing creates a receivable record.

        Args:
            adjustment_request:
                Adjustment request to update.
            billing_payment_request:
                Optional billing payment request created from the
                adjustment.
            invoice:
                Optional invoice created from the adjustment.
            reviewed_by:
                Optional actor linking the billing artifact.

        Returns:
            OrderAdjustmentRequest:
                Updated funding-pending adjustment request.

        Raises:
            ValidationError:
                Raised when the request is not accepted or when no
                billing artifact is supplied.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status != OrderAdjustmentStatus.ACCEPTED:
            raise ValidationError(
                "Only accepted adjustment requests can become "
                "funding pending."
            )

        if billing_payment_request is None and invoice is None:
            raise ValidationError(
                "A billing payment request or invoice is required."
            )

        locked_request.billing_payment_request = billing_payment_request
        locked_request.invoice = invoice
        locked_request.status = OrderAdjustmentStatus.FUNDING_PENDING
        locked_request.reviewed_by = reviewed_by
        locked_request.save(
            update_fields=[
                "billing_payment_request",
                "invoice",
                "status",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def mark_funded(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        funded_at=None,
        reviewed_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Mark an adjustment request as funded after successful settlement.

        Args:
            adjustment_request:
                Adjustment request to update.
            funded_at:
                Optional explicit funding timestamp.
            reviewed_by:
                Optional actor finalizing the funded state.

        Returns:
            OrderAdjustmentRequest:
                Updated funded adjustment request.

        Raises:
            ValidationError:
                Raised when the request is not in funding pending state.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status != OrderAdjustmentStatus.FUNDING_PENDING:
            raise ValidationError(
                "Only funding-pending requests can be marked funded."
            )

        locked_request.status = OrderAdjustmentStatus.FUNDED
        locked_request.funded_at = funded_at or timezone.now()
        locked_request.reviewed_by = reviewed_by
        locked_request.save(
            update_fields=[
                "status",
                "funded_at",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request

    @classmethod
    @transaction.atomic
    def update_request_metadata(
        cls,
        *,
        adjustment_request: OrderAdjustmentRequest,
        title: Optional[str] = None,
        description: Optional[str] = None,
        writer_justification: Optional[str] = None,
        expires_at=None,
        reviewed_by=None,
    ) -> OrderAdjustmentRequest:
        """
        Update editable metadata on an active adjustment request.

        Args:
            adjustment_request:
                Adjustment request to update.
            title:
                Optional new title.
            description:
                Optional new description.
            writer_justification:
                Optional new writer justification.
            expires_at:
                Optional new expiry timestamp.
            reviewed_by:
                Optional actor making the update.

        Returns:
            OrderAdjustmentRequest:
                Updated adjustment request.

        Raises:
            ValidationError:
                Raised when the request is terminal.
        """
        locked_request = cls._get_locked_adjustment_request(
            adjustment_request_id=adjustment_request.pk
        )

        if locked_request.status in cls.TERMINAL_STATUSES:
            raise ValidationError(
                "Terminal adjustment requests cannot be edited."
            )

        if title is not None:
            locked_request.title = title

        if description is not None:
            locked_request.description = description

        if writer_justification is not None:
            locked_request.writer_justification = (
                writer_justification
            )

        if expires_at is not None:
            locked_request.expires_at = expires_at

        if reviewed_by is not None:
            locked_request.reviewed_by = reviewed_by

        locked_request.save(
            update_fields=[
                "title",
                "description",
                "writer_justification",
                "expires_at",
                "reviewed_by",
                "updated_at",
            ]
        )
        return locked_request