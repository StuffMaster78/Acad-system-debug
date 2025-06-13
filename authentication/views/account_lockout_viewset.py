from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from authentication.models.account_lockout import AccountLockout
from authentication.services.account_lockout_service import AccountLockoutService
from authentication.serializers.account_lockout_serializer import (
    AccountLockoutSerializer
)


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Only staff can lock/unlock accounts; others get read-only access.
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve', 'me']:
            return True
        return request.user and request.user.is_staff


class AccountLockoutViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user account lockouts.
    """

    permission_classes = [IsStaffOrReadOnly]

    def list(self, request):
        """
        List all active lockouts for the current tenant.
        Staff only.
        """
        website = request.user.website
        queryset = AccountLockout.objects.filter(
            website=website,
            active=True
        )
        serializer = AccountLockoutSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Show lockouts for the currently logged-in user.
        """
        service = AccountLockoutService(
            user=request.user,
            website=request.user.website
        )
        reasons = service.get_lockout_reasons()
        serializer = AccountLockoutSerializer(reasons, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='lock')
    def lock_user(self, request):
        """
        Lock a specific user account (admin only).
        Payload must include `user_id` and `reason`.
        """
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        reason = request.data.get("reason")
        website = request.user.website

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
            service = AccountLockoutService(user=user, website=website)
            lock = service.lock_account(reason)
            serializer = AccountLockoutSerializer(lock)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='unlock')
    def unlock_user(self, request):
        """
        Unlock a specific user account (admin only).
        Payload must include `user_id`.
        """
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        website = request.user.website

        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            user = User.objects.get(id=user_id)
            service = AccountLockoutService(user=user, website=website)
            count = service.unlock_account()
            return Response({"unlocked": count}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )