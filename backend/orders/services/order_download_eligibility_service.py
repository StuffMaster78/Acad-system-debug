from __future__ import annotations

from django.core.exceptions import PermissionDenied

from files_management.enums import FilePurpose
from files_management.models import FileAttachment


class OrderDownloadEligibilityService:
    """
    Determines whether an order file can be downloaded.

    This service owns order-specific download release rules. It should be
    the only place that decides whether a client may access final,
    revision, or progressive delivery files.

    The files_management app only handles generic file safety, storage,
    signed URLs, and download logs.
    """

    FINAL_PURPOSES = {
        FilePurpose.ORDER_FINAL,
        FilePurpose.ORDER_REVISION,
    }

    WRITER_ALLOWED_PURPOSES = {
        FilePurpose.ORDER_INSTRUCTION,
        FilePurpose.ORDER_REFERENCE,
        FilePurpose.ORDER_DRAFT,
        FilePurpose.ORDER_REVISION,
        FilePurpose.STYLE_REFERENCE,
        FilePurpose.EXTRA_SERVICE_FILE,
    }

    CLIENT_ALLOWED_PURPOSES = {
        FilePurpose.ORDER_INSTRUCTION,
        FilePurpose.ORDER_REFERENCE,
        FilePurpose.ORDER_DRAFT,
        FilePurpose.ORDER_FINAL,
        FilePurpose.ORDER_REVISION,
        FilePurpose.STYLE_REFERENCE,
        FilePurpose.EXTRA_SERVICE_FILE,
    }

    @classmethod
    def ensure_can_download(
        cls,
        *,
        order,
        user,
        attachment: FileAttachment,
    ) -> None:
        """
        Raise PermissionDenied if the user cannot download the file.
        """

        cls._ensure_same_website(order=order, user=user)
        cls._ensure_attachment_belongs_to_order(
            order=order,
            attachment=attachment,
        )

        if cls._is_staff(user=user):
            return

        if cls._is_order_writer(order=order, user=user):
            cls._ensure_writer_can_download(
                order=order,
                attachment=attachment,
            )
            return

        if cls._is_order_client(order=order, user=user):
            cls._ensure_client_can_download(
                order=order,
                attachment=attachment,
            )
            return

        raise PermissionDenied("You cannot download this order file.")

    @classmethod
    def _ensure_writer_can_download(
        cls,
        *,
        order,
        attachment: FileAttachment,
    ) -> None:
        """
        Ensure an assigned writer can download this order file.
        """

        if attachment.purpose not in cls.WRITER_ALLOWED_PURPOSES:
            raise PermissionDenied(
                "Writer cannot download this file type."
            )

        if cls._is_order_cancelled(order=order):
            raise PermissionDenied(
                "Files for cancelled orders are not available."
            )

    @classmethod
    def _ensure_client_can_download(
        cls,
        *,
        order,
        attachment: FileAttachment,
    ) -> None:
        """
        Ensure the client can download this order file.
        """

        if attachment.purpose not in cls.CLIENT_ALLOWED_PURPOSES:
            raise PermissionDenied(
                "Client cannot download this file type."
            )

        if attachment.purpose in cls.FINAL_PURPOSES:
            cls._ensure_final_file_unlocked(order=order)

    @classmethod
    def _ensure_final_file_unlocked(cls, *, order) -> None:
        """
        Ensure final or revision files are released to the client.

        Adapt this method to your exact order/payment fields. The goal is
        to centralize release rules instead of scattering payment checks
        across views and file services.
        """

        if cls._is_order_fully_funded(order=order):
            return

        if cls._has_final_release_override(order=order):
            return

        raise PermissionDenied(
            "Final files are locked until payment and release rules pass."
        )

    @staticmethod
    def _is_order_fully_funded(*, order) -> bool:
        """
        Return whether the order is fully paid or funded.

        This method supports multiple field shapes while the payment
        refactor is still being harmonized.
        """

        if getattr(order, "is_fully_paid", False):
            return True

        if getattr(order, "is_fully_funded", False):
            return True

        payment_status = str(
            getattr(order, "payment_status", "")
        ).lower()

        if payment_status in {"paid", "fully_paid", "funded", "completed"}:
            return True

        funding_status = str(
            getattr(order, "funding_status", "")
        ).lower()

        if funding_status in {"funded", "fully_funded"}:
            return True

        amount_due = getattr(order, "amount_due", None)

        if amount_due is not None and amount_due <= 0:
            return True

        balance_due = getattr(order, "balance_due", None)

        if balance_due is not None and balance_due <= 0:
            return True

        return False

    @staticmethod
    def _has_final_release_override(*, order) -> bool:
        """
        Return whether staff manually released final files.

        Add a real boolean field later if you do not have one yet, for
        example: final_files_released_by_staff.
        """

        if getattr(order, "final_files_released", False):
            return True

        if getattr(order, "final_files_released_by_staff", False):
            return True

        return False

    @staticmethod
    def _is_order_cancelled(*, order) -> bool:
        """
        Return whether the order is cancelled.
        """

        status_value = str(getattr(order, "status", "")).lower()

        return status_value in {"cancelled", "canceled", "refunded"}

    @staticmethod
    def _ensure_same_website(*, order, user) -> None:
        """
        Ensure user and order belong to the same tenant.
        """

        if order.website_id != user.website_id:
            raise PermissionDenied("Cross-tenant access denied.")

    @staticmethod
    def _ensure_attachment_belongs_to_order(
        *,
        order,
        attachment: FileAttachment,
    ) -> None:
        """
        Ensure attachment belongs to the given order.
        """

        if attachment.website.pk != order.website_id:
            raise PermissionDenied("Cross-tenant file access denied.")

        if attachment.content_object != order:
            raise PermissionDenied("File does not belong to this order.")

    @staticmethod
    def _is_staff(*, user) -> bool:
        """
        Return whether user has staff-like authority.
        """

        return bool(
            getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
            or getattr(user, "is_admin", False)
            or getattr(user, "is_super_admin", False)
        )

    @staticmethod
    def _is_order_client(*, order, user) -> bool:
        """
        Return whether user is the order client.
        """

        user_id = getattr(user, "id", None)

        if getattr(order, "client_id", None) == user_id:
            return True

        client = getattr(order, "client", None)

        if getattr(client, "user_id", None) == user_id:
            return True

        return getattr(client, "id", None) == user_id

    @staticmethod
    def _is_order_writer(*, order, user) -> bool:
        """
        Return whether user is the assigned writer.
        """

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