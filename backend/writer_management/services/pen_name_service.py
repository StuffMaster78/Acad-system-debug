"""
Owns WriterPenNameChangeRequest lifecycle.
"""
import logging
 
from django.db import transaction
from django.utils.timezone import now
 
from writer_management.models.pen_name import WriterPenNameChangeRequest
 
logger = logging.getLogger(__name__)
 
 
class PenNameService:
 
    @staticmethod
    @transaction.atomic
    def submit_request(
        writer,
        requested_name: str,
        reason: str,
    ) -> WriterPenNameChangeRequest:
        """
        Writer submits a pen name change request.
 
        One pending request per writer at a time enforced by
        UniqueConstraint on the model.
 
        Args:
            writer: WriterProfile instance.
            requested_name: Desired new pen name.
            reason: Why the writer wants to change.
 
        Returns:
            WriterPenNameChangeRequest (status=PENDING).
 
        Raises:
            ValueError: If requested_name is blank or a pending request exists.
        """
        if not requested_name.strip():
            raise ValueError("Requested pen name cannot be blank.")
 
        existing = WriterPenNameChangeRequest.objects.filter(
            writer=writer,
            status=WriterPenNameChangeRequest.Status.PENDING,
        ).first()
        if existing:
            raise ValueError(
                f"A pending pen name request already exists (pk={existing.pk}). "
                "Wait for it to be reviewed before submitting another."
            )
 
        from writer_management.utils import resolve_website_for_writer
        website = resolve_website_for_writer(writer)
 
        request = WriterPenNameChangeRequest.objects.create(
            website=website,
            writer=writer,
            current_name=writer.pen_name or "",
            requested_name=requested_name.strip(),
            reason=reason.strip(),
            status=WriterPenNameChangeRequest.Status.PENDING,
        )
 
        logger.info(
            "PenNameRequest submitted: writer=%s pk=%s name=%r",
            writer.registration_id,
            request.pk,
            requested_name,
        )
 
        # Notify admins
        PenNameService._notify_admins(request)
 
        return request
 
    @staticmethod
    @transaction.atomic
    def approve_request(
        request: WriterPenNameChangeRequest,
        reviewed_by,
        notes: str = "",
    ) -> WriterPenNameChangeRequest:
        """
        Admin approves a pen name change request.
        Updates WriterProfile.pen_name.
        """
        if request.status != WriterPenNameChangeRequest.Status.PENDING:
            raise ValueError(
                f"Cannot approve request {request.pk}. "
                f"Status: {request.status}."
            )
 
        writer = request.writer
        old_name = writer.pen_name
 
        # Update profile
        writer.pen_name = request.requested_name
        writer.save(update_fields=["pen_name", "updated_at"])
 
        # Close request
        request.status = WriterPenNameChangeRequest.Status.APPROVED
        request.reviewed_by = reviewed_by
        request.review_notes = notes
        request.reviewed_at = now()
        request.save(update_fields=[
            "status", "reviewed_by", "review_notes", "reviewed_at"
        ])
 
        logger.info(
            "PenNameRequest approved: writer=%s %r → %r by=%s",
            writer.registration_id,
            old_name,
            request.requested_name,
            getattr(reviewed_by, "pk", "?"),
        )
 
        PenNameService._notify_writer(
            request=request,
            event_key="writer.pen_name.request_approved",
        )
 
        return request
 
    @staticmethod
    @transaction.atomic
    def reject_request(
        request: WriterPenNameChangeRequest,
        reviewed_by,
        notes: str,
    ) -> WriterPenNameChangeRequest:
        """Admin rejects a pen name change request."""
        if request.status != WriterPenNameChangeRequest.Status.PENDING:
            raise ValueError(
                f"Cannot reject request {request.pk}. "
                f"Status: {request.status}."
            )
 
        if not notes.strip():
            raise ValueError("Review notes required when rejecting a request.")
 
        request.status = WriterPenNameChangeRequest.Status.REJECTED
        request.reviewed_by = reviewed_by
        request.review_notes = notes.strip()
        request.reviewed_at = now()
        request.save(update_fields=[
            "status", "reviewed_by", "review_notes", "reviewed_at"
        ])
 
        logger.info(
            "PenNameRequest rejected: writer=%s pk=%s by=%s",
            request.writer.registration_id,
            request.pk,
            getattr(reviewed_by, "pk", "?"),
        )
 
        PenNameService._notify_writer(
            request=request,
            event_key="writer.pen_name.request_rejected",
        )
 
        return request
 
    @staticmethod
    def _notify_admins(request: WriterPenNameChangeRequest) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify_role(
                event_key="writer.pen_name.request_submitted",
                role="admin",
                website=request.website,
                context={
                    "registration_id": request.writer.registration_id,
                    "current_name":    request.current_name,
                    "requested_name":  request.requested_name,
                    "reason":          request.reason,
                },
            )
        except Exception as exc:
            logger.exception(
                "PenNameService._notify_admins failed: %s", exc
            )
 
    @staticmethod
    def _notify_writer(
        request: WriterPenNameChangeRequest,
        event_key: str,
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            user = request.writer.account_profile.user
            NotificationService.notify(
                event_key=event_key,
                recipient=user,
                website=request.website,
                context={
                    "registration_id": request.writer.registration_id,
                    "requested_name":  request.requested_name,
                    "approved_name":   (
                        request.requested_name
                        if request.status == WriterPenNameChangeRequest.Status.APPROVED
                        else None
                    ),
                    "review_notes":    request.review_notes,
                },
            )
        except Exception as exc:
            logger.exception(
                "PenNameService._notify_writer failed: %s", exc
            )