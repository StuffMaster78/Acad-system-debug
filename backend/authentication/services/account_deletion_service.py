from datetime import timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from authentication.models.account_deletion_request import (
    AccountDeletionRequest,
)
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.login_session_service import (
    LoginSessionService,
)
from authentication.services.token_service import TokenService
from core.urls.frontend_url import build_frontend_url


class AccountDeletionService:
    """
    Handle account deletion request workflows, including
    immediate access revocation, undo window, and 
    retained deletion cycle.


    This service is responsible for:
        - creating deletion requests
        - confirming and scheduling deletion
        - generating undo tokens
        - cancelling scheduled deletion via undo token
        - performing soft deletion
        - retrieving active deletion requests
    """

    DEFAULT_UNDO_HOURS = 72
    DEFAULT_RETENTION_DAYS = 180

    def __init__(self, user, website):
        """
        Initialize the account deletion service.

        Args:
            user: User requesting deletion.
            website: Website context.

        Raises:
            ValueError: If website is missing.
        """
        if website is None:
            raise ValueError(
                "Website context is required for account deletion."
            )

        self.user = user
        self.website = website

    @transaction.atomic
    def request_deletion(
        self,
        *,
        reason: str = "",
    ) -> AccountDeletionRequest:
        """
        Create a new account deletion request.

        Any currently active deletion requests for the same user and
        website are cancelled before the new request is created.

        Args:
            reason: Optional user-provided reason.

        Returns:
            Created AccountDeletionRequest instance.
        """
        self.cancel_active_requests()

        return AccountDeletionRequest.objects.create(
            user=self.user,
            website=self.website,
            reason=reason,
            status=AccountDeletionRequest.Status.PENDING,
        )

    @transaction.atomic
    def confirm_deletion(
        self,
        *,
        request_obj: AccountDeletionRequest,
    ) -> AccountDeletionRequest:
        """
        Confirm an account deletion request without scheduling it yet.

        Args:
            request_obj: AccountDeletionRequest instance.

        Returns:
            Updated request object.
        """
        if request_obj.status != AccountDeletionRequest.Status.PENDING:
            raise ValidationError(
                "Only pending deletion requests can be confirmed."
            )

        request_obj.status = AccountDeletionRequest.Status.CONFIRMED
        request_obj.confirmed_at = timezone.now()
        request_obj.save(update_fields=["status", "confirmed_at"])

        return request_obj

    @transaction.atomic
    def schedule_deletion(
        self,
        *,
        request_obj: AccountDeletionRequest,
        delay_hours: int = DEFAULT_UNDO_HOURS,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> tuple[AccountDeletionRequest, str]:
        """
        Schedule account deletion, revoke access immediately,
        and generate an undo token to open undo window.

        Args:
            request_obj: Confirmed deletion request.
            delay_hours: Undo window before deletion is finalized.

        Returns:
            Tuple of:
                - updated AccountDeletionRequest
                - raw undo token
        """
        if request_obj.status not in {
            AccountDeletionRequest.Status.PENDING,
            AccountDeletionRequest.Status.CONFIRMED,
        }:
            raise ValidationError(
                "Deletion request cannot be scheduled from its current state."
            )

        raw_token, token_hash = TokenService.generate_hashed_token()

        now = timezone.now()
        scheduled_deletion_at = now + timezone.timedelta(
            hours=delay_hours,
        )
        retained_until = scheduled_deletion_at + timedelta(
            days=retention_days
        )

        request_obj.status = AccountDeletionRequest.Status.SCHEDULED
        request_obj.confirmed_at = request_obj.confirmed_at or now
        request_obj.access_revoked_at = now
        request_obj.scheduled_deletion_at = scheduled_deletion_at
        request_obj.retained_until = retained_until
        request_obj.undo_token_hash = token_hash
        request_obj.undo_token_expires_at = scheduled_deletion_at
        request_obj.save(
            update_fields=[
                "status",
                "confirmed_at",
                "access_revoked_at",
                "scheduled_deletion_at",
                "retained_until",
                "undo_token_hash",
                "undo_token_expires_at",
            ],
        )

        self._revoke_account_access()

        undo_url = self.build_undo_url(raw_token=raw_token)

        AuthNotificationBridgeService.send_account_deletion_scheduled_notification(
            user=self.user,
            website=self.website,
            undo_url=undo_url,
            expiry_hours=delay_hours,
            reason=request_obj.reason or "",
        )

        return request_obj, raw_token

    @transaction.atomic
    def cancel_scheduled_deletion_by_token(
        self,
        *,
        raw_token: str,
    ) -> AccountDeletionRequest:
        """
        Cancel a scheduled deletion using a valid undo token.

        Args:
            raw_token: Raw undo token.

        Returns:
            Updated AccountDeletionRequest instance.

        Raises:
            ValidationError: If token is invalid or expired.
        """
        token_hash = TokenService.hash_value(raw_token)

        request_obj = AccountDeletionRequest.objects.filter(
            user=self.user,
            website=self.website,
            undo_token_hash=token_hash,
            status=AccountDeletionRequest.Status.SCHEDULED,
        ).order_by("-requested_at").first()

        if request_obj is None:
            raise ValidationError("Invalid undo token.")

        if not request_obj.is_undo_token_valid:
            raise ValidationError("Undo token has expired.")

        request_obj.status = AccountDeletionRequest.Status.CANCELLED
        request_obj.undo_token_hash = None
        request_obj.undo_token_expires_at = None
        request_obj.scheduled_deletion_at = None
        request_obj.retained_until = None
        request_obj.save(
            update_fields=[
                "status",
                "undo_token_hash",
                "undo_token_expires_at",
                "scheduled_deletion_at",
                "retained_until",
            ],
        )

        if not self.user.is_active:
            self.user.is_active = True
            self.user.save(update_fields=["is_active"])

        AuthNotificationBridgeService.send_account_deletion_cancelled_notification(
            user=self.user,
            website=self.website,
        )

        return request_obj

    @transaction.atomic
    def perform_soft_delete(
        self,
        *,
        request_obj: AccountDeletionRequest,
    ) -> AccountDeletionRequest:
        """
        Perform the final soft deletion after the undo window expires.
        Moves the scheduled deletion into retained state after undo window ends.

        Args:
            request_obj: Scheduled deletion request.

        Returns:
            Updated AccountDeletionRequest instance.
        """
        if request_obj.status != AccountDeletionRequest.Status.SCHEDULED:
            raise ValidationError(
                "Only scheduled deletion requests can be completed."
            )
        
        if (
            request_obj.scheduled_deletion_at is not None
            and timezone.now() < request_obj.scheduled_deletion_at
        ):
            raise ValidationError(
                "Undo window has not expired yet."
            )

        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        request_obj.status = AccountDeletionRequest.Status.COMPLETED
        request_obj.completed_at = timezone.now()
        request_obj.undo_token_hash = None
        request_obj.undo_token_expires_at = None
        request_obj.save(
            update_fields=[
                "status",
                "completed_at",
                "undo_token_hash",
                "undo_token_espires_at",
            ],
        )

        AuthNotificationBridgeService.send_account_deletion_completed_notification(
            user=self.user,
            website=self.website,
        )

        return request_obj
    
    @transaction.atomic
    def mark_purged(
        self,
        *,
        request_obj: AccountDeletionRequest,
    ) -> AccountDeletionRequest:
        """
        Mark retained deletion request as purged after retention.
        """
        if request_obj.status != AccountDeletionRequest.Status.RETAINED:
            raise ValidationError(
                "Only retained deletion requests can be purged."
            )

        if not request_obj.is_retention_expired:
            raise ValidationError(
                "Retention window has not expired."
            )

        request_obj.status = AccountDeletionRequest.Status.PURGED
        request_obj.purged_at = timezone.now()
        request_obj.save(update_fields=["status", "purged_at"])

        return request_obj

    def get_active_request(self) -> Optional[AccountDeletionRequest]:
        """
        Return the most recent active deletion request.

        Returns:
            Active AccountDeletionRequest or None.
        """
        return AccountDeletionRequest.objects.filter(
            user=self.user,
            website=self.website,
            status__in=[
                AccountDeletionRequest.Status.PENDING,
                AccountDeletionRequest.Status.CONFIRMED,
                AccountDeletionRequest.Status.SCHEDULED,
                AccountDeletionRequest.Status.RETAINED,
            ],
        ).order_by("-requested_at").first()

    @transaction.atomic
    def cancel_active_requests(self) -> int:
        """
        Cancel all active deletion requests for the current user.

        Returns:
            Number of updated rows.
        """
        return AccountDeletionRequest.objects.filter(
            user=self.user,
            website=self.website,
            status__in=[
                AccountDeletionRequest.Status.PENDING,
                AccountDeletionRequest.Status.CONFIRMED,
                AccountDeletionRequest.Status.SCHEDULED,
            ],
        ).update(status=AccountDeletionRequest.Status.CANCELLED)

    def _revoke_account_access(self) -> None:
        """
        Immediately kill access while deletion is pending/scheduled.
        """
        if self.user.is_active:
            self.user.is_active = False
            self.user.save(update_fields=["is_active"])

        LoginSessionService.revoke_all_sessions(
            user=self.user,
            website=self.website,
        )


    @staticmethod
    def build_undo_url(
        *,
        raw_token: str,
    ) -> str:
        """
        Build the frontend undo-deletion URL.

        Args:
            raw_token: Raw undo token.

        Returns:
            Fully-qualified undo URL.
        """
        return build_frontend_url(
            path="/account/recover-deletion",
            query_params={"token": raw_token},
        )