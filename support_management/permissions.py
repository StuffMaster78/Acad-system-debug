from rest_framework import permissions


class IsSupportAgent(permissions.BasePermission):
    """
    Allows access only to support agents.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "support"


class IsAdminOrSuperAdmin(permissions.BasePermission):
    """
    Grants full access only to Admins and SuperAdmins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["admin", "superadmin"]


class CanManageOrders(permissions.BasePermission):
    """
    Allows support agents to modify order statuses.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "support"
            and request.user.support_profile.permissions.can_manage_tickets
        )


class CanHandleDisputes(permissions.BasePermission):
    """
    Allows support agents to resolve disputes.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "support"
            and request.user.support_profile.permissions.can_handle_disputes
        )


class CanRecommendBlacklist(permissions.BasePermission):
    """
    Allows support agents to recommend blacklisting of a client.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "support"
            and request.user.support_profile.permissions.can_recommend_blacklist
        )


class CanModerateMessages(permissions.BasePermission):
    """
    Allows support agents to moderate messages.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "support"
            and request.user.support_profile.message_access.can_moderate_messages
        )


class CanManageWriterPerformance(permissions.BasePermission):
    """
    Allows support agents to recommend writer probation or promotion.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "support"
            and request.user.support_profile.permissions.can_put_writer_on_probation
        )


class CanEscalateIssues(permissions.BasePermission):
    """
    Allows support agents to escalate cases to admin or superadmin.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "support"


class CanAccessSupportDashboard(permissions.BasePermission):
    """
    Allows only support agents and admins to access the support dashboard.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["support", "admin"]