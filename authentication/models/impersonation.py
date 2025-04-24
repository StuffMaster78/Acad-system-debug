from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
from django.core.exceptions import PermissionDenied
from django.utils import timezone

User = get_user_model()

class ImpersonationToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    admin_user = models.ForeignKey(
        User,
        related_name='impersonation_tokens',
        on_delete=models.CASCADE
    )
    target_user = models.ForeignKey(
        User,
        related_name='impersonated_by',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Impersonation token for {self.admin_user} -> {self.target_user}"

    @classmethod
    def generate_token(cls, admin_user, target_user):
        token = str(uuid.uuid4())[:8]  # You can adjust token length here
        expiration_time = timezone.now() + timezone.timedelta(hours=1)  # Token expires in 1 hour
        return cls.objects.create(
            token=token,
            admin_user=admin_user,
            target_user=target_user,
            expires_at=expiration_time
        )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def impersonate_user(request, token):
        """
        Handles impersonating a user.
        """
        try:
            impersonation_token = ImpersonationToken.objects.get(token=token)

            # Check for expiration
            if impersonation_token.is_expired():
                raise PermissionDenied("This impersonation token has expired.")

            # Check if the requesting user is an admin
            if not request.user.is_staff or impersonation_token.admin_user != request.user:
                raise PermissionDenied("You are not authorized to impersonate this user.")

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
            raise PermissionDenied("Invalid impersonation token.")
        

    def end_impersonation(request):
        """
        Ends the impersonation and logs the admin back in.
        """
        try:
            original_user = User.objects.get(id=request.session['_auth_user_id'])

            # Check if the current user is impersonating
            if request.user == original_user:
                raise PermissionDenied("You are not impersonating anyone.")

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
            raise PermissionDenied("You are not impersonating anyone.")


class ImpersonationLog(models.Model):
    admin_user = models.ForeignKey(
        User,
        related_name='impersonation_logs',
        on_delete=models.CASCADE
    )
    target_user = models.ForeignKey(
        User,
        related_name='impersonation_logs',
        on_delete=models.CASCADE
    )
    token = models.ForeignKey(ImpersonationToken, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Impersonation log: {self.admin_user} -> {self.target_user} on {self.created_at}"