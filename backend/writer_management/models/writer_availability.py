"""
Writer availability system.

The writers self-manage their availability.
There is no leave system, no approval flow, no admin gate.

Three distinct layers — each answers a different question:

    WriterStatus (writer_status.py)
        "Is this writer at their keyboard right now?"
        ONLINE / OFFLINE / AWAY / BUSY
        High-churn presence data.
        Has NO effect on assignment routing.

    WriterAvailabilityPreference (this file)
        "What are this writer's standing availability settings?"
        One row per writer. Low-churn.
        Contains preferred working hours and auto-offline behaviour.

    WriterAvailabilityWindow (this file)
        "Has this writer declared a specific unavailability period?"
        Zero or more rows per writer.
        Has a start and optional end.
        An active window blocks assignment routing.

ASSIGNMENT ROUTING GATE ORDER
------------------------------
WriterEligibilityService checks in this order (cheapest first):

    1. WriterProfile.is_deleted
    2. WriterProfile.onboarding_status == COMPLETED
    3. WriterCapacity.can_take_orders (platform discipline gate)
    4. WriterCapacity.is_accepting_orders (writer instant toggle)
    5. WriterCapacity.active_orders_count < ceiling
    6. WriterDisciplineState.is_suspended / is_blacklisted
    7. WriterAvailabilityWindow active? (DB query — runs last)

WHAT LIVES WHERE
----------------
    can_take_orders → WriterCapacity (platform-controlled gate)
    is_accepting_orders → WriterCapacity (writer instant toggle)
    Online presence → WriterStatus
    Dated windows → WriterAvailabilityWindow (this file)
    Hour preferences → WriterAvailabilityPreference (this file)

DEPENDENCY
----------
    No imports from orders, writer_compensation, or tips.
"""

from django.db import models
from django.utils.timezone import now


class UnavailabilityReason(models.TextChoices):
    PERSONAL = "personal", "Personal"
    OVERLOADED = "overloaded", "Taking a Break from New Work"
    TECHNICAL = "technical", "Technical Issues"
    SCHEDULED = "scheduled", "Scheduled Unavailability"
    OTHER = "other", "Other"


class WriterAvailabilityWindow(models.Model):
    """
    A declared period during which a writer is not accepting new orders.

    Self-managed. No approval required. Effective immediately on start_at.

    Rules:
        - start_at can be in the future (advance scheduling)
        - end_at is optional — null means indefinite
        - Multiple windows can coexist — ANY active window blocks routing
        - Expired windows removed by cleanup_expired_windows Celery task

    Created by:
        Writer via availability API
        System (e.g. after auto-suspension lifts)

    Deleted by:
        Writer ending early via API
        Celery task after end_at passes
    """

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="availability_windows",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_availability_windows",
    )

    start_at = models.DateTimeField(
        db_index=True,
        help_text=(
            "When the unavailability begins. "
            "Can be in the future for advance scheduling."
        ),
    )
    end_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=(
            "When the unavailability ends. "
            "Null means indefinite — writer must end it manually."
        ),
    )

    reason = models.CharField(
        max_length=20,
        choices=UnavailabilityReason.choices,
        default=UnavailabilityReason.PERSONAL,
    )
    note = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Optional note. Visible to admins only.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Writer Availability Window"
        verbose_name_plural = "Writer Availability Windows"
        ordering = ["-start_at"]
        indexes = [
            models.Index(
                fields=["writer", "start_at", "end_at"],
                name="avail_window_writer_period_idx",
            ),
            models.Index(
                fields=["website", "start_at"],
                name="avail_window_site_start_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(end_at__isnull=True) |
                    models.Q(end_at__gt=models.F("start_at"))
                ),
                name="avail_window_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        end = self.end_at.date() if self.end_at else "open-ended"
        return (
            f"AvailabilityWindow<{self.writer.id}> "
            f"{self.start_at.date()} → {end} [{self.reason}]"
        )

    # ----------------------------------------------------------------
    # PROPERTIES — single-instance checks only
    # Use WriterEligibilityService for bulk routing.
    # ----------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """Currently blocking routing."""
        n = now()
        if self.start_at > n:
            return False
        if self.end_at is not None and self.end_at <= n:
            return False
        return True

    @property
    def is_future(self) -> bool:
        """Not yet started."""
        return self.start_at > now()

    @property
    def is_expired(self) -> bool:
        """Past its end_at."""
        if self.end_at is None:
            return False
        return self.end_at <= now()


class WriterAvailabilityPreference(models.Model):
    """
    Standing availability preferences for a writer.

    One row per writer per website.
    Created automatically by signal on WriterProfile creation.

    LOW CHURN — changes only when writer deliberately updates settings.

    Owns:
        Preferred working hours and days (informational, not routing gates)
        Auto-offline behaviour (controls WriterStatus automation)

    Does NOT own:
        is_accepting_orders → WriterCapacity
        can_take_orders → WriterCapacity
        Online presence → WriterStatus

    Key method:
        is_currently_unavailable() → queries WriterAvailabilityWindow
        Called by WriterEligibilityService as the final routing check.
    """

    writer = models.OneToOneField(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="availability_preference",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_availability_preferences",
    )

    # ----------------------------------------------------------------
    # PREFERRED WORKING HOURS
    # Informational. Interpreted in WriterProfile.timezone.
    # Never a hard routing gate.
    # ----------------------------------------------------------------

    preferred_start_hour = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Preferred start hour (0–23) in writer's timezone.",
    )
    preferred_end_hour = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Preferred end hour (0–23) in writer's timezone.",
    )
    preferred_days = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Preferred working days as integers. "
            "0=Monday … 6=Sunday. "
            "Example: [0,1,2,3,4] = Mon–Fri. "
            "Empty list means no preference."
        ),
    )

    # ----------------------------------------------------------------
    # AUTO-OFFLINE BEHAVIOUR
    # Controls WriterStatus automation only — not routing eligibility.
    # ----------------------------------------------------------------

    auto_go_offline = models.BooleanField(
        default=True,
        help_text=(
            "Set WriterStatus to OFFLINE automatically "
            "after auto_offline_after_minutes of inactivity."
        ),
    )
    auto_offline_after_minutes = models.PositiveSmallIntegerField(
        default=30,
        help_text="Minutes of inactivity before auto-offline triggers.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Availability Preference"
        verbose_name_plural = "Writer Availability Preferences"
        constraints = [
            models.UniqueConstraint(
                fields=["writer", "website"],
                name="unique_avail_pref_per_writer",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(preferred_start_hour__isnull=True) |
                    models.Q(preferred_start_hour__lte=23)
                ),
                name="avail_pref_start_hour_valid",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(preferred_end_hour__isnull=True) |
                    models.Q(preferred_end_hour__lte=23)
                ),
                name="avail_pref_end_hour_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(auto_offline_after_minutes__gte=1),
                name="avail_pref_offline_minutes_gte_1",
            ),
        ]

    def __str__(self) -> str:
        return f"AvailabilityPreference<{self.writer.id}>"

    # ----------------------------------------------------------------
    # ROUTING SUPPORT
    # ----------------------------------------------------------------

    def is_currently_unavailable(self) -> bool:
        """
        True if an active WriterAvailabilityWindow exists right now.

        One DB query. Called by WriterEligibilityService.is_eligible()
        as the final single-instance check.

        For bulk routing use WriterEligibilityService.get_eligible_queryset()
        which resolves this as a subquery — no per-row query.
        """
        n = now()
        return (
            self.writer.availability_windows
            .filter(start_at__lte=n)
            .filter(
                models.Q(end_at__isnull=True) |
                models.Q(end_at__gt=n)
            )
            .exists()
        )

    def get_active_window(self):
        """
        Current active WriterAvailabilityWindow or None.
        Used by API to explain why a writer is unavailable.
        """
        n = now()
        return (
            self.writer.availability_windows
            .filter(start_at__lte=n)
            .filter(
                models.Q(end_at__isnull=True) |
                models.Q(end_at__gt=n)
            )
            .order_by("start_at")
            .first()
        )

    def get_upcoming_windows(self):
        """
        Future windows not yet active.
        Used by writer dashboard to show scheduled unavailability.
        """
        return (
            self.writer.availability_windows
            .filter(start_at__gt=now())
            .order_by("start_at")
        )