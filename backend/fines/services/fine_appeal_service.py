"""Service to handle fine appeals/disputes workflow."""

from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError
from fines.models import Fine, FineAppeal, FineStatus
from audit_logging.services.audit_log_service import AuditLogService


class FineAppealService:
    """Encapsulates fine appeal/dispute submission and review logic."""

    @staticmethod
    def submit_appeal(
        fine, appealed_by, reason
    ):
        """Submit a dispute/appeal for a given fine.

        Args:
            fine (Fine): The fine being appealed.
            appealed_by (User): The writer submitting the appeal.
            reason (str): Justification for appealing the fine.

        Returns:
            FineAppeal: The created FineAppeal instance.

        Raises:
            ValueError: If fine is not eligible or already appealed.
            PermissionDenied: If user is not the writer for this order.
        """
        # Verify user is the writer for this order
        if fine.order.assigned_writer != appealed_by:
            raise PermissionDenied(
                "Only the writer assigned to this order can dispute the fine."
            )
        
        # Check if writer role
        if appealed_by.role != 'writer':
            raise PermissionDenied("Only writers can dispute fines.")

        if fine.status != FineStatus.ISSUED:
            raise ValueError(
                f"Fine with status '{fine.status}' cannot be appealed. "
                "Only 'issued' fines can be disputed."
            )

        if hasattr(fine, "appeal"):
            raise ValueError("Fine already has an active appeal/dispute.")

        appeal = FineAppeal.objects.create(
            fine=fine,
            appealed_by=appealed_by,
            reason=reason,
            created_at=timezone.now(),
        )

        fine.status = FineStatus.DISPUTED  # Changed from APPEALED to DISPUTED
        fine.save(update_fields=["status"])

        AuditLogService.log_auto(
            actor=appealed_by,
            action="fine_disputed",
            target=fine,
            changes={"appeal_reason": reason, "status": FineStatus.DISPUTED},
            context={"appeal_id": appeal.id},
        )

        return appeal
    
    @staticmethod
    def escalate_dispute(appeal, escalated_to, escalation_reason=None):
        """
        Escalate a dispute to admin/superadmin for resolution.
        
        Args:
            appeal: The FineAppeal to escalate
            escalated_to: Admin/superadmin handling escalation
            escalation_reason: Optional reason for escalation
            
        Returns:
            FineAppeal: Updated appeal instance
        """
        if appeal.escalated:
            raise ValueError("Dispute already escalated.")
        
        if escalated_to.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins or superadmins can handle escalations.")
        
        appeal.escalated = True
        appeal.escalated_at = timezone.now()
        appeal.escalated_to = escalated_to
        
        if escalation_reason:
            appeal.resolution_notes = f"Escalation: {escalation_reason}"
        
        appeal.save(update_fields=['escalated', 'escalated_at', 'escalated_to', 'resolution_notes'])
        
        appeal.fine.status = FineStatus.ESCALATED
        appeal.fine.save(update_fields=['status'])
        
        AuditLogService.log_auto(
            actor=escalated_to,
            action="fine_dispute_escalated",
            target=appeal.fine,
            changes={"escalated_to": escalated_to.username},
            context={"appeal_id": appeal.id},
        )
        
        return appeal

    @staticmethod
    def review_appeal(appeal, reviewed_by, accept, review_notes=None):
        """Review a submitted fine appeal/dispute.

        Args:
            appeal (FineAppeal): The FineAppeal instance to review.
            reviewed_by (User): Admin/superadmin user reviewing the appeal.
            accept (bool): True if appeal is accepted (fine waived), else False (fine upheld).
            review_notes (str, optional): Optional notes for context.

        Returns:
            FineAppeal: The updated FineAppeal instance.

        Raises:
            ValueError: If already reviewed or fine not in disputed/escalated status.
            PermissionDenied: If user is not admin/superadmin.
        """
        if reviewed_by.role not in ['admin', 'superadmin', 'support']:
            raise PermissionDenied("Only admins, superadmins, or support can review disputes.")
        
        if appeal.reviewed_at is not None:
            raise ValueError(
                "This appeal has already been reviewed."
            )

        fine = appeal.fine
        if fine.status not in [FineStatus.DISPUTED, FineStatus.ESCALATED, FineStatus.APPEALED]:
            raise ValueError(
                f"Fine must be in 'disputed', 'escalated', or 'appealed' status to review. "
                f"Current status: {fine.status}"
            )

        appeal.reviewed_by = reviewed_by
        appeal.reviewed_at = timezone.now()
        appeal.accepted = accept

        if review_notes:
            appeal.resolution_notes = review_notes
        else:
            appeal.resolution_notes = (
                "Appeal accepted - fine waived."
                if accept else "Appeal rejected - fine upheld."
            )

        appeal.save(update_fields=[
            'reviewed_by', 'reviewed_at', 'accepted', 'resolution_notes'
        ])

        # If appeal accepted, waive the fine and restore compensation
        if accept:
            from fines.services.fine_services import FineService
            FineService.waive_fine(fine, reviewed_by, review_notes or "Dispute accepted")
        else:
            # Appeal rejected - fine stands
            fine.status = FineStatus.RESOLVED
            fine.resolved = True
            fine.resolved_at = timezone.now()
            fine.resolved_reason = "Dispute reviewed and rejected - fine upheld."

        fine.save(update_fields=[
            "status", "resolved", "resolved_at", "resolved_reason"
        ])

        AuditLogService.log_auto(
            actor=reviewed_by,
            action="fine_dispute_reviewed",
            target=fine,
            changes={
                "appeal_accepted": accept,
                "review_notes": review_notes,
            },
            context={"appeal_id": appeal.id},
        )

        return appeal