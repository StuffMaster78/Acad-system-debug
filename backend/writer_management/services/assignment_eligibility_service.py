"""
writer_management/services/assignment_eligibility_service.py

Single source of truth for writer assignment eligibility.

This service owns all routing eligibility logic that was
previously scattered across WriterProfile, WriterCapacity,
and WriterStatus.

WriterProfile no longer has is_assignment_eligible.
WriterCapacity no longer has can_accept_order().
This service is the only place that answers:
    "Can this writer receive an assignment right now?"

Two entry points:
  1. is_eligible(profile)       — single writer, full check including DB
  2. get_eligible_queryset(...)  — bulk routing, single optimised query
"""

import logging

from django.db import models
from django.utils.timezone import now

logger = logging.getLogger(__name__)


class WriterEligibilityService:
    """
    Computes and explains writer assignment eligibility.

    All methods are static — no instance state.
    Import and call directly:
        from writer_management.services.assignment_eligibility_service import (
            WriterEligibilityService,
        )
        eligible = WriterEligibilityService.is_eligible(profile)
    """

    @staticmethod
    def is_eligible(profile) -> bool:
        """
        Full eligibility check for a single WriterProfile instance.

        Checks in order of cost (cheapest first, DB queries last).
        Returns False at the first failing condition.

        Call this for single-writer checks (e.g. admin dashboard,
        pre-assignment validation). For bulk routing use
        get_eligible_queryset() instead.
        """
        # --- Identity / lifecycle (in-memory, free) ---
        if profile.is_deleted:
            logger.debug("Writer %s ineligible: deleted.", profile.registration_id)
            return False

        if profile.onboarding_status != "completed":
            logger.debug(
                "Writer %s ineligible: onboarding %s.",
                profile.registration_id,
                profile.onboarding_status,
            )
            return False

        # --- Capacity (FK row — needs prefetch or select_related) ---
        try:
            capacity = profile.capacity
        except profile.__class__.capacity.RelatedObjectDoesNotExist:
            logger.warning(
                "Writer %s has no WriterCapacity row.",
                profile.registration_id,
            )
            return False

        if not capacity.can_take_orders:
            logger.debug(
                "Writer %s ineligible: can_take_orders=False.",
                profile.registration_id,
            )
            return False

        if not capacity.is_accepting_orders:
            logger.debug(
                "Writer %s ineligible: is_accepting_orders=False.",
                profile.registration_id,
            )
            return False

        effective_max = WriterEligibilityService._resolve_max_active_orders(
            profile, capacity
        )
        if capacity.active_orders_count >= effective_max:
            logger.debug(
                "Writer %s ineligible: at capacity (%d/%d).",
                profile.registration_id,
                capacity.active_orders_count,
                effective_max,
            )
            return False

        # --- Discipline state (FK row) ---
        try:
            discipline = profile.discipline_state
            if discipline.is_suspended or discipline.is_blacklisted:
                logger.debug(
                    "Writer %s ineligible: discipline state suspended=%s blacklisted=%s.",
                    profile.registration_id,
                    discipline.is_suspended,
                    discipline.is_blacklisted,
                )
                return False
        except profile.__class__.discipline_state.RelatedObjectDoesNotExist:
            # No discipline row means no active restrictions
            pass

        # --- Availability windows (DB query — last) ---
        if WriterEligibilityService._has_active_window(profile):
            logger.debug(
                "Writer %s ineligible: active availability window.",
                profile.registration_id,
            )
            return False

        return True

    @staticmethod
    def explain(profile) -> dict:
        """
        Returns a dict describing eligibility and the reason for
        any failure. Useful for admin dashboards and debugging.

        Does not short-circuit — checks all conditions.
        """
        from writer_management.models.writer_availability import WriterAvailabilityWindow

        reasons = []
        n = now()

        if profile.is_deleted:
            reasons.append("profile_deleted")

        if profile.onboarding_status != "completed":
            reasons.append(f"onboarding_incomplete:{profile.onboarding_status}")

        try:
            capacity = profile.capacity
            if not capacity.can_take_orders:
                reasons.append("platform_restricted")
            if not capacity.is_accepting_orders:
                reasons.append("not_accepting_orders")

            effective_max = WriterEligibilityService._resolve_max_active_orders(
                profile, capacity
            )
            if capacity.active_orders_count >= effective_max:
                reasons.append(
                    f"at_capacity:{capacity.active_orders_count}/{effective_max}"
                )
        except Exception:
            reasons.append("no_capacity_row")

        try:
            discipline = profile.discipline_state
            if discipline.is_suspended:
                reasons.append("suspended")
            if discipline.is_blacklisted:
                reasons.append("blacklisted")
        except Exception:
            pass

        active_window = (
            WriterAvailabilityWindow.objects
            .filter(
                writer=profile,
                start_at__lte=n,
            )
            .filter(
                models.Q(end_at__isnull=True) |
                models.Q(end_at__gt=n)
            )
            .first()
        )
        if active_window:
            reasons.append(
                f"unavailability_window:{active_window.reason}"
                f"_until:{active_window.end_at or 'indefinite'}"
            )

        return {
            "eligible": len(reasons) == 0,
            "reasons": reasons,
            "writer": profile.registration_id,
            "checked_at": n,
        }

    @staticmethod
    def get_eligible_queryset(website):
        """
        Optimised queryset for bulk assignment routing.

        Single query. All conditions applied as DB-level filters
        and annotations. No Python-level filtering.

        Returns a WriterProfile queryset — callers can chain further
        filters (e.g. preferred_subjects, level, etc.).

        Usage:
            eligible = WriterEligibilityService.get_eligible_queryset(website)
            eligible = eligible.filter(
                writer_level__name="senior",
                capacity__preferred_subjects=order.subject,
            )
        """
        from writer_management.models.writer_profile import WriterProfile
        from writer_management.models.writer_availability import WriterAvailabilityWindow

        n = now()

        active_window_subquery = WriterAvailabilityWindow.objects.filter(
            writer=models.OuterRef("pk"),
            start_at__lte=n,
        ).filter(
            models.Q(end_at__isnull=True) |
            models.Q(end_at__gt=n)
        )

        return (
            WriterProfile.objects
            .filter(
                is_deleted=False,
                onboarding_status="completed",
                writer_level__website=website,
                writer_level__is_active=True,
                # Capacity gates
                capacity__can_take_orders=True,
                capacity__is_accepting_orders=True,
            )
            # Capacity ceiling — resolved at query time using
            # override if set, otherwise level default
            .filter(
                models.Q(
                    # Override is set — use it
                    capacity__override_max_active_orders__isnull=False,
                    capacity__active_orders_count__lt=models.F(
                        "capacity__override_max_active_orders"
                    ),
                ) | models.Q(
                    # No override — use level settings default
                    capacity__override_max_active_orders__isnull=True,
                    capacity__active_orders_count__lt=models.F(
                        "writer_level__settings__max_active_orders"
                    ),
                )
            )
            # Exclude suspended or blacklisted
            .exclude(
                models.Q(discipline_state__is_suspended=True) |
                models.Q(discipline_state__is_blacklisted=True)
            )
            # Exclude writers with an active unavailability window
            .annotate(
                has_active_window=models.Exists(active_window_subquery)
            )
            .filter(has_active_window=False)
            # Prefetch everything routing needs — no N+1 in callers
            .select_related(
                "writer_level",
                "writer_level__settings",
                "capacity",
                "discipline_state",
                "availability_preference",
            )
        )

    # ----------------------------------------------------------------
    # PRIVATE HELPERS
    # ----------------------------------------------------------------

    @staticmethod
    def _resolve_max_active_orders(profile, capacity) -> int:
        """
        Ceiling resolution:
          1. capacity.override_max_active_orders  (admin per-writer override)
          2. writer_level.settings.max_active_orders  (level default)
          3. 10  (absolute fallback — should never be reached in production)
        """
        if capacity.override_max_active_orders is not None:
            return capacity.override_max_active_orders

        try:
            settings = profile.writer_level.settings
            if settings and settings.max_active_orders:
                return settings.max_active_orders
        except AttributeError:
            pass

        logger.warning(
            "Writer %s has no level or level settings — "
            "falling back to max_active_orders=10.",
            profile.registration_id,
        )
        return 10

    @staticmethod
    def _has_active_window(profile) -> bool:
        """Single existence check for an active availability window."""
        from writer_management.models.writer_availability import WriterAvailabilityWindow

        n = now()
        return (
            WriterAvailabilityWindow.objects
            .filter(
                writer=profile,
                start_at__lte=n,
            )
            .filter(
                models.Q(end_at__isnull=True) |
                models.Q(end_at__gt=n)
            )
            .exists()
        )