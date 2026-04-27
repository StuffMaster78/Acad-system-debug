import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from authentication.models import AccountDeletionRequest


class AccountDeletionService:
    """Handles account deletion flow including undo, scheduling, and email."""

    def __init__(self, user, website=None):
        """
        Initialize the deletion service.

        Args:
            user (User): The user requesting deletion.
            website (Website, optional): Tenant or site context.
        """
        self.user = user
        self.website = website

    def request_deletion(self, reason=None):
        """
        Create or update an account deletion request.

        Args:
            reason (str, optional): Reason for account deletion.

        Returns:
            AccountDeletionRequest: The active deletion request.
        """
        request, created = AccountDeletionRequest.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={'reason': reason}
        )

        if not created and request.status == AccountDeletionRequest.PENDING:
            return request

        request.status = AccountDeletionRequest.PENDING
        request.request_time = timezone.now()
        request.reason = reason
        request.generate_undo_token()
        request.save()

        self._send_undo_email(request.undo_token)
        return request

    def confirm_deletion(self, delay_hours=72):
        """
        Confirm and schedule account deletion.

        Args:
            delay_hours (int, optional): Delay before deletion in hours.
        """
        try:
            request = AccountDeletionRequest.objects.get(
                user=self.user,
                website=self.website,
                status=AccountDeletionRequest.PENDING
            )
            request.schedule_deletion(delay_hours)
            request.perform_soft_delete()
        except AccountDeletionRequest.DoesNotExist:
            pass

    @staticmethod
    def cancel_deletion_by_token(token):
        """
        Cancel deletion if undo token is valid.

        Args:
            token (str): Undo token from the recovery email.

        Returns:
            bool: True if cancelled successfully, False otherwise.
        """
        try:
            request = AccountDeletionRequest.objects.get(
                undo_token=token
            )
            now = timezone.now()
            if request.undo_token_expiry and now <= request.undo_token_expiry:
                request.status = AccountDeletionRequest.REJECTED
                request.undo_token = None
                request.undo_token_expiry = None
                request.save()
                request.user.is_active = True
                request.user.save()
                return True
        except AccountDeletionRequest.DoesNotExist:
            pass
        return False

    def _send_undo_email(self, token):
        """
        Send an undo deletion link to the user.

        Args:
            token (str): Undo token to include in the link.
        """
        domain = self._get_website_domain()
        url = f"{domain}/account/recover-deletion/{token}"

        subject = "Your Account Deletion Request"
        message = (
            "We received a request to delete your account.\n\n"
            "You can cancel this request within 72 hours by clicking:\n\n"
            f"{url}"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email]
        )

    def _get_website_domain(self):
        """
        Return the fully-qualified domain for this tenant.

        Returns:
            str: The tenant's domain name.
        """
        if hasattr(self.website, "custom_domain"):
            return f"https://{self.website.custom_domain}"
        return "https://yourapp.com"