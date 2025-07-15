from writer_management.services.leave_service import WriterLeaveService
from writer_management.models.leave import WriterLeave
from django.core.exceptions import ObjectDoesNotExist

class ReviewLeaveAction:

    @staticmethod
    def run(leave_id, website, reviewed_by, approve: bool, comments=None):
        try:
            leave = WriterLeave.objects.get(id=leave_id, website=website)
        except ObjectDoesNotExist:
            raise ValueError("Leave request not found")

        if approve:
            return WriterLeaveService.approve_leave(leave, reviewed_by, comments)
        return WriterLeaveService.reject_leave(leave, reviewed_by, comments)