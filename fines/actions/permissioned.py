from django.core.exceptions import PermissionDenied
from actions.base import BaseAction
from users.mixins import UserRole


class PermissionedAction(BaseAction):
    """
    Base class for actions that enforce role-based access control.
    Subclasses should define required_roles (as UserRole values).
    """

    required_roles = None

    def validate(self):
        self.check_permissions()
        self.validate_context()

    def check_permissions(self):
        actor_role = getattr(self.actor, 'role', None)

        if actor_role == UserRole.SUPERADMIN:
            return  # full override
        
        if self.required_roles is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define required_roles"
            )

        if self.required_roles and actor_role not in self.required_roles:
            raise PermissionDenied(
                f"Action not permitted for role '{actor_role}'. "
                f"Requires one of: {self.required_roles}"
            )


    def validate_context(self):
        """Override for custom validation logic."""
        pass
