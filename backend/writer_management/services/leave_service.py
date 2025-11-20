from writer_management.models.leave import WriterLeave, WriterLeaveAdminReview
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class WriterLeaveService:

    @staticmethod
    def approve_leave(leave: WriterLeave, reviewed_by, comments=None):
        if leave.approved:
            raise ValidationError("Leave is already approved.")

        leave.approved = True
        leave.save()

        WriterLeaveAdminReview.objects.create(
            leave=leave,
            reviewed_by=reviewed_by,
            review_date=now(),
            comments=comments
        )
        return leave

    @staticmethod
    def reject_leave(leave: WriterLeave, reviewed_by, comments=None):
        if leave.approved:
            raise ValidationError("Cannot reject an already approved leave.")

        leave.delete()  # or leave.approved = False if you want to soft reject

        WriterLeaveAdminReview.objects.create(
            leave=leave,
            reviewed_by=reviewed_by,
            review_date=now(),
            comments=comments or "Leave rejected"
        )