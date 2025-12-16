from django.core.exceptions import ValidationError
from django.db import transaction
from typing import Optional
from django.utils import timezone

from websites.models import Website
from orders.models import Dispute, DisputeWriterResponse, Order
from users.models import User
from orders.services.dispute_enums import DisputeStatus, ResolutionOutcome
from orders.services.dispute_helpers import (
    validate_dispute_status_transition,
    send_dispute_notification,
)
from orders.services.transition_helper import OrderTransitionHelper

class DisputeService:
    """
    Service for managing disputes related to orders.

    Handles raising disputes, updating status, resolving disputes, and
    notifying relevant users accordingly.
    """

    def __init__(self, dispute: Dispute):
        """
        Initialize with a Dispute instance.

        Args:
            dispute (Dispute): Dispute object to manage.
        """
        self.dispute = dispute
        self.order = dispute.order

    @classmethod
    def raise_dispute(
        cls, order: Order, raised_by: User,
        reason: str, website
    ) -> Dispute:
        """
        Raise a new dispute for the given order.

        Args:
            order (Order): The order to dispute.
            raised_by (User): User raising the dispute.
            reason (str): Reason for the dispute.
            website: Website instance related to the dispute.

        Returns:
            Dispute: Created dispute instance.

        Raises:
            ValidationError: If order status disallows dispute.
        """
        if order.status in ['cancelled', 'progress']:
            raise ValidationError("Cannot raise dispute for this order status.")

        dispute = Dispute.objects.create(
            website=website,
            order=order,
            raised_by=raised_by,
            reason=reason,
            status=DisputeStatus.OPEN,
        )

        OrderTransitionHelper.transition_order(
            order=order,
            target_status='disputed',
            user=raised_by,
            reason=reason,
            action="raise_dispute",
            is_automatic=False,
            metadata={
                "dispute_id": dispute.id,
                "dispute_reason": reason,
            }
        )

        send_dispute_notification(
            dispute,
            subject="New Dispute Raised",
            message=(
                f"A dispute has been raised for Order #{order.id}. "
                "Admin attention required."
            ),
        )

        return dispute

    def update_dispute_status(
            self, new_status: str,
            updated_by: User,
            note: Optional[str] = None
    ) -> None:
        """
        Update dispute status with validation.

        Args:
            new_status (str): New status to assign.

        Raises:
            ValidationError: If invalid status or forbidden transition.
        """
        validate_dispute_status_transition(
            self.dispute.status, new_status
        )
        if new_status == DisputeStatus.RESOLVED:
                    raise ValidationError(
                        "Use `resolve_dispute` to resolve disputes."
                    )

        self.dispute.status = new_status
        self.dispute.last_updated_by = updated_by
        self.dispute.last_updated_at = timezone.now()
        
        if note:
            self.dispute.internal_note = note

        self.dispute.save()

        # Note: Dispute status and order status are separate
        # We don't automatically change order status when dispute status changes
        # Order status should remain 'disputed' until dispute is resolved

        send_dispute_notification(
            self.dispute,
            subject=f"Dispute status updated to {new_status.upper()}",
            message=note or f"The dispute was updated by {updated_by.email}."
        )

    @transaction.atomic
    def resolve_dispute(
        self, resolution_outcome: str, resolved_by: User,
        website: Website,
        resolution_notes: Optional[str] = None,
        extended_deadline=None
    ) -> Dispute:
        """
        Resolve the dispute and update order accordingly.

        Args:
            resolution_outcome (str): Outcome of resolution.
            resolved_by (User): User resolving the dispute.
            resolution_notes (str, optional): Notes about the resolution.
            extended_deadline (datetime, optional): New deadline if extended.

        Returns:
            Dispute: Updated dispute instance.

        Raises:
            ValidationError: If resolution_outcome is unknown or data invalid.
        """

        if self.dispute.status == DisputeStatus.RESOLVED.value:
            raise ValidationError("Dispute is already resolved.")
        
        if resolution_outcome not in ResolutionOutcome.__dict__.values():
            raise ValidationError("Invalid resolution outcome.")
    
        if resolution_outcome == ResolutionOutcome.WRITER_WINS:
            """
            When the writer wins a dispute, the order should be considered
            resolved in the writer's favour and moved out of the disputed
            flow into a final or post‑review state.

            Business rule (simplified, but explicit and easy to reason about):
            - We close the disputed order, using the unified transition helper.
            - This moves the order to the terminal `closed` status from `disputed`,
              which is an allowed transition in `VALID_TRANSITIONS`.

            If, in the future, we want to distinguish between:
            - "work accepted but not reviewed yet" (e.g. `submitted` / `reviewed`)
            - "fully finalised" (`closed`)
            we can extend this method to inspect additional order fields
            (review/rating timestamps, previous status snapshots, etc.)
            and choose a more granular target state.
            """
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='closed',
                user=resolved_by,
                reason=f"Dispute resolved: Writer wins. {resolution_notes or ''}",
                action="resolve_dispute",
                is_automatic=False,
                metadata={
                    "dispute_id": self.dispute.id,
                    "resolution_outcome": resolution_outcome,
                    "resolution_notes": resolution_notes,
                }
            )

        elif resolution_outcome == ResolutionOutcome.CLIENT_WINS:
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='cancelled',
                user=resolved_by,
                reason=f"Dispute resolved: Client wins. {resolution_notes or ''}",
                action="resolve_dispute",
                is_automatic=False,
                metadata={
                    "dispute_id": self.dispute.id,
                    "resolution_outcome": resolution_outcome,
                    "resolution_notes": resolution_notes,
                }
            )

        elif resolution_outcome == ResolutionOutcome.EXTEND_DEADLINE:
            if not extended_deadline:
                raise ValidationError("Extended deadline must be provided.")
            self.order.change_deadline(extended_deadline)
            self.dispute.admin_extended_deadline = extended_deadline
            # Note: 'revision_requested' might not be a valid transition from 'disputed'
            # Check VALID_TRANSITIONS - disputed can go to revision_requested
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='revision_requested',
                user=resolved_by,
                reason=f"Dispute resolved: Deadline extended. {resolution_notes or ''}",
                action="resolve_dispute",
                is_automatic=False,
                metadata={
                    "dispute_id": self.dispute.id,
                    "resolution_outcome": resolution_outcome,
                    "extended_deadline": extended_deadline.isoformat(),
                    "resolution_notes": resolution_notes,
                }
            )

        elif resolution_outcome == ResolutionOutcome.REASSIGN:
            OrderTransitionHelper.transition_order(
                order=self.order,
                target_status='available',
                user=resolved_by,
                reason=f"Dispute resolved: Order reassigned. {resolution_notes or ''}",
                action="resolve_dispute",
                is_automatic=False,
                metadata={
                    "dispute_id": self.dispute.id,
                    "resolution_outcome": resolution_outcome,
                    "resolution_notes": resolution_notes,
                }
            )
            # Clear assigned writer after transition
            self.order.assigned_writer = None
            self.order.save(update_fields=["assigned_writer"])

        else:
            raise ValidationError(
                "Unknown resolution outcome."
            )

        self.dispute.status = DisputeStatus.RESOLVED
        self.dispute.resolution_outcome = resolution_outcome
        self.dispute.resolution_notes = resolution_notes
        self.dispute.resolved_by = resolved_by
        self.dispute.resolved_at = timezone.now()

        self.dispute.save()
        self.order.save()

        send_dispute_notification(
            self.dispute,
            subject="Dispute Resolved",
            message=(
                f"Dispute for Order #{self.order.id} resolved: "
                f"{resolution_outcome.replace('_', ' ').title()}."
            ),
            website=website
        )

        # log_dispute_resolution(
        #     dispute=self.dispute,
        #     order=self.order,
        #     resolved_by=resolved_by,
        #     website=website
        # )

        return self.dispute
    
    @staticmethod
    def escalate_dispute(dispute: Dispute, escalated_by: User) -> None:
        """
        Escalate a dispute to admin/superadmin.

        Args:
            dispute (Dispute): Dispute instance.
            escalated_by (User): Who escalated.

        Raises:
            ValidationError: If the dispute can't be escalated.
        """
        if dispute.status == DisputeStatus.ESCALATED.value:
            raise ValidationError("Dispute is already escalated.")

        DisputeService.update_dispute_status(
            dispute=dispute,
            new_status=DisputeStatus.ESCALATED.value,
            updated_by=escalated_by,
            note="Dispute has been escalated."
        )

class DisputeWriterResponseService:
    """
    Service to manage writer responses to disputes.
    """

    def __init__(self, dispute: Dispute, writer: User):
        """
        Initialize service for managing responses.

        Args:
            dispute (Dispute): Dispute instance.
            writer (User): Writer user.
        """
        self.dispute = dispute
        self.writer = writer

    def submit_response(self, response_text: str, response_file=None):
        """
        Submit a response for the dispute.

        Args:
            response_text (str): Writer's response text.
            response_file (File, optional): Optional attached file.

        Returns:
            DisputeWriterResponse: Created response instance.

        Raises:
            ValidationError: If writer already responded.
        """
        if self.dispute.writer_responded:
            raise ValidationError(
                "Writer has already responded to this dispute."
            )

        response = DisputeWriterResponse.objects.create(
            dispute=self.dispute,
            responded_by=self.writer,
            response_text=response_text,
            response_file=response_file,
        )
        self.dispute.writer_responded = True
        self.dispute.save()

        return response