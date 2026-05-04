from __future__ import annotations

from collections.abc import Container
from decimal import Decimal
from typing import Any

from django.db import transaction

from class_management.constants import (
    ClassOrderStatus,
    ClassPaymentStatus,
    ClassTimelineEventType,
)
from class_management.exceptions import (
    ClassOrderStateError,
    ClassWriterCompensationError,
)
from class_management.models.class_order import ClassOrder
from class_management.models.class_scope import ClassTask
from class_management.services.class_communication_service import (
    ClassCommunicationService,
)
from class_management.services.class_timeline_service import (
    ClassTimelineService,
)
from class_management.services.class_writer_compensation_service import (
    ClassWriterCompensationService,
)
from class_management.state_machine import ClassOrderStateMachine
from notifications_system.services.notification_service import (
    NotificationService,
)


class ClassOrderService:
    """
    Service layer for class order lifecycle operations.
    """

    SUBMIT_ALLOWED = {
        ClassOrderStatus.DRAFT,
    }
    REVIEW_ALLOWED = {
        ClassOrderStatus.SUBMITTED,
    }
    ACCEPT_PRICE_ALLOWED = {
        ClassOrderStatus.PRICE_PROPOSED,
        ClassOrderStatus.NEGOTIATING,
    }
    ASSIGN_ALLOWED = {
        ClassOrderStatus.PAID,
        ClassOrderStatus.PARTIALLY_PAID,
        ClassOrderStatus.ACCEPTED,
    }
    START_WORK_ALLOWED = {
        ClassOrderStatus.ASSIGNED,
        ClassOrderStatus.PAID,
        ClassOrderStatus.PARTIALLY_PAID,
    }
    COMPLETE_ALLOWED = {
        ClassOrderStatus.IN_PROGRESS,
        ClassOrderStatus.ASSIGNED,
    }
    CANCEL_BLOCKED = {
        ClassOrderStatus.COMPLETED,
        ClassOrderStatus.ARCHIVED,
    }

    @classmethod
    @transaction.atomic
    def create_draft(
        cls,
        *,
        website,
        client,
        title: str,
        created_by=None,
        institution_name: str = "",
        institution_state: str = "",
        class_name: str = "",
        class_code: str = "",
        class_subject: str = "",
        academic_level: str = "",
        starts_on=None,
        ends_on=None,
        initial_client_notes: str = "",
    ) -> ClassOrder:
        """
        Create a draft class order.
        """
        class_order = ClassOrder.objects.create(
            website=website,
            client=client,
            title=title,
            institution_name=institution_name,
            institution_state=institution_state,
            class_name=class_name,
            class_code=class_code,
            class_subject=class_subject,
            academic_level=academic_level,
            starts_on=starts_on,
            ends_on=ends_on,
            initial_client_notes=initial_client_notes,
            created_by=created_by,
            updated_by=created_by,
        )

        ClassTimelineService.record(
            class_order=class_order,
            event_type=ClassTimelineEventType.CREATED,
            title="Class order created",
            triggered_by=created_by,
        )

        return class_order

    @classmethod
    @transaction.atomic
    def submit(
        cls,
        *,
        class_order: ClassOrder,
        submitted_by,
    ) -> ClassOrder:
        """
        Submit a draft class order for admin review.
        """
        cls._require_status(
            class_order=class_order,
            allowed=cls.SUBMIT_ALLOWED,
            action="submit",
        )

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.SUBMITTED,
            triggered_by=submitted_by,
        )

        NotificationService.notify(
            event_key="class.submitted",
            recipient=submitted_by,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
            },
            triggered_by=submitted_by,
        )

        return class_order

    @classmethod
    @transaction.atomic
    def start_review(
        cls,
        *,
        class_order: ClassOrder,
        reviewed_by,
        admin_internal_notes: str = "",
    ) -> ClassOrder:
        """
        Move submitted class order into admin review.
        """
        cls._require_status(
            class_order=class_order,
            allowed=cls.REVIEW_ALLOWED,
            action="start review",
        )

        if admin_internal_notes:
            class_order.admin_internal_notes = admin_internal_notes
            class_order.save(
                update_fields=[
                    "admin_internal_notes",
                    "updated_at",
                ],
            )

        return ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.UNDER_REVIEW,
            triggered_by=reviewed_by,
        )

    @classmethod
    @transaction.atomic
    def mark_price_proposed(
        cls,
        *,
        class_order: ClassOrder,
        quoted_amount: Decimal,
        final_amount: Decimal,
        discount_amount: Decimal = Decimal("0.00"),
        pricing_snapshot: dict[str, Any] | None = None,
        discount_snapshot: dict[str, Any] | None = None,
        proposed_by=None,
    ) -> ClassOrder:
        """
        Mark the class order as having a proposed price.
        """
        class_order.quoted_amount = quoted_amount
        class_order.discount_amount = discount_amount
        class_order.final_amount = final_amount
        class_order.balance_amount = final_amount
        class_order.pricing_snapshot = pricing_snapshot or {}
        class_order.discount_snapshot = discount_snapshot or {}
        class_order.updated_by = proposed_by
        class_order.save(
            update_fields=[
                "quoted_amount",
                "discount_amount",
                "final_amount",
                "balance_amount",
                "pricing_snapshot",
                "discount_snapshot",
                "updated_by",
                "updated_at",
            ],
        )

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.PRICE_PROPOSED,
            triggered_by=proposed_by,
            metadata={
                "quoted_amount": str(quoted_amount),
                "discount_amount": str(discount_amount),
                "final_amount": str(final_amount),
            },
        )

        NotificationService.notify(
            event_key="class.price_proposed",
            recipient=class_order.client,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
                "final_amount": str(final_amount),
                "currency": class_order.currency,
            },
            triggered_by=proposed_by,
        )

        return class_order

    @classmethod
    @transaction.atomic
    def accept_price(
        cls,
        *,
        class_order: ClassOrder,
        accepted_by,
    ) -> ClassOrder:
        """
        Accept the current proposed class price.
        """
        cls._require_status(
            class_order=class_order,
            allowed=cls.ACCEPT_PRICE_ALLOWED,
            action="accept price",
        )

        if class_order.final_amount <= Decimal("0.00"):
            raise ClassOrderStateError(
                "Cannot accept a class order with no final amount."
            )

        class_order.accepted_amount = class_order.final_amount
        class_order.balance_amount = class_order.final_amount
        class_order.updated_by = accepted_by
        class_order.save(
            update_fields=[
                "accepted_amount",
                "balance_amount",
                "updated_by",
                "updated_at",
            ],
        )

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.ACCEPTED,
            triggered_by=accepted_by,
            metadata={
                "accepted_amount": str(class_order.accepted_amount),
            },
        )

        NotificationService.notify(
            event_key="class.price_accepted",
            recipient=accepted_by,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
                "accepted_amount": str(class_order.accepted_amount),
                "currency": class_order.currency,
            },
            triggered_by=accepted_by,
        )

        return class_order

    @classmethod
    @transaction.atomic
    def apply_payment(
        cls,
        *,
        class_order: ClassOrder,
        amount: Decimal,
        triggered_by=None,
    ) -> ClassOrder:
        """
        Apply a payment amount to the class order balance.

        The payment service should call this only after wallet, gateway,
        ledger, and payment allocation records have already been handled.
        """
        if amount <= Decimal("0.00"):
            raise ClassOrderStateError("Payment amount must be positive.")

        class_order.paid_amount += amount
        class_order.refresh_balance(save=False)
        class_order.updated_by = triggered_by
        class_order.save(
            update_fields=[
                "paid_amount",
                "balance_amount",
                "payment_status",
                "updated_by",
                "updated_at",
            ],
        )

        next_status = ClassOrderStatus.PARTIALLY_PAID

        if class_order.payment_status == ClassPaymentStatus.PAID:
            next_status = ClassOrderStatus.PAID

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=next_status,
            triggered_by=triggered_by,
            metadata={
                "amount": str(amount),
                "paid_amount": str(class_order.paid_amount),
                "balance_amount": str(class_order.balance_amount),
            },
        )

        return class_order

    @classmethod
    @transaction.atomic
    def assign_writer(
        cls,
        *,
        class_order: ClassOrder,
        writer,
        assigned_by,
        writer_visible_notes: str = "",
    ) -> ClassOrder:
        """
        Assign a writer to a class order.
        """
        cls._require_status(
            class_order=class_order,
            allowed=cls.ASSIGN_ALLOWED,
            action="assign writer",
        )

        class_order.assigned_writer = writer
        class_order.updated_by = assigned_by

        if writer_visible_notes:
            class_order.writer_visible_notes = writer_visible_notes

        class_order.save(
            update_fields=[
                "assigned_writer",
                "writer_visible_notes",
                "updated_by",
                "updated_at",
            ],
        )

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.ASSIGNED,
            triggered_by=assigned_by,
            metadata={"writer_id": cls._get_pk(writer)},
        )

        ClassCommunicationService.sync_participants(
            class_order=class_order,
        )

        NotificationService.notify(
            event_key="class.writer_assigned",
            recipient=writer,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
            },
            triggered_by=assigned_by,
        )

        return class_order

    @classmethod
    @transaction.atomic
    def start_work(
        cls,
        *,
        class_order: ClassOrder,
        started_by,
    ) -> ClassOrder:
        """
        Mark assigned class work as in progress.
        """
        cls._require_status(
            class_order=class_order,
            allowed=cls.START_WORK_ALLOWED,
            action="start work",
        )

        if cls._get_related_pk(
            obj=class_order,
            field_name="assigned_writer",
        ) is None:
            raise ClassOrderStateError(
                "Cannot start class work without an assigned writer."
            )

        return ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.IN_PROGRESS,
            triggered_by=started_by,
        )

    @classmethod
    @transaction.atomic
    def complete(
        cls,
        *,
        class_order: ClassOrder,
        completed_by,
        notes: str = "",
    ) -> ClassOrder:
        """
        Mark the class order completed.
        """
        cls._require_status(
            class_order=class_order,
            allowed=cls.COMPLETE_ALLOWED,
            action="complete",
        )
        cls._require_fully_paid(class_order=class_order)
        cls._require_no_unfinished_tasks(class_order=class_order)

        if notes:
            class_order.admin_internal_notes = (
                f"{class_order.admin_internal_notes}\n{notes}"
            ).strip()
            class_order.save(
                update_fields=[
                    "admin_internal_notes",
                    "updated_at",
                ],
            )

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.COMPLETED,
            triggered_by=completed_by,
            reason=notes,
        )

        try:
            ClassWriterCompensationService.mark_earned(
                class_order=class_order,
                triggered_by=completed_by,
            )
        except ClassWriterCompensationError:
            pass

        NotificationService.notify(
            event_key="class.completed",
            recipient=class_order.client,
            website=class_order.website,
            context={
                "class_order_id": class_order.pk,
                "title": class_order.title,
            },
            triggered_by=completed_by,
        )

        return class_order

    @classmethod
    @transaction.atomic
    def cancel(
        cls,
        *,
        class_order: ClassOrder,
        cancelled_by,
        reason: str,
    ) -> ClassOrder:
        """
        Cancel a class order.
        """
        if class_order.status in cls.CANCEL_BLOCKED:
            raise ClassOrderStateError(
                f"Cannot cancel class order in {class_order.status} status."
            )

        class_order.admin_internal_notes = (
            f"{class_order.admin_internal_notes}\n"
            f"Cancellation reason: {reason}"
        ).strip()
        class_order.updated_by = cancelled_by
        class_order.save(
            update_fields=[
                "admin_internal_notes",
                "updated_by",
                "updated_at",
            ],
        )

        class_order = ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.CANCELLED,
            triggered_by=cancelled_by,
            reason=reason,
        )

        ClassCommunicationService.disable_thread(class_order=class_order)

        return class_order

    @classmethod
    @transaction.atomic
    def archive(
        cls,
        *,
        class_order: ClassOrder,
        archived_by,
    ) -> ClassOrder:
        """
        Archive a completed or cancelled class order.
        """
        allowed = {
            ClassOrderStatus.COMPLETED,
            ClassOrderStatus.CANCELLED,
        }

        cls._require_status(
            class_order=class_order,
            allowed=allowed,
            action="archive",
        )

        return ClassOrderStateMachine.transition(
            class_order=class_order,
            to_status=ClassOrderStatus.ARCHIVED,
            triggered_by=archived_by,
        )

    @staticmethod
    def _require_status(
        *,
        class_order: ClassOrder,
        allowed: Container[str],
        action: str,
    ) -> None:
        """
        Ensure the class order is in a valid status for an action.
        """
        if class_order.status not in allowed:
            raise ClassOrderStateError(
                f"Cannot {action} class order while status is "
                f"{class_order.status}."
            )

    @staticmethod
    def _require_fully_paid(*, class_order: ClassOrder) -> None:
        """
        Ensure a class order is fully paid before completion.
        """
        if class_order.payment_status != ClassPaymentStatus.PAID:
            raise ClassOrderStateError(
                "Cannot complete class order before full payment."
            )

    @staticmethod
    def _require_no_unfinished_tasks(*, class_order: ClassOrder) -> None:
        """
        Ensure all class tasks are completed or cancelled.
        """
        unfinished_tasks_exist = ClassTask.objects.filter(
            class_order=class_order,
        ).exclude(
            status__in=[
                "completed",
                "cancelled",
            ],
        ).exists()

        if unfinished_tasks_exist:
            raise ClassOrderStateError(
                "Cannot complete class order with unfinished tasks."
            )

    @staticmethod
    def _get_related_pk(*, obj: Any, field_name: str) -> Any:
        """
        Return a related object's primary key safely.
        """
        related_obj = getattr(obj, field_name, None)
        return getattr(related_obj, "pk", None)

    @staticmethod
    def _get_pk(obj: Any) -> Any:
        """
        Return an object's primary key safely.
        """
        return getattr(obj, "pk", None)