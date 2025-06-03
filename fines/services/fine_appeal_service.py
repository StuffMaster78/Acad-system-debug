"""Service to handle fine appeals workflow."""

from django.utils import timezone
from fines.models import Fine, FineAppeal, FineStatus
from audit_logging.services import log_audit_action


class FineAppealService:
    """Encapsulates fine appeal submission and review logic."""

    @staticmethod
    def submit_appeal(fine, appealed_by, reason):
        """Submit an appeal for a given fine.

        Args:
            fine (Fine): The fine being appealed.
            appealed_by (User): The user submitting the appeal.
            reason (str): Justification for appealing the fine.

        Returns:
            FineAppeal: The created FineAppeal instance.

        Raises:
            ValueError: If fine is not eligible or already appealed.
        """
        if fine.status not in [FineStatus.ISSUED, FineStatus.APPEALED]:
            raise ValueError(
                "Only fines with status 'issued' or 'appealed' may be appealed."
            )

        if hasattr(fine, "appeal"):
            raise ValueError("Fine already has an active appeal.")

        appeal = FineAppeal.objects.create(
            fine=fine,
            appealed_by=appealed_by,
            reason=reason,
            created_at=timezone.now(),
        )

        fine.status = FineStatus.APPEALED
        fine.save(update_fields=["status"])

        log_audit_action(
            actor=appealed_by,
            action="fine_appealed",
            target=fine,
            changes={"appeal_reason": reason},
            context={"appeal_id": appeal.id},
        )

        return appeal

    @staticmethod
    def review_appeal(appeal, reviewed_by, accept, review_notes=None):
        """Review a submitted fine appeal.

        Args:
            appeal (FineAppeal): The FineAppeal instance to review.
            reviewed_by (User): Admin user reviewing the appeal.
            accept (bool): True if appeal is accepted, else False.
            review_notes (str, optional): Optional notes for context.

        Returns:
            FineAppeal: The updated FineAppeal instance.

        Raises:
            ValueError: If already reviewed or fine not in appealed status.
        """
        if appeal.reviewed_at is not None:
            raise ValueError("This appeal has already been reviewed.")

        fine = appeal.fine
        if fine.status != FineStatus.APPEALED:
            raise ValueError("Fine must be in 'appealed' status to review.")

        appeal.reviewed_by = reviewed_by
        appeal.reviewed_at = timezone.now()
        appeal.accepted = accept

        if review_notes:
            appeal.reason += f"\n\nReview notes: {review_notes}"

        appeal.save()

        fine.status = FineStatus.WAIVED if accept else FineStatus.RESOLVED
        fine.resolved = True
        fine.resolved_at = timezone.now()
        fine.resolved_reason = (
            "Appeal accepted and fine waived."
            if accept else "Appeal rejected."
        )

        fine.save(update_fields=[
            "status", "resolved", "resolved_at", "resolved_reason"
        ])

        log_audit_action(
            actor=reviewed_by,
            action="fine_appeal_reviewed",
            target=fine,
            changes={
                "appeal_accepted": accept,
                "review_notes": review_notes,
            },
            context={"appeal_id": appeal.id},
        )

        return appeal