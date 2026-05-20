from django.utils.timezone import now

from superadmin_management.models import Appeal
from superadmin_management.services.writer_governance_service import (
    WriterGovernanceService,
)


class AppealService:

    @staticmethod
    def approve(*, superadmin, appeal, review_notes=""):

        if appeal.status != Appeal.Status.PENDING:
            raise ValueError("Not pending")

        if appeal.user.role == "writer":
            WriterGovernanceService.lift_suspension(
                superadmin=superadmin,
                user=appeal.user,
                reason="Appeal approved",
            )

        appeal.status = Appeal.Status.APPROVED
        appeal.reviewed_by = superadmin
        appeal.reviewed_at = now()
        appeal.review_notes = review_notes
        appeal.save()

        return appeal


    @staticmethod
    def reject(*, superadmin, appeal, review_notes):

        if not review_notes.strip():
            raise ValueError("review notes required")

        appeal.status = Appeal.Status.REJECTED
        appeal.reviewed_by = superadmin
        appeal.reviewed_at = now()
        appeal.review_notes = review_notes
        appeal.save()

        return appeal
