from __future__ import annotations

from files_management.enums import FileVisibility
from files_management.models import FileAttachment
from files_management.policies.base import BaseFilePolicy


class OrderFilePolicy(BaseFilePolicy):
    """
    Access policy for files attached to order-like objects.

    This policy is defensive because the orders app is being refactored.
    It checks common attributes without tightly coupling this app to one
    concrete Order model shape.
    """

    domain_key = "orders"

    ORDER_MODEL_NAMES = {
        "order",
        "draftrequest",
        "orderadjustmentrequest",
        "revisionrequest",
    }

    def supports(self, *, attachment: FileAttachment) -> bool:
        """
        Return whether the attachment points to an order domain object.
        """

        model_name = attachment.content_type.model.lower()
        app_label = attachment.content_type.app_label.lower()

        return app_label == "orders" or model_name in self.ORDER_MODEL_NAMES

    def can_view(self, *, user, attachment: FileAttachment) -> bool:
        """
        Return whether a user can view an order file.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        order_obj = attachment.content_object

        if order_obj is None:
            return False

        if attachment.visibility == FileVisibility.STAFF_ONLY:
            return False

        if attachment.visibility == FileVisibility.INTERNAL_ONLY:
            return False

        if self._is_order_client(user=user, order_obj=order_obj):
            return attachment.visibility in {
                FileVisibility.CLIENT_AND_STAFF,
                FileVisibility.CLIENT_WRITER_STAFF,
                FileVisibility.ORDER_PARTICIPANTS,
                FileVisibility.PRIVATE,
            }

        if self._is_order_writer(user=user, order_obj=order_obj):
            return attachment.visibility in {
                FileVisibility.WRITER_AND_STAFF,
                FileVisibility.CLIENT_WRITER_STAFF,
                FileVisibility.ORDER_PARTICIPANTS,
            }

        return False

    def can_replace(self, *, user, attachment: FileAttachment) -> bool:
        """
        Allow uploaders and staff to replace order files.
        """

        if self.is_staff_like(user=user):
            return self.is_same_website(user=user, attachment=attachment)

        return self.is_uploader(user=user, attachment=attachment)

    def can_request_deletion(
        self,
        *,
        user,
        attachment: FileAttachment,
    ) -> bool:
        """
        Allow participants who uploaded a file to request deletion.
        """

        if not self.is_same_website(user=user, attachment=attachment):
            return False

        if self.is_staff_like(user=user):
            return True

        return self.is_uploader(user=user, attachment=attachment)

    def can_delete(self, *, user, attachment: FileAttachment) -> bool:
        """
        Prevent clients and writers from direct deletion.
        """

        return (
            self.is_same_website(user=user, attachment=attachment)
            and self.is_staff_like(user=user)
        )

    @staticmethod
    def _is_order_client(*, user, order_obj) -> bool:
        """
        Return whether the user appears to be the order client.
        """

        user_id = getattr(user, "id", None)

        for attr_name in ("client_id", "user_id", "customer_id"):
            if getattr(order_obj, attr_name, None) == user_id:
                return True

        client = getattr(order_obj, "client", None)

        if getattr(client, "user_id", None) == user_id:
            return True

        return getattr(client, "id", None) == user_id

    @staticmethod
    def _is_order_writer(*, user, order_obj) -> bool:
        """
        Return whether the user appears to be the assigned writer.
        """

        user_id = getattr(user, "id", None)

        for attr_name in ("writer_id", "assigned_writer_id"):
            if getattr(order_obj, attr_name, None) == user_id:
                return True

        writer = getattr(order_obj, "writer", None)

        if getattr(writer, "user_id", None) == user_id:
            return True

        assigned_writer = getattr(order_obj, "assigned_writer", None)

        if getattr(assigned_writer, "user_id", None) == user_id:
            return True

        return False