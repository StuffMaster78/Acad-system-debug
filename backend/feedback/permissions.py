from rest_framework.permissions import BasePermission

STAFF_ROLES = {"admin", "superadmin", "support", "editor"}


def _is_staff(user) -> bool:
    return (
        bool(getattr(user, "is_staff", False))
        or getattr(user, "role", "") in STAFF_ROLES
    )


class CanSubmitFeedback(BasePermission):
    """Any authenticated user may submit a feedback request."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class CanTriageFeedback(BasePermission):
    """Only staff roles may access triage actions."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and _is_staff(request.user)
        )


class FeedbackObjectPermission(BasePermission):
    """
    Object-level:
      - Staff can read/write any request.
      - Requester can read their own and update title/description/priority.
      - Others get 404 (queryset already filtered).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if _is_staff(user):
            return True
        return obj.requester_id == user.pk
