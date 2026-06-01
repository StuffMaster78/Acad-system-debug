"""
Site-level operational configuration for writer management.

THREE MODELS
------------

WriterConfig
    Controls the assignment workflow site-wide.
    One row per website. Created on site setup.
    Answers: can writers take orders directly, or must they request?

WriterConfigHistory
    Append-only audit log of every WriterConfig change.
    Stores a JSON snapshot of the previous values so you can
    always reconstruct what changed and when.

WriterWarningEscalationConfig
    Warning count thresholds for automatic escalation.
    One row per website.
    Read by WriterWarningService after every new warning.

WHAT WAS REMOVED
----------------
- WriterLevelConfig — superseded by WriterLevelCriteria in
  writer_level_criteria.py. Deleted.
- save() Website auto-creation override on WriterConfig.
- unique_together on WriterConfig — redundant with OneToOneField.
- Ordering by -id on WriterConfig — meaningless for a one-row model.
- "Deleted" choice on WriterConfigHistory.change_type — configs
  are never deleted, only updated.

FIELD NAME RECONCILIATION
--------------------------
Old WriterWarningEscalationConfig used:
    probation_threshold
    suspension_threshold

WriterWarningService expects:
    auto_probation_threshold
    auto_suspension_threshold

Renamed to match the service. Migration required if you have
existing data in this table.

OWNERSHIP
---------
Created by: site setup / management command seed_writer_config
Read by: WriterWarningService, DisciplineService, AssignmentService
Updated by: WriterConfigService (not yet written — admin API)
Never written to directly from views.
"""

from django.conf import settings
from django.db import models


class WriterConfig(models.Model):
    """
    Site-level operational settings for writer assignment workflow.

    One row per website. Created during site setup.

    Controls:
        takes_enabled — can writers self-assign orders?
        max_requests_per_writer — pending request cap (site default)
        max_takes_per_writer — concurrent order cap (site default)

    Per-level overrides live on WriterLevelSettings.
    Per-writer overrides live on WriterCapacity.override_max_active_orders.

    Ceiling resolution order (highest priority wins):
        1. WriterCapacity.override_max_active_orders (per writer)
        2. WriterLevelSettings.max_active_orders (per level)
        3. WriterConfig.max_takes_per_writer (site default)
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="writer_config",
    )

    # ----------------------------------------------------------------
    # ASSIGNMENT WORKFLOW
    # ----------------------------------------------------------------

    takes_enabled = models.BooleanField(
        default=True,
        help_text=(
            "If True, writers can self-assign (take) orders directly "
            "without admin approval. "
            "If False, all assignments require a WriterOrderRequest "
            "which an admin must approve."
        ),
    )

    # ----------------------------------------------------------------
    # SITE-LEVEL CAPACITY DEFAULTS
    # These are fallback values used when per-level or per-writer
    # overrides are not set.
    # ----------------------------------------------------------------

    max_requests_per_writer = models.PositiveSmallIntegerField(
        default=5,
        help_text=(
            "Maximum pending order requests a writer can hold at once. "
            "Fallback when WriterLevelSettings does not specify. "
            "Enforced by WriterOrderRequest.clean() in order_actions."
        ),
    )

    max_takes_per_writer = models.PositiveSmallIntegerField(
        default=10,
        help_text=(
            "Maximum concurrent active orders for a writer. "
            "Fallback when WriterLevelSettings.max_active_orders "
            "and WriterCapacity.override_max_active_orders are not set."
        ),
    )

    # ----------------------------------------------------------------
    # ASSIGNMENT BEHAVIOUR
    # ----------------------------------------------------------------

    auto_assign_enabled = models.BooleanField(
        default=False,
        help_text=(
            "If True, the assignment engine automatically routes "
            "orders to eligible writers without admin action. "
            "If False, assignments are always manual."
        ),
    )

    preferred_assignment_window_hours = models.PositiveSmallIntegerField(
        default=24,
        help_text=(
            "Hours before deadline within which the system "
            "sends assignment suggestions to admins. "
            "Only relevant when auto_assign_enabled=False."
        ),
    )

    # ----------------------------------------------------------------
    # AUDIT
    # ----------------------------------------------------------------

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="writer_config_updates",
    )

    class Meta:
        verbose_name = "Writer Config"
        verbose_name_plural = "Writer Configs"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(max_requests_per_writer__gte=1),
                name="writer_config_max_requests_gte_1",
            ),
            models.CheckConstraint(
                condition=models.Q(max_takes_per_writer__gte=1),
                name="writer_config_max_takes_gte_1",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    preferred_assignment_window_hours__gte=1
                ),
                name="writer_config_window_hours_gte_1",
            ),
        ]

    def __str__(self) -> str:
        mode = "takes" if self.takes_enabled else "requests"
        return f"WriterConfig<{self.website.id}> [{mode} mode]"


class WriterConfigHistory(models.Model):
    """
    Append-only audit log of WriterConfig changes.

    Created by WriterConfigService after every config update.
    Never updated after creation.

    previous_values is a JSON snapshot of ALL WriterConfig fields
    before the change — not just the changed fields. This allows
    full reconstruction of the config at any point in time.
    """

    class ChangeType(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"

    config = models.ForeignKey(
        WriterConfig,
        on_delete=models.CASCADE,
        related_name="history",
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="writer_config_history",
    )
    change_type = models.CharField(
        max_length=10,
        choices=ChangeType.choices,
        default=ChangeType.UPDATED,
    )
    previous_values = models.JSONField(
        default=dict,
        help_text=(
            "Snapshot of all WriterConfig field values BEFORE this change. "
            "Schema mirrors WriterConfig fields. "
            "Empty dict for the initial creation record."
        ),
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Optional admin note explaining why the change was made.",
    )
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Writer Config History"
        verbose_name_plural = "Writer Config History"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(
                fields=["config", "changed_at"],
                name="writer_config_history_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"WriterConfigHistory<{self.config.pk}> "
            f"[{self.change_type}] @ {self.changed_at:%Y-%m-%d %H:%M}"
        )


class WriterWarningEscalationConfig(models.Model):
    """
    Warning count thresholds for automatic escalation actions.

    One row per website. Created during site setup.

    Read by WriterWarningService._evaluate_thresholds() after
    every new warning is issued.

    Threshold logic:
        active_warnings >= admin_alert_threshold
            → notify admins (no automated action)

        active_warnings >= auto_probation_threshold
            → DisciplineService.place_on_probation() automatically
            → AND notify admins

        active_warnings >= auto_suspension_threshold
            → DisciplineService.suspend() automatically
            → AND notify admins

    "Active warnings" means:
        is_active=True AND is_voided=False
        AND (expires_at is None OR expires_at > now())

    Thresholds must be in ascending order:
        admin_alert <= auto_probation <= auto_suspension

    Setting auto_probation_threshold or auto_suspension_threshold
    to 0 disables that automatic escalation. Admin alert threshold
    cannot be disabled (always notifies admins).

    FIELD NAMES
    -----------
    These names match what WriterWarningService expects.
    Old names (probation_threshold, suspension_threshold) are
    renamed here. Run the rename migration before deploying.
    """

    website = models.OneToOneField(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="warning_escalation_config",
    )

    # ----------------------------------------------------------------
    # THRESHOLDS
    # ----------------------------------------------------------------

    admin_alert_threshold = models.PositiveSmallIntegerField(
        default=3,
        help_text=(
            "Active warning count that triggers admin notification. "
            "Cannot be 0 — admin is always alerted at this threshold. "
            "Must be <= auto_probation_threshold."
        ),
    )

    auto_probation_threshold = models.PositiveSmallIntegerField(
        default=5,
        help_text=(
            "Active warning count that triggers automatic probation. "
            "0 = auto-probation disabled — admin must act manually. "
            "Must be >= admin_alert_threshold."
        ),
    )

    auto_suspension_threshold = models.PositiveSmallIntegerField(
        default=7,
        help_text=(
            "Active warning count that triggers automatic suspension. "
            "0 = auto-suspension disabled — admin must act manually. "
            "Must be >= auto_probation_threshold."
        ),
    )

    # ----------------------------------------------------------------
    # WARNING DURATION
    # ----------------------------------------------------------------

    default_warning_duration_days = models.PositiveSmallIntegerField(
        default=30,
        help_text=(
            "Default number of days a warning remains active. "
            "After this period the warning expires and no longer "
            "counts toward escalation thresholds. "
            "Can be overridden per warning in WriterWarningService."
        ),
    )

    # ----------------------------------------------------------------
    # AUTO-SUSPENSION SETTINGS
    # ----------------------------------------------------------------

    auto_suspend_days = models.PositiveSmallIntegerField(
        default=7,
        help_text=(
            "Duration in days of a warning-triggered automatic suspension. "
            "Only used when auto_suspension_threshold is crossed. "
            "Manual suspensions set their own duration."
        ),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Writer Warning Escalation Config"
        verbose_name_plural = "Writer Warning Escalation Configs"
        constraints = [
            # Logical ordering: alert <= probation <= suspension
            models.CheckConstraint(
                condition=(
                    models.Q(auto_probation_threshold=0) |
                    models.Q(
                        admin_alert_threshold__lte=models.F(
                            "auto_probation_threshold"
                        )
                    )
                ),
                name="warning_cfg_alert_le_probation",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(auto_suspension_threshold=0) |
                    models.Q(
                        auto_probation_threshold__lte=models.F(
                            "auto_suspension_threshold"
                        )
                    )
                ),
                name="warning_cfg_probation_le_suspension",
            ),
            # Duration sanity
            models.CheckConstraint(
                condition=models.Q(default_warning_duration_days__gte=1),
                name="warning_cfg_duration_gte_1",
            ),
            models.CheckConstraint(
                condition=models.Q(auto_suspend_days__gte=1),
                name="warning_cfg_suspend_days_gte_1",
            ),
            # Admin alert threshold cannot be 0
            models.CheckConstraint(
                condition=models.Q(admin_alert_threshold__gte=1),
                name="warning_cfg_alert_threshold_gte_1",
            ),
        ]

    def __str__(self) -> str:
        return f"WriterWarningEscalationConfig<{self.website.id}>"

    @property
    def probation_enabled(self) -> bool:
        """True if auto-probation is configured."""
        return self.auto_probation_threshold > 0

    @property
    def suspension_enabled(self) -> bool:
        """True if auto-suspension is configured."""
        return self.auto_suspension_threshold > 0