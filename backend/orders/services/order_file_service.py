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

        cls._record_file_event(
            order=order,
            actor=uploaded_by,
            event_type="instruction_file_uploaded",
            attachment=attachment,
        )
        cls._notify_order_file_uploaded(
            order=order,
            actor=uploaded_by,
            attachment=attachment,
            recipient=cls._resolve_writer_user(order),
        )

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

        cls._record_file_event(
            order=order,
            actor=uploaded_by,
            event_type="draft_file_uploaded",
            attachment=attachment,
        )

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

        Links the file to the current open OrderRevisionRequest and stamps
        revision_cycle so the UI can group files by revision round correctly.
        """
        from orders.models.revisions.order_revision_request import OrderRevisionRequest
        from orders.models.orders.enums import OrderRevisionStatus

        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_assigned_writer_or_staff(order=order, user=uploaded_by)

        # Look up the currently open revision request (APPROVED or IN_PROGRESS).
        open_revision = (
            OrderRevisionRequest.objects
            .filter(
                order=order,
                status__in=[OrderRevisionStatus.APPROVED, OrderRevisionStatus.IN_PROGRESS],
            )
            .order_by("-created_at")
            .first()
        )

        # revision_cycle = total number of revision requests on this order so far.
        # 0 = original delivery; 1 = first revision round; 2 = second, etc.
        revision_cycle = OrderRevisionRequest.objects.filter(order=order).count()

        attachment = OrderFileIntegrationService.upload_revision_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            revision_request=open_revision,
        )

        if revision_cycle:
            attachment.revision_cycle = revision_cycle
            attachment.save(update_fields=["revision_cycle"])

        cls._notify_order_file_uploaded(
            order=order,
            actor=uploaded_by,
            attachment=attachment,
            recipient=getattr(order, "client", None),
        )

        return attachment

    @classmethod
    @transaction.atomic
    def staff_upload_writer_guide(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        guide_type: str = "guide",
        description: str = "",
    ) -> FileAttachment:
        """
        Let staff upload a guide/resource intended for assigned writers.
        """

        cls._ensure_same_website(order=order, user=uploaded_by)
        if not cls._is_staff(user=uploaded_by):
            raise PermissionDenied("Only staff can add writer guides.")

        attachment = OrderFileIntegrationService.upload_writer_guide_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            guide_type=guide_type,
            description=description,
        )

        cls._record_file_event(
            order=order,
            actor=uploaded_by,
            event_type="writer_guide_uploaded",
            attachment=attachment,
        )

        return attachment

    @classmethod
    @transaction.atomic
    def client_upload_material(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        purpose: str,
    ) -> FileAttachment:
        """
        Let the order client upload a typed material (sample, outline,
        questionnaire, notes, or class material).
        """
        cls._ensure_same_website(order=order, user=uploaded_by)
        cls._ensure_order_client_or_staff(order=order, user=uploaded_by)

        attachment = OrderFileIntegrationService.upload_client_material(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            purpose=purpose,
        )

        cls._record_file_event(
            order=order,
            actor=uploaded_by,
            event_type="client_material_uploaded",
            attachment=attachment,
        )
        cls._notify_order_file_uploaded(
            order=order,
            actor=uploaded_by,
            attachment=attachment,
            recipient=cls._resolve_writer_user(order),
        )

        return attachment

    @classmethod
    @transaction.atomic
    def staff_upload_internal(
        cls,
        *,
        order,
        uploaded_by,
        uploaded_file: UploadedFile,
        notes: str = "",
    ) -> FileAttachment:
        """Let staff upload an internal file not visible to clients/writers."""
        cls._ensure_same_website(order=order, user=uploaded_by)
        if not cls._is_staff(user=uploaded_by):
            raise PermissionDenied("Only staff can upload internal files.")

        attachment = OrderFileIntegrationService.upload_internal_file(
            order=order,
            uploaded_by=uploaded_by,
            uploaded_file=uploaded_file,
            notes=notes,
        )

        cls._record_file_event(
            order=order,
            actor=uploaded_by,
            event_type="internal_file_uploaded",
            attachment=attachment,
        )

        return attachment

    @classmethod
    @transaction.atomic
    def submit_final(
        cls,
        *,
        order,
        attachment: FileAttachment,
        submitted_by,
    ) -> FileAttachment:
        """
        Submit a final file for delivery. The writer or staff can call this.
        Sets revision_cycle from the order's current revision count.
        """
        from files_management.integrations.orders import OrderFileIntegrationService as OFIS

        is_writer = cls._is_assigned_writer(order=order, user=submitted_by)
        is_staff = cls._is_staff(user=submitted_by)
        if not (is_writer or is_staff):
            raise PermissionDenied("Only the assigned writer or staff can submit the final file.")

        result = OFIS.submit_final_file(
            attachment=attachment,
            submitted_by=submitted_by,
        )

        cls._record_file_event(
            order=order,
            actor=submitted_by,
            event_type="final_file_submitted",
            attachment=result,
        )

        return result

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
        if purpose == "writer_guide" and not cls._is_staff(user=submitted_by):
            raise PermissionDenied("Only staff can add writer guide links.")
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
    def _resolve_writer_user(order):
        try:
            return order.assigned_writer
        except Exception:
            return None

    @staticmethod
    def _ensure_same_website(*, order, user) -> None:
        if getattr(user, "is_superuser", False) or getattr(user, "role", None) == "superadmin":
            return
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
            or getattr(user, "role", None) in {"admin", "superadmin", "support", "editor"}
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
