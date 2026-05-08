from rest_framework.permissions import BasePermission


class CanViewAuditLogs(BasePermission):
    """
    Base audit viewing permission.
    """

    message = "You do not have permission to view audit logs."

    def has_permission( # type: ignore[override]
            self,
            request,
            view,
        ):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_staff
        )


class CanViewSensitiveAuditLogs(BasePermission):
    """
    Elevated access for sensitive audit events.
    """

    message = "You do not have permission to view sensitive audit logs."

    def has_permission( # type: ignore[override]
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
                or user.has_perm("audit_logging.view_sensitive_audit_logs")
            )
        )


class CanManageAuditFailures(BasePermission):
    """
    DLQ + recovery operations.
    """

    message = "You do not have permission to manage audit failures."

    def has_permission( # type: ignore[override]
            self,
            request,
            view,
        ):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.has_perm("audit_logging.manage_audit_failures")
            )
        )