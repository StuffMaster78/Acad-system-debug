from __future__ import annotations

from typing import Any
from django.utils import timezone
from files_management.models.file_attachment import (
    FileAttachment,
)
from files_management.services.file_download_service import (
    FileDownloadService,
)
from special_orders.models.special_order import SpecialOrder
from special_orders.models.delivery import SpecialOrderDeliverable
from special_orders.services.new_services.special_order_delivery_guard_service import (
    SpecialOrderDeliveryGuardService,
)


class SpecialOrderFilesBridge:
    """
    Bridge special order deliverables to files_management.

    files_management owns uploads, storage, signed URLs, and access records.
    special_orders owns delivery/funding gates.
    """

    @classmethod
    def create_deliverable_from_file(
        cls,
        *,
        special_order: SpecialOrder,
        file_reference: str,
        title: str,
        uploaded_by,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> SpecialOrderDeliverable:
        """
        Register a files_management file as a special order deliverable.
        """
        if not file_reference.strip():
            raise ValueError("File reference is required.")

        if not title.strip():
            raise ValueError("Deliverable title is required.")

        return SpecialOrderDeliverable.objects.create(
            website=special_order.website,
            special_order=special_order,
            title=title.strip(),
            description=description.strip(),
            file_reference=file_reference.strip(),
            uploaded_by=uploaded_by,
            metadata=metadata or {},
        )

    @classmethod
    def get_guarded_download_url(
        cls,
        *,
        deliverable: SpecialOrderDeliverable,
        requested_by,
        request=None,
    ) -> str:
        """
        Return signed download URL only after delivery guard passes.

        Replace placeholder with actual files_management signed URL service.
        """
        special_order = deliverable.special_order

        cls._validate_download_actor(
            special_order=special_order,
            requested_by=requested_by,
        )

        SpecialOrderDeliveryGuardService.assert_can_deliver_final(
            special_order=special_order,
        )

        attachment = cls._get_file_attachment(
            deliverable=deliverable,
        )

        download_url = FileDownloadService.get_download_url(
            user=requested_by,
            website=deliverable.website,
            attachment=attachment,
            ip_address=cls._get_ip_address(request=request),
            user_agent=cls._get_user_agent(request=request),
        )

        if special_order.client_id == getattr(requested_by, "id", None):
            deliverable.delivered_at = timezone.now()
            deliverable.save(
                update_fields=[
                    "delivered_at",
                    "updated_at",
                ]
            )

        return download_url

    @staticmethod
    def _get_file_attachment(
        *,
        deliverable: SpecialOrderDeliverable,
    ) -> FileAttachment:
        """
        Resolve files_management attachment from deliverable.file_reference.
        """
        file_reference = deliverable.file_reference

        if not file_reference:
            raise ValueError("Deliverable has no file reference.")

        return FileAttachment.objects.get(
            website=deliverable.website,
            id=int(file_reference),
        )

    @staticmethod
    def _get_ip_address(*, request) -> str:
        if request is None:
            return ""

        return str(request.META.get("REMOTE_ADDR", ""))

    @staticmethod
    def _get_user_agent(*, request) -> str:
        if request is None:
            return ""

        return str(request.META.get("HTTP_USER_AGENT", ""))

    @staticmethod
    def _validate_download_actor(
        *,
        special_order: SpecialOrder,
        requested_by,
    ) -> None:
        """
        Allow client, assigned writer, or staff to request delivery access.

        Funding/download gating is still enforced separately.
        """
        if getattr(requested_by, "website_id", None) != special_order.website_id:
            raise PermissionError("Cross-tenant file access blocked.")

        role = str(getattr(requested_by, "role", "")).lower()

        staff_roles = {
            "admin",
            "superadmin",
            "support",
            "editor",
            "content_manager",
        }

        if role in staff_roles:
            return

        if special_order.client_id == getattr(requested_by, "id", None):
            return

        if special_order.writer_id == getattr(requested_by, "id", None):
            return

        raise PermissionError("You cannot access this deliverable.")