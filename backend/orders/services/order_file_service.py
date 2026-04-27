from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from files_management.integrations.orders import (
    OrderFileIntegrationService,
)
from files_management.models import FileAttachment


class OrderFileService:
    """
    Order-owned file workflow service.

    This service validates order business rules, then delegates storage
    and attachment work to files_management.
    """

    @classmethod
    @transaction.atomic
    def client_upload_instruction(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Let the order client upload an instruction file.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_order_client(order=order, user=uploaded_by)

        attachment = OrderFileIntegrationService.upload_instruction_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
        )

        # TODO:
        # OrderTimelineService.record_file_uploaded(...)
        # NotificationService.notify(...)

        return attachment

    @classmethod
    @transaction.atomic
    def writer_upload_draft(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Let the assigned writer upload a draft file.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_assigned_writer(order=order, user=uploaded_by)

        attachment = OrderFileIntegrationService.upload_draft_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
        )

        # TODO:
        # DraftWorkflowService.mark_submitted(...)
        # OrderTimelineService.record_draft_uploaded(...)
        # NotificationService.notify(...)

        return attachment

    @classmethod
    @transaction.atomic
    def writer_upload_final(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Let the assigned writer upload the final deliverable.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_assigned_writer(order=order, user=uploaded_by)

        attachment = OrderFileIntegrationService.upload_final_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
        )

        # TODO:
        # OrderWorkflowService.mark_delivered(...)
        # OrderTimelineService.record_final_uploaded(...)
        # NotificationService.notify(...)

        return attachment


    def _record_file_event(
        *,
        order,
        actor,
        event_type: str,
        attachment,
    ) -> None:
        """
        Record order timeline event if the timeline model is available.
        """

        try:
            from orders.models import OrderTimelineEvent
        except ImportError:
            return

        OrderTimelineEvent.objects.create(
            order=order,
            website=order.website,
            actor=actor,
            event_type=event_type,
            metadata={
                "attachment_id": attachment.id,
                "purpose": attachment.purpose,
            },
        )


    def _notify_order_file_uploaded(
        *,
        order,
        actor,
        attachment,
        recipient,
    ) -> None:
        """
        Notify a user about an order file event.
        """

        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
        except ImportError:
            return

        NotificationService.notify(
            event_key="orders.file_uploaded",
            recipient=recipient,
            website=order.website,
            context={
                "order_id": order.id,
                "attachment_id": attachment.id,
                "purpose": attachment.purpose,
            },
            triggered_by=actor,
        )
    
    @staticmethod
    def _ensure_same_website(*, order, user) -> None:
        if order.website_id != user.website_id:
            raise PermissionDenied("Cross-tenant access denied.")

    @staticmethod
    def _ensure_order_client(*, order, user) -> None:
        if getattr(order, "client_id", None) != user.id:
            raise PermissionDenied("Only the order client can do this.")

    @staticmethod
    def _ensure_assigned_writer(*, order, user) -> None:
        writer_id = getattr(order, "writer_id", None)
        assigned_writer_id = getattr(order, "assigned_writer_id", None)

        if user.id not in {writer_id, assigned_writer_id}:
            raise PermissionDenied("Only the assigned writer can do this.")