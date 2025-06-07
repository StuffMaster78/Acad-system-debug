from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsRefundOwner(BasePermission):
    """
    Allows access only to the owner of the refund.
    """
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user

class IsStaffOrRefundOwner(BasePermission):
    """
    Allows access to staff or the owner of the refund.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.client == request.user

class IsStaff(BasePermission):
    """
    Allows access only to staff members.
    """
    def has_permission(self, request, view):
        return request.user.is_staff

class IsStaffOrReadOnly(BasePermission):
    """
    Allows read-only access to anyone, write access to staff only.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff

class IsStaffOrRefundOwnerOrReadOnly(BasePermission):
    """
    Allows read-only access to anyone, write access to staff or refund owner.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff or obj.client == request.user