from __future__ import annotations

from django.core.exceptions import PermissionDenied

from files_management.enums import FilePurpose
from files_management.models import FileAttachment
from files_management.services import FileDownloadService
from orders.services.order_download_eligibility_service import (
    OrderDownloadEligibilityService,
)

class OrderFileDownloadService:
    """
    Order-owned file download gate.

    Files_management checks generic file safety and attachment access.
    This service checks order-specific business rules such as assignment,
    ownership, payment status, and final-deliverable release rules.
    """

    FINAL_PURPOSES = {
        FilePurpose.ORDER_FINAL,
        FilePurpose.ORDER_REVISION,
    }

    @classmethod
    def get_download_url(
        cls,
        *,
        order,
        user,
        attachment: FileAttachment,
        ip_address: str = "",
        user_agent: str = "",
    ) -> str:
        """
        Return a file download URL after order business checks.
        """

        cls._ensure_same_website(order=order, user=user)
        cls._ensure_attachment_belongs_to_order(
            order=order,
            attachment=attachment,
        )
        cls._ensure_user_can_download_order_file(
            order=order,
            user=user,
            attachment=attachment,
        )
        
        OrderDownloadEligibilityService.ensure_can_download(
            order=order,
            user=user,
            attachment=attachment,
        )

        return FileDownloadService.get_download_url(
            user=user,
            website=order.website,
            attachment=attachment,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    def _ensure_user_can_download_order_file(
        cls,
        *,
        order,
        user,
        attachment: FileAttachment,
    ) -> None:
        """
        Enforce order-specific download rules.
        """

        if cls._is_staff(user=user):
            return

        if cls._is_order_writer(order=order, user=user):
            return

        if cls._is_order_client(order=order, user=user):
            if attachment.purpose in cls.FINAL_PURPOSES:
                cls._ensure_final_file_unlocked(order=order)
            return

        raise PermissionDenied("You cannot download this order file.")

    @staticmethod
    def _ensure_same_website(*, order, user) -> None:
        if order.website_id != user.website_id:
            raise PermissionDenied("Cross-tenant access denied.")

    @staticmethod
    def _ensure_attachment_belongs_to_order(
        *,
        order,
        attachment: FileAttachment,
    ) -> None:
        if attachment.website.pk != order.website_id:
            raise PermissionDenied("Cross-tenant file access denied.")

        if attachment.content_object != order:
            raise PermissionDenied("File does not belong to this order.")

    @classmethod
    def _ensure_final_file_unlocked(cls, *, order) -> None:
        """
        Ensure client may download final or revision files.

        Adapt these field names to your actual order/payment model.
        """

        if getattr(order, "is_fully_paid", False):
            return

        if getattr(order, "payment_status", "") in {
            "paid",
            "fully_paid",
            "completed",
        }:
            return

        if getattr(order, "status", "") in {
            "completed",
            "delivered",
            "closed",
        }:
            return

        raise PermissionDenied(
            "Final files are locked until payment and release rules pass."
        )

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

        if getattr(order, "client_id", None) == user_id:
            return True

        client = getattr(order, "client", None)

        if getattr(client, "user_id", None) == user_id:
            return True

        return getattr(client, "id", None) == user_id

    @staticmethod
    def _is_order_writer(*, order, user) -> bool:
        user_id = getattr(user, "id", None)

        for attr_name in ("writer_id", "assigned_writer_id"):
            if getattr(order, attr_name, None) == user_id:
                return True

        writer = getattr(order, "writer", None)
        assigned_writer = getattr(order, "assigned_writer", None)

        if getattr(writer, "user_id", None) == user_id:
            return True

        if getattr(assigned_writer, "user_id", None) == user_id:
            return True

        return False