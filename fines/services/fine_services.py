from decimal import Decimal
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError

from fines.models import Fine, FinePolicy, FineType, FineStatus
from fines.services.compensation import adjust_writer_compensation
from audit_logging.services.audit_log_service import AuditLogService


class FineService:
    """Service to handle fine creation with config-driven amounts."""

    @staticmethod
    def issue_fine(order, fine_type, reason, issued_by):
        """Create and issue a fine for the given order and fine type.

        Args:
            order (Order): The order to fine.
            fine_type (str): FineType enum value.
            reason (str): Explanation for issuing the fine.
            issued_by (User): User issuing the fine.

        Returns:
            Fine: Created Fine instance.

        Raises:
            ValueError: If no active fine policy found.
        """
        now = timezone.now()

        policies = FinePolicy.objects.filter(
            fine_type=fine_type,
            active=True,
            start_date__lte=now
        ).filter(
            models.Q(end_date__gte=now) | models.Q(end_date__isnull=True)
        ).order_by("-start_date")

        if not policies.exists():
            raise ValueError(f"No active fine policy for '{fine_type}'")

        policy = policies.first()

        if policy.fixed_amount is not None:
            amount = policy.fixed_amount
        elif policy.percentage is not None:
            base = order.total_price
            amount = (base * policy.percentage) / Decimal("100.00")
        else:
            raise ValueError("Policy must define fixed_amount or percentage.")

        if amount <= 0:
            raise ValueError(f"Fine amount must be positive (got {amount})")

        fine = Fine.objects.create(
            order=order,
            fine_type=fine_type,
            amount=amount,
            reason=reason,
            issued_by=issued_by,
            status=FineStatus.ISSUED,
            imposed_at=now
        )

        AuditLogService.log(
            actor=issued_by,
            action="fine_issued",
            target=fine,
            changes={"reason": reason, "amount": str(amount)},
            context={"order_id": order.id}
        )

        return fine

    @staticmethod
    def waive_fine(fine, waived_by, reason=None):
        """Waive the specified fine and adjust writer compensation.

        Args:
            fine (Fine): The fine to waive.
            waived_by (User): User waiving the fine.
            reason (str, optional): Reason for the waiver.

        Returns:
            Fine: The updated Fine instance.

        Raises:
            ValueError: If already resolved or waived.
        """
        if fine.status in [FineStatus.RESOLVED, FineStatus.WAIVED]:
            raise ValueError(f"Cannot waive fine with status '{fine.status}'")

        fine.status = FineStatus.WAIVED
        fine.waived_by = waived_by
        fine.waived_at = timezone.now()
        fine.waiver_reason = reason

        adjust_writer_compensation(fine.order, fine.amount)

        fine.save(update_fields=[
            "status", "waived_by", "waived_at", "waiver_reason"
        ])

        AuditLogService.log(
            actor=waived_by,
            action="fine_waived",
            target=fine,
            changes={"status": FineStatus.WAIVED},
            context={
                "reason": reason or "No reason provided.",
                "amount_restored": str(fine.amount),
                "order_id": fine.order_id
            }
        )

        return fine

    @staticmethod
    def void_fine(fine, voided_by, reason=None):
        """Void a fine completely.

        Args:
            fine (Fine): The fine to void.
            voided_by (User): Admin performing the void.
            reason (str, optional): Justification for voiding.

        Returns:
            Fine: The updated Fine instance.

        Raises:
            ValidationError: If already voided.
        """
        if fine.status == FineStatus.VOIDED:
            raise ValidationError("Fine is already voided.")

        fine.status = FineStatus.VOIDED
        fine.resolved = True
        fine.resolved_at = timezone.now()
        fine.resolved_reason = reason or "Fine voided."

        fine.save(update_fields=[
            "status", "resolved", "resolved_at", "resolved_reason"
        ])

        AuditLogService.log(
            actor=voided_by,
            action="fine_voided",
            changes={
                "status": FineStatus.VOIDED,
                "reason": fine.resolved_reason
            },
            target=fine,
            context={
                "voided_by": voided_by.id,
                "order_id": fine.order_id,
                "fine_id": fine.id
            },
            issued_by=voided_by,
            reason=reason or "No reason provided."
            metadata={
                "fine_id": fine.id,
                "order_id": fine.order_id
            },
        )

        return fine