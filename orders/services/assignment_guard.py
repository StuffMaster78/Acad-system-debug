from datetime import timezone
from writer_management.models.profile import WriterProfile
from writer_management.services.status_service import WriterStatusService

def can_writer_take_order(writer: WriterProfile) -> bool:
    status = WriterStatusService.get(writer)

    return (
        status["is_active"]
        and not status["is_suspended"]
        and not status["is_blacklisted"]
        and not status["is_on_probation"]
        and status["active_strikes"] < 3  # Example threshold for strikes
        and (status["suspension_ends_at"] is None or status["suspension_ends_at"] < timezone.now())
        and (status["probation_ends_at"] is None or status["probation_ends_at"] < timezone.now())
    )