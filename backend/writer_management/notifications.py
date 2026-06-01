"""
writer_management/notifications.py

Complete registry of notification event keys used by writer_management.

PURPOSE
-------
This file is the single source of truth for:
    1. Every event_key string used in this app
    2. What context variables each template receives
    3. Which audience receives each notification (writer vs admins)

The notifications_system app must have a template registered for
every event_key listed here. If a template is missing,
NotificationService.notify() will either raise or silently drop
the notification depending on its configuration.

HOW TO USE THIS FILE
--------------------
In services, import the constant instead of hardcoding the string:

    from writer_management.notifications import DisciplineEvents

    NotificationService.notify(
        event_key=DisciplineEvents.WARNING_ISSUED,
        ...
    )

This ensures event keys are consistent and refactorable.

TEMPLATE VARIABLES
------------------
Each event class documents the context dict keys available
to the template. The notifications_system template engine
accesses these as {{ variable_name }}.

CHANNELS
--------
Channel selection (email, in-app, SMS, push) is decided by
notifications_system based on the event_key and user preferences.
writer_management does not set channels.
"""


class DisciplineEvents:
    """Event keys for writer discipline notifications."""

    # ----------------------------------------------------------------
    # WARNINGS — sent to writer
    # ----------------------------------------------------------------

    WARNING_ISSUED = "writer.discipline.warning_issued"
    """
    Sent to: writer
    Context:
        registration_id str — writer's stable identifier
        category str — human-readable category label
        reason str — full reason text
        issued_at str — ISO 8601 timestamp
        expires_at str|null — when warning expires
        days_remaining int|null — days until expiry
        active_warning_count int — total active warnings now
    """

    WARNING_VOIDED = "writer.discipline.warning_voided"
    """
    Sent to: writer
    Context:
        registration_id str
        category str
        void_reason str
        voided_at str — ISO 8601 timestamp
    """

    WARNING_THRESHOLD_REACHED = "writer.discipline.warning_threshold_reached"
    """
    Sent to: all admins on the website
    Context:
        registration_id str
        active_warning_count int
        threshold int — the threshold that was crossed
        suggested_action str — "probation_triggered" | "suspension_triggered"
                                   | "review_recommended"
    """

    # ----------------------------------------------------------------
    # STRIKES — sent to writer
    # ----------------------------------------------------------------

    STRIKE_ISSUED = "writer.discipline.strike_issued"
    """
    Sent to: writer
    Context:
        registration_id str
        category str — human-readable category label
        reason str — public-facing reason
                              (evidence_notes is internal only)
        issued_at str — ISO 8601 timestamp
    """

    STRIKE_VOIDED = "writer.discipline.strike_voided"
    """
    Sent to: writer
    Context:
        registration_id str
        category str
        void_reason str
    """

    # ----------------------------------------------------------------
    # SUSPENSION — sent to writer
    # ----------------------------------------------------------------

    SUSPENDED = "writer.discipline.suspended"
    """
    Sent to: writer
    Context:
        registration_id str
        reason str
        end_date str|null — ISO 8601 date, null = indefinite
        auto_triggered bool
        duration_days int|null
    """

    SUSPENSION_LIFTED = "writer.discipline.suspension_lifted"
    """
    Sent to: writer
    Context:
        registration_id str
        lift_reason str
        lifted_at str — ISO 8601 timestamp
    """

    # ----------------------------------------------------------------
    # BLACKLIST — sent to writer, admins alerted separately
    # ----------------------------------------------------------------

    BLACKLISTED = "writer.discipline.blacklisted"
    """
    Sent to: writer
    is_critical: True
    Context:
        registration_id str
        reason str
        auto_triggered bool
    """

    BLACKLIST_LIFTED = "writer.discipline.blacklist_lifted"
    """
    Sent to: writer
    Context:
        registration_id str
        lift_reason str
    """

    # ----------------------------------------------------------------
    # PROBATION — sent to writer
    # ----------------------------------------------------------------

    PROBATION_PLACED = "writer.discipline.probation_placed"
    """
    Sent to: writer
    Context:
        registration_id str
        reason str
        end_date str — ISO 8601 date
        auto_triggered bool
    """

    PROBATION_ENDED = "writer.discipline.probation_ended"
    """
    Sent to: writer
    Context:
        registration_id str
        ended_at str|null — ISO 8601 timestamp
    """

    # ----------------------------------------------------------------
    # PENALTY — sent to writer
    # ----------------------------------------------------------------

    PENALTY_APPLIED = "writer.discipline.penalty_applied"
    """
    Sent to: writer
    Context:
        registration_id str
        reason str — human-readable reason label
        amount_deducted str — decimal string e.g. "15.00"
        order_id int|null
        notes str|null
    """


class LevelEvents:
    """Event keys for writer level progression notifications."""

    PROMOTED = "writer.level.promoted"
    """
    Sent to: writer
    Context:
        registration_id str
        previous_level str|null — level name before change
        new_level str — level name after change
        change_type str — "promotion"
    """

    DEMOTED = "writer.level.demoted"
    """
    Sent to: writer
    Context:
        registration_id str
        previous_level str|null
        new_level str
        change_type str — "demotion"
    """


class RewardEvents:
    """Event keys for writer reward notifications."""

    REWARD_GRANTED = "writer.reward.granted"
    """
    Sent to: writer
    Context:
        registration_id str
        reward_id int
        title str
        prize_description str
        prize_amount str — decimal string, "0.00" if non-financial
        has_financial_component bool
        awarded_at str — ISO 8601 timestamp
    """


class AvailabilityEvents:
    """Event keys for writer availability notifications."""

    WINDOW_DECLARED = "writer.availability.window_declared"
    """
    Sent to: writer (confirmation)
    Context:
        registration_id str
        start_at str — ISO 8601 datetime
        end_at str|null
        reason str — human-readable reason label
    """

    WINDOW_ENDED = "writer.availability.window_ended"
    """
    Sent to: writer (confirmation)
    Context:
        registration_id str
        ended_at str — ISO 8601 datetime
    """


class PenNameEvents:
    """Event keys for pen name change request notifications."""

    REQUEST_SUBMITTED = "writer.pen_name.request_submitted"
    """
    Sent to: admins
    Context:
        registration_id str
        current_name str
        requested_name str
        reason str
    """

    REQUEST_APPROVED = "writer.pen_name.request_approved"
    """
    Sent to: writer
    Context:
        registration_id str
        approved_name str — the new pen name now active
    """

    REQUEST_REJECTED = "writer.pen_name.request_rejected"
    """
    Sent to: writer
    Context:
        registration_id str
        requested_name str
        review_notes str — why it was rejected
    """


# ----------------------------------------------------------------
# FLAT REGISTRY — all event keys in one place
# Use for validation, documentation generation, admin tooling.
# ----------------------------------------------------------------

ALL_EVENT_KEYS: list[str] = [
    # Discipline
    DisciplineEvents.WARNING_ISSUED,
    DisciplineEvents.WARNING_VOIDED,
    DisciplineEvents.WARNING_THRESHOLD_REACHED,
    DisciplineEvents.STRIKE_ISSUED,
    DisciplineEvents.STRIKE_VOIDED,
    DisciplineEvents.SUSPENDED,
    DisciplineEvents.SUSPENSION_LIFTED,
    DisciplineEvents.BLACKLISTED,
    DisciplineEvents.BLACKLIST_LIFTED,
    DisciplineEvents.PROBATION_PLACED,
    DisciplineEvents.PROBATION_ENDED,
    DisciplineEvents.PENALTY_APPLIED,
    # Level
    LevelEvents.PROMOTED,
    LevelEvents.DEMOTED,
    # Rewards
    RewardEvents.REWARD_GRANTED,
    # Availability
    AvailabilityEvents.WINDOW_DECLARED,
    AvailabilityEvents.WINDOW_ENDED,
    # Pen name
    PenNameEvents.REQUEST_SUBMITTED,
    PenNameEvents.REQUEST_APPROVED,
    PenNameEvents.REQUEST_REJECTED,
]