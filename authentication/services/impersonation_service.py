from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, get_user_model
from authentication.models.impersonation import (
    ImpersonationToken, ImpersonationLog
)


class ImpersonationService:
    """
    Manages admin impersonation of users within a website context.
    """

    def __init__(self, request, website):
        """
        Initialize the impersonation service.

        Args:
            request (HttpRequest): The incoming request object.
            website (Website): The current tenant website instance.
        """
        self.request = request
        self.website = website
        self.admin_user = request.user

    def impersonate_user(self, token_str):
        """
        Impersonate a user using a valid impersonation token.

        Args:
            token_str (str): The impersonation token string.

        Raises:
            PermissionDenied: If token is invalid, expired, or unauthorized.
        """
        try:
            token = ImpersonationToken.objects.get(
                token=token_str, website=self.website
            )
        except ImpersonationToken.DoesNotExist:
            raise PermissionDenied("Invalid impersonation token.")

        if token.is_expired():
            raise PermissionDenied("Token has expired.")

        if token.admin_user != self.admin_user or not self.admin_user.is_staff:
            raise PermissionDenied("You are not authorized.")
        
        if token.admin_user != self.request.user:
            raise PermissionDenied("Token does not belong to you.")

        self.request.session["impersonator_id"] = self.admin_user.id

        login(self.request, token.target_user)

        ImpersonationLog.objects.create(
            admin_user=self.admin_user,
            target_user=token.target_user,
            token=token,
            website=self.website
        )

        # Switch session user
        self.request.session['_impersonator_id'] = self.request.user.pk
        self.request.session['_auth_user_id'] = token.target_user.pk
        self.request.user = token.target_user
        self.request.session.save()

    def end_impersonation(self):
        """
        End an active impersonation session and restore the original admin.

        Raises:
            PermissionDenied: If no impersonation is in progress or
                impersonation is already ended.
        """
        original_user_id = self.request.session.get("impersonator_id")
        if not original_user_id:
            raise PermissionDenied("No impersonation in progress.")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            original_user = User.objects.get(pk=original_user_id)
        except User.DoesNotExist:
            raise PermissionDenied("Original user not found.")

        # Log the ending of impersonation
        ImpersonationLog.objects.create(
            admin_user=original_user,
            target_user=self.request.user,
            website=self.website,
            token=None
        )

        # login(self.request, original_user)
        # del self.request.session["impersonator_id"]

                # Restore original user in session
        self.request.session['_auth_user_id'] = original_user.pk
        del self.request.session['_impersonator_id']
        self.request.user = original_user
        self.request.session.save()