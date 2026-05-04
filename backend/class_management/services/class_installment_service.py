from __future__ import annotations

from decimal import Decimal
from decimal import ROUND_HALF_UP
from typing import Iterable

from django.db import models
from django.db import transaction
from django.utils import timezone

from class_management.constants import (
    ClassInstallmentStatus,
    ClassOrderStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import ClassPaymentError
from class_management.models.class_installments import (
    ClassInstallment,
    ClassInstallmentPlan,
)
from class_management.models.class_order import ClassOrder
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from class_management.state_machine import ClassOrderStateMachine
from notifications_system.services.notification_service import (
    NotificationService,
)


class ClassInstallmentService:
    """
    Service for creating and managing class installment schedules.
    """

    PLAN_ALLOWED_STATUSES = {
        ClassOrderStatus.ACCEPTED,
        ClassOrderStatus.PENDING_PAYMENT,
        ClassOrderStatus.PARTIALLY_PAID,
    }

    @classmethod
    @transaction.atomic
    def create_plan(
        cls,
        *,
        class_order: ClassOrder,
        installment_amounts: Iterable[Decimal],
        due_dates: Iterable,
        created_by=None,
        deposit_amount: Decimal = Decimal("0.00"),
        allow_work_before_full_payment: bool = True,
        pause_work_when_overdue: bool = True,
        notes: str = "",
    ) -> ClassInstallmentPlan:
        """
        Create an installment plan for an accepted class order.
        """
        if class_order.status not in cls.PLAN_ALLOWED_STATUSES:
            raise ClassPaymentError(
                "Cannot create installments while class order status is "
                f"{class_order.status}."
            )

        cls._ensure_no_existing_plan(class_order=class_order)

        amounts = list(installment_amounts)
        dates = list(due_dates)

        cls._validate_installment_inputs(
            class_order=class_order,
            amounts=amounts,
            due_dates=dates,
            deposit_amount=deposit_amount,
        )

        plan = ClassInstallmentPlan.objects.create(
            class_order=class_order,
            total_amount=class_order.final_amount,
            deposit_amount=deposit_amount,
            installment_count=len(amounts),
            allow_work_before_full_payment=allow_work_before_full_payment,
            pause_work_when_overdue=pause_work_when_overdue,
            notes=notes,
        )

        installments = [
            ClassInstallment(
                plan=plan,
                label=f"Installment {index}",
                amount=amount,
                due_at=due_at,
                status=ClassInstallmentStatus.PENDING,
            )
            for index, (amount, due_at) in enumerate(
                zip(amounts, dates),
                start=1,
            )
        ]

        ClassInstallment.objects.bulk_create(installments)

        ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.PENDING_PAYMENT,
            triggered_by=created_by,
            metadata={
                "installment_count": len(amounts),
                "total_amount": str(class_order.final_amount),
                "deposit_amount": str(deposit_amount),
            },
        )

        return plan

    @classmethod
    @transaction.atomic
    def create_equal_plan(
        cls,
        *,
        class_order: ClassOrder,
        installment_count: int,
        due_dates: Iterable,
        created_by=None,
        deposit_amount: Decimal = Decimal("0.00"),
        allow_work_before_full_payment: bool = True,
        pause_work_when_overdue: bool = True,
        notes: str = "",
    ) -> ClassInstallmentPlan:
        """
        Create an equal installment plan.

        Rounding differences are added to the last installment.
        """
        if installment_count <= 0:
            raise ClassPaymentError(
                "Installment count must be greater than zero."
            )

        remaining = class_order.final_amount - deposit_amount

        if remaining <= Decimal("0.00"):
            raise ClassPaymentError(
                "Installment amount after deposit must be positive."
            )

        base_amount = (remaining / installment_count).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        amounts = [base_amount for _ in range(installment_count)]
        rounded_total = sum(amounts, Decimal("0.00"))
        rounding_gap = remaining - rounded_total
        amounts[-1] += rounding_gap

        return cls.create_plan(
            class_order=class_order,
            installment_amounts=amounts,
            due_dates=due_dates,
            created_by=created_by,
            deposit_amount=deposit_amount,
            allow_work_before_full_payment=allow_work_before_full_payment,
            pause_work_when_overdue=pause_work_when_overdue,
            notes=notes,
        )

    @classmethod
    @transaction.atomic
    def apply_payment_to_installment(
        cls,
        *,
        installment: ClassInstallment,
        amount: Decimal,
        payment_intent_id: str = "",
        invoice_id: str = "",
    ) -> ClassInstallment:
        """
        Apply payment to a specific installment.
        """
        if amount <= Decimal("0.00"):
            raise ClassPaymentError("Payment amount must be positive.")

        if installment.status in {
            ClassInstallmentStatus.PAID,
            ClassInstallmentStatus.CANCELLED,
            ClassInstallmentStatus.WAIVED,
        }:
            raise ClassPaymentError(
                "Cannot apply payment to a closed installment."
            )

        installment.paid_amount += amount

        if installment.paid_amount >= installment.amount:
            installment.status = ClassInstallmentStatus.PAID
            installment.paid_at = timezone.now()
        elif installment.due_at <= timezone.now():
            installment.status = ClassInstallmentStatus.OVERDUE
        else:
            installment.status = ClassInstallmentStatus.DUE

        if payment_intent_id:
            installment.payment_intent_id = payment_intent_id

        if invoice_id:
            installment.invoice_id = invoice_id

        installment.save(
            update_fields=[
                "paid_amount",
                "status",
                "paid_at",
                "payment_intent_id",
                "invoice_id",
                "updated_at",
            ],
        )

        return installment

    @classmethod
    @transaction.atomic
    def waive_installment(
        cls,
        *,
        installment: ClassInstallment,
        waived_by,
        reason: str = "",
    ) -> ClassInstallment:
        """
        Waive an unpaid installment.
        """
        if installment.status == ClassInstallmentStatus.PAID:
            raise ClassPaymentError(
                "Cannot waive a paid installment."
            )

        installment.status = ClassInstallmentStatus.WAIVED
        installment.metadata = {
            **installment.metadata,
            "waived_by_id": getattr(waived_by, "pk", None),
            "waived_at": timezone.now().isoformat(),
            "reason": reason,
        }
        installment.save(
            update_fields=[
                "status",
                "metadata",
                "updated_at",
            ],
        )

        ClassTimelineService.record(
            class_order=installment.plan.class_order,
            event_type=ClassTimelineEventType.PAYMENT_APPLIED,
            title="Class installment waived",
            description=reason,
            triggered_by=waived_by,
            metadata={
                "installment_id": installment.pk,
                "amount": str(installment.amount),
            },
        )

        return installment

    @classmethod
    @transaction.atomic
    def cancel_plan(
        cls,
        *,
        plan: ClassInstallmentPlan,
        cancelled_by,
        reason: str = "",
    ) -> ClassInstallmentPlan:
        """
        Cancel all unpaid installments in a plan.
        """
        now = timezone.now()

        ClassInstallment.objects.filter(
            plan=plan,
        ).exclude(
            status__in=[
                ClassInstallmentStatus.PAID,
                ClassInstallmentStatus.WAIVED,
            ],
        ).update(
            status=ClassInstallmentStatus.CANCELLED,
            metadata={
                "cancelled_by_id": getattr(cancelled_by, "pk", None),
                "cancelled_at": now.isoformat(),
                "reason": reason,
            },
            updated_at=now,
        )

        ClassTimelineService.record(
            class_order=plan.class_order,
            event_type=ClassTimelineEventType.CANCELLED,
            title="Class installment plan cancelled",
            description=reason,
            triggered_by=cancelled_by,
        )

        return plan

    @classmethod
    @transaction.atomic
    def mark_due_installments(cls) -> int:
        """
        Mark pending installments as due when due date arrives.
        """
        now = timezone.now()

        return ClassInstallment.objects.filter(
            status=ClassInstallmentStatus.PENDING,
            due_at__lte=now,
        ).update(
            status=ClassInstallmentStatus.DUE,
            updated_at=now,
        )

    @classmethod
    @transaction.atomic
    def mark_overdue_installments(cls) -> int:
        """
        Mark due unpaid installments as overdue.

        Also pauses work when the plan requires it.
        """
        now = timezone.now()

        overdue_installments = ClassInstallment.objects.select_related(
            "plan",
            "plan__class_order",
        ).filter(
            status__in=[
                ClassInstallmentStatus.PENDING,
                ClassInstallmentStatus.DUE,
            ],
            due_at__lt=now,
            paid_amount__lt=models.F("amount"),
        )

        count = 0

        for installment in overdue_installments:
            installment.status = ClassInstallmentStatus.OVERDUE
            installment.save(
                update_fields=[
                    "status",
                    "updated_at",
                ],
            )

            class_order = installment.plan.class_order

            ClassTimelineService.record(
                class_order=class_order,
                event_type=ClassTimelineEventType.INSTALLMENT_OVERDUE,
                title="Class installment overdue",
                metadata={
                    "installment_id": installment.pk,
                    "amount": str(installment.amount),
                    "paid_amount": str(installment.paid_amount),
                },
            )

            if installment.plan.pause_work_when_overdue:
                if ClassOrderStateMachine.can_transition(
                    from_status=class_order.status,
                    to_status=ClassOrderStatus.PAUSED,
                ):
                    cls.pause_work_for_overdue_installment(
                        class_order=class_order,
                    )

            NotificationService.notify(
                event_key="class.installment_overdue",
                recipient=class_order.client,
                website=class_order.website,
                context={
                    "class_order_id": class_order.pk,
                    "title": class_order.title,
                    "installment_id": installment.pk,
                    "amount": str(installment.amount),
                    "currency": class_order.currency,
                },
            )

            count += 1

        return count

    @classmethod
    @transaction.atomic
    def pause_work_for_overdue_installment(
        cls,
        *,
        class_order: ClassOrder,
    ) -> ClassOrder:
        """
        Pause work because an installment is overdue.
        """
        return ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.PAUSED,
            reason="installment_overdue",
            metadata={
                "pause_source": "installment_overdue",
            },
        )

    @classmethod
    @transaction.atomic
    def resume_work(
        cls,
        *,
        class_order: ClassOrder,
        resumed_by,
        reason: str = "",
    ) -> ClassOrder:
        """
        Resume paused class work.
        """
        return ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.IN_PROGRESS,
            triggered_by=resumed_by,
            reason=reason,
            metadata={
                "resume_source": "manual",
            },
        )

    @staticmethod
    def _validate_installment_inputs(
        *,
        class_order: ClassOrder,
        amounts: list[Decimal],
        due_dates: list,
        deposit_amount: Decimal,
    ) -> None:
        """
        Validate plan totals and due date alignment.
        """
        if not amounts:
            raise ClassPaymentError(
                "At least one installment amount is required."
            )

        if len(amounts) != len(due_dates):
            raise ClassPaymentError(
                "Installment amounts and due dates must match."
            )

        if deposit_amount < Decimal("0.00"):
            raise ClassPaymentError(
                "Deposit amount cannot be negative."
            )

        for amount in amounts:
            if amount <= Decimal("0.00"):
                raise ClassPaymentError(
                    "Installment amounts must be positive."
                )

        total_installments = sum(amounts, Decimal("0.00"))
        expected_total = class_order.final_amount - deposit_amount

        if total_installments != expected_total:
            raise ClassPaymentError(
                "Installment total must equal final amount "
                "minus deposit amount."
            )

    @staticmethod
    def _ensure_no_existing_plan(*, class_order: ClassOrder) -> None:
        """
        Ensure a class order does not already have an installment plan.
        """
        existing_plan = ClassInstallmentPlan.objects.filter(
            class_order=class_order,
        ).exists()

        if existing_plan:
            raise ClassPaymentError(
                "This class order already has an installment plan."
            )