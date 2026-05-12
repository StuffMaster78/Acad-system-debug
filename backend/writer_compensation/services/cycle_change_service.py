from __future__ import annotations
 
from decimal import Decimal
 
from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone
 
from writer_compensation.enums.compensation_enums import (
    CycleChangeStatus,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import (
    CycleChangeNotAllowedError,
)
from writer_compensation.models.payment_window import (
    PaymentWindow,
)

from writer_compensation.models.cycle_change_request import (
    PaymentWindowChangeRequest,
)
from writer_compensation.models.writer_payout_preference import (
    WriterPayoutPreference,
)



class PaymentCycleChangeService:
    """
    Writer requests a payout window(cycle) change.
    Admin approves or rejects.
    Change takes effect at the start of the next open window after approval.
    """
 
    @staticmethod
    @transaction.atomic
    def request_change(
        *,
        website,
        writer,
        requested_cycle: str,
        reason: str = "",
    ) -> PaymentWindowChangeRequest:
        """
        Writer submits a cycle change request.
 
        Raises CycleChangeNotAllowedError if a PENDING request already exists.
        """
        preference = WriterPayoutPreference.objects.filter(
            website=website,
            writer=writer,
        ).first()
 
        current_cycle = preference.cycle_type if preference else None
 
        if current_cycle == requested_cycle:
            raise CycleChangeNotAllowedError(
                "Requested cycle is the same as the current cycle."
            )
 
        already_pending = PaymentWindowChangeRequest.objects.filter(
            website=website,
            writer=writer,
            status=CycleChangeStatus.PENDING,
        ).exists()
 
        if already_pending:
            raise CycleChangeNotAllowedError(
                "A pending cycle change request already exists. "
                "Wait for it to be reviewed before submitting another."
            )
 
        return PaymentWindowChangeRequest.objects.create(
            website=website,
            writer=writer,
            from_cycle=current_cycle or "",
            requested_cycle=requested_cycle,
            reason=reason,
            status=CycleChangeStatus.PENDING,
        )
 
    @staticmethod
    @transaction.atomic
    def approve(
        change_request: PaymentWindowChangeRequest,
        reviewed_by,
    ) -> PaymentWindowChangeRequest:
        """
        Approve a cycle change request.
        Updates WriterPayoutPreference to the new cycle.
        effective_from_window is set to the current open window.
        """
        if change_request.status != CycleChangeStatus.PENDING:
            raise ValueError(
                f"Request {change_request.pk} is {change_request.status}, not PENDING."
            )
 
        effective_window = (
            PaymentWindow.objects
            .filter(
                website=change_request.website,
                status=WindowStatus.OPEN,
            )
            .order_by("start_date")
            .first()
        )
 
        now = timezone.now()
        change_request.status = CycleChangeStatus.APPROVED
        change_request.reviewed_by = reviewed_by
        change_request.reviewed_at = now
        change_request.effective_from_window = effective_window
        change_request.save(update_fields=[
            "status", "reviewed_by", "reviewed_at", "effective_from_window", "updated_at",
        ])
 
        # Apply the change to the preference.
        WriterPayoutPreference.objects.update_or_create(
            website=change_request.website,
            writer=change_request.writer,
            defaults={
                "cycle_type": change_request.requested_window,
                "locked":     True,
            },
        )
 
        return change_request
 
    @staticmethod
    @transaction.atomic
    def reject(
        change_request: PaymentWindowChangeRequest,
        reviewed_by,
        rejection_reason: str = "",
    ) -> PaymentWindowChangeRequest:
        """Reject a cycle change request."""
        if change_request.status != CycleChangeStatus.PENDING:
            raise ValueError(
                f"Request {change_request.pk} is {change_request.status}, not PENDING."
            )
 
        now = timezone.now()
        change_request.status = CycleChangeStatus.REJECTED
        change_request.reviewed_by = reviewed_by
        change_request.reviewed_at  = now
        change_request.rejection_reason = rejection_reason
        change_request.save(update_fields=[
            "status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at",
        ])
 
        return change_request