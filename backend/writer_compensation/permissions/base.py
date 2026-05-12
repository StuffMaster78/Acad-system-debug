from rest_framework.permissions import BasePermission


class IsFinanceAdmin(BasePermission):
    """
    Full finance management access.
    """

    message = "Finance administrator access required."

    def has_permission( # type: ignore
            self,
            request,
            view
        ):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.has_perm(
                    "writer_payments_management.manage_financials"
                )
            )
        )


class IsFinanceStaff(BasePermission):
    """
    Finance operational staff access.
    """

    message = "Finance staff access required."

    def has_permission( # type: ignore
            self,
            request,
            view
        ):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.has_perm(
                    "writer_payments_management.view_financials"
                )
            )
        )


class IsOwnerOrFinanceStaff(BasePermission):
    """
    Allows writers to access their own records
    while permitting finance/admin oversight.
    """

    message = "You do not have permission to access this resource."

    def has_object_permission( # type: ignore
            self,
            request,
            view,
            obj,
        ):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if user.has_perm(
            "writer_payments_management.view_financials"
        ):
            return True

        writer = getattr(obj, "writer", None)

        if writer is None:
            return False

        return getattr(writer, "user_id", None) == user.id
