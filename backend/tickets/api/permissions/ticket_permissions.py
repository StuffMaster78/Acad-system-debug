from __future__ import annotations

from rest_framework.permissions import BasePermission, IsAuthenticated

from tickets.constants import TicketRole


class IsTicketParticipantOrStaff(IsAuthenticated):
    """
    Object-level access for ticket participants and support staff.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = getattr(user, "role", None)
        if role in TicketRole.STAFF_ROLES:
            return True

        ticket = getattr(obj, "ticket", None)
        if ticket is not None:
            obj = ticket

        content_object = getattr(obj, "content_object", None)
        if content_object is not None:
            obj = content_object

        return (
            obj.created_by_id == getattr(user, "id", None)
            or obj.assigned_to_id == getattr(user, "id", None)
        )


class IsTicketStaff(BasePermission):
    """
    Only support/admin-style roles can perform staff ticket actions.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) in TicketRole.STAFF_ROLES
        )
