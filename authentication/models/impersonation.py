from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from django.core.exceptions import PermissionDenied

User = get_user_model()

class ImpersonationToken(models.Model):
    """
    Temporary token allowing an admin to impersonate a user.
    """
    token = models.CharField(max_length=64, unique=True)
    admin_user = models.ForeignKey(
        'users.User',
        related_name='user_impersonation_tokens',
        on_delete=models.CASCADE
    )
    target_user = models.ForeignKey(
        'users.User',
        related_name='impersonated_by_tokens',
        on_delete=models.CASCADE
    )

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="impersonation_web_tokens"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    expires_at = models.DateTimeField()

    def __str__(self):
        return (
            f"Impersonation token: {self.admin_user} → {self.target_user}"
        )

    @classmethod
    def generate_token(cls, admin_user, target_user, website, expires_hours: int = 1):
        """
        Creates and stores a new impersonation token.

        Args:
            admin_user (User): Admin initiating impersonation.
            target_user (User): Target user to impersonate.
            website (Website): Current tenant context.
            expires_hours (int): Token expiration in hours (default: 1).

        Returns:
            ImpersonationToken: The created token instance.
        """
        token = str(uuid.uuid4()).replace("-", "")[:32]
        expires = timezone.now() + timezone.timedelta(hours=expires_hours)
        return cls.objects.create(
            token=token,
            admin_user=admin_user,
            target_user=target_user,
            website=website,
            expires_at=expires
        )

    def is_expired(self):
        """
        Checks if the token has expired.

        Returns:
            bool: True if token is expired, else False.
        """
        return timezone.now() > self.expires_at

    def impersonate_user(request, token):
        """
        Handles impersonating a user.
        """
        try:
            impersonation_token = ImpersonationToken.objects.get(token=token)

            # Check for expiration
            if impersonation_token.is_expired():
                raise PermissionDenied(
                    "This impersonation token has expired."
                )

            # Check if the requesting user is an admin
            if not request.user.is_staff or impersonation_token.admin_user != request.user:
                raise PermissionDenied(
                    "You are not authorized to impersonate this user."
                )

            # Create an impersonation log entry
            ImpersonationLog.objects.create(
                admin_user=request.user,
                target_user=impersonation_token.target_user,
                token=impersonation_token
            )

            # Log the admin in as the target user
            request.user = impersonation_token.target_user
            request.session['_auth_user_id'] = impersonation_token.target_user.pk
            request.session.save()

        except ImpersonationToken.DoesNotExist:
            raise PermissionDenied(
                "Invalid impersonation token."
            )
        

    def end_impersonation(request):
        """
        Ends the impersonation and logs the admin back in.
        """
        try:
            original_user = User.objects.get(id=request.session['_auth_user_id'])

            # Check if the current user is impersonating
            if request.user == original_user:
                raise PermissionDenied(
                    "You are not impersonating anyone."
                )

            # Log the action
            ImpersonationLog.objects.create(
                admin_user=request.user,
                target_user=original_user,
                token=None  # No need for a token since it's not a new session
            )

            # Log the admin back in
            request.user = original_user
            request.session['_auth_user_id'] = original_user.pk
            request.session.save()

        except KeyError:
            raise PermissionDenied(
                "You are not impersonating anyone."
            )


class ImpersonationLog(models.Model):
    """
    Records each impersonation action for audit purposes.
    """
    admin_user = models.ForeignKey(
        User,
        related_name='impersonation_logs_for_admin',
        on_delete=models.CASCADE
    )
    target_user = models.ForeignKey(
        User,
        related_name='impersonation_logs_for_target_user',
        on_delete=models.CASCADE
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="impersonation_logs"
    )
    token = models.ForeignKey(ImpersonationToken, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.admin_user} impersonated {self.target_user} "
            f"on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )