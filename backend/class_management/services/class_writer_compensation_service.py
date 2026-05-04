from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassOrderStatus,
    ClassTimelineEventType,
    ClassWriterCompensationStatus,
    ClassWriterCompensationType,
)
from class_management.exceptions import ClassWriterCompensationError
from class_management.models import (
    ClassOrder,
    ClassWriterCompensation,
)
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from notifications_system.services.notification_service import (
    NotificationService,
)


class ClassWriterCompensationService:
    """
    Service for admin-controlled writer compensation.

    Writer payment may be percentage-based or fixed-amount based.
    Posting to wallet happens after approval and class completion.
    """

    @classmethod
    @transaction.atomic
    def set_compensation(
        cls,
        *,
        class_order: ClassOrder,
        writer,
        compensation_type: str,
        set_by,
        percentage: Decimal | None = None,
        fixed_amount: Decimal | None = None,
        admin_notes: str = "",
    ) -> ClassWriterCompensation:
        """
        Create or update writer compensation for a class order.
        """
        cls._validate_writer(
            class_order=class_order,
            writer=writer,
        )

        final_amount = cls._calculate_final_amount(
            class_order=class_order,
            compensation_type=compensation_type,
            percentage=percentage,
            fixed_amount=fixed_amount,
        )

        compensation, _ = (
            ClassWriterCompensation.objects.update_or_create(
                class_order=class_order,
                defaults={
                    "writer": writer,
                    "compensation_type": compensation_type,
                    "percentage": percentage,
                    "fixed_amount": fixed_amount,
                    "final_amount": final_amount,
                    "status": ClassWriterCompensationStatus.DRAFT,
                    "admin_notes": admin_notes,
                },
            )
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.WRITER_ASSIGNED,
            title="Class writer compensation set",
            triggered_by=set_by,
            metadata={
                "writer_id": cls._get_pk(writer),
                "compensation_id": cls._get_pk(compensation),
                "compensation_type": compensation_type,
                "final_amount": str(final_amount),
            },
        )

        return compensation

    @classmethod
    @transaction.atomic
    def approve_compensation(
        cls,
        *,
        compensation: ClassWriterCompensation,
        approved_by,
    ) -> ClassWriterCompensation:
        """
        Approve writer compensation.
        """
        if compensation.status not in {
            ClassWriterCompensationStatus.DRAFT,
            ClassWriterCompensationStatus.APPROVED,
        }:
            raise ClassWriterCompensationError(
                "Only draft compensation can be approved."
            )

        if compensation.final_amount <= Decimal("0.00"):
            raise ClassWriterCompensationError(
                "Compensation amount must be positive."
            )

        compensation.status = ClassWriterCompensationStatus.APPROVED
        compensation.approved_by = approved_by
        compensation.approved_at = timezone.now()
        compensation.save(
            update_fields=[
                "status",
                "approved_by",
                "approved_at",
                "updated_at",
            ],
        )

        ClassTimelineService.record(
            class_order=compensation.class_order,
            event_type=ClassTimelineEventType.WRITER_ASSIGNED,
            title="Class writer compensation approved",
            triggered_by=approved_by,
            metadata={
                "compensation_id": cls._get_pk(compensation),
                "final_amount": str(compensation.final_amount),
            },
        )

        return compensation

    @classmethod
    @transaction.atomic
    def mark_earned(
        cls,
        *,
        class_order: ClassOrder,
        triggered_by=None,
    ) -> ClassWriterCompensation:
        """
        Mark compensation as earned after class completion.
        """
        if class_order.status != ClassOrderStatus.COMPLETED:
            raise ClassWriterCompensationError(
                "Writer compensation can only be earned after completion."
            )

        compensation = cls.get_compensation(class_order=class_order)

        if compensation.status != ClassWriterCompensationStatus.APPROVED:
            raise ClassWriterCompensationError(
                "Only approved compensation can be marked as earned."
            )

        compensation.status = ClassWriterCompensationStatus.EARNED
        compensation.earned_at = timezone.now()
        compensation.save(
            update_fields=[
                "status",
                "earned_at",
                "updated_at",
            ],
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.COMPLETED,
            title="Class writer compensation earned",
            triggered_by=triggered_by,
            metadata={
                "compensation_id": cls._get_pk(compensation),
                "amount": str(compensation.final_amount),
            },
        )

        return compensation

    @classmethod
    @transaction.atomic
    def post_to_writer_wallet(
        cls,
        *,
        compensation: ClassWriterCompensation,
        posted_by,
        metadata: dict[str, Any] | None = None,
    ) -> ClassWriterCompensation:
        """
        Credit earned class compensation to the writer wallet.
        """
        if compensation.status != ClassWriterCompensationStatus.EARNED:
            raise ClassWriterCompensationError(
                "Only earned compensation can be posted to wallet."
            )

        amount_to_post = compensation.final_amount - compensation.paid_amount

        if amount_to_post <= Decimal("0.00"):
            raise ClassWriterCompensationError(
                "No remaining compensation amount to post."
            )

        wallet_transaction_id = cls._credit_writer_wallet(
            compensation=compensation,
            amount=amount_to_post,
            posted_by=posted_by,
            metadata=metadata,
        )

        compensation.paid_amount += amount_to_post
        compensation.status = ClassWriterCompensationStatus.POSTED_TO_WALLET
        compensation.wallet_transaction_id = wallet_transaction_id
        compensation.posted_by = posted_by
        compensation.posted_at = timezone.now()
        compensation.save(
            update_fields=[
                "paid_amount",
                "status",
                "wallet_transaction_id",
                "posted_by",
                "posted_at",
                "updated_at",
            ],
        )

        class_order = compensation.class_order

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.COMPLETED,
            title="Class writer compensation posted to wallet",
            triggered_by=posted_by,
            metadata={
                "compensation_id": cls._get_pk(compensation),
                "amount": str(amount_to_post),
                "wallet_transaction_id": wallet_transaction_id,
            },
        )

        NotificationService.notify(
            event_key="class.writer_compensation_posted",
            recipient=compensation.writer,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "amount": str(amount_to_post),
                "currency": class_order.currency,
            },
            triggered_by=posted_by,
        )

        return compensation

    @staticmethod
    def get_compensation(
        *,
        class_order: ClassOrder,
    ) -> ClassWriterCompensation:
        """
        Return class writer compensation or raise a domain error.
        """
        compensation = ClassWriterCompensation.objects.filter(
            class_order=class_order,
        ).select_related(
            "class_order",
            "writer",
        ).first()

        if compensation is None:
            raise ClassWriterCompensationError(
                "This class order has no writer compensation set."
            )

        return compensation

    @classmethod
    def _validate_writer(
        cls,
        *,
        class_order: ClassOrder,
        writer,
    ) -> None:
        """
        Ensure compensation writer matches the assigned writer.
        """
        assigned_writer_pk = cls._get_related_pk(
            obj=class_order,
            field_name="assigned_writer",
        )
        writer_pk = cls._get_pk(writer)

        if assigned_writer_pk is None:
            raise ClassWriterCompensationError(
                "Assign a writer before setting compensation."
            )

        if assigned_writer_pk != writer_pk:
            raise ClassWriterCompensationError(
                "Compensation writer must match assigned writer."
            )

    @staticmethod
    def _calculate_final_amount(
        *,
        class_order: ClassOrder,
        compensation_type: str,
        percentage: Decimal | None,
        fixed_amount: Decimal | None,
    ) -> Decimal:
        """
        Calculate final writer compensation amount.
        """
        if compensation_type == ClassWriterCompensationType.PERCENTAGE:
            if percentage is None or percentage <= Decimal("0.00"):
                raise ClassWriterCompensationError(
                    "Percentage compensation requires a positive percentage."
                )

            if percentage > Decimal("100.00"):
                raise ClassWriterCompensationError(
                    "Percentage cannot exceed 100."
                )

            return (
                class_order.final_amount * percentage / Decimal("100.00")
            ).quantize(Decimal("0.01"))

        if compensation_type == ClassWriterCompensationType.FIXED_AMOUNT:
            if fixed_amount is None or fixed_amount <= Decimal("0.00"):
                raise ClassWriterCompensationError(
                    "Fixed compensation requires a positive amount."
                )

            if fixed_amount > class_order.final_amount:
                raise ClassWriterCompensationError(
                    "Writer compensation cannot exceed class amount."
                )

            return fixed_amount

        raise ClassWriterCompensationError(
            "Unsupported compensation type."
        )

    @classmethod
    def _credit_writer_wallet(
        cls,
        *,
        compensation: ClassWriterCompensation,
        amount: Decimal,
        posted_by,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Credit the writer wallet using the wallets app service contract.
        """
        from wallets.constants import WalletEntryType
        from wallets.services.wallet_service import WalletService

        class_order = compensation.class_order

        wallet = WalletService.get_writer_wallet(
            website=class_order.website,
            owner_user=compensation.writer,
            currency=class_order.currency,
        )

        transaction_record = WalletService.credit_wallet(
            wallet=wallet,
            amount=amount,
            entry_type=WalletEntryType.WRITER_EARNING,
            website=class_order.website,
            created_by=posted_by,
            description="Class writer compensation",
            reference=f"class_order:{class_order.pk}",
            reference_type="class_order",
            reference_id=str(class_order.pk),
            metadata={
                **(metadata or {}),
                "class_order_id": str(class_order.pk),
                "compensation_id": str(cls._get_pk(compensation)),
            },
        )

        return str(cls._get_pk(transaction_record))

    @staticmethod
    def _get_related_pk(*, obj: Any, field_name: str) -> Any:
        """
        Return the primary key of a related object safely.
        """
        related_obj = getattr(obj, field_name, None)
        return getattr(related_obj, "pk", None)

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return an object's primary key safely.
        """
        return getattr(obj, "pk", None)