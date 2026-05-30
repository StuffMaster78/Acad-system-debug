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
    def client_upload_reference(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Let the order client upload a reference file.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_order_client_or_staff(order=order, user=uploaded_by)

        return OrderFileIntegrationService.upload_reference_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
        )

    @classmethod
    @transaction.atomic
    def client_upload_style_reference(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        reference_type: str = "previous_paper",
        description: str = "",
        is_visible_to_writer: bool = True,
    ) -> FileAttachment:
        """
        Let the order client upload a style reference file.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_order_client_or_staff(order=order, user=uploaded_by)

        return OrderFileIntegrationService.upload_style_reference_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            reference_type=reference_type,
            description=description,
            is_visible_to_writer=is_visible_to_writer,
        )

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
        cls._ensure_assigned_writer_or_staff(order=order, user=uploaded_by)

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
    def writer_upload_extra_service(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        service_code: str = "",
        category_code: str = "",
        description: str = "",
        is_downloadable: bool = False,
    ) -> FileAttachment:
        """
        Let the assigned writer or staff upload an extra service file.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_assigned_writer_or_staff(order=order, user=uploaded_by)

        return OrderFileIntegrationService.upload_extra_service_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            service_code=service_code,
            category_code=category_code,
            description=description,
            is_downloadable=is_downloadable,
        )

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
        cls._ensure_assigned_writer_or_staff(order=order, user=uploaded_by)

        attachment = OrderFileIntegrationService.upload_final_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
        )

        cls._notify_order_file_uploaded(
            order=order,
            actor=uploaded_by,
            attachment=attachment,
            recipient=getattr(order, "client", None),
        )

        return attachment

    @classmethod
    @transaction.atomic
    def writer_upload_revision(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
    ) -> FileAttachment:
        """
        Let the assigned writer or staff upload a revision file.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_assigned_writer_or_staff(order=order, user=uploaded_by)

        attachment = OrderFileIntegrationService.upload_revision_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
        )

        cls._notify_order_file_uploaded(
            order=order,
            actor=uploaded_by,
            attachment=attachment,
            recipient=getattr(order, "client", None),
        )

        return attachment

    @classmethod
    @transaction.atomic
    def submit_external_link(
        cls,
        *,
        order,
        submitted_by,
        url: str,
        purpose: str,
        title: str = "",
    ) -> FileAttachment:
        """
        Submit an external order file link.
        """

        cls._ensure_same_website(order=order, user=submitted_by)
        if not (
            cls._is_staff(user=submitted_by)
            or cls._is_order_client(order=order, user=submitted_by)
            or cls._is_assigned_writer(order=order, user=submitted_by)
        ):
            raise PermissionDenied("You cannot add links to this order.")

        return OrderFileIntegrationService.submit_external_order_link(
            order=order,
            submitted_by=submitted_by,
            url=url,
            purpose=purpose,
            title=title,
        )


    @staticmethod
    def _record_file_event(
        *,
        order,
        actor,
        event_type: str,
        attachment,
    ) -> None:
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

    @staticmethod
    def _notify_order_file_uploaded(
        *,
        order,
        actor,
        attachment,
        recipient,
    ) -> None:
        try:
            from orders.services.order_notification_service import (
                OrderNotificationService,
            )
            OrderNotificationService.notify_file_uploaded(
                order=order,
                uploaded_by=actor,
                attachment=attachment,
                recipient=recipient,
            )
        except Exception:
            import logging
            logging.getLogger(__name__).warning(
                "Failed to send file upload notification for order_id=%s",
                getattr(order, "id", None),
                exc_info=True,
            )
    
    @staticmethod
    def _ensure_same_website(*, order, user) -> None:
        if order.website_id != user.website_id:
            raise PermissionDenied("Cross-tenant access denied.")

    @classmethod
    def _ensure_order_client(cls, *, order, user) -> None:
        if not cls._is_order_client(order=order, user=user):
            raise PermissionDenied("Only the order client can do this.")

    @classmethod
    def _ensure_order_client_or_staff(cls, *, order, user) -> None:
        if cls._is_staff(user=user):
            return
        cls._ensure_order_client(order=order, user=user)

    @classmethod
    def _ensure_assigned_writer(cls, *, order, user) -> None:
        if not cls._is_assigned_writer(order=order, user=user):
            raise PermissionDenied("Only the assigned writer can do this.")

    @classmethod
    def _ensure_assigned_writer_or_staff(cls, *, order, user) -> None:
        if cls._is_staff(user=user):
            return
        cls._ensure_assigned_writer(order=order, user=user)

    @staticmethod
    def _is_staff(*, user) -> bool:
        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_super_admin", False)
        )

    @staticmethod
    def _is_order_client(*, order, user) -> bool:
        user_id = getattr(user, "id", None)

        for attr_name in ("client_id", "created_by_id"):
            if getattr(order, attr_name, None) == user_id:
                return True

        client = getattr(order, "client", None)
        if getattr(client, "user_id", None) == user_id:
            return True
        return getattr(client, "id", None) == user_id

    @staticmethod
    def _is_assigned_writer(*, order, user) -> bool:
        user_id = getattr(user, "id", None)

        for attr_name in ("writer_id", "assigned_writer_id", "assigned_to_id"):
            if getattr(order, attr_name, None) == user_id:
                return True

        writer = getattr(order, "writer", None)
        assigned_writer = getattr(order, "assigned_writer", None)

        if getattr(writer, "user_id", None) == user_id:
            return True
        if getattr(assigned_writer, "user_id", None) == user_id:
            return True
        account_profile = getattr(assigned_writer, "account_profile", None)
        if getattr(account_profile, "user_id", None) == user_id:
            return True

        return False
