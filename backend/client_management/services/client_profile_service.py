"""
All mutations to ClientProfile.

Extracts the business logic that was previously in ClientProfile
model methods (suspend_account, activate_account, deactivate_account,
set_password_reset_code, set_temporary_password).

Models must not import from other apps' services or create
ActivityLog entries. Services own that.

NOTIFICATION
------------
All notifications via NotificationService.notify().
No send_mail() calls.

AUDIT
-----
Every admin action writes:
1. ClientActivityLog (client management audit)
2. AuditService.record() (platform compliance audit)
"""

import logging
import random
import string

from django.apps import apps
from django.db import transaction
from django.utils.timezone import now

from client_management.models import ClientActivityLog, ClientProfile

logger = logging.getLogger(__name__)


class ClientProfileService:

    # ----------------------------------------------------------------
    # SUSPENSION / ACTIVATION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def suspend(
        *,
        client: ClientProfile,
        performed_by,
        reason: str,
    ) -> ClientProfile:
        """
        Suspend a client account.

        Sets is_suspended=True, is_active=False.
        Logs action and notifies client.

        Args:
            client:       ClientProfile to suspend.
            performed_by: Admin User performing the action.
            reason:       Required suspension reason.

        Raises:
            ValueError: If already suspended.
        """
        if client.is_suspended:
            raise ValueError(
                f"Client {client.registration_id} is already suspended."
            )

        client.is_suspended = True
        client.is_active = False
        client.save(update_fields=["is_suspended", "is_active"])

        ClientProfileService._log_action(
            client=client,
            action=f"Account suspended by {performed_by}. Reason: {reason}",
        )

        ClientProfileService._audit(
            action="client.suspended",
            actor=performed_by,
            obj=client,
            metadata={"reason": reason},
            severity="warning",
        )

        ClientProfileService._notify(
            event_key="client.account.suspended",
            client=client,
            context={
                "registration_id": client.registration_id,
                "reason":          reason,
            },
        )

        logger.info(
            "ClientProfile suspended: %s by=%s",
            client.registration_id,
            getattr(performed_by, "pk", "?"),
        )

        return client

    @staticmethod
    @transaction.atomic
    def activate(
        *,
        client: ClientProfile,
        performed_by,
        reason: str = "",
    ) -> ClientProfile:
        """
        Reactivate a suspended or deactivated client account.

        Args:
            client:       ClientProfile to reactivate.
            performed_by: Admin User.
            reason:       Optional reason for reactivation.
        """
        client.is_suspended = False
        client.is_active = True
        client.save(update_fields=["is_suspended", "is_active"])

        ClientProfileService._log_action(
            client=client,
            action=f"Account activated by {performed_by}. {reason}".strip(),
        )

        ClientProfileService._audit(
            action="client.activated",
            actor=performed_by,
            obj=client,
            metadata={"reason": reason},
        )

        ClientProfileService._notify(
            event_key="client.account.activated",
            client=client,
            context={"registration_id": client.registration_id},
        )

        return client

    @staticmethod
    @transaction.atomic
    def deactivate(
        *,
        client: ClientProfile,
        performed_by,
        reason: str = "",
    ) -> ClientProfile:
        """
        Deactivate a client account without suspension.
        Sets is_active=False only.
        """
        client.is_active = False
        client.save(update_fields=["is_active"])

        ClientProfileService._log_action(
            client=client,
            action=f"Account deactivated by {performed_by}. {reason}".strip(),
        )

        ClientProfileService._audit(
            action="client.deactivated",
            actor=performed_by,
            obj=client,
            metadata={"reason": reason},
        )

        return client

    # ----------------------------------------------------------------
    # PROFILE UPDATES
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_profile(
        *,
        client: ClientProfile,
        updated_by,
        **fields,
    ) -> ClientProfile:
        """
        Update ClientProfile fields.

        Allowed fields: country, timezone, phone_number.
        Privilege-gated fields (tier, loyalty_points) require
        explicit separate methods.

        Args:
            client:     ClientProfile to update.
            updated_by: User making the change.
            **fields:   Fields to update.
        """
        allowed = {"country", "timezone", "phone_number"}
        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(
                f"Fields not permitted: {unknown}. Allowed: {allowed}"
            )

        update_fields = []
        for field, value in fields.items():
            if getattr(client, field) != value:
                setattr(client, field, value)
                update_fields.append(field)

        if not update_fields:
            return client

        update_fields.append("date_joined")  # updated_at not on model
        client.save(update_fields=[
            f for f in update_fields if f != "date_joined"
        ])

        ClientProfileService._log_action(
            client=client,
            action=f"Profile updated by {updated_by}: {update_fields}",
        )

        return client

    # ----------------------------------------------------------------
    # LOYALTY
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def add_loyalty_points(
        *,
        client: ClientProfile,
        points: int,
        reason: str = "",
    ) -> ClientProfile:
        """
        Add loyalty points and update tier.

        This is the canonical method — replaces the duplicate
        add_loyalty_points() defined twice on the model.

        Args:
            client: ClientProfile.
            points: Points to add.
            reason: Optional reason for the transaction.
        """
        if points <= 0:
            raise ValueError("Points must be a positive integer.")

        LoyaltyTransaction = apps.get_model(
            "loyalty_management", "LoyaltyTransaction"
        )

        client.loyalty_points += points
        client._update_tier()
        client.save(update_fields=["loyalty_points", "tier"])

        LoyaltyTransaction.objects.create(
            client=client,
            points=points,
            transaction_type="add",
            reason=reason,
            website=client.website,
        )

        return client

    # ----------------------------------------------------------------
    # PASSWORD MANAGEMENT
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def set_temporary_password(
        *,
        client: ClientProfile,
        performed_by,
    ) -> str:
        """
        Set a temporary password for the client.

        Returns the temporary password for the admin to communicate.
        Logs the action. Does not send email directly — caller notifies.
        """
        temp_password = ClientProfileService._generate_temp_password()
        client.user.set_password(temp_password)
        client.user.save(update_fields=["password"])

        ClientProfileService._log_action(
            client=client,
            action=f"Temporary password set by {performed_by}.",
        )

        ClientProfileService._audit(
            action="client.temp_password_set",
            actor=performed_by,
            obj=client,
            metadata={},
            is_sensitive=True,
        )

        return temp_password

    # ----------------------------------------------------------------
    # PROFILE UPDATE REQUESTS
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def approve_profile_update_request(
        *,
        request,
        approved_by,
    ):
        """
        Approve a client ProfileUpdateRequest.
        Applies the requested changes and notifies the client.
        """
        from client_management.models import ProfileUpdateRequest

        if request.status != "pending":
            raise ValueError(
                f"Cannot approve request {request.pk}. "
                f"Status: {request.status}."
            )

        request.status = "approved"
        request.admin_response = f"Approved by {approved_by}."
        request.save(update_fields=["status", "admin_response", "updated_at"])

        ClientProfileService._notify(
            event_key="client.profile_update.approved",
            client=request.client,
            context={"registration_id": request.client.registration_id},
        )

        return request

    @staticmethod
    @transaction.atomic
    def reject_profile_update_request(
        *,
        request,
        rejected_by,
        reason: str,
    ):
        """Reject a client ProfileUpdateRequest."""
        from client_management.models import ProfileUpdateRequest

        if request.status != "pending":
            raise ValueError(
                f"Cannot reject request {request.pk}. "
                f"Status: {request.status}."
            )

        if not reason.strip():
            raise ValueError("Reason required when rejecting a request.")

        request.status = "rejected"
        request.admin_response = reason.strip()
        request.save(update_fields=["status", "admin_response", "updated_at"])

        ClientProfileService._notify(
            event_key="client.profile_update.rejected",
            client=request.client,
            context={
                "registration_id": request.client.registration_id,
                "reason":          reason,
            },
        )

        return request

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _log_action(*, client: ClientProfile, action: str) -> None:
        try:
            ClientActivityLog.objects.create(
                client=client,
                action=action,
            )
        except Exception as exc:
            logger.exception(
                "ClientProfileService._log_action failed: "
                "client=%s: %s",
                client.registration_id,
                exc,
            )

    @staticmethod
    def _audit(
        *,
        action: str,
        actor,
        obj,
        metadata: dict | None = None,
        severity: str = "info",
        is_sensitive: bool = False,
    ) -> None:
        try:
            from audit_logging.services.audit_service import AuditService
            website = getattr(obj, "website", None)
            AuditService.record(
                action=action,
                actor=actor,
                obj=obj,
                website=website,
                metadata=metadata or {},
                severity=severity,
                is_sensitive=is_sensitive,
                service_name="client_management",
            )
        except Exception as exc:
            logger.exception(
                "ClientProfileService._audit failed: %s", exc
            )

    @staticmethod
    def _notify(
        *,
        event_key: str,
        client: ClientProfile,
        context: dict,
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key=event_key,
                recipient=client.user,
                website=client.website,
                context=context,
            )
        except Exception as exc:
            logger.exception(
                "ClientProfileService._notify failed: "
                "event=%s client=%s: %s",
                event_key,
                client.registration_id,
                exc,
            )

    @staticmethod
    def _generate_temp_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choices(alphabet, k=length))