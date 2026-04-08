from django.core.exceptions import PermissionDenied

from authentication.utils.impersonation import is_impersonating


class ImpersonationPolicyService:
    """
    Enforce policy rules around impersonated sessions.
    """

    @staticmethod
    def validate_not_impersonating(
        *,
        request,
        message: str = (
            "This action is not allowed during impersonation."
        ),
    ) -> None:
        """
        Block an action if request is currently impersonated.
        """
        if is_impersonating(request):
            raise PermissionDenied(message)