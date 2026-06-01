"""
writer_management/services/availability_service.py

All mutations to WriterAvailabilityWindow and WriterAvailabilityPreference
go through this service. Views and signals never write to these models
directly.
"""

import logging

from django.db import transaction
from django.utils.timezone import now

from writer_management.models.writer_availability import (
    UnavailabilityReason,
    WriterAvailabilityPreference,
    WriterAvailabilityWindow,
)
from writer_management.models.writer_capacity import WriterCapacity

logger = logging.getLogger(__name__)


class AvailabilityService:

    # ----------------------------------------------------------------
    # WINDOWS
    # ----------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def declare_unavailable(
        writer_profile,
        start_at,
        end_at=None,
        reason: str = UnavailabilityReason.PERSONAL,
        note: str = "",
    ) -> WriterAvailabilityWindow:
        """
        Writer declares an unavailability window.

        If start_at is now or in the past, the writer is immediately
        excluded from routing. If start_at is future, they are
        excluded once that time arrives.

        Args:
            writer_profile: WriterProfile instance.
            start_at: datetime — when unavailability begins.
            end_at: datetime or None — when it ends.
            reason: UnavailabilityReason value.
            note: Optional admin-visible note.

        Returns:
            WriterAvailabilityWindow — saved.

        Raises:
            ValueError if end_at is set and not after start_at.
        """
        if end_at is not None and end_at <= start_at:
            raise ValueError(
                f"end_at ({end_at}) must be after start_at ({start_at})."
            )

        window = WriterAvailabilityWindow.objects.create(
            writer=writer_profile,
            website=writer_profile.writer_level.website
            if writer_profile.writer_level_id
            else _resolve_website(writer_profile),
            start_at=start_at,
            end_at=end_at,
            reason=reason,
            note=note,
        )

        logger.info(
            "AvailabilityWindow created: writer=%s start=%s end=%s reason=%s",
            writer_profile.registration_id,
            start_at,
            end_at,
            reason,
        )

        return window

    @staticmethod
    @transaction.atomic
    def end_window(window: WriterAvailabilityWindow) -> WriterAvailabilityWindow:
        """
        Writer ends an unavailability window early.

        Sets end_at to now, making the window immediately expired.
        The writer becomes routing-eligible again (assuming all
        other gates pass).

        Args:
            window: WriterAvailabilityWindow to end.

        Returns:
            Updated window instance.
        """
        if window.is_expired:
            logger.warning(
                "end_window called on already-expired window %s.",
                window.pk,
            )
            return window

        window.end_at = now()
        window.save(update_fields=["end_at"])

        logger.info(
            "AvailabilityWindow ended early: pk=%s writer=%s",
            window.pk,
            window.writer.id,
        )

        return window

    @staticmethod
    def get_active_window(writer_profile):
        """
        Returns the current active window for a writer or None.
        Convenience wrapper used by API views.
        """
        try:
            return writer_profile.availability_preference.get_active_window()
        except WriterAvailabilityPreference.DoesNotExist:
            return None

    @staticmethod
    def get_upcoming_windows(writer_profile):
        """
        Returns future windows not yet active.
        Used by writer dashboard.
        """
        try:
            return writer_profile.availability_preference.get_upcoming_windows()
        except WriterAvailabilityPreference.DoesNotExist:
            return WriterAvailabilityWindow.objects.none()

    # ----------------------------------------------------------------
    # INSTANT TOGGLE
    # Mutates WriterCapacity.is_accepting_orders — not availability models.
    # Included here for a single import surface for availability concerns.
    # ----------------------------------------------------------------

    @staticmethod
    def set_accepting_orders(writer_profile, accepting: bool) -> None:
        """
        Writer toggles their instant availability switch.

        Updates WriterCapacity.is_accepting_orders.
        Takes effect immediately for all subsequent routing queries.

        Args:
            writer_profile: WriterProfile instance.
            accepting: True = open to new orders. False = not.
        """
        updated = WriterCapacity.objects.filter(
            writer=writer_profile,
        ).update(is_accepting_orders=accepting)

        if updated == 0:
            logger.error(
                "WriterCapacity missing for writer %s — "
                "is_accepting_orders not updated.",
                writer_profile.registration_id,
            )
            return

        logger.info(
            "Writer %s set is_accepting_orders=%s",
            writer_profile.registration_id,
            accepting,
        )

    # ----------------------------------------------------------------
    # PREFERENCES
    # ----------------------------------------------------------------

    @staticmethod
    def update_preferences(
        writer_profile,
        preferred_start_hour=None,
        preferred_end_hour=None,
        preferred_days=None,
        auto_go_offline=None,
        auto_offline_after_minutes=None,
    ) -> WriterAvailabilityPreference:
        """
        Update writer's standing availability preferences.

        Only updates fields that are explicitly passed (not None).
        Partial update safe.

        Returns:
            Updated WriterAvailabilityPreference instance.
        """
        pref, _ = WriterAvailabilityPreference.objects.get_or_create(
            writer=writer_profile,
            defaults={
                "website": _resolve_website(writer_profile),
            },
        )

        update_fields = []

        if preferred_start_hour is not None:
            if not (0 <= preferred_start_hour <= 23):
                raise ValueError(
                    f"preferred_start_hour must be 0–23, got {preferred_start_hour}."
                )
            pref.preferred_start_hour = preferred_start_hour
            update_fields.append("preferred_start_hour")

        if preferred_end_hour is not None:
            if not (0 <= preferred_end_hour <= 23):
                raise ValueError(
                    f"preferred_end_hour must be 0–23, got {preferred_end_hour}."
                )
            pref.preferred_end_hour = preferred_end_hour
            update_fields.append("preferred_end_hour")

        if preferred_days is not None:
            invalid = [d for d in preferred_days if d not in range(7)]
            if invalid:
                raise ValueError(
                    f"preferred_days values must be 0–6. Invalid: {invalid}."
                )
            pref.preferred_days = preferred_days
            update_fields.append("preferred_days")

        if auto_go_offline is not None:
            pref.auto_go_offline = auto_go_offline
            update_fields.append("auto_go_offline")

        if auto_offline_after_minutes is not None:
            if auto_offline_after_minutes < 1:
                raise ValueError(
                    "auto_offline_after_minutes must be at least 1."
                )
            pref.auto_offline_after_minutes = auto_offline_after_minutes
            update_fields.append("auto_offline_after_minutes")

        if update_fields:
            update_fields.append("updated_at")
            pref.save(update_fields=update_fields)

        return pref


# ----------------------------------------------------------------
# PRIVATE HELPERS
# ----------------------------------------------------------------

def _resolve_website(writer_profile):
    """
    Resolve website for a writer when writer_level is not set.
    Falls back through account_profile.
    Should rarely be needed — level is usually set at profile creation.
    """
    try:
        return writer_profile.account_profile.website
    except AttributeError:
        raise ValueError(
            f"Cannot resolve website for writer {writer_profile.registration_id}. "
            "Ensure writer_level or account_profile.website is set."
        )