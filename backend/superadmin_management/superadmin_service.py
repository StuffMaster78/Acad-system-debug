"""
superadmin_management/services/superadmin_service.py

All superadmin mutations. Single entry point for governance actions.

DESIGN RULES
------------
1. Writer discipline always routes through writer_management.DisciplineService.
   Never update WriterSuspension, WriterBlacklist, WriterProbation directly.

2. Non-writer discipline (client, editor, support, admin) operates on
   User flags directly. These roles do not have a domain discipline model.

3. Every action writes a SuperadminLog entry AND calls AuditService.record().
   SuperadminLog = governance dashboard.
   AuditService  = compliance / legal hold.

4. Notifications use NotificationService.notify() or notify_role().
   Never send_mail() directly.

5. All methods are keyword-only to prevent positional argument mistakes
   on high-stakes operations.
"""

import logging
import random
import string

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.timezone import now

from superadmin_management.models import (
    Appeal,
    Blacklist,
    SuperadminLog,
    SuperadminProfile,
)

logger = logging.getLogger(__name__)

User = get_user_model()

# Roles that have domain-specific discipline services
WRITER_ROLE = "writer"


class SuperadminService:

    # ----------------------------------------------------------------
    # USER MANAGEMENT
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_user(
        *,
        superadmin,
        username: str,
        email: str,
        role: str,
        website=None,
        phone_number: str = "",
    ) -> User:
        """
        Create a new platform user with a temporary password.

        Sends onboarding notification via NotificationService.
        Never sends raw email directly.

        Args:
            superadmin: Superadmin User performing the action.
            username:   New user's username.
            email:      New user's email.
            role:       One of admin/support/editor/writer/client.
            website:    Optional website assignment.
            phone_number: Optional contact number.

        Returns:
            Newly created User.

        Raises:
            ValueError: If role is invalid.
        """
        valid_roles = {"admin", "support", "editor", "writer", "client"}
        if role not in valid_roles:
            raise ValueError(
                f"Invalid role '{role}'. Must be one of {valid_roles}."
            )

        temp_password = SuperadminService._generate_temp_password()

        user = User(
            username=username,
            email=email,
            role=role,
            phone_number=phone_number,
        )
        user.set_password(temp_password)
        user.save()

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.USER_MANAGE,
            action=f"Created user {username}",
            action_details=f"Role: {role}. Email: {email}.",
            target_user=user,
            website=website,
        )

        SuperadminService._audit(
            action="superadmin.user.created",
            actor=superadmin,
            obj=user,
            website=website,
            metadata={"role": role, "email": email},
        )

        SuperadminService._notify_user(
            event_key="superadmin.user.created",
            user=user,
            website=website,
            context={
                "username":       username,
                "role":           role,
                "temp_password":  temp_password,
            },
        )

        logger.info(
            "SuperadminService.create_user: user=%s role=%s by=%s",
            username,
            role,
            superadmin.pk,
        )

        return user

    @staticmethod
    @transaction.atomic
    def change_user_role(
        *,
        superadmin,
        user: User,
        new_role: str,
        website=None,
    ) -> User:
        """
        Change a user's role. Logs and notifies.

        Raises:
            ValueError: If new_role is invalid.
        """
        valid_roles = {"admin", "support", "editor", "writer", "client"}
        if new_role not in valid_roles:
            raise ValueError(
                f"Invalid role '{new_role}'. Must be one of {valid_roles}."
            )

        old_role = getattr(user, "role", "unknown")
        user.role = new_role
        user.save(update_fields=["role"])

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.PROMOTION,
            action=f"Changed role: {user.username}",
            action_details=f"{old_role} → {new_role}",
            target_user=user,
            website=website,
        )

        SuperadminService._audit(
            action="superadmin.user.role_changed",
            actor=superadmin,
            obj=user,
            website=website,
            metadata={"old_role": old_role, "new_role": new_role},
        )

        SuperadminService._notify_user(
            event_key="superadmin.user.role_changed",
            user=user,
            website=website,
            context={
                "username": user.username,
                "old_role": old_role,
                "new_role": new_role,
            },
        )

        return user

    # ----------------------------------------------------------------
    # SUSPENSION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def suspend_user(
        *,
        superadmin,
        user: User,
        reason: str,
        website=None,
        duration_days: int | None = None,
    ) -> None:
        """
        Suspend a user.

        For writers: delegates to writer_management.DisciplineService
        so WriterDisciplineState and WriterCapacity are updated.

        For all other roles: sets User.is_suspended = True directly.

        Args:
            superadmin:     Superadmin User.
            user:           User to suspend.
            reason:         Suspension reason.
            website:        Optional website context.
            duration_days:  Optional duration. None = indefinite.
        """
        role = getattr(user, "role", None)

        if role == WRITER_ROLE:
            SuperadminService._suspend_writer(
                superadmin=superadmin,
                user=user,
                reason=reason,
                duration_days=duration_days,
            )
        else:
            user.is_suspended = True
            user.suspension_reason = reason
            user.save(update_fields=["is_suspended", "suspension_reason"])

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.SUSPENSION,
            action=f"Suspended: {user.username}",
            action_details=f"Reason: {reason}",
            target_user=user,
            website=website,
        )

        SuperadminService._audit(
            action="superadmin.user.suspended",
            actor=superadmin,
            obj=user,
            website=website,
            metadata={"reason": reason, "duration_days": duration_days},
            severity="warning",
        )

        SuperadminService._notify_user(
            event_key="superadmin.user.suspended",
            user=user,
            website=website,
            context={"username": user.username, "reason": reason},
        )

    @staticmethod
    @transaction.atomic
    def reactivate_user(
        *,
        superadmin,
        user: User,
        website=None,
        reason: str = "",
    ) -> None:
        """
        Reactivate a suspended user.

        For writers: delegates to DisciplineService.lift_suspension().
        For others: clears User.is_suspended.
        """
        role = getattr(user, "role", None)

        if role == WRITER_ROLE:
            SuperadminService._lift_writer_suspension(
                superadmin=superadmin,
                user=user,
                reason=reason or "Reactivated by superadmin",
            )
        else:
            user.is_suspended = False
            user.suspension_reason = None
            user.save(update_fields=["is_suspended", "suspension_reason"])

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.REACTIVATION,
            action=f"Reactivated: {user.username}",
            action_details=reason,
            target_user=user,
            website=website,
        )

        SuperadminService._audit(
            action="superadmin.user.reactivated",
            actor=superadmin,
            obj=user,
            website=website,
            metadata={"reason": reason},
        )

        SuperadminService._notify_user(
            event_key="superadmin.user.reactivated",
            user=user,
            website=website,
            context={"username": user.username},
        )

    # ----------------------------------------------------------------
    # BLACKLIST
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def blacklist(
        *,
        superadmin,
        reason: str,
        website=None,
        user: User | None = None,
        email: str | None = None,
        ip_address: str | None = None,
    ) -> Blacklist:
        """
        Blacklist a user, email address, or IP address.

        For writer users: ALSO delegates to DisciplineService.blacklist()
        so WriterDisciplineState is updated and the writer cannot take orders.

        Args:
            superadmin:  Superadmin User.
            reason:      Reason for blacklisting.
            website:     Optional website scope. None = platform-wide.
            user:        User to blacklist (optional).
            email:       Email to blacklist (optional).
            ip_address:  IP to blacklist (optional).

        Raises:
            ValueError: If none of user, email, ip_address provided.
        """
        if not user and not email and not ip_address:
            raise ValueError(
                "Must provide at least one of: user, email, ip_address."
            )

        blacklist_type = (
            Blacklist.BlacklistType.USER if user else
            Blacklist.BlacklistType.EMAIL if email else
            Blacklist.BlacklistType.IP
        )

        entry = Blacklist.objects.create(
            blacklist_type=blacklist_type,
            user=user,
            email=email,
            ip_address=ip_address,
            reason=reason,
            blacklisted_by=superadmin,
            website=website,
            is_active=True,
        )

        # For writers additionally route through DisciplineService
        if user and getattr(user, "role", None) == WRITER_ROLE:
            SuperadminService._blacklist_writer(
                superadmin=superadmin,
                user=user,
                reason=reason,
            )

        target = user or email or ip_address
        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.BLACKLIST,
            action=f"Blacklisted: {target}",
            action_details=f"Type: {blacklist_type}. Reason: {reason}",
            target_user=user,
            website=website,
        )

        SuperadminService._audit(
            action="superadmin.blacklist.created",
            actor=superadmin,
            obj=entry,
            website=website,
            metadata={
                "reason":      reason,
                "target_user": getattr(user, "pk", None),
                "email":       email,
                "ip_address":  ip_address,
            },
            severity="critical",
        )

        if user:
            SuperadminService._notify_user(
                event_key="superadmin.user.blacklisted",
                user=user,
                website=website,
                context={"username": user.username, "reason": reason},
            )

        return entry

    @staticmethod
    @transaction.atomic
    def lift_blacklist(
        *,
        superadmin,
        entry: Blacklist,
        reason: str,
        website=None,
    ) -> Blacklist:
        """
        Lift a blacklist entry.

        For writer users: also lifts WriterBlacklist via DisciplineService.
        """
        entry.is_active = False
        entry.lifted_at = now()
        entry.lift_reason = reason
        entry.save(update_fields=["is_active", "lifted_at", "lift_reason"])

        if entry.user and getattr(entry.user, "role", None) == WRITER_ROLE:
            SuperadminService._lift_writer_blacklist(
                superadmin=superadmin,
                user=entry.user,
                reason=reason,
            )

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.BLACKLIST_LIFTED,
            action=f"Lifted blacklist: {entry.user or entry.email or entry.ip_address}",
            action_details=f"Reason: {reason}",
            target_user=entry.user,
            website=website,
        )

        SuperadminService._audit(
            action="superadmin.blacklist.lifted",
            actor=superadmin,
            obj=entry,
            website=website,
            metadata={"reason": reason},
        )

        return entry

    # ----------------------------------------------------------------
    # APPEALS
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def approve_appeal(
        *,
        superadmin,
        appeal: Appeal,
        review_notes: str = "",
    ) -> Appeal:
        """
        Approve an appeal. Routes to the correct domain service
        based on the appellant's role.

        Writers  → writer_management.DisciplineService
        Others   → User flags directly
        """
        if appeal.status != Appeal.Status.PENDING:
            raise ValueError(
                f"Cannot approve appeal {appeal.pk}. "
                f"Status: {appeal.status}."
            )

        role = getattr(appeal.user, "role", None)

        if role == WRITER_ROLE:
            SuperadminService._approve_writer_appeal(
                appeal=appeal,
                superadmin=superadmin,
            )
        else:
            SuperadminService._approve_non_writer_appeal(
                appeal=appeal,
                superadmin=superadmin,
            )

        appeal.status = Appeal.Status.APPROVED
        appeal.reviewed_by = superadmin
        appeal.reviewed_at = now()
        appeal.review_notes = review_notes
        appeal.save(update_fields=[
            "status", "reviewed_by", "reviewed_at", "review_notes"
        ])

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.APPEAL_APPROVED,
            action=f"Appeal approved: {appeal.user.username}",
            action_details=(
                f"Type: {appeal.appeal_type}. "
                f"Notes: {review_notes}"
            ),
            target_user=appeal.user,
            website=appeal.website,
        )

        SuperadminService._audit(
            action="superadmin.appeal.approved",
            actor=superadmin,
            obj=appeal,
            website=appeal.website,
            metadata={
                "appeal_type":  appeal.appeal_type,
                "user_role":    role,
                "review_notes": review_notes,
            },
        )

        SuperadminService._notify_user(
            event_key="superadmin.appeal.approved",
            user=appeal.user,
            website=appeal.website,
            context={
                "username":    appeal.user.username,
                "appeal_type": appeal.appeal_type,
            },
        )

        return appeal

    @staticmethod
    @transaction.atomic
    def reject_appeal(
        *,
        superadmin,
        appeal: Appeal,
        review_notes: str,
    ) -> Appeal:
        """
        Reject an appeal.

        Raises:
            ValueError: If appeal not pending or review_notes blank.
        """
        if appeal.status != Appeal.Status.PENDING:
            raise ValueError(
                f"Cannot reject appeal {appeal.pk}. "
                f"Status: {appeal.status}."
            )

        if not review_notes.strip():
            raise ValueError(
                "review_notes required when rejecting an appeal."
            )

        appeal.status = Appeal.Status.REJECTED
        appeal.reviewed_by = superadmin
        appeal.reviewed_at = now()
        appeal.review_notes = review_notes
        appeal.save(update_fields=[
            "status", "reviewed_by", "reviewed_at", "review_notes"
        ])

        SuperadminService._log(
            superadmin=superadmin,
            action_type=SuperadminLog.ActionType.APPEAL_REJECTED,
            action=f"Appeal rejected: {appeal.user.username}",
            action_details=(
                f"Type: {appeal.appeal_type}. "
                f"Notes: {review_notes}"
            ),
            target_user=appeal.user,
            website=appeal.website,
        )

        SuperadminService._audit(
            action="superadmin.appeal.rejected",
            actor=superadmin,
            obj=appeal,
            website=appeal.website,
            metadata={
                "appeal_type":  appeal.appeal_type,
                "review_notes": review_notes,
            },
        )

        SuperadminService._notify_user(
            event_key="superadmin.appeal.rejected",
            user=appeal.user,
            website=appeal.website,
            context={
                "username":     appeal.user.username,
                "appeal_type":  appeal.appeal_type,
                "review_notes": review_notes,
            },
        )

        return appeal

    # ----------------------------------------------------------------
    # WRITER ROUTING HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _suspend_writer(*, superadmin, user, reason, duration_days=None):
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.services.discipline_service import DisciplineService
        try:
            writer = WriterProfile.objects.get(account_profile__user=user)
            DisciplineService.suspend(
                writer=writer,
                reason=reason,
                suspended_by=superadmin,
                duration_days=duration_days,
            )
        except WriterProfile.DoesNotExist:
            logger.warning(
                "SuperadminService._suspend_writer: no WriterProfile "
                "for user=%s. Setting User.is_suspended flag only.",
                user.pk,
            )
            user.is_suspended = True
            user.suspension_reason = reason
            user.save(update_fields=["is_suspended", "suspension_reason"])

    @staticmethod
    def _lift_writer_suspension(*, superadmin, user, reason):
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.services.discipline_service import DisciplineService
        try:
            writer = WriterProfile.objects.get(account_profile__user=user)
            DisciplineService.lift_suspension(
                writer=writer,
                lifted_by=superadmin,
                reason=reason,
            )
        except WriterProfile.DoesNotExist:
            logger.warning(
                "SuperadminService._lift_writer_suspension: "
                "no WriterProfile for user=%s.",
                user.pk,
            )
            user.is_suspended = False
            user.suspension_reason = None
            user.save(update_fields=["is_suspended", "suspension_reason"])

    @staticmethod
    def _blacklist_writer(*, superadmin, user, reason):
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.services.discipline_service import DisciplineService
        try:
            writer = WriterProfile.objects.get(account_profile__user=user)
            DisciplineService.blacklist(
                writer=writer,
                reason=reason,
                blacklisted_by=superadmin,
            )
        except WriterProfile.DoesNotExist:
            logger.warning(
                "SuperadminService._blacklist_writer: "
                "no WriterProfile for user=%s.",
                user.pk,
            )

    @staticmethod
    def _lift_writer_blacklist(*, superadmin, user, reason):
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.services.discipline_service import DisciplineService
        try:
            writer = WriterProfile.objects.get(account_profile__user=user)
            DisciplineService.lift_blacklist(
                writer=writer,
                lifted_by=superadmin,
                reason=reason,
            )
        except WriterProfile.DoesNotExist:
            logger.warning(
                "SuperadminService._lift_writer_blacklist: "
                "no WriterProfile for user=%s.",
                user.pk,
            )

    @staticmethod
    def _approve_writer_appeal(*, appeal, superadmin):
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.services.discipline_service import DisciplineService

        try:
            writer = WriterProfile.objects.get(
                account_profile__user=appeal.user
            )
        except WriterProfile.DoesNotExist:
            logger.warning(
                "SuperadminService._approve_writer_appeal: "
                "no WriterProfile for user=%s.",
                appeal.user.pk,
            )
            return

        reason = f"Appeal approved by {superadmin.username}"

        if appeal.appeal_type == Appeal.AppealType.SUSPENSION:
            DisciplineService.lift_suspension(
                writer=writer,
                lifted_by=superadmin,
                reason=reason,
            )
        elif appeal.appeal_type == Appeal.AppealType.BLACKLIST:
            DisciplineService.lift_blacklist(
                writer=writer,
                lifted_by=superadmin,
                reason=reason,
            )
        elif appeal.appeal_type == Appeal.AppealType.PROBATION:
            from writer_management.models.writer_discipline import WriterProbation
            probation = WriterProbation.objects.filter(
                writer=writer, is_active=True
            ).first()
            if probation:
                DisciplineService.end_probation(
                    writer=writer,
                    ended_by=superadmin,
                    reason=reason,
                )

    @staticmethod
    def _approve_non_writer_appeal(*, appeal, superadmin):
        user = appeal.user

        if appeal.appeal_type == Appeal.AppealType.SUSPENSION:
            user.is_suspended = False
            user.suspension_reason = None
            user.save(update_fields=["is_suspended", "suspension_reason"])

        elif appeal.appeal_type == Appeal.AppealType.BLACKLIST:
            user.is_blacklisted = False
            user.save(update_fields=["is_blacklisted"])
            Blacklist.objects.filter(
                user=user, is_active=True
            ).update(is_active=False, lifted_at=now())

        elif appeal.appeal_type == Appeal.AppealType.PROBATION:
            if hasattr(user, "is_on_probation"):
                user.is_on_probation = False
                user.save(update_fields=["is_on_probation"])

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _log(
        *,
        superadmin,
        action_type: str,
        action: str,
        action_details: str = "",
        target_user=None,
        website=None,
    ) -> None:
        try:
            SuperadminLog.objects.create(
                superadmin=superadmin,
                action_type=action_type,
                action=action,
                action_details=action_details,
                target_user=target_user,
                website=website,
            )
        except Exception as exc:
            logger.exception(
                "SuperadminService._log failed: %s", exc
            )

    @staticmethod
    def _audit(
        *,
        action: str,
        actor,
        obj,
        website=None,
        metadata: dict | None = None,
        severity: str = "info",
    ) -> None:
        try:
            from audit_logging.services.audit_service import AuditService
            AuditService.record(
                action=action,
                actor=actor,
                obj=obj,
                website=website,
                metadata=metadata or {},
                severity=severity,
                service_name="superadmin_management",
            )
        except Exception as exc:
            logger.exception(
                "SuperadminService._audit failed: %s", exc
            )

    @staticmethod
    def _notify_user(
        *,
        event_key: str,
        user,
        website,
        context: dict,
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify(
                event_key=event_key,
                recipient=user,
                website=website,
                context=context,
            )
        except Exception as exc:
            logger.exception(
                "SuperadminService._notify_user failed: "
                "event=%s user=%s: %s",
                event_key,
                getattr(user, "pk", "?"),
                exc,
            )

    @staticmethod
    def _notify_admins(
        *,
        event_key: str,
        website,
        context: dict,
        is_critical: bool = False,
    ) -> None:
        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            NotificationService.notify_role(
                event_key=event_key,
                role="superadmin",
                website=website,
                context=context,
                is_critical=is_critical,
            )
        except Exception as exc:
            logger.exception(
                "SuperadminService._notify_admins failed: %s", exc
            )

    @staticmethod
    def _generate_temp_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choices(alphabet, k=length))