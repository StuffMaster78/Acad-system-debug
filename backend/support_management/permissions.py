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
        if not (request.user.is_authenticated and request.user.role == "support"):
            return False
        perms = getattr(getattr(request.user, 'support_profile', None), 'permissions', None)
        can_manage = False
        try:
            can_manage = bool(getattr(perms, 'can_manage_tickets', False))
        except Exception:
            can_manage = False
        return can_manage


class CanHandleDisputes(permissions.BasePermission):
    """
    Allows support agents to resolve disputes.
    """

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == "support"):
            return False
        perms = getattr(getattr(request.user, 'support_profile', None), 'permissions', None)
        try:
            return bool(getattr(perms, 'can_handle_disputes', False))
        except Exception:
            return False


class CanRecommendBlacklist(permissions.BasePermission):
    """
    Allows support agents to recommend blacklisting of a client.
    """

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == "support"):
            return False
        perms = getattr(getattr(request.user, 'support_profile', None), 'permissions', None)
        try:
            return bool(getattr(perms, 'can_recommend_blacklist', False))
        except Exception:
            return False


class CanModerateMessages(permissions.BasePermission):
    """
    Allows support agents to moderate messages.
    """

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == "support"):
            return False
        access = getattr(getattr(request.user, 'support_profile', None), 'message_access', None)
        try:
            return bool(getattr(access, 'can_moderate_messages', False))
        except Exception:
            return False


class CanManageWriterPerformance(permissions.BasePermission):
    """
    Allows support agents to recommend writer probation or promotion.
    """

    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == "support"):
            return False
        perms = getattr(getattr(request.user, 'support_profile', None), 'permissions', None)
        try:
            return bool(getattr(perms, 'can_put_writer_on_probation', False))
        except Exception:
            return False


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