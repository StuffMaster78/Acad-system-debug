from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


from authentication.utils.impersonation import is_impersonating


class NotImpersonatingPermission(BasePermission):
    """
    Allow access only when the request is not impersonated.
    """

    message = "This action is not allowed during impersonation."

    def has_permission(self, request:Request, view:APIView) -> bool:
        return not is_impersonating(request)


class IsImpersonatingPermission(BasePermission):
    """
    Allow access only when the request is currently impersonated.
    """

    message = "This endpoint requires an active impersonation session."

    def has_permission(self, request: Request, view: APIView) -> bool:
        return is_impersonating(request)
    

class IsStaffSecurityOperator(BasePermission):
    """
    Restrict security-control endpoints to staff users.
    """

    message = "You do not have permission to perform this security action."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_staff)