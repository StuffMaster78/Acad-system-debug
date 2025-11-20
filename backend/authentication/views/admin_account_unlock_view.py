from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from authentication.services.account_lockout_service import (
    AccountLockoutService
)
from users.models import User


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superadmin


class AdminAccountUnlockViewSet(viewsets.ViewSet):
    permission_classes = [IsSuperAdmin]

    def create(self, request):
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            AccountLockoutService.unlock_user(user)
            return Response(
                {"message": "User unlocked successfully."}
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )