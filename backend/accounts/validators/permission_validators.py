from __future__ import annotations

from django.core.exceptions import ValidationError

from accounts.models import PermissionDefinition, RolePermission


class PermissionValidators:
    """
    Validation helpers for permissions.
    """

    @staticmethod
    def validate_permission_code_available(
        *,
        code: str,
    ) -> None:
        exists = PermissionDefinition.objects.filter(code=code).exists()

        if exists:
            raise ValidationError(
                f"Permission with code '{code}' already exists."
            )

    @staticmethod
    def validate_role_permission_not_duplicate(
        *,
        role,
        permission,
    ) -> None:
        exists = RolePermission.objects.filter(
            role=role,
            permission=permission,
        ).exists()

        if exists:
            raise ValidationError(
                "This role already has this permission."
            )