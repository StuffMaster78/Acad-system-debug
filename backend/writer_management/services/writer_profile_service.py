"""
writer_management/services/writer_profile_service.py

Owns all mutations to WriterProfile.

RESPONSIBILITY
--------------
This service answers one question per method:
    "What needs to happen to the WriterProfile for this action?"

It does NOT:
    - Create AccountProfile → accounts.AccountCreationService
    - Assign roles → accounts.AccountRoleService
    - Grant portal access → accounts.PortalAccessService
    - Grant tenant access → accounts.TenantAccessService
    - Track onboarding session → accounts.OnboardingService

It DOES:
    - Create WriterProfile (after accounts setup is complete)
    - Update profile identity fields (bio, timezone, qualifications)
    - Progress WriterProfile.onboarding_status through writer-domain steps
    - Soft-delete and restore profiles
    - Manage verification status
    - Generate registration_id

ONBOARDING STATUS OWNERSHIP
----------------------------
AccountProfile.onboarding_status → accounts app (platform setup)
WriterProfile.onboarding_status → this service (writer domain)

These are separate concerns. Do not read one to set the other.

CALLED BY
---------
WriterApplicationService.approve() → create_for_approved_application()
Admin API → update_profile(), soft_delete()
Writer API → update_own_profile()
Onboarding pipeline → advance_onboarding_status()
"""

import logging
import random
import string
from datetime import date

from django.db import transaction
from django.utils.timezone import now

from writer_management.enums import (
    WriterOnboardingStatus,
    WriterVerificationStatus,
)
from writer_management.exceptions import WriterProfileNotFoundError
from writer_management.models.writer_profile import WriterProfile

logger = logging.getLogger(__name__)

# Fields writers can update themselves via the profile API
WRITER_EDITABLE_FIELDS = {
    "bio",
    "timezone",
    "qualifications",
    "years_of_experience",
}

# Fields only admins can update
ADMIN_EDITABLE_FIELDS = {
    "pen_name",
    "is_verified",
    "verification_status",
    "onboarding_status",
    "writer_level",
}


class WriterProfileService:

    # ----------------------------------------------------------------
    # CREATION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def create_for_approved_application(
        account_profile,
        application,
        initial_level=None,
    ) -> WriterProfile:
        """
        Create a WriterProfile for an approved WriterApplication.

        Called AFTER accounts.WriterOnboardingService.complete_onboarding()
        has finished. AccountProfile, role, portal access, and tenant
        access are already set up by that point.

        Args:
            account_profile: AccountProfile (fully platform-onboarded).
            application: Approved WriterApplication (source data).
            initial_level: Optional WriterLevel. Null until admin assigns.

        Returns:
            WriterProfile with onboarding_status=IN_PROGRESS.

        Raises:
            ValueError: If a WriterProfile already exists for this
                        AccountProfile (idempotency guard).
        """
        # Idempotency guard
        if WriterProfile.objects.filter(
            account_profile=account_profile
        ).exists():
            existing = WriterProfile.objects.get(
                account_profile=account_profile
            )
            logger.warning(
                "WriterProfile already exists for account_profile=%s. "
                "Returning existing: %s",
                account_profile.pk,
                existing.registration_id,
            )
            return existing

        registration_id = WriterProfileService._generate_registration_id()

        writer_profile = WriterProfile.objects.create(
            account_profile=account_profile,
            registration_id=registration_id,
            writer_level=initial_level,
            pen_name="",
            timezone="UTC",
            bio="",
            qualifications=[],
            years_of_experience=application.years_of_experience or 0,
            is_verified=False,
            verification_status=WriterVerificationStatus.UNVERIFIED,
            onboarding_status=WriterOnboardingStatus.IN_PROGRESS,
        )

        logger.info(
            "WriterProfile created: registration_id=%s "
            "account_profile=%s application=%s",
            registration_id,
            account_profile.pk,
            application.pk,
        )

        return writer_profile

    # ----------------------------------------------------------------
    # PROFILE UPDATES
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_profile(
        writer: WriterProfile,
        updated_by,
        is_admin: bool = False,
        **fields,
    ) -> WriterProfile:
        """
        Update WriterProfile fields.

        Writers can update WRITER_EDITABLE_FIELDS only.
        Admins can update ADMIN_EDITABLE_FIELDS in addition.

        Creates a WriterProfileUpdateLog entry for every change.

        Args:
            writer: WriterProfile to update.
            updated_by: User making the change.
            is_admin: True if the caller is an admin.
            **fields: Fields to update with new values.

        Returns:
            Updated WriterProfile.

        Raises:
            ValueError: If unknown or unpermitted fields are passed.
        """
        allowed = WRITER_EDITABLE_FIELDS.copy()
        if is_admin:
            allowed |= ADMIN_EDITABLE_FIELDS

        unknown = set(fields) - allowed
        if unknown:
            raise ValueError(
                f"Fields not permitted for this caller: {unknown}. "
                f"Allowed: {allowed}"
            )

        if not fields:
            return writer

        # Snapshot previous values for audit log
        previous_values = {
            field: getattr(writer, field)
            for field in fields
        }

        update_fields = []
        for field, value in fields.items():
            if getattr(writer, field) != value:
                setattr(writer, field, value)
                update_fields.append(field)

        if not update_fields:
            return writer

        update_fields.append("updated_at")
        writer.save(update_fields=update_fields)

        # Audit log
        WriterProfileService._create_update_log(
            writer=writer,
            updated_fields=update_fields,
            previous_values=previous_values,
            updated_by=updated_by,
        )

        logger.info(
            "WriterProfile updated: writer=%s fields=%s by=%s",
            writer.registration_id,
            update_fields,
            getattr(updated_by, "pk", "system"),
        )

        return writer

    # ----------------------------------------------------------------
    # ONBOARDING STATUS PROGRESSION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def advance_onboarding_status(
        writer: WriterProfile,
        new_status: str,
        advanced_by=None,
        notes: str = "",
    ) -> WriterProfile:
        """
        Advance WriterProfile.onboarding_status to a new state.

        Valid transitions:
            IN_PROGRESS → DOCUMENTS_PENDING (writer submits documents)
            DOCUMENTS_PENDING → REVIEW_PENDING (admin accepts docs)
            DOCUMENTS_PENDING → REJECTED (admin rejects docs)
            REVIEW_PENDING → COMPLETED (admin final approval)
            REVIEW_PENDING → REJECTED (admin rejects at final review)
            REJECTED → IN_PROGRESS (writer corrects and resubmits)

        Args:
            writer: WriterProfile to advance.
            new_status: Target WriterOnboardingStatus value.
            advanced_by: User performing the advancement.
            notes: Optional reason for this transition.

        Returns:
            Updated WriterProfile.

        Raises:
            ValueError: If transition is invalid.
        """
        valid_transitions = {
            WriterOnboardingStatus.IN_PROGRESS.value: {
                WriterOnboardingStatus.DOCUMENTS_PENDING.value,
            },
            WriterOnboardingStatus.DOCUMENTS_PENDING.value: {
                WriterOnboardingStatus.REVIEW_PENDING.value,
                WriterOnboardingStatus.REJECTED.value,
            },
            WriterOnboardingStatus.REVIEW_PENDING.value: {
                WriterOnboardingStatus.COMPLETED.value,
                WriterOnboardingStatus.REJECTED.value,
            },
            WriterOnboardingStatus.REJECTED.value: {
                WriterOnboardingStatus.IN_PROGRESS.value,
            },
        }

        current = writer.onboarding_status # str from CharField
        allowed_next = valid_transitions.get(current, set())

        if new_status not in allowed_next:
            raise ValueError(
                f"Invalid onboarding status transition: "
                f"{current} → {new_status}. "
                f"Allowed from {current}: {allowed_next}"
            )

        previous_status = writer.onboarding_status
        writer.onboarding_status = new_status
        writer.save(update_fields=["onboarding_status", "updated_at"])

        WriterProfileService._create_update_log(
            writer=writer,
            updated_fields=["onboarding_status"],
            previous_values={"onboarding_status": previous_status},
            updated_by=advanced_by,
        )

        logger.info(
            "WriterProfile onboarding_status: writer=%s %s → %s by=%s",
            writer.registration_id,
            previous_status,
            new_status,
            getattr(advanced_by, "pk", "system"),
        )

        # If completed — sync can_take_orders on WriterCapacity
        if new_status == WriterOnboardingStatus.COMPLETED:
            WriterProfileService._on_onboarding_completed(writer)

        # Notify writer of status change
        WriterProfileService._notify_onboarding_status(
            writer=writer,
            new_status=new_status,
            notes=notes,
        )

        return writer

    @staticmethod
    def _on_onboarding_completed(writer: WriterProfile) -> None:
        """
        Side effects when onboarding reaches COMPLETED.
        WriterCapacity.can_take_orders was False by default —
        set to True now that the writer is eligible.
        """
        from writer_management.models.writer_capacity import WriterCapacity

        updated = WriterCapacity.objects.filter(
            writer=writer,
            can_take_orders=False,
        ).update(can_take_orders=True)

        if updated:
            logger.info(
                "WriterCapacity.can_take_orders set True: writer=%s",
                writer.registration_id,
            )

    # ----------------------------------------------------------------
    # VERIFICATION
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def update_verification(
        writer: WriterProfile,
        new_status: str,
        verified_by,
    ) -> WriterProfile:
        """
        Update verification status. Sets is_verified from status.

        Args:
            writer: WriterProfile to update.
            new_status: WriterVerificationStatus value.
            verified_by: Admin User performing the update.

        Returns:
            Updated WriterProfile.
        """
        is_verified = new_status == WriterVerificationStatus.VERIFIED

        writer.verification_status = new_status
        writer.is_verified = is_verified
        writer.save(update_fields=[
            "verification_status", "is_verified", "updated_at"
        ])

        WriterProfileService._create_update_log(
            writer=writer,
            updated_fields=["verification_status", "is_verified"],
            previous_values={
                "verification_status": writer.verification_status,
                "is_verified": writer.is_verified,
            },
            updated_by=verified_by,
        )

        logger.info(
            "WriterProfile verification updated: writer=%s status=%s by=%s",
            writer.registration_id,
            new_status,
            getattr(verified_by, "pk", "?"),
        )

        return writer

    # ----------------------------------------------------------------
    # SOFT DELETE / RESTORE
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def soft_delete(
        writer: WriterProfile,
        deleted_by,
        reason: str = "",
    ) -> WriterProfile:
        """
        Soft-delete a WriterProfile.

        Sets is_deleted=True and deleted_at=now().
        The writer is immediately excluded from all routing.
        Historical data (orders, payments, ratings) is preserved.

        Args:
            writer: WriterProfile to delete.
            deleted_by: Admin User performing the deletion.
            reason: Optional reason for the deletion.

        Raises:
            ValueError: If already deleted.
        """
        if writer.is_deleted:
            raise ValueError(
                f"WriterProfile {writer.registration_id} is already deleted."
            )

        writer.is_deleted = True
        writer.deleted_at = now()
        writer.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

        # Immediately disable from routing.
        from writer_management.models.writer_capacity import WriterCapacity
        WriterCapacity.objects.filter(writer=writer).update(
            can_take_orders=False,
            is_accepting_orders=False,
        )

        # Release any active order assignments so orders return to pool.
        WriterProfileService._release_writer_assignments(writer=writer, actor=deleted_by)

        # Decline any open bids so orders are not capacity-locked.
        WriterProfileService._decline_writer_interests(writer=writer)

        WriterProfileService._create_update_log(
            writer=writer,
            updated_fields=["is_deleted", "deleted_at"],
            previous_values={"is_deleted": False, "deleted_at": None},
            updated_by=deleted_by,
        )

        logger.warning(
            "WriterProfile soft-deleted: writer=%s by=%s reason=%r",
            writer.registration_id,
            getattr(deleted_by, "pk", "?"),
            reason[:80],
        )

        return writer

    @staticmethod
    def _release_writer_assignments(*, writer, actor) -> None:
        from django.utils.timezone import now as tz_now
        from orders.models.orders.order_assignment import OrderAssignment
        from orders.models.orders.constants import (
            ORDER_ASSIGNMENT_STATUS_ACTIVE,
            ORDER_ASSIGNMENT_STATUS_RELEASED,
        )
        released = OrderAssignment.objects.filter(
            writer=writer,
            status=ORDER_ASSIGNMENT_STATUS_ACTIVE,
        ).update(
            status=ORDER_ASSIGNMENT_STATUS_RELEASED,
            is_current=False,
            released_at=tz_now(),
            release_reason="writer_profile_soft_deleted",
            updated_at=tz_now(),
        )
        if released:
            logger.info(
                "_release_writer_assignments: released %s assignment(s) for writer=%s",
                released, writer.pk,
            )

    @staticmethod
    def _decline_writer_interests(*, writer) -> None:
        from django.utils.timezone import now as tz_now
        from orders.models.orders.order_interest import OrderInterest
        from orders.models.orders.constants import (
            ORDER_INTEREST_STATUS_DECLINED,
            ORDER_INTEREST_TERMINAL_STATUSES,
        )
        declined = OrderInterest.objects.filter(writer=writer).exclude(
            status__in=ORDER_INTEREST_TERMINAL_STATUSES,
        ).update(
            status=ORDER_INTEREST_STATUS_DECLINED,
            updated_at=tz_now(),
        )
        if declined:
            logger.info(
                "_decline_writer_interests: declined %s interest(s) for writer=%s",
                declined, writer.pk,
            )

    @staticmethod
    @transaction.atomic
    def restore(
        writer: WriterProfile,
        restored_by,
        reason: str = "",
    ) -> WriterProfile:
        """
        Restore a soft-deleted WriterProfile.

        Sets is_deleted=False. Does NOT automatically restore
        can_take_orders — admin must explicitly re-enable after
        verifying the writer is ready to receive orders.

        Args:
            writer: WriterProfile to restore.
            restored_by: Admin User performing the restore.
            reason: Required — why the profile is being restored.

        Raises:
            ValueError: If not deleted, or reason is blank.
        """
        if not writer.is_deleted:
            raise ValueError(
                f"WriterProfile {writer.registration_id} is not deleted."
            )

        if not reason.strip():
            raise ValueError("Reason is required when restoring a profile.")

        writer.is_deleted = False
        writer.deleted_at = None
        writer.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

        WriterProfileService._create_update_log(
            writer=writer,
            updated_fields=["is_deleted", "deleted_at"],
            previous_values={"is_deleted": True},
            updated_by=restored_by,
        )

        logger.info(
            "WriterProfile restored: writer=%s by=%s reason=%r",
            writer.registration_id,
            getattr(restored_by, "pk", "?"),
            reason[:80],
        )

        return writer

    # ----------------------------------------------------------------
    # LEVEL ASSIGNMENT
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def assign_initial_level(
        writer: WriterProfile,
        level,
        assigned_by,
    ) -> WriterProfile:
        """
        Assign an initial WriterLevel to a writer with no level.

        Used during onboarding after REVIEW_PENDING.
        For subsequent level changes use LevelProgressionService.

        Args:
            writer: WriterProfile with writer_level=None.
            level: WriterLevel to assign.
            assigned_by: Admin User.

        Raises:
            ValueError: If writer already has a level.
        """
        if writer.writer_level is not None:
            level_name = writer.writer_level.name if writer.writer_level is not None else "unknown"
            raise ValueError(
                f"Writer {writer.registration_id} already has level "
                f"'{level_name}'. "
                "Use LevelProgressionService.manual_level_change() instead."
            )

        from writer_management.models.writer_level_history import (
            WriterLevelChangeLog,
        )
        from writer_management.enums import LevelChangeType, LevelChangeTrigger

        writer.writer_level = level
        writer.save(update_fields=["writer_level", "updated_at"])

        WriterLevelChangeLog.objects.create(
            writer=writer,
            website=level.website,
            previous_level=None,
            previous_level_name="",
            new_level=level,
            new_level_name=level.name,
            change_type=LevelChangeType.INITIAL,
            triggered_by=LevelChangeTrigger.ONBOARDING,
            reason="Initial level assigned during onboarding.",
            changed_by=assigned_by,
            performance_snapshot={},
        )

        logger.info(
            "Initial level assigned: writer=%s level=%s by=%s",
            writer.registration_id,
            level.name,
            getattr(assigned_by, "pk", "?"),
        )

        return writer

    # ----------------------------------------------------------------
    # SELECTORS
    # ----------------------------------------------------------------

    @staticmethod
    def get_by_registration_id(registration_id: str) -> WriterProfile:
        """
        Fetch WriterProfile by registration_id.

        Raises:
            WriterProfileNotFoundError: If not found.
        """
        try:
            return WriterProfile.objects.select_related(
                "account_profile",
                "account_profile__user",
                "writer_level",
                "writer_level__settings",
            ).get(registration_id=registration_id)
        except WriterProfile.DoesNotExist:
            raise WriterProfileNotFoundError(
                f"No WriterProfile found with registration_id="
                f"'{registration_id}'."
            )

    @staticmethod
    def get_by_public_uuid(public_uuid) -> WriterProfile:
        """
        Fetch WriterProfile by public_uuid (API-safe identifier).

        Raises:
            WriterProfileNotFoundError: If not found.
        """
        try:
            return WriterProfile.objects.select_related(
                "account_profile",
                "writer_level",
                "writer_level__settings",
            ).get(public_uuid=public_uuid, is_deleted=False)
        except WriterProfile.DoesNotExist:
            raise WriterProfileNotFoundError(
                f"No WriterProfile found with public_uuid='{public_uuid}'."
            )

    @staticmethod
    def get_for_user(user) -> WriterProfile:
        """
        Resolve WriterProfile from a User instance.
        Chain: User → AccountProfile → WriterProfile.

        Raises:
            WriterProfileNotFoundError: If not found.
        """
        try:
            return user.account_profiles.select_related(
                "writer_profile",
                "writer_profile__writer_level",
            ).get().writer_profile
        except Exception:
            raise WriterProfileNotFoundError(
                f"No WriterProfile found for user pk={getattr(user, 'pk', '?')}."
            )

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _generate_registration_id() -> str:
        """
        Generate a unique registration ID.
        Format: WR-{YYYYMMDD}-{RANDOM6}
        Example: WR-20250113-A7X2QP

        Retries up to 10 times on collision.
        """
        for _ in range(10):
            date_part = date.today().strftime("%Y%m%d")
            random_part = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits, k=6
                )
            )
            registration_id = f"WR-{date_part}-{random_part}"

            if not WriterProfile.objects.filter(
                registration_id=registration_id
            ).exists():
                return registration_id

        raise RuntimeError(
            "Failed to generate unique registration_id after 10 attempts."
        )

    @staticmethod
    def _create_update_log(
        writer: WriterProfile,
        updated_fields: list,
        previous_values: dict,
        updated_by,
    ) -> None:
        """Create a WriterProfileUpdateLog entry."""
        try:
            from writer_management.models.logs import WriterProfileUpdateLog

            # website = (
            # writer.writer_level.website
            # if writer.writer_level
            # else None
            # )
            website = getattr(writer.writer_level, "website", None)
            if website is None:
                try:
                    website = writer.account_profile.website
                except Exception:
                    pass

            if website:
                WriterProfileUpdateLog.objects.create(
                    website=website,
                    writer=writer,
                    updated_fields=[
                        f for f in updated_fields if f != "updated_at"
                    ],
                    previous_values=previous_values,
                    updated_by=updated_by,
                )
        except Exception as exc:
            # Audit log failure must not block the main operation
            logger.exception(
                "Failed to create WriterProfileUpdateLog "
                "for writer=%s: %s",
                writer.registration_id,
                exc,
            )

    @staticmethod
    def _notify_onboarding_status(
        writer: WriterProfile,
        new_status: str,
        notes: str = "",
    ) -> None:
        """Notify writer of onboarding status change."""
        event_map = {
            WriterOnboardingStatus.DOCUMENTS_PENDING.value: (
                "writer.onboarding.documents_requested"
            ),
            WriterOnboardingStatus.REVIEW_PENDING.value: (
                "writer.onboarding.under_review"
            ),
            WriterOnboardingStatus.COMPLETED.value: (
                "writer.onboarding.completed"
            ),
            WriterOnboardingStatus.REJECTED.value: (
                "writer.onboarding.rejected"
            ),
        }

        event_key = event_map.get(new_status)
        if not event_key:
            return

        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )
            user = writer.account_profile.user
            website = (
                writer.writer_level.website
                if writer.writer_level
                else writer.account_profile.website
            )

            NotificationService.notify(
                event_key=event_key,
                recipient=user,
                website=website,
                context={
                    "registration_id": writer.registration_id,
                    "onboarding_status": new_status,
                    "notes": notes or None,
                },
            )
        except Exception as exc:
            logger.exception(
                "Onboarding status notification failed "
                "for writer=%s status=%s: %s",
                writer.registration_id,
                new_status,
                exc,
            )