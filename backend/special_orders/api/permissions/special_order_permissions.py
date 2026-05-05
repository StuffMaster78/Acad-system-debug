from __future__ import annotations

from rest_framework.permissions import BasePermission


class SpecialOrderPortalPermission(BasePermission):
    """
    Base permission for special order portal access.

    Tenancy should already be enforced by core middleware/selectors/views.
    This class handles role and object-level ownership rules.
    """

    message = "You do not have permission to access this special order."

    ADMIN_ROLES = {
        "admin",
        "superadmin",
        "support",
        "content_manager",
    }

    STAFF_ROLES = {
        "admin",
        "superadmin",
        "support",
        "editor",
        "content_manager",
    }

    WRITER_ROLE = "writer"
    CLIENT_ROLE = "client"

    @staticmethod
    def _get_role(user) -> str:
        """
        Return normalized user role.
        """
        return str(getattr(user, "role", "")).lower()

    @classmethod
    def is_admin(cls, user) -> bool:
        """
        Return true if user has admin-level access.
        """
        return cls._get_role(user) in cls.ADMIN_ROLES

    @classmethod
    def is_staff_user(cls, user) -> bool:
        """
        Return true if user can operate staff workflows.
        """
        return cls._get_role(user) in cls.STAFF_ROLES

    @classmethod
    def is_writer(cls, user) -> bool:
        """
        Return true if user is a writer.
        """
        return cls._get_role(user) == cls.WRITER_ROLE

    @classmethod
    def is_client(cls, user) -> bool:
        """
        Return true if user is a client.
        """
        return cls._get_role(user) == cls.CLIENT_ROLE

    @staticmethod
    def same_website(user, obj) -> bool:
        """
        Defensive tenant check.

        Core should enforce tenancy, but object-level permissions should
        still guard against accidental cross-tenant access.
        """
        user_website_id = getattr(user, "website_id", None)
        object_website_id = getattr(obj, "website_id", None)

        return (
            user_website_id is not None
            and object_website_id is not None
            and user_website_id == object_website_id
        )


class CanViewSpecialOrder(SpecialOrderPortalPermission):
    """
    Allow clients, assigned writers, and staff to view special orders.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        if self.is_staff_user(user):
            return True

        if getattr(obj, "client_id", None) == getattr(user, "id", None):
            return True

        if getattr(obj, "writer_id", None) == getattr(user, "id", None):
            return True

        return False


class CanCreateSpecialOrder(SpecialOrderPortalPermission):
    """
    Allow clients and staff to create special orders.
    """

    def has_permission(self, request, view) -> bool: # type: ignore
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return self.is_client(user) or self.is_staff_user(user)


class CanManageSpecialOrderQuote(SpecialOrderPortalPermission):
    """
    Allow staff/admin users to create, edit, send, or expire quotes.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        return self.is_staff_user(user)


class CanAcceptSpecialOrderQuote(SpecialOrderPortalPermission):
    """
    Allow the owning client to accept a sent quote.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        special_order = getattr(obj, "special_order", obj)

        return getattr(
            special_order,
            "client_id",
            None,
        ) == getattr(user, "id", None)


class CanManageSpecialOrderFunding(SpecialOrderPortalPermission):
    """
    Allow staff/admin users to manage funding records manually.

    Client-initiated payment should use payment-intent/checkout flows,
    not direct funding mutation endpoints.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        return self.is_staff_user(user)


class CanPaySpecialOrder(SpecialOrderPortalPermission):
    """
    Allow the owning client to start or complete payment.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        special_order = getattr(obj, "special_order", obj)

        return getattr(
            special_order,
            "client_id",
            None,
        ) == getattr(user, "id", None)


class CanRefundSpecialOrder(SpecialOrderPortalPermission):
    """
    Allow only admin-level users to refund special order payments.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        return self.is_admin(user)


class CanAssignSpecialOrderWriter(SpecialOrderPortalPermission):
    """
    Allow staff/admin users to assign writers.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        return self.is_staff_user(user)


class CanUploadSpecialOrderDeliverable(SpecialOrderPortalPermission):
    """
    Allow assigned writer or staff to upload deliverables.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        if self.is_staff_user(user):
            return True

        return (
            self.is_writer(user)
            and getattr(obj, "writer_id", None) == getattr(user, "id", None)
        )


class CanDownloadSpecialOrderDeliverable(SpecialOrderPortalPermission):
    """
    Allow clients, assigned writers, and staff to access deliverables.

    Actual download gating should still be enforced by delivery/funding
    guard services before returning signed URLs.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        special_order = getattr(obj, "special_order", obj)

        if self.is_staff_user(user):
            return True

        if getattr(special_order, "client_id", None) == getattr(user, "id", None):
            return True

        if getattr(special_order, "writer_id", None) == getattr(user, "id", None):
            return True

        return False


class CanManageSpecialOrderOverride(SpecialOrderPortalPermission):
    """
    Allow only admin-level users to create/apply dangerous overrides.
    """

    def has_object_permission(self, request, view, obj) -> bool: # type: ignore
        user = request.user

        if not self.same_website(user, obj):
            return False

        return self.is_admin(user)